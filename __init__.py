#!/usr/bin/env python3
"""
Papcorns ComfyUI Custom Nodes Package
"""

from .papcorns_aspect_resize import PapcornsAspectResize

# Export the node class mappings required by ComfyUI
NODE_CLASS_MAPPINGS = {
    "PapcornsAspectResize": PapcornsAspectResize
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "PapcornsAspectResize": "Papcorns - Aspect Resize"
}

# Define what gets imported when using "from package import *"
__all__ = [
    "PapcornsAspectResize",
    "NODE_CLASS_MAPPINGS", 
    "NODE_DISPLAY_NAME_MAPPINGS"
] 