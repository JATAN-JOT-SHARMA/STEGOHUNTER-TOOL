import os
from datetime import datetime
from reportlab.lib import colors
from reportlab.platypus import (
    SimpleDocTemplate,
    Spacer,
    Paragraph,
    PageBreak
)
from reportlab.lib.styles import getSampleStyleSheet


class ReportGenerator:

    def __init__(self, gui):
        self.gui = gui

        self.report_folder = os.path.join(
            os.getcwd(),
            "reports"
        )

        os.makedirs(
            self.report_folder,
            exist_ok=True
        )

    def generate(self):

        try:

            timestamp = datetime.now().strftime(
                "%Y%m%d_%H%M%S"
            )

            txt_report = os.path.join(
                self.report_folder,
                f"Stego_Report_{timestamp}.txt"
            )

            pdf_report = os.path.join(
                self.report_folder,
                f"Stego_Report_{timestamp}.pdf"
            )

            # ----------------------------
            # TXT REPORT
            # ----------------------------
            with open(
                txt_report,
                "w",
                encoding="utf-8"
            ) as f:

                f.write(
                    "STEGOHUNTER V4.2 REPORT\n"
                )
                f.write("=" * 50 + "\n\n")

                f.write(
                    f"Generated: {datetime.now()}\n\n"
                )

                f.write(
                    f"Total Suspicious Files: "
                    f"{len(self.gui.suspicious_files)}\n"
                )

                f.write(
                    f"Total Clean Files: "
                    f"{len(self.gui.clean_files)}\n\n"
                )

                f.write(
                    "SUSPICIOUS FILES\n"
                )
                f.write("-" * 50 + "\n")

                for file in self.gui.suspicious_files:
                    f.write(file + "\n")

                f.write("\n")

                f.write(
                    "CLEAN FILES\n"
                )
                f.write("-" * 50 + "\n")

                for file in self.gui.clean_files:
                    f.write(file + "\n")

            # ----------------------------
            # PDF REPORT
            # ----------------------------
            doc = SimpleDocTemplate(
                pdf_report
            )

            styles = getSampleStyleSheet()

            story = []

            title = Paragraph(
                "STEGOHUNTER V4.2 REPORT",
                styles['Title']
            )

            story.append(title)
            story.append(
                Spacer(1, 20)
            )

            story.append(
                Paragraph(
                    f"Generated: "
                    f"{datetime.now()}",
                    styles['BodyText']
                )
            )

            story.append(
                Spacer(1, 15)
            )

            story.append(
                Paragraph(
                    f"Suspicious Files: "
                    f"{len(self.gui.suspicious_files)}",
                    styles['Heading2']
                )
            )

            for file in self.gui.suspicious_files:
                story.append(
                    Paragraph(
                        file,
                        styles['BodyText']
                    )
                )

            story.append(
                Spacer(1, 20)
            )

            story.append(
                Paragraph(
                    f"Clean Files: "
                    f"{len(self.gui.clean_files)}",
                    styles['Heading2']
                )
            )

            for file in self.gui.clean_files:
                story.append(
                    Paragraph(
                        file,
                        styles['BodyText']
                    )
                )

            doc.build(story)

            self.gui.log(
                "[+] Report generated successfully"
            )

            self.gui.log(
                f"[TXT] {txt_report}"
            )

            self.gui.log(
                f"[PDF] {pdf_report}"
            )

        except Exception as e:

            self.gui.log(
                f"[Report Error] {str(e)}"
            )