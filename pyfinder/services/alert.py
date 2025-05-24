import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email.mime.text import MIMEText
from email import encoders
import os
import json
from finderutils import FinderSolution
from datetime import datetime

def footer(html=True):
    if html:
        return '<br><hr><p style="font-size: 0.9em; color: gray;">Do not reply to this email. This address is not monitored.<br>For assistance, contact your EEW support group.</p>'
    else:
        return '\n\n--\nDo not reply to this email. This address is not monitored.\nFor assistance, contact your EEW support group.'

def send_email_with_attachment(subject=None, body=None, attachments=None, finder_solution=None, 
                               event_id=None, metadata=None):
    # Read SMTP configuration from JSON file
    _path = os.path.dirname(os.path.abspath(__file__))
    _path = os.path.join(_path, ".pyfinder_alert_config.json")
    
    if not os.path.exists(_path):
        # Look one directory up
        _path = os.path.dirname(os.path.abspath(__file__))
        _path = os.path.dirname(_path)
        _path = os.path.join(_path, ".pyfinder_alert_config.json")
        
        if not os.path.exists(_path):
            print("Configuration file not found.")
            return
    
    # Read the configuration file
    with open(_path, "r") as f:
        config = json.load(f)
        smtp_server = config.get("smtp_server", None)
        smtp_port = config.get("smtp_port", None)
        if smtp_server is None or smtp_port is None:
            return 
        
        from_addr = config.get("from", None)
        to_addrs = config.get("to", None)
        
        if from_addr is None or to_addrs is None:
            return
        
        password = config.get("password", None)
        if password is None:
            return
        
        if subject is None:
            subject = config.get("subject", None)

        if body is None:
            body = "pyFinder event alert."

        if not attachments:
            attachments = []
        elif isinstance(attachments, str):
            attachments = [attachments]

    if isinstance(to_addrs, str):
        to_addrs = [to_addrs]

    
    msg = MIMEMultipart()

    # From and To fields are the same
    msg["From"] = from_addr
    msg["To"] = from_addr

    # Add all recipients in Bcc
    # msg["Bcc"] = ", ".join(to_addrs)

    msg["Subject"] = subject

    # Build plain and HTML body
    plain_body = body + footer(html=False)
    html_body = "<html><body><p>{}</p>".format(body.replace('\n', '<br>'))

    # Append event and finder_solution info if provided
    if event_id:
        html_body += f"<p><strong>Event ID:</strong> {event_id}</p>"
        plain_body += f"\nEvent ID: {event_id}"
    
    if finder_solution:
        if isinstance(finder_solution, FinderSolution):
            event = finder_solution.get_event()
            if event:
                origin_time = datetime.fromtimestamp(event.get_origin_time_epoch()).strftime('%Y-%m-%d %H:%M:%S UTC')
                lat = round(event.get_latitude(), 3)
                lon = round(event.get_longitude(), 3)
                depth = round(event.get_depth(), 1)
                mag = round(event.get_magnitude(), 1)

                html_body += f"""
                <p><strong>FinDer Event Summary:</strong><br>
                Origin Time: {origin_time}<br>
                Latitude: {lat}<br>
                Longitude: {lon}<br>
                Depth (km): {depth}<br>
                Magnitude: {mag}</p>
                """

                plain_body += (
                    f"\nFinDer Event Summary:\n"
                    f"Origin Time: {origin_time}\n"
                    f"Latitude: {lat}\n"
                    f"Longitude: {lon}\n"
                    f"Depth: {depth} km\n"
                    f"Magnitude: {mag}\n"
                )

    # Include metadata if provided
    if metadata:
        plain_body += "\n\n--- Processing metadata ---\n"
        html_body += "<br><p><strong>Processing metadata:</strong><br>"

        # Hack the delay time field
        if 'minutes_until_next_update' in metadata:
            try:
                next_update = int(metadata['minutes_until_next_update'])

                if next_update <= 60:
                    metadata['time_until_next_update'] = str(next_update) + "m"
                else:
                    hours = int(next_update // 60)
                    minutes = int(next_update % 60)
                    metadata['time_until_next_update'] = f"{hours}h {minutes}m"
                    
                # Remove the old field from metadata
                del metadata['minutes_until_next_update']
            except:
                pass        

        # Also hack the current delay field
        if 'current_delay' in metadata:
            try:
                current_delay = int(metadata['current_delay'])
                if current_delay <= 60:
                    metadata['current_delay'] = str(current_delay) + "m"
                else:
                    hours = int(current_delay // 60)
                    minutes = int(current_delay % 60)
                    metadata['current_delay'] = f"{hours}h {minutes}m"
            except:
                pass    

        # A bit tidy up the metadata
        key_order = ["origin_time", "latitude", "longitude", "depth", "magnitude", "magnitude_type"]
        for key in key_order:
            if key in metadata:
                label = key.replace('_', ' ').capitalize()
                plain_body += f"{label}: {metadata[key]}\n"
                html_body += f"{label}: {metadata[key]}<br>"

        # Add any other keys not in the defined order
        remaining_keys = sorted(k for k in metadata if k not in key_order)
        for key in remaining_keys:
            label = key.replace('_', ' ').capitalize()

            if 'Esm' in label:
                label = label.replace('Esm', 'ESM')
            elif 'Rrsm' in label:
                label = label.replace('Rrsm', 'RRSM')
            elif 'Emsc' in label:
                label = label.replace('Emsc', 'EMSC')

            plain_body += f"{label}: {metadata[key]}\n"
            html_body += f"{label}: {metadata[key]}<br>"
        html_body += "</p>"


    html_body += footer(html=True)
    html_body += "</body></html>"

    alt_part = MIMEMultipart("alternative")
    alt_part.attach(MIMEText(plain_body, "plain"))
    alt_part.attach(MIMEText(html_body, "html"))
    msg.attach(alt_part)

    for filepath in attachments:
        if not os.path.exists(filepath):
            print(f"Attachment file {filepath} does not exist.")
            continue
        if not os.path.isfile(filepath):
            print(f"Attachment {filepath} is not a file.")
            continue
        if not os.access(filepath, os.R_OK):
            print(f"Attachment {filepath} is not readable.")
            continue

        # Create a MIMEBase object for the attachment
        part = MIMEBase("application", "octet-stream")

        with open(filepath, "rb") as f:
            part.set_payload(f.read())
        
        encoders.encode_base64(part)
        filename = os.path.basename(filepath)
        part.add_header("Content-Disposition", f"attachment; filename={filename}")
        msg.attach(part)

    # Connect to Gmail SMTP server over TLS
    with smtplib.SMTP("smtp.gmail.com", smtp_port) as server:
        server.starttls()
        server.login(from_addr, password)

        all_recipients = [from_addr] + to_addrs
        server.sendmail(from_addr, all_recipients, msg.as_string())



# For standlone testing. Run this script from one directory up as 
# "python3 services/alert.py"
if __name__ == "__main__":
    subject = "Alert from FinDer with parametric data"
    body = "THIS IS A PLAYBACK.\npyFinder detected a new event and created a shakemap. Please find the shakemap attached."
    attachments = ["/root/shakemap_profiles/default/data/20230206_0000008/current/products/intensity.jpg"]  # Update path as needed

    # A fake finder_solution object for testing
    finder_solution = FinderSolution()
    
    from finderutils import FinderEvent
    event = FinderEvent()
    event.set_origin_time_epoch(1675645056)  # Example epoch time
    event.set_latitude(37.17)
    event.set_longitude(37.08)
    event.set_depth(20.0)
    event.set_magnitude(7.7)
    finder_solution.set_event(event)
    event_id = "20230206_0000008"

    # Fake metadata for testing
    metadata = {}
    metadata['origin_time'] = event.get_origin_time()
    metadata['longitude'] = event.get_longitude()
    metadata['latitude'] = event.get_latitude()
    metadata['magnitude'] = event.get_magnitude()
    metadata['depth'] = event.get_depth()
    metadata['magnitude_type'] = "Mw"
    
    # Call the function to send the email
    send_email_with_attachment(subject, 
                               body, 
                               attachments, 
                               finder_solution, 
                               event_id,
                               metadata)
    print("Email sent successfully.")
