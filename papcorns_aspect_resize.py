#!/usr/bin/env python3
"""
Papcorns - Aspect Resize ComfyUI Node
Aspect Fill: zoom in (scale with max factor) and crop to exact target dimensions
Aspect Fit: scale to fit within target dimensions and add padding to reach exact size
"""

import torch
import numpy as np
from PIL import Image


class PapcornsAspectResize:
    """
    ComfyUI node for aspect resize image processing.
    Supports both aspect fill (zoom + crop) and aspect fit (scale + pad) modes.
    """
    
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "image": ("IMAGE",),
                "width": ("INT", {"default": 640, "min": 64, "max": 8192, "step": 8}),
                "height": ("INT", {"default": 640, "min": 64, "max": 8192, "step": 8}),
                "mode": (["aspect_fill", "aspect_fit"], {"default": "aspect_fill"}),
                "padding_color": (["black", "white"], {"default": "black"}),
            }
        }
    
    RETURN_TYPES = ("IMAGE",)
    RETURN_NAMES = ("image",)
    FUNCTION = "aspect_resize"
    CATEGORY = "Papcorns🍿"
    
    def aspect_resize(self, image, width, height, mode, padding_color):
        """
        Process the image using aspect resize algorithm.
        
        Args:
            image: Input image tensor [batch, height, width, channels]
            width: Target width
            height: Target height
            mode: "aspect_fill" or "aspect_fit"
            padding_color: "black" or "white"
            
        Returns:
            Processed image tensor
        """
        # Process each image in the batch
        batch_size = image.shape[0]
        results = []
        
        for i in range(batch_size):
            # Convert from ComfyUI tensor format to PIL
            img_tensor = image[i]
            # Convert from [H, W, C] float32 (0-1) to PIL Image
            img_array = (img_tensor.cpu().numpy() * 255).astype(np.uint8)
            pil_image = Image.fromarray(img_array)
            
            # Apply aspect resize processing
            if mode == "aspect_fill":
                processed_pil = self._aspect_fill(pil_image, width, height)
            else:  # aspect_fit
                processed_pil = self._aspect_fit(pil_image, width, height, padding_color)
            
            # Convert back to ComfyUI tensor format
            processed_array = np.array(processed_pil).astype(np.float32) / 255.0
            processed_tensor = torch.from_numpy(processed_array)
            results.append(processed_tensor)
        
        # Stack back into batch format
        result_batch = torch.stack(results, dim=0)
        
        return (result_batch,)
    
    def _aspect_fill(self, im: Image.Image, target_w: int, target_h: int) -> Image.Image:
        """
        Aspect fill: zoom in and crop to exact target dimensions.
        
        Args:
            im: PIL Image
            target_w: Target width
            target_h: Target height
            
        Returns:
            Processed PIL Image
        """
        src_w, src_h = im.size
        
        # Calculate scale factors for both dimensions
        scale_w = target_w / src_w
        scale_h = target_h / src_h
        
        # Use maximum scale factor (zoom in to cover target area)
        scale = max(scale_w, scale_h)
        
        # Scale the image (zoom in)
        new_size = (round(src_w * scale), round(src_h * scale))
        im = im.resize(new_size, Image.Resampling.LANCZOS)
        
        # Center crop to exact target dimensions
        left = (im.width - target_w) // 2
        top = (im.height - target_h) // 2
        right = left + target_w
        bottom = top + target_h
        
        return im.crop((left, top, right, bottom))
    
    def _aspect_fit(self, im: Image.Image, target_w: int, target_h: int, padding_color: str) -> Image.Image:
        """
        Aspect fit: scale to fit within target dimensions and add padding.
        
        Args:
            im: PIL Image
            target_w: Target width
            target_h: Target height
            padding_color: "black" or "white"
            
        Returns:
            Processed PIL Image
        """
        src_w, src_h = im.size
        
        # Calculate scale factors for both dimensions
        scale_w = target_w / src_w
        scale_h = target_h / src_h
        
        # Use minimum scale factor (fit within target area)
        scale = min(scale_w, scale_h)
        
        # Scale the image (fit within)
        new_size = (round(src_w * scale), round(src_h * scale))
        im = im.resize(new_size, Image.Resampling.LANCZOS)
        
        # Create canvas with target dimensions
        bg_color = (0, 0, 0) if padding_color == "black" else (255, 255, 255)
        result = Image.new('RGB', (target_w, target_h), bg_color)
        
        # Center the scaled image on the canvas
        x = (target_w - im.width) // 2
        y = (target_h - im.height) // 2
        result.paste(im, (x, y))
        
        return result


# ComfyUI node mapping
NODE_CLASS_MAPPINGS = {
    "PapcornsAspectResize": PapcornsAspectResize
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "PapcornsAspectResize": "Papcorns - Aspect Resize"
} 