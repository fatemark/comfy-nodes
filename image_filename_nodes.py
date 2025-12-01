import os
import torch
from PIL import Image
import numpy as np
import folder_paths

class LoadImageGetFilename:
    """
    This node loads an image and outputs the image, mask,
    and the filename without its extension as a string.
    """
    @classmethod
    def INPUT_TYPES(s):
        # Get the list of images from the input directory
        input_dir = folder_paths.get_input_directory()
        files = [f for f in os.listdir(input_dir) if os.path.isfile(os.path.join(input_dir, f))]
        return {
            "required": {
                "image": (files, ),
            },
        }

    CATEGORY = "image"
    RETURN_TYPES = ("IMAGE", "MASK", "STRING")
    RETURN_NAMES = ("image", "mask", "filename_no_ext")
    FUNCTION = "load_image"

    def load_image(self, image):
        # --- Standard Image Loading Logic ---
        image_path = folder_paths.get_annotated_filepath(image)
        i = Image.open(image_path)
        i = i.convert("RGBA")
        image_data = np.array(i).astype(np.float32) / 255.0
        image_tensor = torch.from_numpy(image_data)[None,]
        
        # Separate image and mask
        img_out = image_tensor[:, :, :, :3]
        mask_out = image_tensor[:, :, :, 3]
        # --- End of Standard Logic ---

        # --- Get Filename Logic ---
        # os.path.basename gets just the filename (e.g., "my_image.png")
        filename_only = os.path.basename(image_path)
        # os.path.splitext splits it into a tuple (e.g., ("my_image", ".png"))
        filename_no_ext = os.path.splitext(filename_only)[0]
        # --- End of Get Filename Logic ---

        # Return all three outputs. The string must be in a tuple.
        return (img_out, mask_out, (filename_no_ext,))

class StringGetFilenameNoExt:
    """
    This node takes a string (presumed to be a filename or path)
    and outputs the filename without its extension.
    """
    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "filename_or_path": ("STRING", {"default": "ComfyUI_00001_.png"}),
            },
        }

    CATEGORY = "utils" # A good place for string utilities
    RETURN_TYPES = ("STRING",)
    RETURN_NAMES = ("filename_no_ext",)
    FUNCTION = "get_filename"

    def get_filename(self, filename_or_path):
        # Get just the filename (e.g., "my_image.png") from a full path
        filename_only = os.path.basename(filename_or_path)
        
        # Get the name without the extension (e.g., "my_image")
        filename_no_ext = os.path.splitext(filename_only)[0]
        
        # Return it in the tuple format ComfyUI expects
        return (filename_no_ext,)


class GetFilenameFromLoadedImage:
    """
    This node takes an already loaded image and a filename/path string,
    then outputs the same image plus the filename without its extension.
    """
    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "image": ("IMAGE",),
                "filename_or_path": ("STRING", {"default": "ComfyUI_00001_.png"}),
            },
        }

    CATEGORY = "image/utils"
    RETURN_TYPES = ("IMAGE", "STRING",)
    RETURN_NAMES = ("image", "filename_no_ext",)
    FUNCTION = "process"

    def process(self, image, filename_or_path):
        # Extract filename without extension
        filename_only = os.path.basename(filename_or_path)
        filename_no_ext = os.path.splitext(filename_only)[0]

        # Pass the image through unchanged
        return (image, filename_no_ext,)


# --- Node Mappings ---
# This is how ComfyUI knows about your new nodes
NODE_CLASS_MAPPINGS = {
    "LoadImageGetFilename": LoadImageGetFilename,
    "StringGetFilenameNoExt": StringGetFilenameNoExt,
    "GetFilenameFromLoadedImage": GetFilenameFromLoadedImage

}

# This is what will show up in the right-click menu
NODE_DISPLAY_NAME_MAPPINGS = {
    "LoadImageGetFilename": "Load Image (Get Filename)",
    "StringGetFilenameNoExt": "Get Filename (No Ext)",
    "GetFilenameFromLoadedImage": "Get Filename from Loaded Image",

}
