from sender import Sender
from receiver import Receiver
import json


def get_action():
    print("Choose the action you want to perform: ")
    print("1) Read your inbox")
    print("2) Send an email")
    print("3) Quit")
    return input("Enter: ")

f = open('known_mail_hosts.json')
data = json.load(f)

email = input("Enter Your email: ")
sender_domain = email.split("@")[1].lower()
if sender_domain in data:
    smtp_port = data[sender_domain]["smtp_port"]
    imap_port = data[sender_domain]["imap_port"]
    smtp_server = data[sender_domain]["smtp"]
    imap_server = data[sender_domain]["imap"]
else:
    smtp_server = input("Provide smtp server: ")
    smtp_port = input("Provide smtp port: ")

    imap_server = input("Provide imap server: ")
    imap_port = input("Provide imap port: ")

password = input("Enter your password: ")

sender = Sender(email, password, smtp_server, smtp_port)
receiver = Receiver(email, password, imap_server, imap_port)
print(f"Logged In successfully to {email}\n")


action = get_action()
while action != "3":
    if action == "1":
        search = input("Enter your search query: ")
        emails = receiver.search(f"SUBJECT {search}")
        for email in emails:
            print(f"From: {email.from_email}")
            print(f"Date: {email.date}")
            print(f"Subject: {email.subject}")
            print(f"Message: {email.message}")

    if action == "2":
        recipient = input("Recipient Email: ")
        subject = input("Subject: ")
        message = input("Body: ")

        sender.sendMessage(recipient, subject, message)
        print(f"Email Sent to {recipient}\n")

    action = get_action()

print("Bye!")
sender.close()
receiver.close()