import os
import csv
import time
from datetime import datetime, timedelta
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from selenium import webdriver
from selenium.common.exceptions import TimeoutException

script_dir = os.path.dirname(os.path.abspath(__file__))
DestinoRelatorio = os.path.join(script_dir, 'raw_data')

if not os.path.exists(DestinoRelatorio):
    os.makedirs(DestinoRelatorio)

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

def wait_for_loader_after_click(driver):
    time.sleep(2)
    try:
        loader_present = len(driver.find_elements(By.CSS_SELECTOR, "#loader img")) > 0
        if loader_present:
            WebDriverWait(driver, 40).until_not(
                EC.presence_of_element_located((By.CSS_SELECTOR, "#loader img"))
            )
    except Exception as e:
        print(f"Erro ao esperar o loader desaparecer: {str(e)}")
    time.sleep(1)

routes = [
    {"origin": "Belo Horizonte - Terminal Rodoviário (MG)", "destination": "São Paulo (Rod. Tietê) (SP)"},
    {"origin": "Ribeirão Preto (SP)", "destination": "São Paulo (Rod. Tietê) (SP)"},
    {"origin": "Rio de Janeiro (Novo Rio) (RJ)", "destination": "Belo Horizonte - Terminal Rodoviário (MG)"},
]

timestamp = datetime.now().strftime("%d_%m_%Y_%H_%M")
data_inicial = datetime.today()
hoje = data_inicial.date()
datas = [data_inicial + timedelta(days=i) for i in range(3)]

url = 'https://www.viacaocometa.com.br/'
wd_chrome.get(url)
wd_chrome.set_window_size(1392, 1104)

csv_filename = os.path.join(DestinoRelatorio, f"dados_viacao_cometa_{timestamp}.csv")
with open(csv_filename, mode='w', newline='', encoding='utf-8') as csv_file:
    fieldnames = ['Origem', 'Destino', 'Data', 'Tipo de assento', 'Preco', 'Mensagem_rota_indisp', 'Timestamp_Scraped']
    writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
    writer.writeheader()

    for route in routes:
        try:
            wd_chrome.get(url)
            time.sleep(5)

            # selecionar origem
            departure_input = WebDriverWait(wd_chrome, 10).until(
                EC.element_to_be_clickable((By.ID, "input-departure"))
            )
            departure_input.click()
            wait_for_loader_after_click(wd_chrome)
            departure_input.clear()
            time.sleep(1)
            departure_input.send_keys(route['origin'])
            dropdown_option = WebDriverWait(wd_chrome, 10).until(
                EC.element_to_be_clickable((By.XPATH, f"//li[contains(., '{route['origin']}')]"))
            )
            dropdown_option.click()
            wait_for_loader_after_click(wd_chrome)

            # selecionar destino
            destination_input = wd_chrome.find_element(By.ID, "input-destination")
            destination_input.click()
            wait_for_loader_after_click(wd_chrome)
            destination_input.clear()
            destination_input.send_keys(route['destination'])
            dropdown_option_dest = WebDriverWait(wd_chrome, 10).until(
                EC.element_to_be_clickable((By.XPATH, f"//li[contains(., '{route['destination']}')]"))
            )
            dropdown_option_dest.click()
            wait_for_loader_after_click(wd_chrome)

            # data de ida
            date_input = wd_chrome.find_element(By.ID, "input-date")
            date_input.click()
            wait_for_loader_after_click(wd_chrome)
            date_input.clear()
            date_input.send_keys(datas[0].strftime("%d/%m/%Y"))
            date_input.send_keys(Keys.ENTER)
            time.sleep(1)

            # data de volta
            date_return_input = wd_chrome.find_element(By.ID, "input-date-return")
            date_return_input.click()
            wait_for_loader_after_click(wd_chrome)
            date_return_input.clear()
            date_return_input.send_keys(datas[-1].strftime("%d/%m/%Y"))
            date_return_input.send_keys(Keys.ENTER)
            time.sleep(1)

            # buscar
            search_button = wd_chrome.find_element(By.ID, "search-button")
            search_button.click()
            wait_for_loader_after_click(wd_chrome)

            #TODO: Este caso aqui costuma aparecer quando o script roda varias vezes seguidas, caso for rodar em um curto periodo de tempo é necessario implementar a logica do proxy como acredito que esse não seja o objetivo optei pro não implementar, o proxy comentado no webdriver config é grátis e de baixa qualidade podendo afetar o desempenho ou até mesmo nem funcionar.
            try:
                message_element = wd_chrome.find_element(
                    By.CSS_SELECTOR, "span.message-val[data-js='message-validation']"
                )
                message_text = message_element.text.strip()
                if "Não existe serviço para o trecho e/ou data selecionados." in message_text:
                    writer.writerow({
                        'Origem': route['origin'],
                        'Destino': route['destination'],
                        'Data': '',
                        'Tipo de assento': '',
                        'Preco': '',
                        'Mensagem_rota_indisp': message_text,
                        'Timestamp_Scraped': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    })
                    print(f"Rota indisponível {route['origin']} -> {route['destination']}")
                    continue
            except:
                pass

            # loop pelas próximas datas
            for data in datas[1:]:
                date_str = f"{data.day}/{data.month}"
                if data.date() == hoje:
                    print(f"[SKIP] {date_str} já é hoje, não clico.")
                    continue

                xpath = (
                    f"//div[@data-js='date' "
                    f"and contains(text(), '{date_str}') "
                    f"and not(contains(@class,'selected'))]"
                )
                try:
                    dia_element = WebDriverWait(wd_chrome, 10).until(
                        EC.element_to_be_clickable((By.XPATH, xpath))
                    )
                except TimeoutException:
                    print(f"[WARN] Não achei elemento não-selecionado para {date_str}. Pulando.")
                    continue

                time.sleep(1)
                dia_element.click()
                wait_for_loader_after_click(wd_chrome)

                # rota indisponível nesta data?
                try:
                    message_element = wd_chrome.find_element(
                        By.CSS_SELECTOR, "span.message-val[data-js='message-validation']"
                    )
                    message_text = message_element.text.strip()
                    if "Não existe serviço para o trecho e/ou data selecionados." in message_text:
                        writer.writerow({
                            'Origem': route['origin'],
                            'Destino': route['destination'],
                            'Data': data.strftime('%d/%m/%Y'),
                            'Tipo de assento': '',
                            'Preco': '',
                            'Mensagem_rota_indisp': message_text,
                            'Timestamp_Scraped': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                        })
                        print(f"Rota indisponível em {date_str} para {route['origin']} -> {route['destination']}")
                        continue
                except:
                    pass

                # coleta ofertas
                WebDriverWait(wd_chrome, 10).until(
                    EC.presence_of_all_elements_located((By.XPATH, "//li[contains(@data-js, 'offer-element')]"))
                )
                ofertas = wd_chrome.find_elements(By.XPATH, "//li[contains(@data-js, 'offer-element')]")
                for oferta in ofertas:
                    try:
                        tipo_assento = oferta.find_element(
                            By.XPATH, ".//span[contains(@class, 'classtypeLabel')]"
                        ).text.strip()
                        preco_inteiro = oferta.find_element(
                            By.XPATH, ".//span[@data-js='priceLabel']"
                        ).text.strip()
                        preco_decimal = oferta.find_element(
                            By.XPATH, ".//span[@data-js='decimalLabel']"
                        ).text.strip()
                        preco_completo = f"R${preco_inteiro}{preco_decimal}"
                        writer.writerow({
                            'Origem': route['origin'],
                            'Destino': route['destination'],
                            'Data': data.strftime('%d/%m/%Y'),
                            'Tipo de assento': tipo_assento,
                            'Preco': preco_completo,
                            'Mensagem_rota_indisp': '',
                            'Timestamp_Scraped': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                        })
                    except Exception as e:
                        print(f"Erro oferta {date_str}: {e}")

            time.sleep(2)

        except Exception as e:
            print(f"Erro na rota {route['origin']} -> {route['destination']}: {e}")
            continue

wd_chrome.quit()
