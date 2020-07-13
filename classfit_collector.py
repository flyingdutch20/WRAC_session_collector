from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
from fpdf import FPDF
# https://pyfpdf.readthedocs.io/en/latest/Tutorial/index.html
import argparse
import os


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
                        help='Enter the password for ClassFit',
                        type=str,
                        default='')

    return parser.parse_args()

def main():
    args = get_args()

    options = Options()
    options.headless = True
    driver = webdriver.Chrome(executable_path="./drivers/chromedriver.exe", options=options)

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

    driver.get("https://classfit.com/index.php/c/MBMClasses")
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

    pdf = FPDF()
    for session in sessions.items():
        out = session[1] + ' - ' + session[0]
        driver.get("https://classfit.com" + session[0])
        soup_session = BeautifulSoup(driver.page_source, features="html.parser")
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
        pdf.set_font('Arial', 'B', 16)
        pdf.cell(0, 10, session_date + ' - ' + session_time + ' - ' + session_trainer, 0, 1)
        pdf.cell(0, 10, session[1], 0, 1)
        pdf.set_font('Arial', '', 12)
        pdf.multi_cell(0, 7, session_description, 0, 1)
        pdf.cell(0, 7, '', 0, 1)
        pdf.set_font('Arial', 'B', 12)
        pdf.cell(0, 7, 'Bookings:', 0, 1)
        pdf.set_font('Arial', '', 12)
        for member in session_members:
            try:
                name = member.find('a').text
            except AttributeError:
                name = 'No members have booked yet'
            pdf.cell(0, 7, name, 0, 1)
        pdf.cell(0, 7, '', 0, 1)
        pdf.set_font('Arial', 'B', 12)
        pdf.cell(0, 7, 'Waiting list:', 0, 1)
        pdf.set_font('Arial', '', 12)
        for member in session_waitlist:
            try:
                name = member.find('a').text
            except AttributeError:
                name = 'Waiting list is empty'
            pdf.cell(0, 7, name, 0, 1)

    if not os.path.isdir('./output'):
        os.mkdir('./output')
    pdf.output('./output/' + date + '.pdf', 'F')

    driver.quit()


if __name__ == '__main__':
    main()
