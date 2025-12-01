import {rgthreeApi} from "./rgthree_api.js";
import {api} from "../../scripts/api.js";

/**
 * Abstract class defining information syncing for different types.
 */
class BaseModelInfoService extends EventTarget {
  constructor() {
    super();
    this.fileToInfo = new Map();
    this.init();
  }

  init() {
    api.addEventListener(
      this.apiRefreshEventString,
      this.handleAsyncUpdate.bind(this),
    );
  }

  async getInfo(file, refresh, light) {
    if (this.fileToInfo.has(file) && !refresh) {
      return this.fileToInfo.get(file);
    }
    return this.fetchInfo(file, refresh, light);
  }

  async refreshInfo(file) {
    return this.fetchInfo(file, true);
  }

  async clearFetchedInfo(file) {
    await rgthreeApi.clearModelsInfo({type: this.modelInfoType, files: [file]});
    this.fileToInfo.delete(file);
    return null;
  }

  async savePartialInfo(file, data) {
    let info = await rgthreeApi.saveModelInfo(this.modelInfoType, file, data);
    this.fileToInfo.set(file, info);
    return info;
  }

  handleAsyncUpdate(event) {
    const info = event.detail?.data;
    if (info?.file) {
      this.setFreshInfo(info.file, info);
    }
  }

  async fetchInfo(file, refresh = false, light = false) {
    let info = null;
    if (!refresh) {
      info = await rgthreeApi.getModelsInfo({type: this.modelInfoType, files: [file], light});
    } else {
      info = await rgthreeApi.refreshModelsInfo({type: this.modelInfoType, files: [file]});
    }
    info = info?.[0] ?? null;
    if (!light) {
      this.fileToInfo.set(file, info);
    }
    return info;
  }

  /**
   * Single point to set data into the info cache, and fire an event. Note, this doesn't determine
   * if the data is actually different.
   */
  setFreshInfo(file, info) {
    this.fileToInfo.set(file, info);
    // this.dispatchEvent(
    //   new CustomEvent("rgthree-model-service-lora-details", { detail: { lora: info } }),
    // );
  }
}

/**
 * Lora type implementation of ModelInfoTypeService.
 */
class LoraInfoService extends BaseModelInfoService {
  constructor() {
    super();
    this.apiRefreshEventString = "rgthree-refreshed-loras-info";
    this.modelInfoType = 'loras';
  }
}

/**
 * Checkpoint type implementation of ModelInfoTypeService.
 */
class CheckpointInfoService extends BaseModelInfoService {
  constructor() {
    super();
    this.apiRefreshEventString = "rgthree-refreshed-checkpoints-info";
    this.modelInfoType = 'checkpoints';
  }
}

export const LORA_INFO_SERVICE = new LoraInfoService();
export const CHECKPOINT_INFO_SERVICE = new CheckpointInfoService();
