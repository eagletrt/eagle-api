import smtplib
from email.message import EmailMessage


class Gmail:
    def __init__(self, username: str, password: str):
        self._username = username
        self._password = password

    def send_email(self, to_address: str, subject: str, body: str):
        msg = EmailMessage()
        msg["From"] = self._username
        msg["To"] = to_address
        msg["Subject"] = subject
        msg.set_content(body)

        with smtplib.SMTP("smtp.gmail.com", 587) as server:
            server.starttls()
            server.login(self._username, self._password)
            server.send_message(msg)
