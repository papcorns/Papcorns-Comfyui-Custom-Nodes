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
                "clear_cache": ("BOOLEAN", {"default": True}),
            }
        }

    RETURN_TYPES = ("IMAGE", "STRING",)
    RETURN_NAMES = ("image", "status",)
    FUNCTION = "simple_memory_check"
    CATEGORY = "Papcorns🍿"

    def simple_memory_check(self, image, model_names, clear_cache):
        """
        Simple memory management: clear cache based on clear_cache setting.
        
        Args:
            image: Input image to pass through
            model_names (str): String containing model names for reference
            clear_cache (bool): Whether to clear the cache
            
        Returns:
            A tuple containing the passthrough image and status message.
        """
        # Get memory usage before
        ram_info = psutil.virtual_memory()
        ram_usage_percent = ram_info.percent
        ram_total_gb = ram_info.total / (1024**3)
        ram_used_gb = ram_info.used / (1024**3)
        
        vram_usage_percent = 0
        vram_total_gb = 0
        vram_used_gb = 0
        if torch.cuda.is_available():
            vram_total = comfy.model_management.get_total_memory()
            vram_free, _ = torch.cuda.mem_get_info()
            vram_used = vram_total - vram_free
            vram_total_gb = vram_total / (1024**3)
            vram_used_gb = vram_used / (1024**3)
            vram_usage_percent = (vram_used / vram_total) * 100 if vram_total > 0 else 0
        
        print(f"🍿|MEMORY| Before - RAM: {ram_used_gb:.1f}/{ram_total_gb:.1f}GB ({ram_usage_percent:.1f}%) | VRAM: {vram_used_gb:.1f}/{vram_total_gb:.1f}GB ({vram_usage_percent:.1f}%)")
        
        if clear_cache:
            # Clear all cache
            status_message = "Clearing all memory cache."
            
            # Clear models and cache
            comfy.model_management.unload_all_models()
            comfy.model_management.soft_empty_cache()
            
            # Also clear PyTorch cache if CUDA is available
            if torch.cuda.is_available():
                torch.cuda.empty_cache()
            
            # Check memory after cleaning
            ram_info_after = psutil.virtual_memory()
            ram_used_gb_after = ram_info_after.used / (1024**3)
            ram_usage_percent_after = ram_info_after.percent
            
            vram_used_gb_after = 0
            vram_usage_percent_after = 0
            if torch.cuda.is_available():
                vram_free_after, _ = torch.cuda.mem_get_info()
                vram_used_after = vram_total - vram_free_after
                vram_used_gb_after = vram_used_after / (1024**3)
                vram_usage_percent_after = (vram_used_after / vram_total) * 100 if vram_total > 0 else 0
            
            print("🍿|MEMORY| Cache cleared.")
            print(f"🍿|MEMORY| After - RAM: {ram_used_gb_after:.1f}/{ram_total_gb:.1f}GB ({ram_usage_percent_after:.1f}%) | VRAM: {vram_used_gb_after:.1f}/{vram_total_gb:.1f}GB ({vram_usage_percent_after:.1f}%)")
            
            status_message += "\nActions: Unloaded all models, cleared cache."
        else:
            status_message = "Cache clearing disabled. Memory preserved."
            print("🍿|MEMORY| Cache clearing disabled.")
            
        if model_names:
            model_names_list = [name.strip() for name in model_names.split(", ") if name.strip()]
            status_message += f"\nModel names ({len(model_names_list)}): {', '.join(model_names_list)}"
            
        return (image, status_message,)
