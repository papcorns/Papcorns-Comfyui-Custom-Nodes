#!/usr/bin/env python3
"""
Papcorns ComfyUI Custom Nodes Package
"""

from .papcorns_aspect_resize import PapcornsAspectResize
from .upload_gcs_node import UploadImageToGCS
from .papcorns_audio_trimmer import PapcornsAudioTrimmer, PapcornsAudioTrimAndSave
from .papcorns_memory_manager import PapcornsMemoryManager

# Export the node class mappings required by ComfyUI
NODE_CLASS_MAPPINGS = {
    "PapcornsAspectResize": PapcornsAspectResize,
    "UploadImageToGCS": UploadImageToGCS,
    "PapcornsAudioTrimmer": PapcornsAudioTrimmer,
    "PapcornsAudioTrimAndSave": PapcornsAudioTrimAndSave,
    "PapcornsMemoryManager": PapcornsMemoryManager
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "PapcornsAspectResize": "Papcorns - Aspect Resize",
    "UploadImageToGCS": "Upload Image To GCS",
    "PapcornsAudioTrimmer": "Papcorns - Audio Trimmer",
    "PapcornsAudioTrimAndSave": "Papcorns - Audio Trim & Save",
    "PapcornsMemoryManager": "Papcorns - Memory Manager"
}

# Define what gets imported when using "from package import *"
__all__ = [
    "PapcornsAspectResize",
    "UploadImageToGCS",
    "PapcornsAudioTrimmer",
    "PapcornsAudioTrimAndSave",
    "PapcornsMemoryManager",
    "NODE_CLASS_MAPPINGS", 
    "NODE_DISPLAY_NAME_MAPPINGS"
] 