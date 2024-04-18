from flask import Flask, render_template, redirect, url_for, request
from sender import Sender
from receiver import Receiver
import json
import threading
import imapclient
from plyer import notification

f = open('known_mail_hosts.json')
data = json.load(f)

app = Flask(__name__)

app.isLoggedIn = False
app.sender = None
app.receiver = None
app.email = None

def check_for_emails():
    with imapclient.IMAPClient(app.receiver.imap_server, port=app.receiver.port) as client:
        client.login(app.receiver.email_address, app.receiver.password)
        client.idle()
        print("Started listening for emails")
        try:
            while True:
                responses = client.idle_check(timeout=10)  # Check for notifications every 10 seconds
                if responses:
                    print(responses)
                    notification_title = "New Emails"
                    notification_message = "You have new emails in your inbox."
                    notification.notify(title=notification_title, message=notification_message)
        finally:
            client.idle_done()

app.email_thread = threading.Thread(target=check_for_emails)

@app.route("/")
def index():
    if not app.isLoggedIn:
        return redirect(url_for('login'))

    criteria = request.args.get("criteria", 'SUBJECT "Hello"').strip()
    try:
        emails = app.receiver.search(criteria)
    except:
        print(f"Criteria ({criteria}) is invalid!")
        emails = []
    message = request.args.get("message")
    return render_template(
        'index.html.jinja',
        my_email=app.email,
        emails=emails,
        search=criteria,
        message=message,
    )

@app.get("/login")
def login():
    if app.isLoggedIn:
        return redirect(url_for("index"))

    return render_template('login.html.jinja', error=request.args.get('error'))

@app.post("/send")
def send():
    if not app.isLoggedIn:
        return redirect(url_for("login"))

    app.sender.sendMessage(request.form["email"], request.form["subject"], request.form["message"])

    return redirect(url_for("index", message="Email sent successfully"))

@app.post('/login')
def login_perform():
    app.email = email = request.form["email"]
    password = request.form["password"]
    domain = email.split("@")[1].lower()
    if domain in data:
        smtp_port = data[domain]["smtp_port"]
        imap_port = data[domain]["imap_port"]
        smtp_server = data[domain]["smtp"]
        imap_server = data[domain]["imap"]
        try:
            app.sender = Sender(email, password, smtp_server, smtp_port)
            app.receiver = Receiver(email, password, imap_server, imap_port)
        except:
            return redirect(url_for("login", error="Wrong Email or password"))
    else:
        return redirect(url_for("login", error="Domain not supported"))

    app.isLoggedIn = True
    app.email_thread.start()
    return redirect(url_for("index"))

@app.post("/logout")
def logout():
    app.email_thread.join()
    app.isLoggedIn = False
    if app.sender:
        app.sender.close()
    if app.receiver:
        app.receiver.close()
    app.sender = app.receiver = None

    return redirect(url_for("login"))

@app.get("/email/<email_id>")
def view_email(email_id):
    if not app.isLoggedIn:
        return redirect(url_for('login'))

    criteria = request.args.get("criteria", 'SUBJECT "Hello"')
    emails = app.receiver.search(criteria)
    message = request.args.get("message")
    current_email = app.receiver.get_email_by_id(email_id)
    return render_template('index.html.jinja', my_email=app.email, emails=emails, search=criteria, message=message, current_email=current_email)