#!/usr/bin/env python3
"""
Papcorns - Audio Trimmer ComfyUI Node
Trims audio files to specified duration and start time
"""

import os
import tempfile
import io
import numpy as np
from pydub import AudioSegment


class PapcornsAudioTrimmer:
    """
    ComfyUI node for trimming audio data directly in memory.
    Takes audio input and returns trimmed audio without file operations.
    """
    
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "audio": ("AUDIO",),
                "start_time_ms": ("INT", {"default": 0, "min": 0, "max": 3600000, "step": 100}),
                "duration_ms": ("INT", {"default": 7000, "min": 100, "max": 3600000, "step": 100}),
            }
        }
    
    RETURN_TYPES = ("AUDIO",)
    RETURN_NAMES = ("audio",)
    FUNCTION = "trim_audio"
    CATEGORY = "Papcorns🍿"
    
    def trim_audio(self, audio, start_time_ms, duration_ms):
        """
        Trim the audio data to specified duration and start time.
        
        Args:
            audio: Input audio data
            start_time_ms: Start time in milliseconds
            duration_ms: Duration to trim in milliseconds
            
        Returns:
            Trimmed audio data
        """
        try:
            # Extract audio data and sample rate from ComfyUI audio format
            # ComfyUI audio format: {"waveform": tensor, "sample_rate": int}
            waveform = audio["waveform"]
            sample_rate = audio["sample_rate"]
            
            # Convert tensor to numpy array for processing
            audio_array = waveform.cpu().numpy()
            
            # Calculate sample indices for trimming
            start_sample = int((start_time_ms / 1000.0) * sample_rate)
            duration_samples = int((duration_ms / 1000.0) * sample_rate)
            end_sample = min(start_sample + duration_samples, audio_array.shape[-1])
            
            # Validate start time
            if start_sample >= audio_array.shape[-1]:
                print(f"Warning: Start time ({start_time_ms}ms) exceeds audio duration")
                start_sample = 0
                end_sample = min(duration_samples, audio_array.shape[-1])
            
            # Trim the audio array
            if len(audio_array.shape) == 2:  # Stereo
                trimmed_array = audio_array[:, start_sample:end_sample]
            else:  # Mono or batch
                trimmed_array = audio_array[start_sample:end_sample]
            
            # Convert back to tensor
            import torch
            trimmed_tensor = torch.from_numpy(trimmed_array)
            
            # Return in ComfyUI audio format
            result_audio = {
                "waveform": trimmed_tensor,
                "sample_rate": sample_rate
            }
            
            original_duration_ms = (audio_array.shape[-1] / sample_rate) * 1000
            trimmed_duration_ms = (trimmed_array.shape[-1] / sample_rate) * 1000
            
            print(f"Audio trimmed successfully in memory")
            print(f"Original duration: {original_duration_ms:.0f}ms, Trimmed duration: {trimmed_duration_ms:.0f}ms")
            
            return (result_audio,)
            
        except Exception as e:
            print(f"Error processing audio: {str(e)}")
            # Return original audio on error
            return (audio,)


class PapcornsAudioTrimAndSave:
    """
    ComfyUI node for trimming audio files and saving to disk.
    Supports various audio formats and configurable start time and duration.
    """
    
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "audio_path": ("STRING", {"default": "input_audio.mp3"}),
                "start_time_ms": ("INT", {"default": 0, "min": 0, "max": 3600000, "step": 100}),
                "duration_ms": ("INT", {"default": 7000, "min": 100, "max": 3600000, "step": 100}),
                "output_format": (["mp3", "wav", "ogg", "m4a"], {"default": "mp3"}),
                "output_filename": ("STRING", {"default": "trimmed_audio"}),
            }
        }
    
    RETURN_TYPES = ("STRING",)
    RETURN_NAMES = ("output_path",)
    FUNCTION = "trim_audio"
    CATEGORY = "Papcorns🍿"
    
    def trim_audio(self, audio_path, start_time_ms, duration_ms, output_format, output_filename):
        """
        Trim the audio file to specified duration and start time.
        
        Args:
            audio_path: Path to input audio file
            start_time_ms: Start time in milliseconds
            duration_ms: Duration to trim in milliseconds
            output_format: Output audio format
            output_filename: Output filename (without extension)
            
        Returns:
            Path to the trimmed audio file
        """
        try:
            # Check if input file exists
            if not os.path.exists(audio_path):
                error_message = f"Error: Input audio file not found: {audio_path}"
                print(error_message)
                return (error_message,)
            
            # Load the audio file
            audio = AudioSegment.from_file(audio_path)
            
            # Get audio duration and validate parameters
            audio_duration = len(audio)
            
            if start_time_ms >= audio_duration:
                error_message = f"Error: Start time ({start_time_ms}ms) exceeds audio duration ({audio_duration}ms)"
                print(error_message)
                return (error_message,)
            
            # Calculate end time
            end_time_ms = min(start_time_ms + duration_ms, audio_duration)
            
            # Debug logging
            print(f"🍿|AUDIO| DEBUG: start_time_ms={start_time_ms}, duration_ms={duration_ms}, end_time_ms={end_time_ms}")
            print(f"🍿|AUDIO| DEBUG: audio_duration={audio_duration}ms")
            
            # Trim the audio using pydub slicing (milliseconds)
            # Method 1: Try direct slicing
            trimmed = audio[start_time_ms:end_time_ms]
            actual_duration_1 = len(trimmed)
            
            # Method 2: Alternative approach - extract specific segment
            if actual_duration_1 != (end_time_ms - start_time_ms):
                print(f"🍿|AUDIO| WARNING: Direct slicing failed, trying alternative method")
                # Try using pydub's built-in methods
                trimmed = audio[start_time_ms:]  # From start time to end
                if len(trimmed) > duration_ms:
                    trimmed = trimmed[:duration_ms]  # Then limit to duration
                
            # Verify the trimmed length
            actual_trimmed_duration = len(trimmed)
            expected_duration = end_time_ms - start_time_ms
            print(f"🍿|AUDIO| DEBUG: Expected trimmed duration: {expected_duration}ms")
            print(f"🍿|AUDIO| DEBUG: Actual trimmed duration: {actual_trimmed_duration}ms")
            
            # Final verification
            if actual_trimmed_duration != expected_duration:
                print(f"🍿|AUDIO| WARNING: Duration mismatch! Expected {expected_duration}ms, got {actual_trimmed_duration}ms")
            
            # Generate output path
            output_path = f"{output_filename}.{output_format}"
            
            # Export the trimmed audio
            trimmed.export(output_path, format=output_format)
            
            # Get absolute path for return
            output_path = os.path.abspath(output_path)
            
            print(f"Audio trimmed successfully: {output_path}")
            print(f"Original duration: {audio_duration}ms, Trimmed duration: {len(trimmed)}ms")
            
            return (output_path,)
            
        except Exception as e:
            error_message = f"Error processing audio: {str(e)}"
            print(error_message)
            return (error_message,)