#!/usr/bin/env python3
"""
Apple HDR JPEG to EXR Converter
Converts Apple HDR JPEG files (with MPF gain maps) to EXR format
"""

import argparse
import sys
import subprocess
import tempfile
from pathlib import Path
import numpy as np
from PIL import Image
import cv2

try:
    import OpenEXR
    import Imath
    OPENEXR_AVAILABLE = True
except ImportError:
    OPENEXR_AVAILABLE = False
    print("Warning: OpenEXR not available. Install with: pip install OpenEXR")

def extract_gain_map(jpeg_path, output_dir):
    """Extract gain map from Apple HDR JPEG"""
    gain_map_path = output_dir / "gain_map.jpg"
    try:
        subprocess.run([
            "exiftool", "-b", "-MPImage2", str(jpeg_path)
        ], stdout=open(gain_map_path, 'wb'), check=True)
        print(f"✓ Extracted gain map")
        return gain_map_path
    except subprocess.CalledProcessError:
        print("✗ Failed to extract gain map")
        return None

def analyze_gain_map_metadata(gain_map_path):
    """Analyze gain map metadata"""
    try:
        result = subprocess.run([
            "exiftool", str(gain_map_path)
        ], capture_output=True, text=True, check=True)
        metadata = result.stdout
        hdr_info = {}
        
        # Extract key HDR parameters
        if "HDR Capacity Max" in metadata:
            hdr_info['max_capacity'] = float(metadata.split("HDR Capacity Max")[1].split(":")[1].split("\n")[0].strip())
        if "HDR Capacity Min" in metadata:
            hdr_info['min_capacity'] = float(metadata.split("HDR Capacity Min")[1].split(":")[1].split("\n")[0].strip())
        if "Gain Map Max" in metadata:
            hdr_info['gain_map_max'] = float(metadata.split("Gain Map Max")[1].split(":")[1].split("\n")[0].strip())
        if "Gain Map Min" in metadata:
            hdr_info['gain_map_min'] = float(metadata.split("Gain Map Min")[1].split(":")[1].split("\n")[0].strip())
        if "Gamma" in metadata:
            hdr_info['gamma'] = float(metadata.split("Gamma")[1].split(":")[1].split("\n")[0].strip())
        if "Offset SDR" in metadata:
            hdr_info['offset_sdr'] = float(metadata.split("Offset SDR")[1].split(":")[1].split("\n")[0].strip())
        if "Offset HDR" in metadata:
            hdr_info['offset_hdr'] = float(metadata.split("Offset HDR")[1].split(":")[1].split("\n")[0].strip())
            
        return hdr_info
    except subprocess.CalledProcessError as e:
        print(f"✗ Failed to read gain map metadata: {e}")
        return None

def load_images(main_image_path, gain_map_path):
    """Load main image and gain map"""
    # Load main image
    with Image.open(main_image_path) as img:
        main_array = np.array(img)
    
    # Load gain map
    with Image.open(gain_map_path) as img:
        gain_array = np.array(img)
        
        # Convert to grayscale
        if len(gain_array.shape) == 3:
            gain_gray = cv2.cvtColor(gain_array, cv2.COLOR_RGB2GRAY)
        else:
            gain_gray = gain_array
    
    return main_array, gain_gray

def apply_gain_map(main_array, gain_gray, hdr_info):
    """Apply gain map to synthesize HDR"""
    # Convert to float
    main_float = main_array.astype(np.float32) / 255.0
    gain_float = gain_gray.astype(np.float32) / 255.0
    
    # Get HDR parameters
    max_capacity = hdr_info.get('max_capacity', 3.0)
    min_capacity = hdr_info.get('min_capacity', 0.0)
    gamma = hdr_info.get('gamma', 1.0)
    offset_sdr = hdr_info.get('offset_sdr', 0.0)
    
    # Resize gain map if needed
    if gain_float.shape != main_float.shape[:2]:
        gain_float = cv2.resize(gain_float, (main_float.shape[1], main_float.shape[0]), 
                               interpolation=cv2.INTER_LANCZOS4)
    
    # Apply offset and gamma correction
    gain_float = np.clip(gain_float + offset_sdr, 0.0, 1.0)
    if gamma != 1.0:
        gain_float = np.power(gain_float, gamma)
    
    # Calculate headroom
    if min_capacity > 0:
        headroom = max_capacity / min_capacity
    else:
        headroom = max_capacity
    
    # Apply gain map algorithm: HDR = SDR × (1 + (headroom - 1) × gain_map)
    scale_factor = 1.0 + (headroom - 1.0) * gain_float
    hdr_result = main_float * scale_factor[:, :, np.newaxis]
    
    # Clip to reasonable range
    hdr_result = np.clip(hdr_result, 0.0, headroom)
    
    return hdr_result

def apply_tone_mapping(hdr_array):
    """Apply Reinhard tone mapping"""
    # Calculate luminance
    luminance = 0.2126 * hdr_array[:, :, 0] + 0.7152 * hdr_array[:, :, 1] + 0.0722 * hdr_array[:, :, 2]
    luminance = np.clip(luminance, 1e-6, None)
    
    # Reinhard tone mapping
    scale = 1.0 / (1.0 + luminance)
    tone_mapped = hdr_array * scale[:, :, np.newaxis]
    tone_mapped = np.clip(tone_mapped, 0.0, 1.0)
    
    return tone_mapped

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
        description="Convert Apple HDR JPEG to EXR",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s input.jpg
  %(prog)s input.jpg --output custom_output.exr
  %(prog)s input.jpg --tone-mapping
        """
    )
    parser.add_argument("input", help="Input Apple HDR JPEG file")
    parser.add_argument("--output", "-o", help="Output EXR file path (default: input_name.exr)")
    parser.add_argument("--tone-mapping", action="store_true",
                       help="Apply tone mapping to reduce brightness")
    
    args = parser.parse_args()
    
    input_path = Path(args.input)
    
    # Generate output path if not specified
    if args.output:
        output_path = Path(args.output)
    else:
        # Default: same name as input but with .exr extension
        output_path = input_path.with_suffix('.exr')
    
    if not input_path.exists():
        print(f"Error: Input file '{input_path}' does not exist")
        sys.exit(1)
    
    if not input_path.suffix.lower() in ['.jpg', '.jpeg']:
        print(f"Error: Input file must be a JPEG file")
        sys.exit(1)
    
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_dir = Path(temp_dir)
        
        try:
            print(f"Processing Apple HDR JPEG: {input_path}")
            
            # Extract gain map
            gain_map_path = extract_gain_map(input_path, temp_dir)
            if not gain_map_path:
                print("Failed to extract gain map")
                sys.exit(1)
            
            # Analyze metadata
            hdr_info = analyze_gain_map_metadata(gain_map_path)
            if not hdr_info:
                print("Failed to read gain map metadata")
                sys.exit(1)
            
            # Load images
            main_array, gain_gray = load_images(input_path, gain_map_path)
            
            # Synthesize HDR
            hdr_result = apply_gain_map(main_array, gain_gray, hdr_info)
            
            # Apply tone mapping if requested
            if args.tone_mapping:
                hdr_result = apply_tone_mapping(hdr_result)
            
            # Save result as EXR
            save_exr(hdr_result, output_path)
            print(f"✓ Saved as EXR: {output_path}")
            
        except Exception as e:
            print(f"Error during processing: {e}")
            sys.exit(1)

if __name__ == "__main__":
    main() 