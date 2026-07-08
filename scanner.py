import os


class StegoScanner:

    def __init__(self, gui):
        self.gui = gui

        self.supported_extensions = (
            ".jpg",
            ".jpeg",
            ".png",
            ".bmp",
            ".gif"
        )

    def scan_folder(self, folder_path, deep_scan=False):

        if not folder_path:
            self.gui.log("[ERROR] No folder selected")
            return

        files = []

        for root, dirs, filenames in os.walk(folder_path):

            for file in filenames:

                filepath = os.path.join(root, file)

                if filepath.lower().endswith(
                        self.supported_extensions):
                    files.append(filepath)

        total_files = len(files)

        self.gui.total_files_label.configure(
            text=f"Total Files: {total_files}"
        )

        if total_files == 0:
            self.gui.log("[!] No supported image files found")
            return

        suspicious_count = 0
        clean_count = 0

        for index, filepath in enumerate(files):

            if self.gui.stop_scan_flag:
                self.gui.log("[!] Scan stopped")
                break

            filename = os.path.basename(filepath)

            self.gui.progress_label.configure(
                text=f"Scanning: {filename}"
            )

            progress = (index + 1) / total_files
            self.gui.progress_bar.set(progress)

            is_suspicious = self.detect_stego(
                filepath,
                deep_scan
            )

            if is_suspicious:

                suspicious_count += 1

                self.gui.suspicious_files.append(filepath)

                self.gui.suspicious_listbox.insert(
                    "end",
                    filepath
                )

                self.gui.log(
                    f"[SUSPICIOUS] {filename}"
                )

            else:

                clean_count += 1

                self.gui.clean_files.append(filepath)

                self.gui.clean_listbox.insert(
                    "end",
                    filepath
                )

                self.gui.log(
                    f"[CLEAN] {filename}"
                )

            self.gui.suspicious_label.configure(
                text=f"Suspicious: {suspicious_count}"
            )

            self.gui.clean_label.configure(
                text=f"Clean: {clean_count}"
            )

        self.gui.progress_label.configure(
            text="Scan Completed"
        )

        self.gui.progress_bar.set(1)

        self.gui.log("[+] Scan completed")

        self.gui.scanning = False

    def detect_stego(self, filepath, deep_scan=False):

        try:
            ext = os.path.splitext(filepath)[1].lower()

            # JPG/JPEG appended payload detection
            if ext in [".jpg", ".jpeg"]:

                with open(filepath, "rb") as f:
                    content = f.read()

                eof_index = content.rfind(b'\xff\xd9')

                if eof_index != -1:

                    extra_data = content[eof_index + 2:]

                    if len(extra_data) > 100:
                        return True

            # PNG hidden keyword detection
            elif ext == ".png":

                with open(filepath, "rb") as f:
                    data = f.read().lower()

                suspicious_keywords = [
                    b"stego",
                    b"hidden",
                    b"secret",
                    b"payload"
                ]

                for keyword in suspicious_keywords:
                    if keyword in data:
                        return True

            # Deep Scan
            if deep_scan:

                file_size = os.path.getsize(filepath)

                # suspicious oversized image
                if file_size > 25 * 1024 * 1024:
                    return True

            return False

        except Exception as e:

            self.gui.log(
                f"[ERROR] {str(e)}"
            )

            return False