#!/usr/bin/env python3
import sys
import os
import subprocess
import shlex
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                             QHBoxLayout, QLabel, QPushButton, QTextEdit, 
                             QProgressBar, QMessageBox, QFrame, QLineEdit,
                             QInputDialog)
from PyQt6.QtCore import Qt, QThread, pyqtSignal, QSize
from PyQt6.QtGui import QIcon, QFont

class Worker(QThread):
    progress_signal = pyqtSignal(str)
    finished_signal = pyqtSignal(bool, str)

    def __init__(self, command):
        super().__init__()
        self.command = command

    def run(self):
        try:
            full_cmd = f"pkexec {self.command}"
            process = subprocess.Popen(
                shlex.split(full_cmd),
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True
            )
            while True:
                output = process.stdout.readline()
                if output == '' and process.poll() is not None:
                    break
                if output:
                    self.progress_signal.emit(output.strip())
            rc = process.poll()
            if rc == 0:
                self.finished_signal.emit(True, "Operation completed successfully.")
            else:
                self.finished_signal.emit(False, f"Operation failed with exit code {rc}")
        except Exception as e:
            self.finished_signal.emit(False, str(e))

class RPMInstallerWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("RPM Manager")
        self.setMinimumSize(600, 550)
        
        self.target_file = None
        self.pkg_name = None
        self.worker = None

        self.init_ui()
        self.process_arguments()

    def init_ui(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)
        layout.setSpacing(10)
        layout.setContentsMargins(20, 20, 20, 20)

        # --- Search Section ---
        search_layout = QHBoxLayout()
        self.input_search = QLineEdit()
        self.input_search.setPlaceholderText("Search installed packages (e.g. 'chrome' or 'firefox')")
        self.input_search.returnPressed.connect(self.perform_search)
        search_layout.addWidget(self.input_search)
        
        self.btn_search = QPushButton("Search")
        self.btn_search.clicked.connect(self.perform_search)
        search_layout.addWidget(self.btn_search)
        layout.addLayout(search_layout)

        line1 = QFrame()
        line1.setFrameShape(QFrame.Shape.HLine)
        line1.setFrameShadow(QFrame.Shadow.Sunken)
        layout.addWidget(line1)

        # --- Header ---
        header_layout = QHBoxLayout()
        self.icon_label = QLabel()
        self.icon_label.setPixmap(self.style().standardIcon(
            self.style().StandardPixmap.SP_DriveCDIcon).pixmap(QSize(64, 64)))
        header_layout.addWidget(self.icon_label)

        info_layout = QVBoxLayout()
        self.lbl_name = QLabel("RPM Manager")
        self.lbl_name.setFont(QFont("Sans Serif", 16, QFont.Weight.Bold))
        self.lbl_version = QLabel("v0.4")
        self.lbl_version.setStyleSheet("color: #666;")
        info_layout.addWidget(self.lbl_name)
        info_layout.addWidget(self.lbl_version)
        header_layout.addLayout(info_layout)
        header_layout.addStretch()
        layout.addLayout(header_layout)

        line2 = QFrame()
        line2.setFrameShape(QFrame.Shape.HLine)
        line2.setFrameShadow(QFrame.Shadow.Sunken)
        layout.addWidget(line2)

        # --- Description ---
        self.txt_description = QTextEdit()
        self.txt_description.setReadOnly(True)
        self.txt_description.setStyleSheet("background-color: #f5f5f5; border: 1px solid #ccc; padding: 5px;")
        layout.addWidget(self.txt_description)

        # --- Status ---
        self.lbl_status = QLabel("Ready")
        layout.addWidget(self.lbl_status)
        
        self.progress_bar = QProgressBar()
        self.progress_bar.setTextVisible(False)
        self.progress_bar.hide()
        layout.addWidget(self.progress_bar)

        # --- Buttons ---
        btn_layout = QHBoxLayout()
        
        self.btn_remove = QPushButton("Remove Package")
        self.btn_remove.setStyleSheet("background-color: #d9534f; color: white; padding: 8px 15px; font-weight: bold;")
        self.btn_remove.clicked.connect(self.start_removal)
        self.btn_remove.hide()
        btn_layout.addWidget(self.btn_remove)

        btn_layout.addStretch()
        
        self.btn_close = QPushButton("Close")
        self.btn_close.clicked.connect(self.close)
        btn_layout.addWidget(self.btn_close)

        self.btn_action = QPushButton("Install Package")
        self.btn_action.setFont(QFont("Sans Serif", 10, QFont.Weight.Bold))
        self.btn_action.setStyleSheet("padding: 8px 20px;")
        self.btn_action.clicked.connect(self.start_installation)
        self.btn_action.setEnabled(False)
        btn_layout.addWidget(self.btn_action)

        layout.addLayout(btn_layout)

    def process_arguments(self):
        args = sys.argv[1:]
        if not args:
            self.lbl_name.setText("Manage Packages")
            self.txt_description.setText("Use the search bar above to find installed packages,\nor open an .rpm file directly.")
            return

        if args[0] == "--remove" or args[0] == "-r":
            if len(args) > 1:
                self.input_search.setText(args[1])
                self.perform_search()
        elif os.path.isfile(args[0]) and args[0].endswith(".rpm"):
            self.target_file = args[0]
            self.load_rpm_file_info(self.target_file)

    def perform_search(self):
        """Search for installed packages with fuzzy matching"""
        term = self.input_search.text().strip()
        if not term:
            return
        
        # 1. Get list of all installed packages matching the term (case insensitive)
        # rpm -qa --queryformat "%{NAME}\n" gives clean names
        try:
            cmd = f"rpm -qa --queryformat '%{{NAME}}\\n' | grep -i '{term}'"
            # shell=True is needed for the pipe (|), keep it safe by not passing user input directly to shell=True usually,
            # but grep is safer here. Better: run rpm -qa and filter in python.
            
            # Safer approach: Get all names, filter in Python
            proc = subprocess.run(["rpm", "-qa", "--queryformat", "%{NAME}\n"], capture_output=True, text=True)
            all_pkgs = proc.stdout.splitlines()
            
            matches = [pkg for pkg in all_pkgs if term.lower() in pkg.lower()]
            matches.sort()

            if not matches:
                QMessageBox.information(self, "No Results", f"No installed packages found matching '{term}'.")
                return

            selected_pkg = None
            if len(matches) == 1:
                selected_pkg = matches[0]
            else:
                # 2. If multiple matches, show a selection dialog
                item, ok = QInputDialog.getItem(self, "Select Package", 
                                              f"Found {len(matches)} packages. Select one:", 
                                              matches, 0, False)
                if ok and item:
                    selected_pkg = item
            
            if selected_pkg:
                self.load_installed_info(selected_pkg)

        except Exception as e:
            QMessageBox.critical(self, "Search Error", str(e))

    def load_installed_info(self, pkg_name):
        """Loads info for an ALREADY INSTALLED package"""
        try:
            cmd = ["rpm", "-qi", pkg_name]
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            if result.returncode != 0:
                return

            info = result.stdout
            summary = "Package Details"
            for line in info.split('\n'):
                if line.startswith("Summary"):
                    summary = line.split(":", 1)[1].strip()
                if line.startswith("Version"):
                    ver = line.split(":", 1)[1].strip()
                    self.lbl_version.setText(f"Version: {ver}")

            self.pkg_name = pkg_name
            self.lbl_name.setText(pkg_name)
            self.txt_description.setText(f"<b>{summary}</b><br><br>{info}")
            self.lbl_status.setText("Uninstall Mode")

            self.target_file = None 
            self.btn_action.hide() 
            self.btn_remove.show() 
            
        except Exception as e:
            self.lbl_name.setText("Error")
            self.txt_description.setText(str(e))

    def load_rpm_file_info(self, filepath):
        try:
            qfmt = "%{NAME}|%{VERSION}|%{RELEASE}|%{SUMMARY}|%{DESCRIPTION}|%{ARCH}"
            cmd = ["rpm", "-qp", "--queryformat", qfmt, filepath]
            result = subprocess.run(cmd, capture_output=True, text=True, check=True)
            data = result.stdout.split("|")
            
            if len(data) >= 6:
                name, ver, rel, summary, desc, arch = data[:6]
                self.pkg_name = name
                self.lbl_name.setText(f"{name} ({arch})")
                self.lbl_version.setText(f"Version: {ver}-{rel}")
                self.txt_description.setText(f"<b>{summary}</b><br><br>{desc}")
                
                check_inst = subprocess.run(["rpm", "-q", name], capture_output=True)
                if check_inst.returncode == 0:
                    self.lbl_status.setText("Package is installed.")
                    self.btn_action.setText("Reinstall Package")
                    self.btn_remove.show()
                else:
                    self.lbl_status.setText("Package is not installed.")
                    self.btn_action.setText("Install Package")
                    self.btn_remove.hide()
                
                self.btn_action.show()
                self.btn_action.setEnabled(True)
        except Exception as e:
            self.lbl_name.setText("Error reading package")
            self.txt_description.setText(str(e))

    def start_installation(self):
        if not self.target_file: return
        cmd = f"dnf install -y \"{self.target_file}\""
        self.run_worker(cmd, "Installing...")

    def start_removal(self):
        if not self.pkg_name: return
        confirm = QMessageBox.question(self, "Confirm Removal", 
            f"Are you sure you want to remove {self.pkg_name}?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        
        if confirm == QMessageBox.StandardButton.Yes:
            cmd = f"dnf remove -y {self.pkg_name}"
            self.run_worker(cmd, "Removing...")

    def run_worker(self, cmd, status_msg):
        self.worker = Worker(cmd)
        self.worker.progress_signal.connect(self.update_log)
        self.worker.finished_signal.connect(self.action_finished)
        
        self.btn_action.setEnabled(False)
        self.btn_remove.setEnabled(False)
        self.btn_close.setEnabled(False)
        self.progress_bar.show()
        self.txt_description.clear()
        self.lbl_status.setText(status_msg)
        self.worker.start()

    def update_log(self, text):
        self.txt_description.append(text)
        sb = self.txt_description.verticalScrollBar()
        sb.setValue(sb.maximum())

    def action_finished(self, success, message):
        self.progress_bar.hide()
        self.btn_close.setEnabled(True)
        if self.target_file: 
            self.btn_action.setEnabled(True)
            self.load_rpm_file_info(self.target_file)
        elif self.pkg_name:
            # Re-search the last term to update list if item removed, 
            # or just clear if success
            if success:
                self.lbl_name.setText("Removed")
                self.txt_description.setText("Package has been uninstalled.")
                self.btn_remove.hide()
            else:
                self.load_installed_info(self.pkg_name)
            
        if success:
            QMessageBox.information(self, "Finished", message)
        else:
            QMessageBox.critical(self, "Error", f"Operation failed:\n{message}")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = RPMInstallerWindow()
    window.show()
    sys.exit(app.exec())


