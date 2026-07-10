import re
from zipfile import ZipFile
from xml.etree import ElementTree as ET



class WordParser:
    NAMESPACE = {
        "w": "http://schemas.openxmlformats.org/wordprocessingml/2006/main"
    }

    def __init__(self, file_path):
        self.file_path = file_path
        self.text = self._extract_all_text()

    def _read_xml_text(self, zip_file, xml_path):
        """
        Read all text (<w:t>) from a DOCX XML file.
        """

        try:
            xml_data = zip_file.read(xml_path)
        except KeyError:
            return ""

        root = ET.fromstring(xml_data)

        texts = [
            node.text
            for node in root.findall(".//w:t", self.NAMESPACE)
            if node.text
        ]

        return " ".join(texts)

    def _extract_all_text(self):
        """
        Extract text from:
            - document.xml
            - header*.xml
            - footer*.xml
        """

        all_text = []

        with ZipFile(self.file_path) as docx:

            # Main document
            all_text.append(
                self._read_xml_text(docx, "word/document.xml")
            )

            # Headers
            for file in docx.namelist():
                if file.startswith("word/header") and file.endswith(".xml"):
                    all_text.append(
                        self._read_xml_text(docx, file)
                    )

            # Footers (future-proof)
            for file in docx.namelist():
                if file.startswith("word/footer") and file.endswith(".xml"):
                    all_text.append(
                        self._read_xml_text(docx, file)
                    )

        text = " ".join(all_text)

        # Normalize whitespace
        text = re.sub(r"\s+", " ", text)

        return text.strip()

    def extract_invoice_number(self):
        match = re.search(
            r"Invoice\s*#\s*(\d+)",
            self.text,
            re.IGNORECASE
        )

        return match.group(1) if match else None

    def extract_invoice_date(self):
        match = re.search(
            r"Date:\s*([A-Za-z0-9,\s]+?)\s+SALES INVOICE",
            self.text,
            re.IGNORECASE
        )

        return match.group(1).strip() if match else None

    def extract_fbr_di(self):
        match = re.search(
            r"FBR\s*DI\s*#\s*([A-Z0-9]+)",
            self.text,
            re.IGNORECASE
        )

        return match.group(1) if match else None

    def parse(self):
        return {
            "invoice_number": self.extract_invoice_number(),
            "invoice_date": self.extract_invoice_date(),
            "fbr_di": self.extract_fbr_di(),
        }

