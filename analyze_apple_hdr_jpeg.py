#!/usr/bin/env python3
"""
Apple HDR JPEG Analyzer
Analyzes Apple HDR JPEG files and extracts gain map information
"""

import argparse
import sys
import subprocess
import tempfile
from pathlib import Path
import numpy as np
from PIL import Image
import cv2

def extract_gain_map(jpeg_path, output_dir):
    """Extract gain map from Apple HDR JPEG"""
    gain_map_path = output_dir / "gain_map.jpg"
    try:
        subprocess.run([
            "exiftool", "-b", "-MPImage2", str(jpeg_path)
        ], stdout=open(gain_map_path, 'wb'), check=True)
        return gain_map_path
    except subprocess.CalledProcessError:
        return None

def analyze_gain_map_metadata(gain_map_path):
    """Analyze gain map metadata"""
    try:
        result = subprocess.run([
            "exiftool", str(gain_map_path)
        ], capture_output=True, text=True, check=True)
        return result.stdout
    except subprocess.CalledProcessError:
        return None

def analyze_main_image_metadata(jpeg_path):
    """Analyze main image metadata"""
    try:
        result = subprocess.run([
            "exiftool", str(jpeg_path)
        ], capture_output=True, text=True, check=True)
        return result.stdout
    except subprocess.CalledProcessError:
        return None

def analyze_gain_map_image(gain_map_path):
    """Analyze gain map image statistics"""
    try:
        with Image.open(gain_map_path) as img:
            gain_array = np.array(img)
            
        if len(gain_array.shape) == 3:
            gain_gray = cv2.cvtColor(gain_array, cv2.COLOR_RGB2GRAY)
        else:
            gain_gray = gain_array
        
        stats = {
            'shape': gain_gray.shape,
            'dtype': str(gain_gray.dtype),
            'min': float(gain_gray.min()),
            'max': float(gain_gray.max()),
            'mean': float(gain_gray.mean()),
            'std': float(gain_gray.std()),
            'median': float(np.median(gain_gray))
        }
        
        return stats
    except Exception as e:
        return f"Error analyzing gain map: {e}"

def main():
    parser = argparse.ArgumentParser(
        description="Analyze Apple HDR JPEG files",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s input.jpg
        """
    )
    parser.add_argument("input", help="Input Apple HDR JPEG file")
    
    args = parser.parse_args()
    
    input_path = Path(args.input)
    
    if not input_path.exists():
        print(f"Error: Input file '{input_path}' does not exist")
        sys.exit(1)
    
    print(f"Analyzing Apple HDR JPEG: {input_path}")
    print("=" * 60)
    
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_dir = Path(temp_dir)
        
        # Extract gain map
        print("1. Extracting gain map...")
        gain_map_path = extract_gain_map(input_path, temp_dir)
        if gain_map_path:
            print(f"✓ Gain map extracted: {gain_map_path}")
        else:
            print("✗ Failed to extract gain map")
            sys.exit(1)
        
        # Analyze main image metadata
        print("\n2. Main image metadata:")
        main_metadata = analyze_main_image_metadata(input_path)
        if main_metadata:
            # Extract key information
            lines = main_metadata.split('\n')
            key_info = []
            for line in lines:
                if any(keyword in line for keyword in [
                    'File Type', 'Image Size', 'Color Space', 'Color Profile',
                    'Bits Per Sample', 'Compression', 'Make', 'Model'
                ]):
                    key_info.append(line.strip())
            
            for info in key_info[:10]:  # Show first 10 relevant lines
                print(f"   {info}")
        else:
            print("   Failed to read main image metadata")
        
        # Analyze gain map metadata
        print("\n3. Gain map metadata:")
        gain_metadata = analyze_gain_map_metadata(gain_map_path)
        if gain_metadata:
            lines = gain_metadata.split('\n')
            hdr_info = []
            for line in lines:
                if any(keyword in line for keyword in [
                    'HDR Capacity', 'Gain Map', 'Gamma', 'Offset'
                ]):
                    hdr_info.append(line.strip())
            
            if hdr_info:
                for info in hdr_info:
                    print(f"   {info}")
            else:
                print("   No HDR-specific metadata found")
        else:
            print("   Failed to read gain map metadata")
        
        # Analyze gain map image
        print("\n4. Gain map image analysis:")
        gain_stats = analyze_gain_map_image(gain_map_path)
        if isinstance(gain_stats, dict):
            print(f"   Shape: {gain_stats['shape']}")
            print(f"   Data type: {gain_stats['dtype']}")
            print(f"   Min value: {gain_stats['min']}")
            print(f"   Max value: {gain_stats['max']}")
            print(f"   Mean value: {gain_stats['mean']:.3f}")
            print(f"   Standard deviation: {gain_stats['std']:.3f}")
            print(f"   Median value: {gain_stats['median']}")
        else:
            print(f"   {gain_stats}")
        
        print("\n" + "=" * 60)
        print("Analysis complete!")

if __name__ == "__main__":
    main() 