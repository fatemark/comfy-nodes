import { app } from "../../scripts/app.js";
import { RgthreeBaseServerNode } from "./base_node.js";
import { rgthreeApi, RgthreeApi } from "../../rgthree/common/rgthree_api.js";
import { RgthreeBetterButtonWidget } from "./utils_widgets.js";
import { moveArrayItem } from "../../rgthree/common/shared_utils.js";

const powerApi = new RgthreeApi('./power/api');

async function getTextPresets() {
    return powerApi.fetchJson('/text/presets');
}

async function saveTextPreset(data) {
    return powerApi.postJson('/text/presets', data);
}

async function deleteTextPreset(data) {
    return powerApi.fetchJson('/text/presets', {
        method: "DELETE",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(data),
    });
}

class RgthreeTextPresets extends RgthreeBaseServerNode {
    constructor(title = "Text Presets (rgthree)") {
        super(title);
        this.presets = {};
        this.updating = false;
    }

    onNodeCreated() {
        super.onNodeCreated?.();

        // Find the text widget (created by backend def)
        const textWidget = this.widgets.find(w => w.name === "text");

        // Add Category Widget
        this.categoryWidget = this.addWidget("combo", "Category", "", (v) => { this.onCategoryChange(v); });

        // Add Preset Widget
        this.presetWidget = this.addWidget("combo", "Preset", "", (v) => { this.onPresetChange(v); });

        // Add Buttons
        this.addCustomWidget(new RgthreeBetterButtonWidget("💾 Save / Update", () => this.onSave()));
        this.addCustomWidget(new RgthreeBetterButtonWidget("➕ Add New", () => this.onAdd()));
        this.addCustomWidget(new RgthreeBetterButtonWidget("🗑️ Delete", () => this.onDelete()));

        // Reorder widgets: Category, Preset, Buttons..., Text
        // Buttons are added at the end by default (except addCustomWidget pushes to widgets array).
        // textWidget is already in widgets array.

        // Let's explicitly order them.
        // We want: Category, Preset, Save, Add, Delete, Text.

        const widgets = this.widgets;
        // Move textWidget to the very end
        moveArrayItem(widgets, textWidget, widgets.length - 1);

        this.refreshPresets();
    }

    async refreshPresets() {
        this.presets = await getTextPresets();
        this.updateCategoryOptions();
    }

    updateCategoryOptions() {
        const categories = Object.keys(this.presets).sort();
        this.categoryWidget.options.values = categories;

        // If current value is not in categories, select first or empty
        if (!categories.includes(this.categoryWidget.value)) {
            this.categoryWidget.value = categories.length > 0 ? categories[0] : "";
        }

        // Trigger category change to update presets
        this.onCategoryChange(this.categoryWidget.value);
    }

    onCategoryChange(category) {
        if (!this.presets[category]) {
            this.presetWidget.options.values = [];
            this.presetWidget.value = "";
            return;
        }

        const presets = Object.keys(this.presets[category]).sort();
        this.presetWidget.options.values = presets;

        if (!presets.includes(this.presetWidget.value)) {
            this.presetWidget.value = presets.length > 0 ? presets[0] : "";
        }

        this.onPresetChange(this.presetWidget.value);
    }

    onPresetChange(presetName) {
        if (this.updating) return;

        const category = this.categoryWidget.value;
        if (category && presetName && this.presets[category] && this.presets[category][presetName]) {
            const text = this.presets[category][presetName];
            const textWidget = this.widgets.find(w => w.name === "text");
            if (textWidget) {
                textWidget.value = text;
            }
        }
    }

    async onSave() {
        const category = this.categoryWidget.value;
        let presetName = this.presetWidget.value;
        const textWidget = this.widgets.find(w => w.name === "text");
        const text = textWidget ? textWidget.value : "";

        if (!category) {
            alert("Please select or add a category first.");
            return;
        }

        if (!presetName) {
            presetName = prompt("Enter preset name:");
            if (!presetName) return;
        }

        // Confirm overwrite?
        // Logic: If presetName matches dropdown value, it's an update. If different, it's a new one.
        // But prompt logic above only runs if presetName is empty.
        // User workflow for "Edit": Select preset, edit text, click Save.
        // User workflow for "New": Click "Add New".

        await saveTextPreset({ category, name: presetName, text });
        await this.refreshPresets();

        // Restore selection
        this.categoryWidget.value = category;
        this.presetWidget.value = presetName;
        // Ensure text is kept
        if (textWidget) textWidget.value = text;
    }

    async onAdd() {
        const type = prompt("Add what?\n1. New Category\n2. New Preset to current Category");
        if (type === "1") {
            const category = prompt("Enter new category name:");
            if (category) {
                // We just need to save a dummy preset or handle empty categories in backend.
                // My backend creates category if it doesn't exist when saving a preset.
                // So I need a preset name.
                const presetName = prompt("Enter first preset name for this category:");
                if (presetName) {
                    const textWidget = this.widgets.find(w => w.name === "text");
                    const text = textWidget ? textWidget.value : "";
                    await saveTextPreset({ category, name: presetName, text });
                    await this.refreshPresets();
                    this.categoryWidget.value = category;
                    this.onCategoryChange(category);
                    this.presetWidget.value = presetName;
                }
            }
        } else if (type === "2") {
            const category = this.categoryWidget.value;
            if (!category) {
                alert("No category selected.");
                return;
            }
            const presetName = prompt("Enter new preset name:");
            if (presetName) {
                const textWidget = this.widgets.find(w => w.name === "text");
                const text = textWidget ? textWidget.value : "";
                await saveTextPreset({ category, name: presetName, text });
                await this.refreshPresets();
                 // Restore selection
                this.categoryWidget.value = category;
                this.onCategoryChange(category);
                this.presetWidget.value = presetName;
            }
        }
    }

    async onDelete() {
        const category = this.categoryWidget.value;
        const presetName = this.presetWidget.value;

        if (!category || !presetName) return;

        if (confirm(`Delete preset "${presetName}" from "${category}"?`)) {
            await deleteTextPreset({ category, name: presetName });
            await this.refreshPresets();
             // Restore selection (category likely still exists)
            this.categoryWidget.value = category;
            this.onCategoryChange(category);
        }
    }
}

app.registerExtension({
    name: "rgthree.TextPresets",
    async beforeRegisterNodeDef(nodeType, nodeData) {
        if (nodeData.name === "Text Presets (rgthree)") {
            RgthreeBaseServerNode.registerForOverride(nodeType, nodeData, RgthreeTextPresets);
        }
    },
});
