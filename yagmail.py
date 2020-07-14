import yagmail
# https://yagmail.readthedocs.io/en/latest/api.html#authentication
receiver = "your@gmail.com"
body = "Hello there from Yagmail"
filename = "document.pdf"

yag = yagmail.SMTP("my@gmail.com")
yag.send(
    to=receiver,
    subject="Yagmail test with attachment",
    contents=body,
    attachments=filename,
)