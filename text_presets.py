from .constants import get_category, get_name

NODE_NAME = get_name('Text Presets')

class RgthreeTextPresets:
    """A node that allows saving and loading text presets."""

    NAME = NODE_NAME
    CATEGORY = get_category()

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "text": ("STRING", {"multiline": True, "default": ""}),
            },
        }

    RETURN_TYPES = ("STRING",)
    RETURN_NAMES = ("text",)
    FUNCTION = "get_text"

    def get_text(self, text):
        return (text,)
