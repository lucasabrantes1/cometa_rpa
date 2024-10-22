from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from selenium import webdriver
import time
from datetime import datetime, timedelta
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium import webdriver
import time
from datetime import datetime, timedelta

# Configurações do WebDriver
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

# Abrindo o site
url = 'https://www.viacaocometa.com.br/'
wd_chrome.get(url)
wd_chrome.set_window_size(1392, 1104)

# Interações para preencher o formulário
time.sleep(4)
departure_input = wd_chrome.find_element(By.ID, "input-departure")
departure_input.click()
time.sleep(4)
departure_input.send_keys("São Paulo (Rod. Tietê) (SP)")
time.sleep(5)

dropdown_option = wd_chrome.find_element(By.XPATH, "//li[contains(., 'São Paulo (Rod. Tietê) (SP)')]")
dropdown_option.click()
time.sleep(4)

destination_input = wd_chrome.find_element(By.ID, "input-destination")
destination_input.click()
time.sleep(4)
destination_input.send_keys("Belo Horizonte (MG)")
time.sleep(4)

dropdown_option_dest = wd_chrome.find_element(By.XPATH, "//li[contains(., 'Belo Horizonte (MG)')]")
dropdown_option_dest.click()
time.sleep(4)

# Calcular as datas de hoje e os próximos 6 dias
data_inicial = datetime.today()
datas = [data_inicial + timedelta(days=i) for i in range(7)]

# Inserir a primeira data no campo de partida
wd_chrome.find_element(By.ID, "input-date").click()
time.sleep(1)
wd_chrome.find_element(By.ID, "input-date").send_keys(datas[0].strftime("%d/%m/%Y"))  # Ex: 21/10/2024
wd_chrome.find_element(By.ID, "input-date").send_keys(Keys.ENTER)
time.sleep(2)

# Inserir a última data no campo de retorno (após 6 dias)
wd_chrome.find_element(By.ID, "input-date-return").click()
time.sleep(1)
wd_chrome.find_element(By.ID, "input-date-return").send_keys(datas[-1].strftime("%d/%m/%Y"))  # Ex: 28/10/2024
wd_chrome.find_element(By.ID, "input-date-return").send_keys(Keys.ENTER)
time.sleep(2)

# Clicar no botão de busca
wd_chrome.find_element(By.ID, "search-button").click()
time.sleep(10)

# Calcular as datas de hoje e os próximos 6 dias
data_inicial = datetime.today()
datas = [data_inicial + timedelta(days=i) for i in range(7)]

# Agora iterar pelas datas para capturar os preços de cada dia
for data in datas:
    # Esperar até o elemento do dia estar presente e visível na página
    dia_element = WebDriverWait(wd_chrome, 10).until(
        EC.presence_of_element_located((By.XPATH, f"//div[@data-js='date' and contains(text(), '{data.strftime('%d/%m')}')]"))
    )
    
    # Clicar no dia
    dia_element.click()
    
    # Esperar até que as ofertas de assento e preço estejam presentes
    WebDriverWait(wd_chrome, 10).until(
        EC.presence_of_all_elements_located((By.XPATH, "//li[contains(@data-js, 'offer-element')]"))
    )

    # Pegar as ofertas de assento e preço
    ofertas = wd_chrome.find_elements(By.XPATH, "//li[contains(@data-js, 'offer-element')]")
    
    print(f"\n---{data.strftime('%d/%m/%Y')}")
    
    for oferta in ofertas:
        tipo_assento = oferta.find_element(By.XPATH, ".//span[contains(@class, 'classtypeLabel')]").text.strip()
        preco_inteiro = oferta.find_element(By.XPATH, ".//span[@data-js='priceLabel']").text.strip()
        preco_decimal = oferta.find_element(By.XPATH, ".//span[@data-js='decimalLabel']").text.strip()
        preco_completo = f"R${preco_inteiro}{preco_decimal}"
        
        # Imprimindo as informações para o dia atual
        print(f"Tipo de assento: {tipo_assento}")
        print(f"Preço: {preco_completo}\n")

# Fechar o navegador (opcional)
# wd_chrome.quit()