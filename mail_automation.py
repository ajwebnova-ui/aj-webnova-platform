import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os

class AJWebnovaMail:
    def __init__(self, email=None, password=None):
        self.email = email or os.getenv("SENDER_EMAIL")
        self.password = password or os.getenv("SENDER_PASSWORD")
        self.smtp_server = "smtp.gmail.com"
        self.smtp_port = 587

    def _send_raw_email(self, receiver_email, subject, body):
        if not self.email or not self.password:
            print("Email credentials missing!")
            return False

        message = MIMEMultipart()
        message["From"] = f"AJ Webnova <{self.email}>"
        message["To"] = receiver_email
        message["Subject"] = subject

        message.attach(MIMEText(body, "plain"))

        try:
            server = smtplib.SMTP(self.smtp_server, self.smtp_port)
            server.starttls()
            server.login(self.email, self.password)
            server.send_message(message)
            server.quit()
            return True
        except Exception as e:
            print(f"Mail Error: {e}")
            return False

    def send_proposal(self, receiver_email, client_name, proposal_content):
        """Sends the High-Ticket proposal to the client."""
        subject = f"Strategic Digital Growth Audit for {client_name}"
        body = f"Hello {client_name},\n\n{proposal_content}\n\nBest regards,\n\nVikas A J\nFounder, AJ Webnova"
        return self._send_raw_email(receiver_email, subject, body)

    def send_invoice(self, receiver_email, client_name, amount, upi_id):
        """Sends a formal payment request/invoice to the client."""
        subject = f"Payment Request: Project Advance for {client_name}"
        body = (
            f"Hello {client_name},\n\n"
            f"Following our proposal, we are ready to begin the project. To secure your slot in our calendar, "
            f"please process the 10% advance payment.\n\n"
            f"Amount Due: {amount}\n"
            f"Payment Method (UPI): {upi_id}\n\n"
            f"Please share a screenshot of the transaction once completed so we can initiate the project.\n\n"
            f"Best regards,\n\nVikas A J\nFounder, AJ Webnova"
        )
        return self._send_raw_email(receiver_email, subject, body)

    def send_internal_notification(self, receiver_email, subject, message):
        """Sends an alert to Vikas about a lead's status."""
        return self._send_raw_email(receiver_email, f"[AJ Webnova Alert] {subject}", message)
