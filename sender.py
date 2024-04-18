import smtplib, ssl
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

class Sender:
    def __init__(self, from_email, password, smtp_server, port):
        self.from_email = from_email
        self.password = password
        self.smtp_server = smtp_server
        self.port = port
        self.server = None

        self.initiate_connection()

    def initiate_connection(self):
        context = ssl.create_default_context()

        self.server = smtplib.SMTP(self.smtp_server, self.port)
        self.server.starttls(context=context)
        self.server.login(self.from_email, self.password)

    def sendMessage(self, to, subject, body, body_type="plain"):
        message = MIMEMultipart("alternative")
        message["Subject"] = subject
        message["From"] = self.from_email
        message["To"] = to
        message.attach(MIMEText(body, body_type))

        try:
            self.server.sendmail(self.from_email, to, message.as_string())
        except:
            self.initiate_connection()
            self.server.sendmail(self.from_email, to, message.as_string())

    def close(self):
        try:
            self.server.close()
        except Exception as e:
            print(e)