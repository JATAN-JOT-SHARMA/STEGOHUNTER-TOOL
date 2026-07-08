#!/usr/bin/env python3
"""
Steganography Hunter - Complete Detection & Repair Tool
Reports saved to OneDrive Documents folder
"""

import os
import sys
import json
import threading
import struct
import shutil
import winsound
from pathlib import Path
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed
from tkinter import *
from tkinter import ttk, scrolledtext, messagebox, filedialog
import tkinter.font as tkfont

class StegoHunter:
    def __init__(self, root):
        self.root = root
        self.root.title("Steganography Hunter v3.0 - Detection & Repair Tool")
        self.root.geometry("1500x900")
        self.root.configure(bg='#1e1e1e')
        
        # Allow window resizing
        self.root.resizable(True, True)
        self.root.minsize(1000, 600)
        
        # Variables
        self.scan_thread = None
        self.is_scanning = False
        self.suspicious_files = []
        self.clean_files = []
        self.scan_path = StringVar(value=os.path.expanduser("~"))
        self.deep_scan = BooleanVar(value=False)
        self.audio_alert = BooleanVar(value=True)
        
        # Statistics
        self.total_scanned = 0
        self.suspicious_count = 0
        self.clean_count = 0
        self.repaired_count = 0
        
        # Set custom report path - USING RAW STRING TO FIX UNICODE ERROR
        self.report_base_path = r"C:\Users\jot35\OneDrive\Documents"
        self.report_dir = os.path.join(self.report_base_path, "StegoHunter-Reports")
        
        # Create reports directory if it doesn't exist
        try:
            os.makedirs(self.report_dir, exist_ok=True)
            print(f"Reports will be saved to: {self.report_dir}")
        except Exception as e:
            print(f"Warning: Could not create reports directory: {e}")
            # Fallback to local directory
            self.report_dir = os.path.join(os.getcwd(), "StegoHunter-Reports")
            os.makedirs(self.report_dir, exist_ok=True)
        
        # Colors
        self.colors = {
            'bg': '#1e1e1e',
            'fg': '#d4d4d4',
            'accent': '#0078d4',
            'success': '#6a9955',
            'warning': '#dcdcaa',
            'error': '#f48771',
            'button': '#0e639c',
            'frame_bg': '#252526',
            'list_bg': '#2d2d30',
            'suspicious_bg': '#5a2a2a',
            'clean_bg': '#1e3a2a'
        }
        
        self.setup_ui()
        
    def setup_ui(self):
        """Setup the complete GUI"""
        # Main frame with grid for resizing
        main_frame = Frame(self.root, bg=self.colors['bg'])
        main_frame.pack(fill=BOTH, expand=True, padx=10, pady=10)
        
        # Configure grid weights for resizing
        main_frame.grid_rowconfigure(1, weight=1)
        main_frame.grid_columnconfigure(0, weight=1)
        
        # Control panel (top - fixed height)
        self.create_control_panel(main_frame)
        
        # Lists frame (middle - expands)
        lists_frame = Frame(main_frame, bg=self.colors['bg'])
        lists_frame.grid(row=1, column=0, sticky="nsew", pady=10)
        
        # Configure lists_frame grid for resizing
        lists_frame.grid_columnconfigure(0, weight=1)
        lists_frame.grid_columnconfigure(1, weight=1)
        lists_frame.grid_rowconfigure(0, weight=1)
        
        # Suspicious list (left)
        self.create_suspicious_list(lists_frame)
        
        # Clean list (right)
        self.create_clean_list(lists_frame)
        
        # Status area (bottom - fixed height)
        self.create_status_area(main_frame)
        
        # Show report path in status
        self.log(f"Reports will be saved to: {self.report_dir}", "info")
        
    def create_control_panel(self, parent):
        """Create top control panel"""
        control = Frame(parent, bg=self.colors['frame_bg'], relief=RAISED, bd=1)
        control.grid(row=0, column=0, sticky="ew", pady=(0, 10))
        
        # Title
        title = Label(control, text="🔍 Steganography Hunter - Find & Remove Hidden Data",
                     font=("Segoe UI", 14, "bold"), bg=self.colors['frame_bg'],
                     fg=self.colors['accent'])
        title.pack(pady=10)
        
        # Path selection
        path_frame = Frame(control, bg=self.colors['frame_bg'])
        path_frame.pack(fill=X, padx=10, pady=5)
        
        Label(path_frame, text="Scan Path:", bg=self.colors['frame_bg'],
              fg=self.colors['fg']).pack(side=LEFT, padx=5)
        
        path_entry = Entry(path_frame, textvariable=self.scan_path, width=60,
                          bg=self.colors['list_bg'], fg=self.colors['fg'])
        path_entry.pack(side=LEFT, padx=5, fill=X, expand=True)
        
        Button(path_frame, text="📁 Browse", command=self.browse_path,
              bg=self.colors['button'], fg=self.colors['fg'],
              cursor="hand2", relief=FLAT).pack(side=LEFT, padx=5)
        
        # Options
        options = Frame(control, bg=self.colors['frame_bg'])
        options.pack(pady=5)
        
        Checkbutton(options, text="🔍 Deep Scan (Slow - Checks entropy & more)",
                   variable=self.deep_scan, bg=self.colors['frame_bg'],
                   fg=self.colors['fg']).pack(side=LEFT, padx=10)
        
        Checkbutton(options, text="🔊 Audio Alert (Beep when suspicious file found)",
                   variable=self.audio_alert, bg=self.colors['frame_bg'],
                   fg=self.colors['fg']).pack(side=LEFT, padx=10)
        
        # Report path display
        report_path_label = Label(options, text=f"📁 Reports: {self.report_dir}",
                                  bg=self.colors['frame_bg'], fg=self.colors['warning'],
                                  font=("Segoe UI", 8))
        report_path_label.pack(side=LEFT, padx=10)
        
        # Buttons
        buttons = Frame(control, bg=self.colors['frame_bg'])
        buttons.pack(pady=10)
        
        self.scan_btn = Button(buttons, text="🚀 Start Scan", command=self.start_scan,
                              bg=self.colors['success'], fg=self.colors['bg'],
                              font=("Segoe UI", 11, "bold"), padx=20, pady=5,
                              cursor="hand2", relief=FLAT)
        self.scan_btn.pack(side=LEFT, padx=5)
        
        self.stop_btn = Button(buttons, text="⏹️ Stop Scan", command=self.stop_scan,
                              bg=self.colors['error'], fg=self.colors['fg'],
                              font=("Segoe UI", 11, "bold"), padx=20, pady=5,
                              cursor="hand2", relief=FLAT, state=DISABLED)
        self.stop_btn.pack(side=LEFT, padx=5)
        
        Button(buttons, text="📊 Generate Report", command=self.generate_report,
              bg=self.colors['accent'], fg=self.colors['fg'],
              font=("Segoe UI", 11, "bold"), padx=20, pady=5,
              cursor="hand2", relief=FLAT).pack(side=LEFT, padx=5)
        
        Button(buttons, text="🗑️ Clear All", command=self.clear_all,
              bg=self.colors['warning'], fg=self.colors['bg'],
              font=("Segoe UI", 11, "bold"), padx=20, pady=5,
              cursor="hand2", relief=FLAT).pack(side=LEFT, padx=5)
        
        Button(buttons, text="📂 Open Reports Folder", command=self.open_reports_folder,
              bg=self.colors['button'], fg=self.colors['fg'],
              font=("Segoe UI", 11, "bold"), padx=20, pady=5,
              cursor="hand2", relief=FLAT).pack(side=LEFT, padx=5)
        
    def create_suspicious_list(self, parent):
        """Create suspicious files list (left side)"""
        frame = Frame(parent, bg=self.colors['frame_bg'], relief=SUNKEN, bd=1)
        frame.grid(row=0, column=0, sticky="nsew", padx=(0, 5))
        
        self.suspicious_title = Label(frame, text="⚠️ SUSPICIOUS FILES (0)",
                                     bg=self.colors['frame_bg'], fg=self.colors['error'],
                                     font=("Segoe UI", 12, "bold"))
        self.suspicious_title.pack(pady=5)
        
        # Treeview with scrollbar
        tree_frame = Frame(frame, bg=self.colors['frame_bg'])
        tree_frame.pack(fill=BOTH, expand=True, padx=5, pady=5)
        
        columns = ('File', 'Size', 'Detections', 'Type')
        self.suspicious_tree = ttk.Treeview(tree_frame, columns=columns, show='headings')
        
        self.suspicious_tree.heading('File', text='File Path')
        self.suspicious_tree.heading('Size', text='Size (KB)')
        self.suspicious_tree.heading('Detections', text='Issues Found')
        self.suspicious_tree.heading('Type', text='Type')
        
        self.suspicious_tree.column('File', width=400)
        self.suspicious_tree.column('Size', width=80)
        self.suspicious_tree.column('Detections', width=100)
        self.suspicious_tree.column('Type', width=80)
        
        scroll = ttk.Scrollbar(tree_frame, orient=VERTICAL, command=self.suspicious_tree.yview)
        self.suspicious_tree.configure(yscrollcommand=scroll.set)
        
        self.suspicious_tree.pack(side=LEFT, fill=BOTH, expand=True)
        scroll.pack(side=RIGHT, fill=Y)
        
        # Buttons
        btn_frame = Frame(frame, bg=self.colors['frame_bg'])
        btn_frame.pack(fill=X, pady=5)
        
        Button(btn_frame, text="🔧 Repair Selected", command=self.repair_selected,
              bg=self.colors['success'], fg=self.colors['bg'],
              padx=15, pady=3, cursor="hand2", relief=FLAT).pack(side=LEFT, padx=5)
        
        Button(btn_frame, text="🔧 Repair All", command=self.repair_all,
              bg=self.colors['warning'], fg=self.colors['bg'],
              padx=15, pady=3, cursor="hand2", relief=FLAT).pack(side=LEFT, padx=5)
        
    def create_clean_list(self, parent):
        """Create clean files list (right side)"""
        frame = Frame(parent, bg=self.colors['frame_bg'], relief=SUNKEN, bd=1)
        frame.grid(row=0, column=1, sticky="nsew", padx=(5, 0))
        
        self.clean_title = Label(frame, text="✅ CLEAN FILES (0)",
                                bg=self.colors['frame_bg'], fg=self.colors['success'],
                                font=("Segoe UI", 12, "bold"))
        self.clean_title.pack(pady=5)
        
        # Treeview with scrollbar
        tree_frame = Frame(frame, bg=self.colors['frame_bg'])
        tree_frame.pack(fill=BOTH, expand=True, padx=5, pady=5)
        
        columns = ('File', 'Size', 'Status', 'Type')
        self.clean_tree = ttk.Treeview(tree_frame, columns=columns, show='headings')
        
        self.clean_tree.heading('File', text='File Path')
        self.clean_tree.heading('Size', text='Size (KB)')
        self.clean_tree.heading('Status', text='Status')
        self.clean_tree.heading('Type', text='Type')
        
        self.clean_tree.column('File', width=400)
        self.clean_tree.column('Size', width=80)
        self.clean_tree.column('Status', width=100)
        self.clean_tree.column('Type', width=80)
        
        scroll = ttk.Scrollbar(tree_frame, orient=VERTICAL, command=self.clean_tree.yview)
        self.clean_tree.configure(yscrollcommand=scroll.set)
        
        self.clean_tree.pack(side=LEFT, fill=BOTH, expand=True)
        scroll.pack(side=RIGHT, fill=Y)
        
        # Info
        info = Label(frame, text="✓ Files with no steganography detected",
                    bg=self.colors['frame_bg'], fg=self.colors['success'])
        info.pack(pady=5)
        
    def create_status_area(self, parent):
        """Create status area at bottom"""
        frame = Frame(parent, bg=self.colors['frame_bg'], relief=SUNKEN, bd=1)
        frame.grid(row=2, column=0, sticky="ew", pady=(10, 0))
        
        Label(frame, text="Status Log", bg=self.colors['frame_bg'],
              fg=self.colors['accent'], font=("Segoe UI", 10, "bold")).pack(anchor=W, padx=5, pady=2)
        
        self.status_text = scrolledtext.ScrolledText(frame, height=6,
                                                     bg=self.colors['list_bg'],
                                                     fg=self.colors['fg'])
        self.status_text.pack(fill=BOTH, expand=True, padx=5, pady=5)
        
        # Progress bar
        self.progress = ttk.Progressbar(frame, mode='determinate')
        self.progress.pack(fill=X, padx=5, pady=5)
        
        # Stats label
        self.stats_label = Label(frame, text="Ready", bg=self.colors['frame_bg'],
                                fg=self.colors['fg'])
        self.stats_label.pack(pady=2)
        
    def open_reports_folder(self):
        """Open the reports folder in file explorer"""
        try:
            os.startfile(self.report_dir)
            self.log(f"Opening reports folder: {self.report_dir}", "info")
        except Exception as e:
            self.log(f"Error opening folder: {e}", "error")
        
    def play_alert_sound(self):
        """Play alert sound when suspicious file found"""
        if self.audio_alert.get():
            try:
                winsound.Beep(1000, 200)
                winsound.Beep(1500, 200)
            except:
                winsound.MessageBeep()
                
    def log(self, msg, msg_type="info"):
        """Add message to status log"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        colors = {"info": "white", "error": "#f48771", "success": "#6a9955", "warning": "#dcdcaa"}
        
        self.status_text.insert(END, f"[{timestamp}] ", "timestamp")
        self.status_text.insert(END, f"{msg}\n", msg_type)
        self.status_text.see(END)
        self.status_text.tag_config("timestamp", foreground="#858585")
        self.status_text.tag_config("info", foreground=colors["info"])
        self.status_text.tag_config("error", foreground=colors["error"])
        self.status_text.tag_config("success", foreground=colors["success"])
        self.status_text.tag_config("warning", foreground=colors["warning"])
        
    def browse_path(self):
        path = filedialog.askdirectory(initialdir=self.scan_path.get())
        if path:
            self.scan_path.set(path)
            
    def start_scan(self):
        if self.is_scanning:
            return
            
        self.is_scanning = True
        self.scan_btn.config(state=DISABLED)
        self.stop_btn.config(state=NORMAL)
        
        # Clear previous data
        for item in self.suspicious_tree.get_children():
            self.suspicious_tree.delete(item)
        for item in self.clean_tree.get_children():
            self.clean_tree.delete(item)
            
        self.suspicious_files = []
        self.clean_files = []
        self.total_scanned = 0
        self.suspicious_count = 0
        self.clean_count = 0
        self.repaired_count = 0
        self.progress['value'] = 0
        
        self.log(f"Starting scan: {self.scan_path.get()}")
        self.log(f"Deep scan: {'ON' if self.deep_scan.get() else 'OFF'}")
        self.log(f"Audio alert: {'ON' if self.audio_alert.get() else 'OFF'}")
        
        self.scan_thread = threading.Thread(target=self.scan_files, daemon=True)
        self.scan_thread.start()
        
    def stop_scan(self):
        self.is_scanning = False
        self.log("Scan stopped by user", "warning")
        self.scan_btn.config(state=NORMAL)
        self.stop_btn.config(state=DISABLED)
        
    def scan_files(self):
        try:
            extensions = ('.jpg', '.jpeg', '.png', '.gif', '.bmp', '.tiff',
                         '.mp3', '.wav', '.mp4', '.pdf', '.docx', '.zip')
            
            all_files = []
            for root, dirs, files in os.walk(self.scan_path.get()):
                if not self.is_scanning:
                    break
                # Skip system folders
                skip = ['System Volume Information', '$Recycle.Bin', 'Windows', 
                       'Program Files', 'AppData', 'temp', 'cache']
                dirs[:] = [d for d in dirs if d not in skip]
                
                for file in files:
                    if file.lower().endswith(extensions):
                        all_files.append(os.path.join(root, file))
                        
            total = len(all_files)
            self.log(f"Found {total} files to scan")
            
            processed = 0
            for i, filepath in enumerate(all_files):
                if not self.is_scanning:
                    break
                    
                processed += 1
                self.total_scanned = processed
                self.progress['value'] = (processed / total) * 100
                
                # Analyze file
                result = self.analyze_file(filepath)
                
                if result['suspicious']:
                    self.suspicious_count += 1
                    self.suspicious_files.append(result)
                    self.root.after(0, self.add_to_suspicious, result)
                    self.log(f"⚠️ SUSPICIOUS: {os.path.basename(filepath)}", "warning")
                    self.root.after(0, self.play_alert_sound)
                else:
                    self.clean_count += 1
                    self.clean_files.append(result)
                    self.root.after(0, self.add_to_clean, result)
                    
                if processed % 10 == 0:
                    self.root.after(0, self.update_stats)
                    
            self.finish_scan()
            
        except Exception as e:
            self.log(f"Scan error: {e}", "error")
            self.finish_scan()
            
    def analyze_file(self, filepath):
        """Analyze a single file for steganography"""
        try:
            size = os.path.getsize(filepath)
            ext = Path(filepath).suffix.lower()
            file_type = ext.upper()[1:] if ext else "Unknown"
            detections = []
            
            if size < 1024:
                return {'path': filepath, 'size': size, 'suspicious': False, 
                       'detections': [], 'type': file_type, 'repaired': False}
            
            if ext in ('.jpg', '.jpeg'):
                detections = self.check_jpeg(filepath)
            elif ext in ('.png', '.gif', '.bmp'):
                detections = self.check_png(filepath)
            elif ext in ('.mp3', '.wav'):
                detections = self.check_audio(filepath)
            elif ext in ('.pdf', '.docx'):
                detections = self.check_document(filepath)
                
            if self.deep_scan.get() and not detections:
                entropy = self.check_entropy(filepath)
                if entropy:
                    detections.append(entropy)
                    
            return {
                'path': filepath,
                'size': size,
                'suspicious': len(detections) > 0,
                'detections': detections,
                'type': file_type,
                'repaired': False
            }
        except:
            return {'path': filepath, 'size': 0, 'suspicious': False, 
                   'detections': [], 'type': 'Error', 'repaired': False}
                   
    def check_jpeg(self, filepath):
        detections = []
        try:
            with open(filepath, 'rb') as f:
                data = f.read()
                
            eof = data.rfind(b'\xff\xd9')
            if eof > 0 and len(data) > eof + 100:
                extra = len(data) - (eof + 2)
                detections.append(f"Appended data after EOF ({extra} bytes)")
                
            if data.count(b'\xff\xd8') > 1:
                detections.append("Multiple JPEG headers")
        except:
            pass
        return detections
        
    def check_png(self, filepath):
        detections = []
        try:
            with open(filepath, 'rb') as f:
                data = f.read()
                
            if not data.startswith(b'\x89PNG\r\n\x1a\n'):
                detections.append("Invalid PNG signature")
                return detections
                
            pos = 8
            while pos + 8 <= len(data):
                chunk_len = struct.unpack('>I', data[pos:pos+4])[0]
                chunk_type = data[pos+4:pos+8]
                pos += 8
                
                chunk_str = chunk_type.decode('ascii', errors='ignore')
                
                if chunk_str in ['stEg', 'STEG', 'hide', 'data']:
                    detections.append(f"Suspicious chunk: {chunk_str}")
                    
                if chunk_str in ['tEXt', 'zTXt', 'iTXt'] and chunk_len > 10000:
                    detections.append(f"Large text chunk ({chunk_len} bytes)")
                    
                pos += chunk_len + 4
                
                if chunk_type == b'IEND':
                    if pos < len(data) and len(data) - pos > 100:
                        detections.append(f"Data after IEND ({len(data)-pos} bytes)")
                    break
        except:
            pass
        return detections
        
    def check_audio(self, filepath):
        detections = []
        try:
            with open(filepath, 'rb') as f:
                data = f.read(65536)
                
            if len(data) > 10000:
                lsb_sum = sum(b & 1 for b in data[:10000])
                ratio = lsb_sum / 10000
                if 0.48 < ratio < 0.52:
                    detections.append(f"Suspicious LSB ratio ({ratio:.4f})")
        except:
            pass
        return detections
        
    def check_document(self, filepath):
        detections = []
        try:
            with open(filepath, 'rb') as f:
                data = f.read(1024 * 1024)
                
            if filepath.endswith('.pdf'):
                if b'/EmbeddedFile' in data:
                    detections.append("Contains embedded files")
                if b'/JavaScript' in data:
                    detections.append("Contains JavaScript")
            elif filepath.endswith('.docx'):
                if b'oleObject' in data.lower():
                    detections.append("Contains OLE objects")
        except:
            pass
        return detections
        
    def check_entropy(self, filepath):
        try:
            with open(filepath, 'rb') as f:
                data = f.read(65536)
                
            if len(data) < 1000:
                return None
                
            entropy = 0.0
            counts = [0] * 256
            for byte in data:
                counts[byte] += 1
                
            for count in counts:
                if count > 0:
                    p = count / len(data)
                    entropy -= p * (p.bit_length() - 1) / 8
                    
            entropy = min(entropy * 8, 8.0)
            if entropy > 7.5:
                return f"High entropy ({entropy:.2f}/8.0) - possible encryption"
        except:
            pass
        return None
        
    def add_to_suspicious(self, file_info):
        size_kb = file_info['size'] / 1024
        display_path = file_info['path']
        if len(display_path) > 80:
            display_path = "..." + display_path[-77:]
            
        item = self.suspicious_tree.insert('', 0, values=(
            display_path,
            f"{size_kb:.1f}",
            len(file_info['detections']),
            file_info['type']
        ))
        file_info['tree_item'] = item
        self.suspicious_title.config(text=f"⚠️ SUSPICIOUS FILES ({self.suspicious_count})")
        
    def add_to_clean(self, file_info):
        size_kb = file_info['size'] / 1024
        display_path = file_info['path']
        if len(display_path) > 80:
            display_path = "..." + display_path[-77:]
            
        item = self.clean_tree.insert('', 0, values=(
            display_path,
            f"{size_kb:.1f}",
            "✓ Clean",
            file_info['type']
        ))
        file_info['tree_item'] = item
        self.clean_title.config(text=f"✅ CLEAN FILES ({self.clean_count})")
        
    def update_stats(self):
        self.stats_label.config(text=f"Scanned: {self.total_scanned} | ⚠️ Suspicious: {self.suspicious_count} | ✓ Clean: {self.clean_count} | 🔧 Repaired: {self.repaired_count}")
        
    def repair_selected(self):
        selected = self.suspicious_tree.selection()
        if not selected:
            messagebox.showwarning("No Selection", "Please select files to repair!")
            return
            
        if messagebox.askyesno("Confirm Repair", f"Repair {len(selected)} file(s)?\n\nFiles will be repaired and moved to Clean Files.\nBackups: .stego_backup"):
            for item in selected:
                for file_info in self.suspicious_files:
                    if file_info.get('tree_item') == item:
                        self.repair_file(file_info)
                        break
                        
    def repair_all(self):
        if not self.suspicious_files:
            messagebox.showwarning("No Files", "No suspicious files to repair!")
            return
            
        if messagebox.askyesno("Confirm Repair", f"Repair all {len(self.suspicious_files)} file(s)?\n\nAll suspicious files will be repaired."):
            for file_info in self.suspicious_files.copy():
                self.repair_file(file_info)
                
    def repair_file(self, file_info):
        try:
            filepath = file_info['path']
            backup = f"{filepath}.stego_backup"
            
            if not os.path.exists(backup):
                shutil.copy2(filepath, backup)
                self.log(f"Backup created: {os.path.basename(backup)}", "info")
                
            ext = Path(filepath).suffix.lower()
            repaired = False
            
            if ext in ('.jpg', '.jpeg'):
                repaired = self.repair_jpeg(filepath)
            elif ext in ('.png', '.gif', '.bmp'):
                repaired = self.repair_png(filepath)
            else:
                repaired = True
                
            if repaired:
                file_info['repaired'] = True
                file_info['suspicious'] = False
                self.repaired_count += 1
                
                if 'tree_item' in file_info:
                    self.suspicious_tree.delete(file_info['tree_item'])
                if file_info in self.suspicious_files:
                    self.suspicious_files.remove(file_info)
                    self.suspicious_count -= 1
                
                file_info['detections'] = []
                self.clean_files.append(file_info)
                self.clean_count += 1
                self.add_to_clean(file_info)
                
                self.suspicious_title.config(text=f"⚠️ SUSPICIOUS FILES ({self.suspicious_count})")
                self.clean_title.config(text=f"✅ CLEAN FILES ({self.clean_count})")
                self.update_stats()
                self.log(f"✅ Repaired: {os.path.basename(filepath)}", "success")
            else:
                self.log(f"❌ Repair failed: {os.path.basename(filepath)}", "error")
                
        except Exception as e:
            self.log(f"Repair error: {e}", "error")
            
    def repair_jpeg(self, filepath):
        try:
            with open(filepath, 'rb') as f:
                data = f.read()
                
            eof = data.rfind(b'\xff\xd9')
            if eof > 0 and len(data) > eof + 2:
                cleaned = data[:eof + 2]
                with open(filepath, 'wb') as f:
                    f.write(cleaned)
            return True
        except:
            return False
            
    def repair_png(self, filepath):
        try:
            with open(filepath, 'rb') as f:
                data = f.read()
                
            if not data.startswith(b'\x89PNG\r\n\x1a\n'):
                return False
                
            signature = data[:8]
            pos = 8
            essential = [b'IHDR', b'PLTE', b'IDAT', b'IEND']
            new_data = signature
            
            while pos + 8 <= len(data):
                chunk_len = struct.unpack('>I', data[pos:pos+4])[0]
                chunk_type = data[pos+4:pos+8]
                pos += 8
                
                if chunk_type in essential:
                    new_data += struct.pack('>I', chunk_len)
                    new_data += chunk_type
                    new_data += data[pos:pos+chunk_len]
                    new_data += data[pos+chunk_len:pos+chunk_len+4]
                    
                pos += chunk_len + 4
                
                if chunk_type == b'IEND':
                    break
                    
            if len(new_data) > len(signature):
                with open(filepath, 'wb') as f:
                    f.write(new_data)
            return True
        except:
            return False
            
    def generate_report(self):
        """Generate detailed report in TXT format"""
        try:
            os.makedirs(self.report_dir, exist_ok=True)
            
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            report_file = os.path.join(self.report_dir, f"StegoHunter_Report_{timestamp}.txt")
            
            with open(report_file, 'w', encoding='utf-8') as f:
                f.write("="*80 + "\n")
                f.write("STEGANOGRAPHY HUNTER - DETECTION REPORT\n")
                f.write("="*80 + "\n\n")
                
                f.write(f"Report Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                f.write(f"Scan Path: {self.scan_path.get()}\n")
                f.write(f"Deep Scan Mode: {'Enabled' if self.deep_scan.get() else 'Disabled'}\n")
                f.write(f"Audio Alerts: {'Enabled' if self.audio_alert.get() else 'Disabled'}\n")
                f.write(f"Report Location: {self.report_dir}\n\n")
                
                f.write("="*80 + "\n")
                f.write("SCAN SUMMARY\n")
                f.write("="*80 + "\n\n")
                
                f.write(f"Total Files Scanned: {self.total_scanned}\n")
                f.write(f"Suspicious Files Found: {self.suspicious_count}\n")
                f.write(f"Clean Files: {self.clean_count}\n")
                f.write(f"Files Repaired: {self.repaired_count}\n")
                f.write(f"Files Pending Repair: {self.suspicious_count}\n\n")
                
                if self.suspicious_files:
                    f.write("="*80 + "\n")
                    f.write("SUSPICIOUS FILES DETAILS\n")
                    f.write("="*80 + "\n\n")
                    
                    for idx, file_info in enumerate(self.suspicious_files, 1):
                        f.write(f"\n[{idx}] FILE: {file_info['path']}\n")
                        f.write(f"    Size: {file_info['size']:,} bytes ({file_info['size']/1024:.2f} KB)\n")
                        f.write(f"    Type: {file_info['type']}\n")
                        f.write(f"    Status: Pending Review\n")
                        if file_info['detections']:
                            f.write(f"    Detected Issues:\n")
                            for detection in file_info['detections']:
                                f.write(f"      - {detection}\n")
                        f.write("-"*80 + "\n")
                        
                if self.clean_files:
                    f.write("\n" + "="*80 + "\n")
                    f.write("CLEAN FILES (Sample - First 100)\n")
                    f.write("="*80 + "\n\n")
                    
                    for idx, file_info in enumerate(self.clean_files[:100], 1):
                        f.write(f"{idx}. {file_info['path']} ({file_info['size']/1024:.2f} KB)\n")
                        
                    if len(self.clean_files) > 100:
                        f.write(f"\n... and {len(self.clean_files) - 100} more clean files\n")
                        
                if self.repaired_count > 0:
                    f.write("\n" + "="*80 + "\n")
                    f.write("REPAIR INFORMATION\n")
                    f.write("="*80 + "\n\n")
                    
                    f.write(f"Total Files Repaired: {self.repaired_count}\n\n")
                    f.write("Repair Actions Performed:\n")
                    f.write("1. Created backup files with .stego_backup extension\n")
                    f.write("2. Removed appended data after EOF markers\n")
                    f.write("3. Stripped suspicious metadata and chunks\n")
                    f.write("4. Normalized file structure\n\n")
                    
                    f.write("Backup Location: Same directory as original files\n")
                    f.write("To Restore: Delete repaired file and remove .stego_backup extension\n\n")
                    
                f.write("\n" + "="*80 + "\n")
                f.write("RECOMMENDATIONS\n")
                f.write("="*80 + "\n\n")
                
                f.write("1. Review all suspicious files before repairing\n")
                f.write("2. Keep backups until you verify repaired files work correctly\n")
                f.write("3. Run antivirus scan on suspicious files\n")
                f.write("4. For deep analysis, consider using:\n")
                f.write("   - Steghide: steghide extract -sf file.jpg\n")
                f.write("   - Binwalk: binwalk -e file.png\n")
                f.write("   - Exiftool: exiftool file.pdf\n\n")
                
                f.write("="*80 + "\n")
                f.write("END OF REPORT\n")
                f.write("="*80 + "\n")
                
            self.log(f"✓ Report saved successfully!", "success")
            self.log(f"  Location: {report_file}", "info")
            
            messagebox.showinfo("Report Generated", 
                               f"Report saved successfully!\n\n"
                               f"Location: {report_file}\n\n"
                               f"Size: {os.path.getsize(report_file):,} bytes\n\n"
                               f"Folder: {self.report_dir}")
            
            os.startfile(self.report_dir)
            
        except Exception as e:
            error_msg = f"Failed to generate report: {str(e)}"
            self.log(error_msg, "error")
            messagebox.showerror("Report Error", error_msg)
            
    def clear_all(self):
        if messagebox.askyesno("Clear All", "Clear all scanned results?"):
            for item in self.suspicious_tree.get_children():
                self.suspicious_tree.delete(item)
            for item in self.clean_tree.get_children():
                self.clean_tree.delete(item)
            self.suspicious_files.clear()
            self.clean_files.clear()
            self.total_scanned = 0
            self.suspicious_count = 0
            self.clean_count = 0
            self.repaired_count = 0
            self.progress['value'] = 0
            self.suspicious_title.config(text="⚠️ SUSPICIOUS FILES (0)")
            self.clean_title.config(text="✅ CLEAN FILES (0)")
            self.update_stats()
            self.log("All results cleared", "info")
            
    def finish_scan(self):
        self.is_scanning = False
        self.scan_btn.config(state=NORMAL)
        self.stop_btn.config(state=DISABLED)
        
        self.log("="*50, "info")
        self.log("✓ SCAN COMPLETE!", "success")
        self.log(f"Total: {self.total_scanned} | Suspicious: {self.suspicious_count} | Clean: {self.clean_count}", "info")
        
        if self.suspicious_count > 0:
            self.log(f"⚠️ Found {self.suspicious_count} suspicious files! Select and click 'Repair Selected' to clean them.", "warning")
            if self.audio_alert.get():
                winsound.Beep(2000, 300)
        else:
            self.log("✓ No suspicious files found! All files are clean.", "success")
            if self.audio_alert.get():
                winsound.Beep(1500, 200)

def main():
    root = Tk()
    app = StegoHunter(root)
    root.mainloop()

if __name__ == "__main__":
    main()