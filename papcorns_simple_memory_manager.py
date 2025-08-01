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
            "optional": {
                "model": ("MODEL",),
            }
        }

    RETURN_TYPES = ("STRING",)
    RETURN_NAMES = ("status",)
    FUNCTION = "simple_memory_check"
    CATEGORY = "Papcorns🍿"

    def simple_memory_check(self, model=None):
        """
        Simple memory management: clear cache only if no model is provided.
        
        Args:
            model: Optional model input
            
        Returns:
            A string containing a status message of the operations performed.
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
            
        return (status_message,)
