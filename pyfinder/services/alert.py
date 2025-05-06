import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email.mime.text import MIMEText
from email import encoders
import os

def send_email_with_attachment_smtp(from_addr, password, to_addrs, subject, body, attachments):
    if isinstance(to_addrs, str):
        to_addrs = [to_addrs]

    msg = MIMEMultipart()
    msg["From"] = from_addr
    msg["To"] = ", ".join(to_addrs)
    msg["Subject"] = subject
    msg.attach(MIMEText(body, "plain"))

    for filepath in attachments:
        part = MIMEBase("application", "octet-stream")
        with open(filepath, "rb") as f:
            part.set_payload(f.read())
        encoders.encode_base64(part)
        filename = os.path.basename(filepath)
        part.add_header("Content-Disposition", f"attachment; filename={filename}")
        msg.attach(part)

    # Connect to Gmail SMTP server over TLS
    with smtplib.SMTP("smtp.gmail.com", 587) as server:
        server.starttls()
        server.login(from_addr, password)
        server.sendmail(from_addr, to_addrs, msg.as_string())

if __name__ == "__main__":
    to_addresses = ["xxx@xxx.com", "yyy@xxx.ch", "zzz@xxx.ch"]
    app_password = ""  
    from_address = "xxx@xxx.com"
    subject = "FinDer with parametric data"
    body = "THIS IS A PLAYBACK.\npyFinder detected a new event and created a shakemap. Please find the shakemap attached."
    attachments = ["/root/shakemap_profiles/default/data/20230206_0000008/current/products/intensity.jpg"]  # Update path as needed

    send_email_with_attachment_smtp(from_address, app_password, to_addresses, subject, body, attachments)
    print("Email sent successfully.")