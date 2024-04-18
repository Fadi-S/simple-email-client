import json
from sender import Sender
from receiver import Receiver

f = open('known_mail_hosts.json')
data = json.load(f)

sender_email = "nwspring94@gmail.com"
password = "kbfe gguf unuc xiwe"
smtp_server = data["gmail.com"]["smtp"]
smtp_port = data["gmail.com"]["smtp_port"]

receipient1 = sender_email
receipient2 = "nwsp24@awgarstone.com"

imap_server = data["gmail.com"]["imap"]
imap_port = data["gmail.com"]["imap_port"]

sender = Sender(sender_email, password, smtp_server, smtp_port)
receiver = Receiver(receipient1, password, imap_server, imap_port)
print("Logged in!\n")

sender.sendMessage(receipient1, "Hello 7432", "Sending test email")
sender.sendMessage(receipient2, "Hello 7432", "Sending test email")
print(f"Email sent successfully to {receipient1} and {receipient2}\n")

email = receiver.search("ALL").pop()
print("Last Email:")
print(f"From: {email.from_email}")
print(f"Date: {email.date}")
print(f"Subject: {email.subject}")
print("Body:")
for message in email.stripped_messages:
    print(message)