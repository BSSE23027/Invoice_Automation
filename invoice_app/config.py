from django.conf import settings


GMAIL_QUERY = (
    f'from:{settings.GMAIL_SENDER} '
    f'subject:"{settings.GMAIL_SUBJECT}" '
    'has:attachment'
)


