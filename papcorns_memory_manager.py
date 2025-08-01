#!/usr/bin/env python3
"""
Papcorns - Memory Manager ComfyUI Node
A node to monitor and manage RAM and VRAM usage.
"""

import torch
import psutil
import comfy.model_management

class PapcornsMemoryManager:
    """
    ComfyUI node for monitoring and managing RAM and VRAM.
    If usage exceeds specified thresholds, it can unload models and clear the cache.
    """
    
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "ram_threshold": ("INT", {"default": 70, "min": 0, "max": 100, "step": 1}),
                "vram_threshold": ("INT", {"default": 70, "min": 0, "max": 100, "step": 1}),
                "clear_models_on_exceed": ("BOOLEAN", {"default": True}),
                "clear_cache_on_exceed": ("BOOLEAN", {"default": True}),
            }
        }

    RETURN_TYPES = ("STRING",)
    RETURN_NAMES = ("status",)
    FUNCTION = "manage_memory"
    CATEGORY = "Papcorns🍿"

    def manage_memory(self, ram_threshold, vram_threshold, clear_models_on_exceed, clear_cache_on_exceed):
        """
        Checks memory usage and clears caches if thresholds are exceeded.
        
        Args:
            ram_threshold (int): The RAM usage percentage threshold.
            vram_threshold (int): The VRAM usage percentage threshold.
            clear_models_on_exceed (bool): Whether to unload all models from VRAM.
            clear_cache_on_exceed (bool): Whether to empty the PyTorch cache.
            
        Returns:
            A string containing a status message of the operations performed.
        """
        # Get RAM usage
        ram_usage_percent = psutil.virtual_memory().percent
        
        # Get VRAM usage if CUDA is available
        vram_usage_percent = 0
        if torch.cuda.is_available():
            vram_total = comfy.model_management.get_total_memory()
            vram_free, _ = torch.cuda.mem_get_info()
            vram_used = vram_total - vram_free
            vram_usage_percent = (vram_used / vram_total) * 100 if vram_total > 0 else 0
        
        status_message = f"RAM Usage: {ram_usage_percent:.1f}% | VRAM Usage: {vram_usage_percent:.1f}%"
        
        ram_exceeded = ram_usage_percent > ram_threshold
        vram_exceeded = vram_usage_percent > vram_threshold
        
        if ram_exceeded or vram_exceeded:
            actions_taken = []
            if ram_exceeded:
                status_message += f"\n- RAM threshold exceeded ({ram_threshold}%)"
            if vram_exceeded:
                status_message += f"\n- VRAM threshold exceeded ({vram_threshold}%)"

            if clear_models_on_exceed:
                comfy.model_management.unload_all_models()
                actions_taken.append("Unloaded all models")
                
            if clear_cache_on_exceed:
                comfy.model_management.soft_empty_cache()
                actions_taken.append("Cleared cache")
            
            if actions_taken:
                status_message += "\nActions: " + ", ".join(actions_taken) + "."
        else:
            status_message += "\nMemory usage is within thresholds. No action taken."
            
        return (status_message,)

