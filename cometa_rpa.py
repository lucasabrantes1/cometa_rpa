from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium import webdriver
import time

DestinoRelatorio = r'H:\POWER_BI.sao\Bases_Shein\Latromi'
chrome_option = webdriver.ChromeOptions()
chrome_option.add_argument('--no-sandbox')
chrome_option.add_argument('--disable-dev-shm-usage')
chrome_option.add_experimental_option("prefs", {
    "download.default_directory": DestinoRelatorio,
    "download.prompt_for_download": False,  
    "download.directory_upgrade": True,
    "safebrowsing.enabled": False,
    "profile.default_content_setting_values.notifications": 2 
})
wd_chrome = webdriver.Chrome(options=chrome_option)

url = 'https://www.viacaocometa.com.br/'
wd_chrome.get(url)
wd_chrome.set_window_size(1392, 1104)
departure_input = WebDriverWait(wd_chrome, 10).until(
    EC.element_to_be_clickable((By.ID, "input-departure"))
)
departure_input.click()
time.sleep(1)
departure_input.send_keys("São Paulo (Rod. Tietê) (SP)")
time.sleep(2)
dropdown_option = WebDriverWait(wd_chrome, 10).until(
    EC.element_to_be_clickable((By.XPATH, "//li[contains(., 'São Paulo (Rod. Tietê) (SP)')]"))
)
dropdown_option.click()
destination_input = WebDriverWait(wd_chrome, 10).until(
    EC.element_to_be_clickable((By.ID, "input-destination"))
)
destination_input.click()
time.sleep(1)
destination_input.send_keys("Belo Horizonte (MG)")
time.sleep(2)
dropdown_option_dest = WebDriverWait(wd_chrome, 10).until(
    EC.element_to_be_clickable((By.XPATH, "//li[contains(., 'Belo Horizonte (MG)')]"))
)
dropdown_option_dest.click()
wd_chrome.find_element(By.ID, "input-date").click()
time.sleep(1)
wd_chrome.find_element(By.ID, "input-date").send_keys("21/10/2024")
wd_chrome.find_element(By.ID, "input-date").send_keys(Keys.ENTER)
wd_chrome.find_element(By.ID, "input-date-return").click()
time.sleep(1)
wd_chrome.find_element(By.ID, "input-date-return").send_keys("28/10/2024")
wd_chrome.find_element(By.ID, "input-date-return").send_keys(Keys.ENTER)
wd_chrome.find_element(By.ID, "search-button").click()
time.sleep(30)
