# Apple HEIC to EXR 转换器

[English](README.md) | 中文

一个Python工具，用于将Apple HDR HEIC文件转换为EXR格式，同时保留HDR信息。该工具从Apple专有的HDR格式中提取增益映射，并将其合成为标准的HDR EXR文件。

## 背景

![hdr截图示例](./examples/sample_output_acr_hdr_output.jpg)

macOS Tahoe引入了HDR截图支持，但生成的包含HDR信息的HEIC文件只能在Apple设备上查看。此工具将Apple HDR格式转换为标准EXR格式，便于在Adobe Photoshop、Camera Raw和Affinity Photo等软件中轻松分享和编辑。

---

> [!IMPORTANT]
> 为确保完整保留HDR信息，您必须首先从Mac照片应用中将照片导出为JPEG格式，并在导出对话框中将"颜色配置文件"设置为**原始状态**。只有这种导出方法才会在JPEG文件中包含Apple HDR增益映射。直接使用HEIC或其他导出选项将不会保留HDR增益映射。

---

## 功能特性

- ✅ 从Apple HDR JPEG文件中提取增益映射（MPF格式）
- ✅ 保留HDR动态范围信息
- ✅ 转换为行业标准EXR格式
- ✅ 支持HEIC和Apple HDR JPEG输入
- ✅ 可配置的色调映射选项
- ✅ 跨平台兼容性

## 系统要求

### 必需软件

1. **Python 3.8+**
2. **ExifTool** - 用于提取元数据和增益映射
   - macOS: `brew install exiftool`
   - Ubuntu/Debian: `sudo apt-get install exiftool`
   - Windows: 从[ExifTool网站](https://exiftool.org/)下载

### Python依赖

安装所需的Python包：

```bash
pip install numpy pillow opencv-python openexr
```

或从requirements.txt安装：

```bash
pip install -r requirements.txt
```

## 安装

1. 克隆此仓库：
```bash
git clone https://github.com/yourusername/appleheic2exr.git
cd appleheic2exr
```

2. 安装依赖：
```bash
pip install -r requirements.txt
```

3. 验证ExifTool安装：
```bash
exiftool -ver
```

## 使用方法

### 基本用法

将Apple HDR JPEG转换为EXR：

```bash
python apple_hdr_converter.py input.jpg output.exr
```

### 高级选项

```bash
# 使用色调映射转换（为SDR显示器降低亮度）
python apple_hdr_converter.py input.jpg output.exr --tone-mapping

# 转换为PNG格式（16位）
python apple_hdr_converter.py input.jpg output.png --format png

# 转换HEIC文件（需要macOS上的sips）
python heic_converter.py input.heic output.exr
```

### 命令行选项

- `input`: 输入的Apple HDR JPEG或HEIC文件
- `output`: 输出文件路径
- `--format`: 输出格式（`exr`或`png`，默认：`exr`）
- `--tone-mapping`: 应用色调映射以降低亮度

## 支持的输入格式

### Apple HDR JPEG
- 从Mac照片应用导出的启用HDR的文件
- 包含MPF（多图片格式）增益映射
- 自动提取增益映射和元数据

### Apple HDR HEIC
- 原生Apple HDR格式
- 使用macOS `sips`工具进行转换
- 仅限于macOS系统

## 工作原理

1. **增益映射提取**: 使用ExifTool从MPF格式中提取增益映射
2. **元数据分析**: 读取HDR容量、伽马和偏移信息
3. **HDR合成**: 使用Apple算法将增益映射应用到基础图像
4. **输出生成**: 保存为保留HDR信息的EXR格式

## 文件结构

```
appleheic2exr/
├── README.md
├── README_zh.md
├── LICENSE
├── requirements.txt
├── apple_hdr_converter.py      # Apple HDR JPEG主转换器
├── heic_converter.py           # HEIC文件转换器
├── analyze_apple_hdr_jpeg.py   # 调试分析工具
└── examples/
    └── sample_output.exr
```

## 示例

### 转换Apple HDR JPEG
```bash
# 基本转换
python apple_hdr_converter.py photo.jpg photo.exr

# 为SDR显示器使用色调映射
python apple_hdr_converter.py photo.jpg photo_sdr.exr --tone-mapping
```

### 转换HEIC（仅限macOS）
```bash
python heic_converter.py photo.heic photo.exr
```

### 分析HDR信息
```bash
python analyze_apple_hdr_jpeg.py photo.jpg
```

## 故障排除

### 常见问题

1. **"找不到ExifTool"**
   - 安装ExifTool: `brew install exiftool` (macOS) 或 `sudo apt-get install exiftool` (Linux)

2. **"OpenEXR不可用"**
   - 安装OpenEXR: `pip install openexr`

3. **"未找到增益映射"**
   - 确保输入文件是包含MPF格式的Apple HDR JPEG
   - 检查文件是否从启用HDR的Mac照片应用导出

4. **"输出过亮"**
   - 使用`--tone-mapping`标志降低亮度
   - 尝试不同的输出格式

### 调试模式

详细分析HDR信息：

```bash
python analyze_apple_hdr_jpeg.py input.jpg
```

这将显示：
- 增益映射统计信息
- HDR容量信息
- 图像元数据

## 技术细节

### HDR合成算法

该工具实现了Apple的增益映射算法：

```
HDR = SDR × (1 + (headroom - 1) × gain_map)
```

其中：
- `headroom` = HDR容量最大值 / 最小值
- `gain_map` = 提取的增益映射（标准化）
- `SDR` = 基础图像

### 支持的颜色空间

- Display P3（Apple默认）
- sRGB（备用）
- BT.2020（EXR输出）

## 致谢

- Apple提供的HDR增益映射格式
- ExifTool提供的元数据提取
- OpenEXR提供的HDR文件格式支持
- **Cursor** - 此仓库中的所有Python代码均由Cursor AI生成

## 支持

如果您遇到问题或有疑问：

1. 查看故障排除部分
2. 在GitHub上提出issue
3. 包含输入文件格式和错误消息

---

**注意**: 此工具专为Apple HDR文件设计。对于其他HDR格式，请考虑使用专门的工具如`ffmpeg`或`ImageMagick`。 