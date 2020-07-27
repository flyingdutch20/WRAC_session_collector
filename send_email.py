import email, smtplib, ssl

from email import encoders
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

subject = "Session bookings"
body = "Please find attached the session details"
sender_email = "ted@wetherbyrunnersac.co.uk"
receivers = [andreanormington29@gmail.com,
    emmacoster@hotmail.co.uk,
    ianmlegg@gmail.com,
    pauljwindle@yahoo.co.uk,
    daveyrichard@doctors.org.uk,
    david_yeomans@tiscali.co.uk,
    callumdraper@yahoo.co.uk,
    pmlandd@gmail.com,
    garyothick@gmail.com]
#cc_email = "ted@bracht.uk"
cc_email = ["ted@wetherbyrunnersac.co.uk", "ted@bracht.uk"]
email_password = input("Type your password and press enter: ")

# Create a multipart message and set headers
message = MIMEMultipart()
message["From"] = sender_email
message["To"] = ", ".join(receivers)
message["To"] = "tedbracht@gmail.com"
message["Cc"] = ", ".join(cc_email)
message["Subject"] = subject

# Add body to email
message.attach(MIMEText(body, "plain"))

filename = "./output/15 July.pdf"  # In same directory as script

# Open PDF file in binary mode
with open(filename, "rb") as attachment:
    # Add file as application/octet-stream
    # Email client can usually download this automatically as attachment
    part = MIMEBase("application", "octet-stream")
    part.set_payload(attachment.read())

# Encode file in ASCII characters to send by email
encoders.encode_base64(part)

# Add header as key/value pair to attachment part
part.add_header(
    "Content-Disposition",
    f"attachment; filename= {filename}",
)

# Add attachment to message and convert message to string
message.attach(part)
text = message.as_string()

# Log in to server using secure context and send email
context = ssl.create_default_context()
with smtplib.SMTP_SSL("mail.wetherbyrunnersac.co.uk", 465, context=context) as server:
    server.login(sender_email, email_password)
    server.sendmail(sender_email, receivers + cc_email, text)