from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
import argparse
import os
import email, smtplib, ssl
from email import encoders
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

import fpdf
fpdf.set_global("SYSTEM_TTFONTS", os.path.join(os.path.dirname(__file__),'fonts'))

# --------------------------------------------------
def get_args():
    """Get command-line arguments"""

    parser = argparse.ArgumentParser(
        description='WRAC Session output generator',
        formatter_class=argparse.ArgumentDefaultsHelpFormatter)

    parser.add_argument('-u',
                        '--user',
                        metavar='user',
                        help='Enter either "juniors" or "sessions" depending on which output is required',
                        type=str,
                        choices=['sessions', 'juniors'],
                        default='sessions')

    parser.add_argument('-p',
                        '--password',
                        metavar='password',
                        help='Enter the password for ClassFit and email',
                        type=str,
                        default='')

    parser.add_argument('-t',
                        '--test',
                        help='Set to send test email',
                        action='store_true')

    return parser.parse_args()


def scrape_classfit():
    # login to ClassFit, collect the session details, output to pdf
    options = Options()
#    options.headless = True
    driver = webdriver.Chrome(executable_path="./drivers/chromedriver.exe", options=options)
#    driver = webdriver.Firefox(executable_path="./drivers/geckodriver.exe")

    print("Logging onto Classfit ...")
    driver.get("https://classfit.com/index.php/c/Login")

    username = driver.find_element_by_id("Email")
    username.clear()
    username.send_keys(args.user + "@wetherbyrunnersac.co.uk")
    password = driver.find_element_by_id("Pass")
    password.clear()
    password.send_keys(args.password)
    driver.find_element_by_id("LoginBtn").click()

    element = WebDriverWait(driver, 3).until(
        EC.presence_of_element_located((By.ID, "leftHeader"))
        )
    login_user = element.text
    #text = driver.find_element_by_id("leftHeader").text
    print(login_user)

    print("Retrieving classes ...")
    driver.get("https://classfit.com/index.php/c/MBMClasses")
    global date
    date = driver.find_element_by_class_name("hc_date").text
    print(date)

    soup_main = BeautifulSoup(driver.page_source, features="html.parser")

    sessions = {}

    links = soup_main.find('div',{'id': 'mgm-MyGm'}).find_all('a')
    for link in links:
        session_url = link.attrs['href']
        session_name = link.text
        sessions[session_url] = session_name
        print(session_url + ' - ' + session_name)

    print("Collecting individual classes and creating PDF ...")
#    pdf = FPDF()
    pdf = fpdf.FPDF()
    pdf.add_font("NotoSans", style="", fname="NotoSans-Regular.ttf", uni=True)
    pdf.add_font("NotoSans", style="B", fname="NotoSans-Bold.ttf", uni=True)
    pdf.add_font("NotoSans", style="I", fname="NotoSans-Italic.ttf", uni=True)
    pdf.add_font("NotoSans", style="BI", fname="NotoSans-BoldItalic.ttf", uni=True)
    for session in sessions.items():
        out = session[1] + ' - ' + session[0]
        driver.get("https://classfit.com" + session[0])
        soup_session = BeautifulSoup(driver.page_source, features="html.parser")
        try:
            session_details = soup_session.find('div', {'class': 'event-details'}).find_all('span')
            session_date = session_details[1].text.strip()
            split_date = session_date.split()
            strip_date = ' '.join(split_date[1:])
            if not strip_date == date:
                break
            session_time = session_details[2].text.strip()
            session_trainer = soup_session.find('div', {'class': 'event-creator-sub'}).find('h3').text
            session_description = soup_session.find('div', {'class': 'game-head'}).find('p').text
            session_members = soup_session.find('div', {'id': 'members'}).find_all('h3')
            session_waitlist = soup_session.find('div', {'id': 'waitinglist'}).find_all('h3')
            pdf.add_page()
            pdf.set_font('NotoSans', 'B', 16)
            pdf.cell(0, 10, session_date + ' - ' + session_time + ' - ' + session_trainer, 0, 1)
            pdf.cell(0, 10, session[1], 0, 1)
            pdf.set_font('NotoSans', '', 12)
            pdf.multi_cell(0, 7, session_description, 0, 1)
            pdf.cell(0, 7, '', 0, 1)
            pdf.set_font('NotoSans', 'B', 12)
            pdf.cell(0, 7, 'Bookings:', 0, 1)
            pdf.set_font('NotoSans', '', 12)
        except:
            None
        for member in session_members:
            try:
                name = member.find('a').text
            except AttributeError:
                name = 'No members have booked yet'
            pdf.cell(0, 7, name, 0, 1)
        pdf.cell(0, 7, '', 0, 1)
        pdf.set_font('NotoSans', 'B', 12)
        pdf.cell(0, 7, 'Waiting list:', 0, 1)
        pdf.set_font('NotoSans', '', 12)
        for member in session_waitlist:
            try:
                name = member.find('a').text
            except AttributeError:
                name = 'Waiting list is empty'
            pdf.cell(0, 7, name, 0, 1)

    if not os.path.isdir('./output'):
        os.mkdir('./output')
    global my_file
    my_file = date.replace(" ", "_") + ".pdf"
#    pdf.output(dest='S').encode('latin-1', 'ignore')
    pdf.output('./output/' + my_file, 'F')

    driver.quit()

def set_receivers():
    # set the receivers for the email; if juniors, reduce the list
    senior_receivers = ["andreanormington29@gmail.com",
                        "emmacoster@hotmail.co.uk",
                        "ianmlegg@gmail.com",
                        "pauljwindle@yahoo.co.uk",
                        "daveyrichard@doctors.org.uk",
                        "david_yeomans@tiscali.co.uk",
                        "callumdraper@yahoo.co.uk",
                        "pmlandd@gmail.com",
                        "garyothick@gmail.com",
                        "mail@chrisplews.co.uk",
#                        "fiona.knapton@live.co.uk",
                        "richard.bell@communisis.com",
                        "fiveeurochamps@gmail.com"]
    junior_receivers = ["andreanormington29@gmail.com",
                        "emmacoster@hotmail.co.uk",
                        "ianmlegg@gmail.com",
                        "pauljwindle@yahoo.co.uk",
                        "daveyrichard@doctors.org.uk",
                        "callumdraper@yahoo.co.uk"]
    wellbeing_receivers = ["andreanormington29@gmail.com",
                        "originaljamman@gmail.com",
                        "ianmlegg@gmail.com"]
    return junior_receivers if args.user == 'juniors' else senior_receivers

def create_and_send_mail():
    # create email and send it to the coaches
    print("Creating email ...")
    subject = "Session bookings for {}".format(date)
    body = "Please find attached the session details for {}".format(date)
    # TODO put the email addresses in a params file and parse that
    sender_email = "ted@wetherbyrunnersac.co.uk"
    to_email = set_receivers()
    cc_email = ["ted@wetherbyrunnersac.co.uk", "ted@bracht.uk"]
    email_password = args.password

    # Create a multipart message and set headers
    message = MIMEMultipart()
    message["From"] = sender_email
    message["To"] = ", ".join(to_email)
    message["Cc"] = ", ".join(cc_email)
    message["Subject"] = subject

    # Add body to email
    message.attach(MIMEText(body, "plain"))

    # Open PDF file in binary mode
    with open("./output/" + my_file, "rb") as attachment:
        # Add file as application/octet-stream
        # Email client can usually download this automatically as attachment
        part = MIMEBase("application", "octet-stream")
        part.set_payload(attachment.read())

    # Encode file in ASCII characters to send by email
    encoders.encode_base64(part)

    # Add header as key/value pair to attachment part
    part.add_header(
        "Content-Disposition",
        f"attachment; filename= {my_file}",
    )

    # Add attachment to message and convert message to string
    message.attach(part)
    text = message.as_string()

    print("Sending email ...")
    # Log in to server using secure context and send email
    test_receivers = ["ted@bracht.uk", "tedbracht@gmail.com", "ted@wetherbyrunnersac.co.uk"]
    receivers = test_receivers if args.test else to_email + cc_email
    context = ssl.create_default_context()
    with smtplib.SMTP_SSL("mail.wetherbyrunnersac.co.uk", 465, context=context) as server:
        server.login(sender_email, email_password)
        server.sendmail(sender_email, receivers, text)


def main():
    global args
    args = get_args()
    scrape_classfit()
    create_and_send_mail()
    print("All done, thank you and tot ziens!")


if __name__ == '__main__':
    main()
