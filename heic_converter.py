#!/usr/bin/env python3
"""
HEIC to EXR Converter (macOS only)
Converts HEIC files to EXR format using macOS sips tool
"""

import argparse
import sys
import subprocess
import platform
from pathlib import Path
import numpy as np
import cv2

try:
    import OpenEXR
    import Imath
    OPENEXR_AVAILABLE = True
except ImportError:
    OPENEXR_AVAILABLE = False
    print("Warning: OpenEXR not available. Install with: pip install OpenEXR")

def check_macos():
    """Check if running on macOS"""
    if platform.system() != "Darwin":
        print("Error: HEIC conversion requires macOS (sips tool)")
        return False
    return True

def convert_heic_to_tiff(heic_path, tiff_path):
    """Convert HEIC to TIFF using sips"""
    try:
        subprocess.run([
            "sips", "-s", "format", "tiff", str(heic_path), "--out", str(tiff_path)
        ], check=True)
        print(f"✓ Converted HEIC to TIFF")
        return True
    except subprocess.CalledProcessError as e:
        print(f"✗ Failed to convert HEIC: {e}")
        return False

def load_tiff_as_float(tiff_path):
    """Load TIFF as float array"""
    img = cv2.imread(str(tiff_path), cv2.IMREAD_UNCHANGED)
    if img is None:
        raise ValueError("Failed to load TIFF file")
    
    # Convert BGR to RGB
    if len(img.shape) == 3:
        img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    
    # Convert to float
    if img.dtype == np.uint8:
        img = img.astype(np.float32) / 255.0
    elif img.dtype == np.uint16:
        img = img.astype(np.float32) / 65535.0
    
    return img

def save_exr(hdr_array, output_path):
    """Save as EXR file"""
    if not OPENEXR_AVAILABLE:
        raise RuntimeError("OpenEXR not available. Install with: pip install OpenEXR")
    
    if hdr_array.dtype != np.float32:
        hdr_array = hdr_array.astype(np.float32)
    
    channels = {
        "R": hdr_array[:, :, 0].copy(),
        "G": hdr_array[:, :, 1].copy(),
        "B": hdr_array[:, :, 2].copy()
    }
    
    header = OpenEXR.Header(hdr_array.shape[1], hdr_array.shape[0])
    header['channels'] = {
        'R': Imath.Channel(Imath.PixelType(Imath.PixelType.FLOAT)),
        'G': Imath.Channel(Imath.PixelType(Imath.PixelType.FLOAT)),
        'B': Imath.Channel(Imath.PixelType(Imath.PixelType.FLOAT))
    }
    header['compression'] = Imath.Compression(Imath.Compression.ZIP_COMPRESSION)
    
    exr_file = OpenEXR.OutputFile(str(output_path), header)
    exr_file.writePixels(channels)
    exr_file.close()

def main():
    parser = argparse.ArgumentParser(
        description="Convert HEIC to EXR (macOS only)",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s input.heic output.exr
        """
    )
    parser.add_argument("input", help="Input HEIC file")
    parser.add_argument("output", help="Output EXR file")
    
    args = parser.parse_args()
    
    if not check_macos():
        sys.exit(1)
    
    input_path = Path(args.input)
    output_path = Path(args.output)
    
    if not input_path.exists():
        print(f"Error: Input file '{input_path}' does not exist")
        sys.exit(1)
    
    if not input_path.suffix.lower() in ['.heic', '.heif']:
        print(f"Error: Input file must be a HEIC/HEIF file")
        sys.exit(1)
    
    if output_path.suffix.lower() != '.exr':
        print(f"Error: Output file must have .exr extension")
        sys.exit(1)
    
    try:
        print(f"Processing HEIC file: {input_path}")
        
        # Create temporary TIFF file
        temp_tiff = output_path.with_suffix('.tiff')
        
        # Convert HEIC to TIFF
        if not convert_heic_to_tiff(input_path, temp_tiff):
            sys.exit(1)
        
        # Load TIFF as float
        hdr_array = load_tiff_as_float(temp_tiff)
        
        # Save as EXR
        save_exr(hdr_array, output_path)
        print(f"✓ Saved as EXR: {output_path}")
        
        # Clean up temporary file
        temp_tiff.unlink()
        
    except Exception as e:
        print(f"Error during processing: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main() 