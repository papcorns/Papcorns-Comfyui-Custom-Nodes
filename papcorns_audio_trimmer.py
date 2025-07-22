#!/usr/bin/env python3
"""
Papcorns - Audio Trimmer ComfyUI Node
Trims audio files to specified duration and start time
"""

import os
import tempfile
from pydub import AudioSegment


class PapcornsAudioTrimmer:
    """
    ComfyUI node for trimming audio files.
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
            
            # Trim the audio
            trimmed = audio[start_time_ms:end_time_ms]
            
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