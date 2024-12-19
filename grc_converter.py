import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import xml.etree.ElementTree as ET
import json
import os
from pathlib import Path

class GRCConverter(tk.Tk):
    def __init__(self):
        super().__init__()

        self.title("GNU Radio Companion File Converter")
        self.geometry("800x600")
        
        # Load block conversion mappings
        self.conversion_map = {
            # Core blocks
            'wxgui_fftsink2': 'qtgui_freq_sink_x',
            'wxgui_waterfallsink2': 'qtgui_waterfall_sink_x',
            'wxgui_scopesink2': 'qtgui_time_sink_x',
            'wxgui_constellationsink2': 'qtgui_const_sink_x',
            'gr_throttle': 'blocks_throttle',
            'gr_file_source': 'blocks_file_source',
            'gr_file_sink': 'blocks_file_sink',
            'gr_complex_to_float': 'blocks_complex_to_float',
            'gr_float_to_complex': 'blocks_float_to_complex',
            'variable_slider': 'variable_qtgui_range',
            'osmosdr_source': 'soapy_rtlsdr_source',
            'blks2_selector': 'blocks_selector',
            'gr_multiply_xx': 'blocks_multiply_xx',
            'gr_add_xx': 'blocks_add_xx'
        }

        self.parameter_updates = {
            'variable_qtgui_range': {
                'style': {'old': 'wx.SL_HORIZONTAL', 'new': 'QtCore.Qt.Horizontal'},
                'grid_pos': {'new_name': 'gui_hint'},
                'notebook': {'remove': True}
            },
            'qtgui_freq_sink_x': {
                'baseband_freq': {'new_name': 'center_freq'},
                'y_per_div': {'new_name': 'y_per_div', 'note': 'Now in dB'},
                'ref_level': {'new_name': 'ref_level', 'note': 'Now in dB'}
            }
        }

        # Version indicators
        self.version_indicators = {
            # WX GUI indicators
            'wxgui_': '3.7',
            'gr_': '3.7',
            'blks2_': '3.7',
            # Qt GUI indicators
            'qtgui_': '3.8',
            'blocks_': '3.8',
            # Modern indicators
            'soapy_': '3.10',
            'pdu_': '3.9'
        }

        # Create main frame
        self.main_frame = ttk.Frame(self)
        self.main_frame.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)

        # Create widgets
        self.create_widgets()

    def create_widgets(self):
        # File selection
        file_frame = ttk.LabelFrame(self.main_frame, text="File Selection")
        file_frame.pack(fill=tk.X, padx=5, pady=5)

        self.input_path = tk.StringVar()
        self.input_path.trace('w', self.on_file_path_change)  # Add trace for file path changes
        
        ttk.Label(file_frame, text="Input GRC File:").pack(side=tk.LEFT, padx=5)
        ttk.Entry(file_frame, textvariable=self.input_path, width=50).pack(side=tk.LEFT, padx=5)
        ttk.Button(file_frame, text="Browse", command=self.browse_input).pack(side=tk.LEFT, padx=5)

        # Detected version frame
        detected_frame = ttk.LabelFrame(self.main_frame, text="Detected Version")
        detected_frame.pack(fill=tk.X, padx=5, pady=5)
        
        self.detected_version = tk.StringVar(value="No file selected")
        ttk.Label(detected_frame, text="Source Version:").pack(side=tk.LEFT, padx=5)
        self.version_label = ttk.Label(detected_frame, textvariable=self.detected_version)
        self.version_label.pack(side=tk.LEFT, padx=5)

        # Version selection
        version_frame = ttk.LabelFrame(self.main_frame, text="Target Version")
        version_frame.pack(fill=tk.X, padx=5, pady=5)

        self.target_version = tk.StringVar(value="3.10")
        ttk.Label(version_frame, text="Convert To:").pack(side=tk.LEFT, padx=5)
        self.target_version_combo = ttk.Combobox(version_frame, textvariable=self.target_version,
                                               values=["3.8", "3.9", "3.10"], width=10)
        self.target_version_combo.pack(side=tk.LEFT, padx=5)

        # Version details
        details_frame = ttk.LabelFrame(self.main_frame, text="Version Details")
        details_frame.pack(fill=tk.X, padx=5, pady=5)
        
        self.version_details = tk.Text(details_frame, height=4, width=80)
        self.version_details.pack(fill=tk.X, padx=5, pady=5)
        self.version_details.config(state='disabled')

        # Convert button
        ttk.Button(self.main_frame, text="Convert", command=self.convert_file).pack(pady=10)

        # Log area
        log_frame = ttk.LabelFrame(self.main_frame, text="Conversion Log")
        log_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        self.log_text = tk.Text(log_frame, height=15, width=80)
        self.log_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        # Scrollbar for log
        scrollbar = ttk.Scrollbar(log_frame, orient=tk.VERTICAL, command=self.log_text.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.log_text.config(yscrollcommand=scrollbar.set)

    def detect_version(self, file_path):
        try:
            tree = ET.parse(file_path)
            root = tree.getroot()
            
            # Try to get version from grc format attribute
            grc_format = root.get('created')
            if grc_format:
                self.log_message(f"GRC format version found: {grc_format}")
                return grc_format.split('.')[0] + '.' + grc_format.split('.')[1]
            
            # Check for version indicators in blocks
            versions = []
            for block in root.findall('.//block'):
                key = block.find('key')
                if key is not None:
                    block_type = key.text
                    for indicator, version in self.version_indicators.items():
                        if block_type.startswith(indicator):
                            versions.append(version)
            
            if versions:
                # Return the oldest version found
                oldest_version = min(versions)
                self.log_message(f"Detected version {oldest_version} based on block types")
                return oldest_version
            
            self.log_message("Could not detect version automatically")
            return "Unknown"
            
        except Exception as e:
            self.log_message(f"Error detecting version: {str(e)}")
            return "Error"

    def update_version_details(self, version):
        details = {
            "3.7": "Legacy version with WX GUI\n- Uses old block names (gr_, blks2_)\n- WX GUI components\n- Python 2 compatibility",
            "3.8": "Transition version\n- Introduces Qt GUI\n- Removes XMLRPC\n- Python 3 required",
            "3.9": "Modern version\n- SWIG replaced with Pybind11\n- Improved naming consistency\n- Better type handling",
            "3.10": "Latest stable version\n- Enhanced Qt GUI\n- Improved error messages\n- Modern parameter names",
            "Unknown": "Version could not be detected\nPlease check the file manually",
            "Error": "Error occurred while detecting version\nPlease check if the file is a valid GRC file"
        }
        
        self.version_details.config(state='normal')
        self.version_details.delete(1.0, tk.END)
        self.version_details.insert(tk.END, details.get(version, "Version information not available"))
        self.version_details.config(state='disabled')

    def on_file_path_change(self, *args):
        file_path = self.input_path.get()
        if file_path and os.path.exists(file_path):
            version = self.detect_version(file_path)
            self.detected_version.set(version)
            self.update_version_details(version)
            
            # Update target version options
            current_version = float(version.split('.')[-1]) if version not in ["Unknown", "Error"] else 3.7
            available_versions = [str(v) for v in [3.8, 3.9, 3.10] if v > current_version]
            self.target_version_combo['values'] = available_versions
            if available_versions:
                self.target_version.set(available_versions[-1])

    def browse_input(self):
        filename = filedialog.askopenfilename(
            title="Select GRC File",
            filetypes=[("GNU Radio Companion", "*.grc"), ("All Files", "*.*")]
        )
        if filename:
            self.input_path.set(filename)

    def log_message(self, message):
        self.log_text.insert(tk.END, message + "\n")
        self.log_text.see(tk.END)
        self.update_idletasks()

    def convert_block(self, block):
        key = block.find('key').text
        if key in self.conversion_map:
            new_key = self.conversion_map[key]
            self.log_message(f"Converting block: {key} -> {new_key}")
            block.find('key').text = new_key

            # Update parameters if needed
            if new_key in self.parameter_updates:
                params = self.parameter_updates[new_key]
                for param in block.findall('param'):
                    param_key = param.find('key').text
                    param_value = param.find('value')
                    
                    # Handle parameter name changes
                    if param_key in params:
                        param_info = params[param_key]
                        if 'new_name' in param_info:
                            param.find('key').text = param_info['new_name']
                            self.log_message(f"  Updated parameter: {param_key} -> {param_info['new_name']}")
                        
                        # Handle value conversions
                        if 'old' in param_info and param_value.text == param_info['old']:
                            param_value.text = param_info['new']
                            self.log_message(f"  Updated value: {param_info['old']} -> {param_info['new']}")

                        # Handle parameter removal
                        if 'remove' in param_info and param_info['remove']:
                            block.remove(param)
                            self.log_message(f"  Removed parameter: {param_key}")

    def convert_file(self):
        input_path = self.input_path.get()
        if not input_path:
            messagebox.showerror("Error", "Please select an input file")
            return

        try:
            # Parse the input file
            tree = ET.parse(input_path)
            root = tree.getroot()

            # Update format version
            grc_format = root.find(".//param/[key='generate_options']")
            if grc_format is not None:
                old_format = grc_format.find('value').text
                if 'wx_gui' in old_format:
                    grc_format.find('value').text = 'qt_gui'
                    self.log_message("Updated generate_options: wx_gui -> qt_gui")

            # Convert blocks
            for block in root.findall('.//block'):
                self.convert_block(block)

            # Save the converted file
            output_path = str(Path(input_path).with_suffix('')) + f"_converted_{self.target_version.get()}.grc"
            tree.write(output_path, encoding='utf-8', xml_declaration=True)
            
            self.log_message(f"\nConversion completed successfully!")
            self.log_message(f"Output file saved as: {output_path}")
            
            messagebox.showinfo("Success", "File converted successfully!")
            
        except Exception as e:
            self.log_message(f"Error during conversion: {str(e)}")
            messagebox.showerror("Error", f"Conversion failed: {str(e)}")

if __name__ == "__main__":
    app = GRCConverter()
    app.mainloop()
