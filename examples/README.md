# Examples

This directory contains example files and outputs demonstrating the Apple HEIC to EXR Converter.

## Sample Files

### Input Files
- `sample_apple_hdr.jpg` - Apple HDR JPEG file exported from Mac Photos app
- `sample_heic.heic` - Apple HDR HEIC file (native format)

### Output Files
- `sample_output.exr` - EXR output from Apple HDR JPEG conversion (preserves HDR gain map)
- `sample_heic_output.exr` - EXR output from HEIC conversion (base image only)

## Usage Examples

### Convert Apple HDR JPEG (Recommended)
```bash
# From project root
python apple_hdr_converter.py examples/sample_apple_hdr.jpg examples/sample_output.exr
```

**Result**: `sample_output.exr` - Preserves HDR dynamic range using gain map

### Convert HEIC (macOS only)
```bash
python heic_converter.py examples/sample_heic.heic examples/sample_heic_output.exr
```

**Result**: `sample_heic_output.exr` - Base image only (HDR gain map not preserved)

### Analyze HDR Information
```bash
python analyze_apple_hdr_jpeg.py examples/sample_apple_hdr.jpg
```

**Output**:
```
HDR Capacity Max: 3.281809
HDR Capacity Min: 0.000000
Gain Map Max: 3.281809
Gamma: 1.000000
```

## File Comparison

| File | Format | HDR Info | Size | Quality |
|------|--------|----------|------|---------|
| `sample_apple_hdr.jpg` | Apple HDR JPEG | ✅ Full HDR | 195KB | Original |
| `sample_output.exr` | EXR | ✅ Preserved HDR | 655KB | High |
| `sample_heic.heic` | Apple HDR HEIC | ✅ Full HDR | 115KB | Original |
| `sample_heic_output.exr` | EXR | ❌ Base only | 605KB | Medium |

## Expected Results

### Apple HDR JPEG → EXR
- ✅ Preserves HDR dynamic range
- ✅ Maintains highlight details
- ✅ Compatible with professional software
- ✅ Larger file size (uncompressed HDR)

### HEIC → EXR
- ⚠️ Loses HDR gain map information
- ✅ Preserves base image quality
- ✅ Compatible with professional software
- ⚠️ Reduced dynamic range

## Troubleshooting

If you encounter issues:
1. Run `python test_installation.py` to verify dependencies
2. Check that ExifTool is installed: `exiftool -ver`
3. Verify input file is Apple HDR format
4. Ensure sufficient disk space for output files

## Technical Notes

- Apple HDR JPEG files contain MPF (Multi-Picture Format) with gain maps
- HEIC files use Apple's proprietary HDR format (gain maps not accessible)
- EXR format preserves full dynamic range for professional workflows
- Output files are significantly larger due to uncompressed HDR data 