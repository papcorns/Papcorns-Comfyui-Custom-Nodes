#!/usr/bin/env python3
"""
Papcorns - Simple Memory Manager ComfyUI Node
A simple node that clears memory cache only if no model is connected.
"""

import torch
import psutil
import comfy.model_management

class PapcornsSimpleMemoryManager:
    """
    ComfyUI node for simple memory management.
    If a model is connected, it passes through. If no model, it clears all cache.
    """
    
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "image": ("IMAGE",),
                "model_names": ("STRING", {"default": ""}),
            },
            "optional": {
                "model": ("MODEL",),
            }
        }

    RETURN_TYPES = ("IMAGE", "STRING",)
    RETURN_NAMES = ("image", "status",)
    FUNCTION = "simple_memory_check"
    CATEGORY = "Papcorns🍿"

    def simple_memory_check(self, image, model_names, model=None):
        """
        Simple memory management: clear cache only if no model is provided.
        
        Args:
            image: Input image to pass through
            model_names (str): String containing model names for reference
            model: Optional model input
            
        Returns:
            A tuple containing the passthrough image and status message.
        """
        if model is not None:
            # Model exists, don't clear cache
            status_message = "Model is connected. Memory cache preserved."
            print("🍿|MEMORY| Model exists and cache is not cleared.")
        else:
            # No model provided, clear all cache
            status_message = "No model connected. Clearing all memory cache."
            
            # Clear models and cache
            comfy.model_management.unload_all_models()
            comfy.model_management.soft_empty_cache()
            
            # Also clear PyTorch cache if CUDA is available
            if torch.cuda.is_available():
                torch.cuda.empty_cache()
            
            print("🍿|MEMORY| Cache cleared - no model detected.")
            status_message += "\nActions: Unloaded all models, cleared cache."
            
        if model_names:
            status_message += f"\nModel names: {model_names}"
            
        return (image, status_message,)
