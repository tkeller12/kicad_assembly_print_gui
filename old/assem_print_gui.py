
import sys
import subprocess
import os
from PyQt6.QtWidgets import (
    QApplication, QWidget, QPushButton, QVBoxLayout, QLabel,
    QFileDialog, QCheckBox, QHBoxLayout, QGroupBox
)
from PyQt6.QtCore import Qt

class KiCadAssemblyExporter(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("KiCad Assembly Exporter")

        self.kicad_pcb_path = ""

        layout = QVBoxLayout()
        self.setLayout(layout)

        # File label
        self.file_label = QLabel("No .kicad_pcb file selected.")
        self.file_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.file_label)

        # Select file button
        self.select_button = QPushButton("Select .kicad_pcb File")
        self.select_button.clicked.connect(self.select_file)
        layout.addWidget(self.select_button)

        # Options Group: Layers
        layers_group = QGroupBox("Plot Layers")
        layers_layout = QVBoxLayout()
        self.layer_ffab = QCheckBox("F.Fab")
        self.layer_ffab.setChecked(True)
        self.layer_edge = QCheckBox("Edge.Cuts")
        self.layer_edge.setChecked(True)
        self.layer_comments = QCheckBox("User.Comments")
        self.layer_comments.setChecked(True)
        layers_layout.addWidget(self.layer_ffab)
        layers_layout.addWidget(self.layer_edge)
        layers_layout.addWidget(self.layer_comments)
        layers_group.setLayout(layers_layout)
        layout.addWidget(layers_group)

        # Options Group: Extra Flags
        flags_group = QGroupBox("Options")
        flags_layout = QVBoxLayout()
        self.option_sp = QCheckBox("Sketch Pads on Fab Layers (--sp)")
        self.option_sp.setChecked(True)
        self.option_bw = QCheckBox("Black & White (--black-and-white)")
        self.option_bw.setChecked(True)
        self.option_ibt = QCheckBox("Include Border Title (--ibt)")
        self.option_ibt.setChecked(True)
        flags_layout.addWidget(self.option_sp)
        flags_layout.addWidget(self.option_bw)
        flags_layout.addWidget(self.option_ibt)
        flags_group.setLayout(flags_layout)
        layout.addWidget(flags_group)

        # Export button
        self.export_button = QPushButton("Export Assembly Drawing")
        self.export_button.setEnabled(False)
        self.export_button.clicked.connect(self.export_assembly)
        layout.addWidget(self.export_button)

        # Status label
        self.status_label = QLabel("")
        self.status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.status_label)

    def select_file(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Open KiCad PCB File",
            "",
            "KiCad PCB Files (*.kicad_pcb)"
        )
        if file_path:
            self.kicad_pcb_path = file_path
            self.file_label.setText(f"Selected: {file_path}")
            self.export_button.setEnabled(True)
            self.status_label.setText("")

    def export_assembly(self):
        if not self.kicad_pcb_path:
            return

        input_filename = os.path.basename(self.kicad_pcb_path)
        base_name, _ = os.path.splitext(input_filename)
        output_filename = f"assembly_print_{base_name}.pdf"
        output_path = os.path.join(os.path.dirname(self.kicad_pcb_path), output_filename)

        # Collect selected layers
        layers = []
        if self.layer_ffab.isChecked():
            layers.append("F.Fab")
        if self.layer_edge.isChecked():
            layers.append("Edge.Cuts")
        if self.layer_comments.isChecked():
            layers.append("User.Comments")

        if not layers:
            self.status_label.setText("❌ No layers selected.")
            return

        # Build command
        cmd = [
            "kicad-cli", "pcb", "export", "pdf",
            "--output", output_path,
            "--layers", ",".join(layers)
        ]

        # Add optional flags
        if self.option_sp.isChecked():
            cmd.append("--sp")
        if self.option_bw.isChecked():
            cmd.append("--black-and-white")
        if self.option_ibt.isChecked():
            cmd.append("--ibt")

        cmd.append(self.kicad_pcb_path)

        try:
            result = subprocess.run(cmd, capture_output=True, text=True)
            if result.returncode == 0:
                self.status_label.setText(f"✅ Exported: {output_path}")
            else:
                self.status_label.setText(f"❌ Error:\n{result.stderr}")
        except FileNotFoundError:
            self.status_label.setText("❌ Error: 'kicad-cli' not found in PATH.")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = KiCadAssemblyExporter()
    window.show()
    sys.exit(app.exec())
