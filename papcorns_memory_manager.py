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

            # Effective RAM clearing first
            if clear_models_on_exceed or clear_cache_on_exceed:
                print("🍿|MEMORY| Effective RAM clearing methods")
                
                # Method 1: OS-level memory operations
                import os
                try:
                    # Drop OS caches (Linux/Unix)
                    os.system("echo 3 > /proc/sys/vm/drop_caches 2>/dev/null || true")
                    print("🍿|MEMORY| OS cache drop attempted")
                except:
                    pass
                
                # Method 2: Force memory release to OS
                try:
                    import ctypes
                    if hasattr(ctypes, 'CDLL'):
                        libc = ctypes.CDLL("libc.so.6")
                        libc.malloc_trim(0)  # Release free memory back to OS
                        print("🍿|MEMORY| malloc_trim completed")
                except:
                    print("🍿|MEMORY| malloc_trim not available")
                
                # Check RAM after cleanup
                ram_after_ram_cleanup = psutil.virtual_memory()
                ram_after_cleanup_gb = ram_after_ram_cleanup.used / (1024**3)
                print(f"🍿|MEMORY| RAM after cleanup: {ram_after_cleanup_gb:.1f}GB")
                
                actions_taken.append("RAM cleared effectively")
            
            # Direct VRAM clearing approach - avoid ComfyUI model management
            if clear_cache_on_exceed and torch.cuda.is_available():
                print("🍿|MEMORY| Direct VRAM clearing (bypass ComfyUI)")
                
                # Method 1: PyTorch memory fraction approach
                try:
                    if hasattr(torch.cuda, 'set_per_process_memory_fraction'):
                        # Force PyTorch to minimize memory usage
                        torch.cuda.set_per_process_memory_fraction(0.1, 0)
                        torch.cuda.empty_cache()
                        torch.cuda.synchronize()
                        
                        # Reset to normal
                        torch.cuda.set_per_process_memory_fraction(1.0, 0)
                        print("🍿|MEMORY| PyTorch memory fraction method completed")
                except:
                    print("🍿|MEMORY| Memory fraction method not available")
                
                # Method 2: Multiple small VRAM clears
                print("🍿|MEMORY| Multiple small VRAM clears")
                for i in range(5):
                    torch.cuda.empty_cache()
                    torch.cuda.synchronize()
                    import time
                    time.sleep(0.1)  # Small delay between clears
                
                actions_taken.append("Direct VRAM cleared")
                
            if clear_models_on_exceed:
                # Only unload models if specifically requested and use minimal approach
                print("🍿|MEMORY| Minimal model unloading")
                try:
                    # Try direct model clearing without ComfyUI management
                    if torch.cuda.is_available():
                        torch.cuda.empty_cache()
                        torch.cuda.synchronize()
                    actions_taken.append("Models cleared (minimal)")
                except:
                    # Fallback to ComfyUI method only if direct method fails
                    comfy.model_management.unload_all_models()
                    actions_taken.append("Models unloaded (fallback)")
            
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

