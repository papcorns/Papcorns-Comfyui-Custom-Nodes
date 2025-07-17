#!/usr/bin/env python3
"""
Papcorns ComfyUI Custom Nodes Package
"""

from .papcorns_aspect_resize import PapcornsAspectResize
from .upload_gcs_node import UploadImageToGCS

# Export the node class mappings required by ComfyUI
NODE_CLASS_MAPPINGS = {
    "PapcornsAspectResize": PapcornsAspectResize,
    "UploadImageToGCS": UploadImageToGCS
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "PapcornsAspectResize": "Papcorns - Aspect Resize",
    "UploadImageToGCS": "Upload Image To GCS"
}

# Define what gets imported when using "from package import *"
__all__ = [
    "PapcornsAspectResize",
    "UploadImageToGCS",
    "NODE_CLASS_MAPPINGS", 
    "NODE_DISPLAY_NAME_MAPPINGS"
] 