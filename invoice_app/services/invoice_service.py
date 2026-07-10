from django.core.cache import cache
from django.utils import timezone
from invoice_app.services.gmail_service import GmailService
from invoice_app.services.validator import Validator
from invoice_app.services.word_parser import WordParser
from invoice_app.services.excel_service import ExcelService
from invoice_app.services.file_manager import FileManager


class InvoiceService:

    CACHE_KEY = "latest_invoice"

    def get_latest_invoice(self):

        cached = cache.get(self.CACHE_KEY)

        if cached:
            return cached

        gmail = GmailService()

        path = gmail.download_latest_invoice()

        if path is None:
            return None
        try:
            parser = WordParser(path)
            invoice = parser.parse()
            invoice["cached_at"] = timezone.now()
        finally:
            FileManager().delete_file(path)


        cache.set(self.CACHE_KEY, invoice, timeout=None)

        return invoice

    def refresh_latest_invoice(self):

        cache.delete(self.CACHE_KEY)

        return self.get_latest_invoice()

    def process_invoice(self, excel_path):

        invoice = self.get_latest_invoice()

        if invoice is None:
            raise Exception("No latest invoice found.")

        validator = Validator()

        validator.validate_invoice_number(
            excel_path,
            invoice["invoice_number"]
        )

        excel = ExcelService()

        return excel.update_invoice(
            excel_path,
            invoice["fbr_di"]
        )
