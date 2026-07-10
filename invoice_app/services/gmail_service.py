import os
import base64

from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from django.conf import settings
from invoice_app.config import GMAIL_QUERY

# Gmail API scope (read-only access)
SCOPES = ['https://www.googleapis.com/auth/gmail.readonly']


class GmailService:
    def __init__(self):
        self.service = self.authenticate()

    def authenticate(self):
        """
        Authenticate with Gmail API.
        Creates token.json the first time and reuses it afterwards.
        """
        creds = None

        if os.path.exists("token.json"):
            creds = Credentials.from_authorized_user_file(
                "token.json",
                SCOPES
            )

        if not creds or not creds.valid:

            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())

            else:
                flow = InstalledAppFlow.from_client_secrets_file(
                    "credentials.json",
                    SCOPES
                )

                creds = flow.run_local_server(port=0)

            with open("token.json", "w") as token:
                token.write(creds.to_json())

        return build(
            "gmail",
            "v1",
            credentials=creds
        )

    def get_latest_invoice_email(self):
        """
        Fetch the latest invoice email matching sender, subject,
        and containing an attachment.
        """

        query = GMAIL_QUERY

        results = self.service.users().messages().list(
            userId="me",
            q=query,
            maxResults=1
        ).execute()

        messages = results.get("messages", [])

        if not messages:
            return None

        message = self.service.users().messages().get(
            userId="me",
            id=messages[0]["id"]
        ).execute()

        return message

    def download_docx_attachment(self, message):
        """
        Downloads the DOCX attachment from the email
        into media/uploads and returns the saved path.
        """

        payload = message["payload"]
        parts = payload.get("parts", [])

        # Ensure upload directory exists
        upload_dir = settings.UPLOAD_FOLDER
        os.makedirs(upload_dir, exist_ok=True)

        for part in parts:

            filename = part.get("filename", "")

            if filename.endswith(".docx"):

                attachment_id = part["body"]["attachmentId"]

                attachment = self.service.users().messages().attachments().get(
                    userId="me",
                    messageId=message["id"],
                    id=attachment_id
                ).execute()

                file_data = base64.urlsafe_b64decode(
                    attachment["data"]
                )

                save_path = os.path.join(upload_dir, filename)

                with open(save_path, "wb") as f:
                    f.write(file_data)

                return save_path

        return None

    def download_latest_invoice(self):
        """
        Downloads the latest invoice DOCX and returns its path.
        """

        message = self.get_latest_invoice_email()

        if message is None:
            return None

        return self.download_docx_attachment(message)

