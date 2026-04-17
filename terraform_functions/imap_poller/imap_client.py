import imaplib
import email
import logging
from config import IMAP_HOST, IMAP_USER, IMAP_PASSWORD

logger = logging.getLogger(__name__)


def connect():
    """Подключение к IMAP серверу."""
    m = imaplib.IMAP4_SSL(IMAP_HOST)
    m.login(IMAP_USER, IMAP_PASSWORD)
    return m


def get_unread_emails():
    """Получение непрочитанных писем с вложениями."""
    m = connect()
    m.select('INBOX')

    try:
        typ, data = m.search(None, 'UNSEEN', 'HASATTACHMENT')
        if typ != 'OK' or not data[0]:
            m.logout()
            return []
    except Exception as e:
        logger.warning(f"IMAP search failed: {e}")
        m.logout()
        return []

    emails = []
    for num in data[0].split():
        try:
            typ, msg_data = m.fetch(num, '(RFC822)')
            if typ != 'OK':
                continue

            msg = email.message_from_bytes(msg_data[0][1])
            email_data = parse_email(msg)

            if email_data.get('body'):
                emails.append(email_data)
                m.store(num, '+FLAGS', '\\Seen')
        except Exception as e:
            logger.error(f"Failed to fetch email {num}: {e}")
            continue

    m.close()
    m.logout()
    return emails


def parse_email(msg) -> dict:
    """Парсинг email сообщения."""
    result = {
        'id': msg.get('message-id', ''),
        'from': msg.get('from', ''),
        'subject': msg.get('subject', ''),
        'body': None,
        'attachments': []
    }

    if msg.is_multipart():
        for part in msg.walk():
            content_type = part.get_content_type()
            if content_type == 'text/plain' and not result['body']:
                try:
                    payload = part.get_payload(decode=True)
                    if payload:
                        result['body'] = payload.decode('utf-8')
                except:
                    pass
    else:
        try:
            payload = msg.get_payload(decode=True)
            if payload:
                result['body'] = payload.decode('utf-8')
        except:
            pass

    for part in msg.walk():
        if part.get_content_disposition() == 'attachment':
            filename = part.get_filename()
            if filename:
                try:
                    result['attachments'].append({
                        'filename': filename,
                        'data': part.get_payload(decode=True)
                    })
                except:
                    pass

    return result