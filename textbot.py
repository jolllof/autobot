import smtplib
from email.mime.text import MIMEText
import os

def send_sms_via_email(message,recipient="4342295810@txt.att.net"):

    sender_email = os.getenv('jolllofemail')
    sender_password = os.getenv('jolllofpw')

    # Create the email content
    msg = MIMEText(message)
    msg["Subject"] = "Trading Bot Alert"
    msg["From"] = sender_email
    msg["To"] = recipient

    # Send the email
    try:
        with smtplib.SMTP("smtp.gmail.com", 587) as server:
            server.starttls()
            server.login(sender_email, sender_password)
            server.sendmail(sender_email, recipient, msg.as_string())
            print("SMS sent successfully.")
    except Exception as e:
        print(f"Failed to send SMS: {e}")

# Example usage
#send_sms_via_email("1234567890", "att", "RSI Alert: Check your trading bot!")
