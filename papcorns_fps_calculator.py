#!/usr/bin/env python3
"""
Papcorns - FPS Calculator ComfyUI Node
Calculates frames per second from frame count and video length
"""


class PapcornsFpsCalculator:
    """
    ComfyUI node for calculating FPS (frames per second).
    Takes frame count and video length to calculate frame rate.
    """
    
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "frame_count": ("INT", {"default": 30, "min": 1, "max": 999999, "step": 1}),
                "video_length": ("INT", {"default": 1, "min": 1, "max": 86400, "step": 1}),
            }
        }
    
    RETURN_TYPES = ("FLOAT",)
    RETURN_NAMES = ("FPS",)
    FUNCTION = "calculate_fps"
    CATEGORY = "Papcorns🍿"
    
    def calculate_fps(self, frame_count, video_length):
        """
        Calculate frames per second from frame count and video length.
        
        Args:
            frame_count (int): Total number of frames
            video_length (int): Video length in seconds
            
        Returns:
            Calculated FPS as float
        """
        try:
            # Calculate FPS
            fps = frame_count / video_length
            
            # Log the calculation
            print(f"🍿|FPS| Calculation: {frame_count} frames ÷ {video_length} seconds = {fps:.2f} FPS")
            
            return (fps,)
            
        except ZeroDivisionError:
            print("🍿|FPS| Error: Video length cannot be zero")
            return (0.0,)
        except Exception as e:
            print(f"🍿|FPS| Error calculating FPS: {str(e)}")
            return (0.0,)