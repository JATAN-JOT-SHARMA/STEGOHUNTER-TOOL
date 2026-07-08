import os
import shutil
from PIL import Image


class StegoRepair:

    def __init__(self, gui):
        self.gui = gui

        self.repaired_folder = os.path.join(
            os.getcwd(),
            "repaired_files"
        )

        os.makedirs(
            self.repaired_folder,
            exist_ok=True
        )

    def repair_file(self, filepath):

        try:

            filename = os.path.basename(filepath)
            ext = os.path.splitext(filepath)[1].lower()

            output_path = os.path.join(
                self.repaired_folder,
                filename
            )

            # -------------------------
            # JPG / JPEG Repair
            # -------------------------
            if ext in [".jpg", ".jpeg"]:

                with open(filepath, "rb") as f:
                    content = f.read()

                eof_index = content.rfind(
                    b'\xff\xd9'
                )

                if eof_index != -1:

                    cleaned = content[:eof_index + 2]

                    with open(output_path, "wb") as out:
                        out.write(cleaned)

                    return True, output_path

            # -------------------------
            # PNG Repair
            # -------------------------
            elif ext == ".png":

                img = Image.open(filepath)
                img.save(output_path)

                return True, output_path

            # -------------------------
            # BMP/GIF Copy
            # -------------------------
            elif ext in [".bmp", ".gif"]:

                shutil.copy(filepath, output_path)

                return True, output_path

            return False, None

        except Exception as e:

            self.gui.log(
                f"[Repair Error] {str(e)}"
            )

            return False, None

    def repair_all(self):

        repaired_count = 0

        for filepath in self.gui.suspicious_files:

            success, repaired_path = self.repair_file(
                filepath
            )

            if success:

                repaired_count += 1

                self.gui.log(
                    f"[REPAIRED] {os.path.basename(filepath)}"
                )

        self.gui.log(
            f"[+] Repaired {repaired_count} files"
        )

    def repair_selected(self):

        selected = self.gui.suspicious_listbox.curselection()

        if not selected:
            self.gui.log(
                "[!] No file selected"
            )
            return

        filepath = self.gui.suspicious_files[
            selected[0]
        ]

        success, repaired_path = self.repair_file(
            filepath
        )

        if success:

            self.gui.log(
                f"[REPAIRED] {os.path.basename(filepath)}"
            )

        else:

            self.gui.log(
                "[!] Repair failed"
            )