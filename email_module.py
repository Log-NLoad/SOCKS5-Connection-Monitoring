import smtplib
from email.mime.text import MIMEText

def send_email(smtp_host, smtp_port, sender_email, sender_password, recipient_email, subject, body, failed_proxy=None):

    try:
        if failed_proxy:
            body += f"\n\nFailed Proxy: {failed_proxy['server']}:{failed_proxy['port']}"

        msg = MIMEText(body, 'plain')
        msg['Subject'] = subject
        msg['From'] = sender_email
        msg['To'] = recipient_email

        if smtp_port == 587:
            with smtplib.SMTP(smtp_host, smtp_port) as smtp_server:
                smtp_server.ehlo()
                smtp_server.starttls()
                smtp_server.login(sender_email, sender_password)
                smtp_server.sendmail(sender_email, recipient_email, msg.as_string())
        elif smtp_port == 465:
            with smtplib.SMTP_SSL(smtp_host, smtp_port) as smtp_server:
                smtp_server.login(sender_email, sender_password)
                smtp_server.sendmail(sender_email, recipient_email, msg.as_string())
        else:
            print(f"❌ Error: unsupported SMTP port: {smtp_port}")
            return

        print("📨 Email sent successfully.")

    except Exception as e:
        print(f"❌ Error sending the email: {e}")