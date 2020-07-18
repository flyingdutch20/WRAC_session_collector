import yagmail
# https://yagmail.readthedocs.io/en/latest/api.html#authentication
receiver = "ted@bracht.uk"
body = "Hello there from Yagmail"
filename = "output/15 July.pdf"

yag = yagmail.SMTP("tedbracht@gmail.com", input("Password"))
yag.send(
    to=receiver,
    subject="Yagmail test with attachment",
    contents=body,
    attachments=filename,
)