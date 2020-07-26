from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import time
options = Options()
options.headless = True
# options.add_argument("--headless")
driver = webdriver.Chrome(executable_path="C:/Program Files (x86)/Google/ChromeDriver/chromedriver.exe", options=options)
# driver = webdriver.Chrome(options=options)

driver.get("https://classfit.com/index.php/c/Login")

username = driver.find_element_by_id("Email")
username.clear()
username.send_keys("juniors@wetherbyrunnersac.co.uk")
password = driver.find_element_by_id("Pass")
password.clear()
password.send_keys("MySecretPassword")
submit = driver.find_element_by_id("LoginBtn").click()

time.sleep(5)

text = driver.find_element_by_id("leftHeader").text
print(text)

driver.get("https://classfit.com/index.php/c/MBMClasses")
text = driver.find_element_by_class_name("hc_date").text
print(text)


driver.quit()
