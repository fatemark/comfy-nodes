from .server import rgthree_server
from .lora_loader import RgthreePowerLoraLoader
from .image_filename_nodes import NODE_CLASS_MAPPINGS as IMAGE_NODE_CLASS_MAPPINGS
from .image_filename_nodes import NODE_DISPLAY_NAME_MAPPINGS as IMAGE_NODE_DISPLAY_NAME_MAPPINGS

NODE_CLASS_MAPPINGS = {
    **IMAGE_NODE_CLASS_MAPPINGS,
    RgthreePowerLoraLoader.NAME: RgthreePowerLoraLoader,
}

NODE_DISPLAY_NAME_MAPPINGS = {
    **IMAGE_NODE_DISPLAY_NAME_MAPPINGS,
    RgthreePowerLoraLoader.NAME: RgthreePowerLoraLoader.NAME,
}

WEB_DIRECTORY = "./web/comfyui"

__all__ = ['NODE_CLASS_MAPPINGS', 'NODE_DISPLAY_NAME_MAPPINGS', 'WEB_DIRECTORY']
