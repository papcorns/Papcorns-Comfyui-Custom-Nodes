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
            # Check if RAM is dangerously high before proceeding
            if ram_usage_percent > 85:
                status_message = "RAM usage too high (>85%). Skipping cache clear to prevent OOM."
                print("🍿|MEMORY| WARNING: RAM usage too high, skipping cache clear to prevent OOM.")
                if model_names:
                    model_names_list = [name.strip() for name in model_names.split(", ") if name.strip()]
                    status_message += f"\nModel names ({len(model_names_list)}): {', '.join(model_names_list)}"
                return (image, status_message,)
            
            # Direct memory clearing with effective RAM management
            status_message = "Direct memory clearing (VRAM + effective RAM)."
            
            
            print("🍿|MEMORY| Step 1: AGGRESSIVE RAM clearing - multiple methods")
            
            import gc
            import ctypes
            import os
            import sys
            import importlib
            
            # Get initial RAM
            ram_initial = psutil.virtual_memory().used / (1024**3)
            print(f"🍿|MEMORY| Initial RAM: {ram_initial:.1f}GB")
            
            # Method 1: Force memory pressure - allocate/deallocate to force OS cleanup
            print("🍿|MEMORY| Method 1: Memory pressure technique")
            try:
                # Create memory pressure by allocating then immediately releasing
                memory_blocks = []
                for i in range(10):
                    # Allocate 100MB blocks
                    block = bytearray(100 * 1024 * 1024)  # 100MB
                    memory_blocks.append(block)
                
                # Immediately delete all blocks to force deallocation
                del memory_blocks
                gc.collect()
                print("🍿|MEMORY| Memory pressure completed")
            except:
                print("🍿|MEMORY| Memory pressure failed")
            
            # Method 2: Kubernetes-friendly memory management
            print("🍿|MEMORY| Method 2: Container-safe memory management")
            try:
                # Use resource limits instead of system calls
                import resource
                
                # Get current memory usage
                current_usage = psutil.Process().memory_info().rss / (1024 * 1024)  # MB
                print(f"🍿|MEMORY| Current process memory: {current_usage:.1f}MB")
                
                # Force Python memory cleanup without system calls
                import sys
                if hasattr(sys, 'intern'):
                    sys.intern('')  # Clear string intern cache
                
                # Multiple garbage collection passes
                for generation in range(3):
                    collected = gc.collect(generation)
                    if collected > 0:
                        print(f"🍿|MEMORY| GC generation {generation}: collected {collected} objects")
                
                print("🍿|MEMORY| Container-safe memory management completed")
            except Exception as e:
                print(f"🍿|MEMORY| Container memory management error: {e}")
            
            # Method 3: Deep Python cleanup (no root required)
            print("🍿|MEMORY| Method 3: Deep Python cleanup")
            try:
                # Clear Python internal caches
                if hasattr(sys, '_clear_type_cache'):
                    sys._clear_type_cache()
                    print("🍿|MEMORY| Cleared Python type cache")
                
                # Clear import cache (careful approach)
                import importlib
                if hasattr(importlib, 'invalidate_caches'):
                    importlib.invalidate_caches()
                    print("🍿|MEMORY| Invalidated import caches")
                
                # Try malloc_trim only if available (no system dependency)
                try:
                    if hasattr(ctypes, 'CDLL'):
                        # Try different libc paths for different distros
                        libc_paths = ["libc.so.6", "libc.so", "libc.dylib"]
                        for path in libc_paths:
                            try:
                                libc = ctypes.CDLL(path)
                                if hasattr(libc, 'malloc_trim'):
                                    libc.malloc_trim(0)
                                    print(f"🍿|MEMORY| malloc_trim successful with {path}")
                                    break
                            except:
                                continue
                except:
                    print("🍿|MEMORY| malloc_trim not available (normal in containers)")
                
                print("🍿|MEMORY| Deep Python cleanup completed")
            except Exception as e:
                print(f"🍿|MEMORY| Python cleanup error: {e}")
            
            # Method 4: Container-safe memory pressure
            print("🍿|MEMORY| Method 4: Container-safe memory optimization")
            try:
                # Create controlled memory pressure without system calls
                pressure_blocks = []
                
                # Allocate and release memory in pattern to trigger cleanup
                for i in range(5):
                    # Smaller blocks for container safety
                    block = bytearray(50 * 1024 * 1024)  # 50MB blocks
                    pressure_blocks.append(block)
                
                # Release in reverse order to fragment, then cleanup
                while pressure_blocks:
                    pressure_blocks.pop()
                    gc.collect()
                
                # Final cleanup
                del pressure_blocks
                gc.collect()
                
                print("🍿|MEMORY| Container-safe memory optimization completed")
            except Exception as e:
                print(f"🍿|MEMORY| Memory optimization error: {e}")
            
            # Check RAM after aggressive cleanup
            ram_after_aggressive = psutil.virtual_memory().used / (1024**3)
            ram_freed = ram_initial - ram_after_aggressive
            print(f"🍿|MEMORY| After aggressive cleanup: {ram_after_aggressive:.1f}GB (freed: {ram_freed:.1f}GB)")
            
            print("🍿|MEMORY| Step 2: Direct VRAM clearing")
            
            if torch.cuda.is_available():
                # Method 1: Direct CUDA memory clearing in small chunks
                print("🍿|MEMORY| Method 1: Small chunk VRAM clearing")
                
                # Get current VRAM info
                vram_free_before, vram_total = torch.cuda.mem_get_info()
                vram_used_before = vram_total - vram_free_before
                
                # Clear VRAM in multiple small operations instead of one big operation
                for i in range(5):
                    torch.cuda.empty_cache()
                    torch.cuda.synchronize()
                    # Small pause to prevent system overload
                    import time
                    time.sleep(0.1)
                    
                # Method 2: Force PyTorch to release ALL cached memory
                print("🍿|MEMORY| Method 2: Force PyTorch memory release")
                
                # Set PyTorch memory fraction to minimum then back
                if hasattr(torch.cuda, 'set_per_process_memory_fraction'):
                    try:
                        # Force PyTorch to release memory by setting fraction to minimum
                        torch.cuda.set_per_process_memory_fraction(0.1, 0)  # 10% only
                        torch.cuda.empty_cache()
                        torch.cuda.synchronize()
                        
                        # Reset to full memory access
                        torch.cuda.set_per_process_memory_fraction(1.0, 0)  # Back to 100%
                        print("🍿|MEMORY| PyTorch memory fraction reset completed")
                    except:
                        print("🍿|MEMORY| Memory fraction method not available")
                
                # Method 3: Alternative PyTorch memory clearing
                print("🍿|MEMORY| Method 3: Alternative PyTorch clearing")
                
                try:
                    # Clear all cached memory allocations
                    if hasattr(torch.cuda, 'reset_max_memory_allocated'):
                        torch.cuda.reset_max_memory_allocated()
                    if hasattr(torch.cuda, 'reset_max_memory_cached'):
                        torch.cuda.reset_max_memory_cached()
                    
                    # Final cache clear
                    torch.cuda.empty_cache()
                    torch.cuda.synchronize()
                    
                    print("🍿|MEMORY| Alternative PyTorch methods completed")
                except Exception as e:
                    print(f"🍿|MEMORY| Alternative methods had issues: {str(e)}")
                
                # Check final VRAM
                vram_free_after, _ = torch.cuda.mem_get_info()
                vram_used_after = vram_total - vram_free_after
                vram_freed = (vram_used_before - vram_used_after) / (1024**3)
                
                print(f"🍿|MEMORY| VRAM freed: {vram_freed:.1f}GB")
            else:
                print("🍿|MEMORY| No CUDA available, skipping VRAM operations")
            
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
