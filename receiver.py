import imaplib
import email
from io import StringIO
from html.parser import HTMLParser

class MLStripper(HTMLParser):
    def __init__(self):
        super().__init__()
        self.reset()
        self.strict = True
        self.convert_charrefs = True
        self.text = StringIO()

    def handle_data(self, d):
        self.text.write(d)

    def get_data(self):
        return self.text.getvalue()

def decode_payload(payload, charset):
    # Decoding the payload using the charset provided by the email message
    try:
        return payload.decode(charset)
    except UnicodeDecodeError:
        return payload.decode('utf-8', 'ignore')


def strip_tags(html):
    # Stripping html tags
    s = MLStripper()
    s.feed(html)
    return s.get_data()
class Email:
    def __init__(self, eid, from_email, subject, date, message):
        self.id = eid
        self.from_email = from_email
        self.subject = self._decode_subject(subject)
        self.date = date
        self.messages = []
        self.stripped_messages = []

        if message.is_multipart():
            # Some emails contain html and plain text, I only want one or the other not both
            # But preferably the html will look nicer - 7432 this is not copied :)
            has_html_content = False
            for part in message.walk():
                content_type = part.get_content_type()
                if content_type == "text/html":
                    has_html_content = True
                    break

            for part in message.walk():
                content_type = part.get_content_type()
                content_disposition = str(part.get("Content-Disposition"))
                if "attachment" not in content_disposition:
                    if (not has_html_content and content_type == "text/plain") or content_type == "text/html":
                        charset = part.get_content_charset() or 'utf-8'
                        m = (decode_payload(part.get_payload(decode=True), charset))
                        self.messages.append(m)
                        self.stripped_messages.append(strip_tags(m))
        else:
            charset = message.get_content_charset() or 'utf-8'
            m = decode_payload(message.get_payload(decode=True), charset)
            self.messages.append(m)
            self.stripped_messages.append(strip_tags(m))

    @staticmethod
    def _decode_subject(subject):
        # Decode the subject header using the provided encoding
        decoded_parts = email.header.decode_header(subject)
        decoded_subject = ""
        for part, encoding in decoded_parts:
            if isinstance(part, bytes):
                decoded_subject += part.decode(encoding or "utf-8", errors="replace")
            else:
                decoded_subject += part
        return decoded_subject

class Receiver:
    def __init__(self, email_address, password, imap_server, port):
        self.email_address = email_address
        self.password = password
        self.imap_server = imap_server
        self.port = port

        # Logging in to be able to receive messages
        self.mail = imaplib.IMAP4_SSL(imap_server, port=port)
        self.mail.login(email_address, password)
        self.mail.select('inbox')
        self.emails = {}


    def close(self):
        try:
            self.mail.close()
            self.mail.logout()
        except Exception as e:
            print(e)

    def search(self, criteria):
        status, data = self.mail.search(None, criteria)

        emails = []
        nums = data[0].split()
        # Display messages in reverse order, because messages where coming in ascending order
        for i in range(len(nums)-1, -1, -1):
            e = self.get_email_by_id(nums[i])
            if e is None:
                continue
            emails.append(e)

        return emails

    def get_email_by_id(self, eid):
        # Different email clients use different encoding for the email id
        eid = eid.decode('utf-8') if isinstance(eid, bytes) else eid

        # If email is already cached return the cached version
        if eid in self.emails:
            return self.emails[eid]

        # Fetching the email using the id
        status, data = self.mail.fetch(eid, '(RFC822)')

        if status == 'OK' and data:
            # iCloud was not working for some reason
            if isinstance(data[0][1], int):
                return None
            email_message = email.message_from_bytes(data[0][1])
            self.emails[eid] = Email(
                eid,
                email_message['From'],
                email_message['Subject'],
                email.utils.parsedate_to_datetime(email_message["Date"]),
                email_message
            )

            # Cache email to improve performance
            return self.emails[eid]
        else:
            return None
