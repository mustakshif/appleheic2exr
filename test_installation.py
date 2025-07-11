#!/usr/bin/env python3
"""
Installation Test Script
Tests if all dependencies are properly installed
"""

import sys
import subprocess
from pathlib import Path

def test_python_version():
    """Test Python version"""
    print("Testing Python version...")
    version = sys.version_info
    if version.major >= 3 and version.minor >= 8:
        print(f"✓ Python {version.major}.{version.minor}.{version.micro} - OK")
        return True
    else:
        print(f"✗ Python {version.major}.{version.minor}.{version.micro} - Requires Python 3.8+")
        return False

def test_exiftool():
    """Test ExifTool installation"""
    print("\nTesting ExifTool...")
    try:
        result = subprocess.run(["exiftool", "-ver"], 
                              capture_output=True, text=True, check=True)
        version = result.stdout.strip()
        print(f"✓ ExifTool {version} - OK")
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("✗ ExifTool not found")
        print("  Install with: brew install exiftool (macOS) or sudo apt-get install exiftool (Linux)")
        return False

def test_python_packages():
    """Test Python package dependencies"""
    print("\nTesting Python packages...")
    packages = [
        ("numpy", "numpy"),
        ("Pillow", "PIL"),
        ("opencv-python", "cv2"),
        ("OpenEXR", "OpenEXR")
    ]
    
    all_ok = True
    for package_name, import_name in packages:
        try:
            __import__(import_name)
            print(f"✓ {package_name} - OK")
        except ImportError:
            print(f"✗ {package_name} - Not installed")
            print(f"  Install with: pip install {package_name}")
            all_ok = False
    
    return all_ok

def test_platform():
    """Test platform compatibility"""
    print("\nTesting platform...")
    import platform
    system = platform.system()
    
    if system == "Darwin":
        print("✓ macOS - OK (Full support)")
        return True
    elif system == "Linux":
        print("✓ Linux - OK (Limited HEIC support)")
        return True
    elif system == "Windows":
        print("⚠ Windows - Limited support (HEIC conversion not available)")
        return True
    else:
        print(f"⚠ {system} - Unknown platform")
        return True

def main():
    print("Apple HEIC to EXR Converter - Installation Test")
    print("=" * 50)
    
    tests = [
        test_python_version,
        test_exiftool,
        test_python_packages,
        test_platform
    ]
    
    results = []
    for test in tests:
        results.append(test())
    
    print("\n" + "=" * 50)
    if all(results):
        print("✓ All tests passed! Installation is complete.")
        print("\nYou can now use the converter:")
        print("  python apple_hdr_converter.py input.jpg output.exr")
        print("  python heic_converter.py input.heic output.exr (macOS only)")
    else:
        print("✗ Some tests failed. Please install missing dependencies.")
        print("\nInstallation instructions:")
        print("1. Install ExifTool: brew install exiftool (macOS) or sudo apt-get install exiftool (Linux)")
        print("2. Install Python packages: pip install -r requirements.txt")
        sys.exit(1)

if __name__ == "__main__":
    main() 