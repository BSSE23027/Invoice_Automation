from pathlib import Path
from django.conf import settings
from django.core.files.storage import FileSystemStorage
import os


class FileManager:

    def __init__(self):
        self.upload_dir = Path(settings.MEDIA_ROOT) / "uploads"

        self.upload_dir.mkdir(
            parents=True,
            exist_ok=True
        )

        self.storage = FileSystemStorage(
            location=self.upload_dir
        )

    def save_uploaded_excel(self, uploaded_file):
        filename = self.storage.save(
            uploaded_file.name,
            uploaded_file
        )

        return str(self.upload_dir / filename)

    def delete_file(self, path):
        if path and os.path.exists(path):
            os.remove(path)
