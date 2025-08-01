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
                "image": ("IMAGE",),
                "ram_threshold": ("INT", {"default": 70, "min": 0, "max": 100, "step": 1}),
                "vram_threshold": ("INT", {"default": 70, "min": 0, "max": 100, "step": 1}),
                "clear_models_on_exceed": ("BOOLEAN", {"default": True}),
                "clear_cache_on_exceed": ("BOOLEAN", {"default": True}),
                "model_names": ("STRING", {"default": ""}),
            }
        }

    RETURN_TYPES = ("IMAGE", "STRING",)
    RETURN_NAMES = ("image", "status",)
    FUNCTION = "manage_memory"
    CATEGORY = "Papcorns🍿"

    def manage_memory(self, image, ram_threshold, vram_threshold, clear_models_on_exceed, clear_cache_on_exceed, model_names):
        """
        Checks memory usage and clears caches if thresholds are exceeded.
        
        Args:
            image: Input image to pass through
            ram_threshold (int): The RAM usage percentage threshold.
            vram_threshold (int): The VRAM usage percentage threshold.
            clear_models_on_exceed (bool): Whether to unload all models from VRAM.
            clear_cache_on_exceed (bool): Whether to empty the PyTorch cache.
            model_names (str): String containing model names for reference.
            
        Returns:
            A tuple containing the passthrough image and status message.
        """
        # Get RAM usage
        ram_info = psutil.virtual_memory()
        ram_usage_percent = ram_info.percent
        ram_total_gb = ram_info.total / (1024**3)
        ram_used_gb = ram_info.used / (1024**3)
        
        # Get VRAM usage if CUDA is available
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
        
        status_message = f"RAM: {ram_used_gb:.1f}/{ram_total_gb:.1f}GB ({ram_usage_percent:.1f}%) | VRAM: {vram_used_gb:.1f}/{vram_total_gb:.1f}GB ({vram_usage_percent:.1f}%)"
        
        print(f"🍿|MEMORY| Before - RAM: {ram_used_gb:.1f}/{ram_total_gb:.1f}GB ({ram_usage_percent:.1f}%) | VRAM: {vram_used_gb:.1f}/{vram_total_gb:.1f}GB ({vram_usage_percent:.1f}%)")
        
        ram_exceeded = ram_usage_percent > ram_threshold
        vram_exceeded = vram_usage_percent > vram_threshold
        
        if ram_exceeded or vram_exceeded:
            # Safety check: Don't clear if RAM is critically high
            if ram_usage_percent > 90:
                status_message += f"\nWARNING: RAM critically high ({ram_usage_percent:.1f}%). Skipping cleanup to prevent OOM."
                print("🍿|MEMORY| WARNING: RAM critically high, skipping cleanup to prevent system crash.")
                if model_names:
                    model_names_list = [name.strip() for name in model_names.split(", ") if name.strip()]
                    status_message += f"\nModel names ({len(model_names_list)}): {', '.join(model_names_list)}"
                return (image, status_message,)
            
            actions_taken = []
            if ram_exceeded:
                status_message += f"\n- RAM threshold exceeded ({ram_threshold}%)"
            if vram_exceeded:
                status_message += f"\n- VRAM threshold exceeded ({vram_threshold}%)"

            if clear_models_on_exceed:
                # Clear RAM first to prevent OOM when clearing VRAM
                import gc
                gc.collect()  # Python garbage collection
                actions_taken.append("Cleared RAM")
                
                # Then safely unload models
                comfy.model_management.unload_all_models()
                actions_taken.append("Unloaded all models")
                
            if clear_cache_on_exceed:
                # Clear RAM again before VRAM operations
                import gc
                if "Cleared RAM" not in actions_taken:
                    gc.collect()
                    actions_taken.append("Cleared RAM")
                
                # Clear VRAM carefully
                comfy.model_management.soft_empty_cache()
                if torch.cuda.is_available():
                    torch.cuda.empty_cache()
                    torch.cuda.synchronize()  # Wait for operations to complete
                actions_taken.append("Cleared cache")
            
            if actions_taken:
                action_str = " and ".join(actions_taken)
                print(f"🍿|MEMORY| {action_str}.")
                
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
                
                print(f"🍿|MEMORY| After - RAM: {ram_used_gb_after:.1f}/{ram_total_gb:.1f}GB ({ram_usage_percent_after:.1f}%) | VRAM: {vram_used_gb_after:.1f}/{vram_total_gb:.1f}GB ({vram_usage_percent_after:.1f}%)")
                
                status_message += "\nActions: " + ", ".join(actions_taken) + "."
        else:
            status_message += "\nMemory usage is within thresholds. No action taken."
            print("🍿|MEMORY| Model exists and cache is not cleared.")
            
        if model_names:
            model_names_list = [name.strip() for name in model_names.split(", ") if name.strip()]
            status_message += f"\nModel names ({len(model_names_list)}): {', '.join(model_names_list)}"
            
        return (image, status_message,)

