# GNU Radio Companion File Converter

*Developed by Khanfar Systems*

## Overview
GNU Radio Companion File Converter is a graphical tool designed to help users migrate their GNU Radio Companion (GRC) flowgraph files between different versions of GNU Radio. It specializes in converting legacy WX GUI-based flowgraphs to modern Qt GUI-based ones.

## Features
- **Automatic Version Detection**: Automatically detects the source version of GRC files based on block types and format
- **Smart Block Conversion**: Converts legacy blocks to their modern equivalents:
  - WX GUI blocks → Qt GUI blocks
  - Legacy core blocks → Modern block names
  - Parameter name and value updates
- **Version Support**:
  - Source versions: 3.7 (legacy with WX GUI)
  - Target versions: 3.8, 3.9, 3.10
- **User-Friendly Interface**:
  - Simple file selection
  - Automatic version detection
  - Detailed conversion logging
  - Progress feedback

## Block Conversions
The tool handles conversion of various block types, including:
- FFT Sinks (wxgui_fftsink2 → qtgui_freq_sink_x)
- Waterfall Sinks (wxgui_waterfallsink2 → qtgui_waterfall_sink_x)
- Scope Sinks (wxgui_scopesink2 → qtgui_time_sink_x)
- Constellation Sinks (wxgui_constellationsink2 → qtgui_const_sink_x)
- And many more core blocks

## Usage
1. Launch the application
2. Select your input GRC file using the "Browse" button
3. The tool will automatically detect the source version
4. Choose your target GNU Radio version
5. Click "Convert" to start the conversion process
6. The converted file will be saved with a "_converted_[version]" suffix

## Requirements
- Python 3.x
- tkinter (usually comes with Python)
- GNU Radio installation (for running the converted flowgraphs)

## Notes
- Original files are never modified; converted files are saved with a new name
- Detailed conversion logs are provided in the application window
- Some manual adjustments might be needed after conversion, especially for complex flowgraphs
