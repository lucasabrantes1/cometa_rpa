import os
import csv
import time
from datetime import datetime, timedelta
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from selenium import webdriver

# Obter o diretório onde o script está localizado
script_dir = os.path.dirname(os.path.abspath(__file__))

# Definir o diretório de download como 'raw_data' no mesmo diretório do script
DestinoRelatorio = os.path.join(script_dir, 'raw_data')

# Criar o diretório se não existir
if not os.path.exists(DestinoRelatorio):
    os.makedirs(DestinoRelatorio)

# Configurações do WebDriver
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

# Função para esperar o loader desaparecer após clicar e esperar 5 segundos
def wait_for_loader_after_click(driver):
    time.sleep(5)  # Esperar 5 segundos após clicar
    try:
        # Verificar se o loader aparece
        loader_present = len(driver.find_elements(By.CSS_SELECTOR, "#loader img")) > 0
        if loader_present:
            # Esperar até que o loader desapareça
            WebDriverWait(driver, 10).until_not(
                EC.presence_of_element_located((By.CSS_SELECTOR, "#loader img"))
            )
    except Exception as e:
        print(f"Erro ao esperar o loader desaparecer: {str(e)}")
    time.sleep(1)  # Esperar 1 segundo adicional

# Lista de rotas
routes = [
    {"origin": "São Paulo (Rod. Tietê) (SP)", "destination": "Belo Horizonte (MG)"},
    {"origin": "Belo Horizonte (MG)", "destination": "São Paulo (Rod. Tietê) (SP)"},
    {"origin": "São Paulo (Rod. Tietê) (SP)", "destination": "Ribeirão Preto (SP)"},
    {"origin": "Ribeirão Preto (SP)", "destination": "São Paulo (Rod. Tietê) (SP)"},
    {"origin": "São Paulo (Rod. Tietê) (SP)", "destination": "Curitiba (PR)"},
    {"origin": "Rio de Janeiro (Novo Rio) (RJ)", "destination": "Belo Horizonte (MG)"},
    {"origin": "São Paulo (Rod. Barra Funda) (SP)", "destination": "São José do Rio Preto (Rodoviária) (SP)"},
    {"origin": "Curitiba - Rodoviária (PR)", "destination": "São Paulo (Rod. Tietê) (SP)"},
    {"origin": "São José do Rio Preto (Rodoviária) (SP)", "destination": "São Paulo (Rod. Barra Funda) (SP)"},
    {"origin": "Rio de Janeiro (Novo Rio) (RJ)", "destination": "Campinas (SP)"}
]

# Calcular as datas de hoje e os próximos 6 dias
data_inicial = datetime.today()
datas = [data_inicial + timedelta(days=i) for i in range(7)]

# Abrindo o site fora do loop para evitar reabrir várias vezes
url = 'https://www.viacaocometa.com.br/'
wd_chrome.get(url)
wd_chrome.set_window_size(1392, 1104)

# Arquivo CSV único para salvar os dados
csv_filename = os.path.join(DestinoRelatorio, "dados_viacao_cometa.csv")
with open(csv_filename, mode='w', newline='', encoding='utf-8') as csv_file:
    fieldnames = ['Origem', 'Destino', 'Data', 'Tipo de assento', 'Preço', 'Mensagem', 'Timestamp_Scraped']
    writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
    writer.writeheader()

    for route in routes:
        try:
            # Reiniciar a página para cada rota
            wd_chrome.get(url)
            time.sleep(5)
            # Não precisa chamar wait_for_loader aqui, pois acabamos de carregar a página

            # Interações para preencher o formulário
            departure_input = WebDriverWait(wd_chrome, 10).until(
                EC.element_to_be_clickable((By.ID, "input-departure"))
            )
            departure_input.click()
            # Após clicar, esperar 5 segundos e verificar o loader
            wait_for_loader_after_click(wd_chrome)

            departure_input.clear()
            departure_input.send_keys(route['origin'])
            time.sleep(1)  # Esperar o dropdown aparecer

            # Selecionar a opção de origem
            dropdown_option = WebDriverWait(wd_chrome, 10).until(
                EC.element_to_be_clickable((By.XPATH, f"//li[contains(., '{route['origin']}')]"))
            )
            dropdown_option.click()

            # Após clicar, esperar 5 segundos e verificar o loader
            wait_for_loader_after_click(wd_chrome)

            # Preencher o destino
            destination_input = wd_chrome.find_element(By.ID, "input-destination")
            destination_input.click()

            # Após clicar, esperar 5 segundos e verificar o loader
            wait_for_loader_after_click(wd_chrome)

            destination_input.clear()
            destination_input.send_keys(route['destination'])
            time.sleep(1)  # Esperar o dropdown aparecer

            # Selecionar a opção de destino
            dropdown_option_dest = WebDriverWait(wd_chrome, 10).until(
                EC.element_to_be_clickable((By.XPATH, f"//li[contains(., '{route['destination']}')]"))
            )
            dropdown_option_dest.click()

            # Após clicar, esperar 5 segundos e verificar o loader
            wait_for_loader_after_click(wd_chrome)

            # Inserir a primeira data no campo de partida
            date_input = wd_chrome.find_element(By.ID, "input-date")
            date_input.click()

            # Após clicar, esperar 5 segundos e verificar o loader
            wait_for_loader_after_click(wd_chrome)

            date_input.clear()
            date_input.send_keys(datas[0].strftime("%d/%m/%Y"))
            date_input.send_keys(Keys.ENTER)
            time.sleep(1)

            # Inserir a última data no campo de retorno
            date_return_input = wd_chrome.find_element(By.ID, "input-date-return")
            date_return_input.click()

            # Após clicar, esperar 5 segundos e verificar o loader
            wait_for_loader_after_click(wd_chrome)

            date_return_input.clear()
            date_return_input.send_keys(datas[-1].strftime("%d/%m/%Y"))
            date_return_input.send_keys(Keys.ENTER)
            time.sleep(1)

            # Clicar no botão de busca
            search_button = wd_chrome.find_element(By.ID, "search-button")
            search_button.click()

            # Após clicar, esperar o loader e verificar se a mensagem aparece
            wait_for_loader_after_click(wd_chrome)

            # Verificar se a mensagem de "Não existe serviço..." aparece após a busca
            try:
                message_element = wd_chrome.find_element(By.CSS_SELECTOR, "span.message-val[data-js='message-validation']")
                message_text = message_element.text.strip()
                if "Não existe serviço para o trecho e/ou data selecionados." in message_text:
                    timestamp_scraped = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    writer.writerow({
                        'Origem': route['origin'],
                        'Destino': route['destination'],
                        'Data': 'Todas as datas',
                        'Tipo de assento': '',
                        'Preço': '',
                        'Mensagem': message_text,
                        'Timestamp_Scraped': timestamp_scraped
                    })
                    print(f"Mensagem para rota {route['origin']} -> {route['destination']}: {message_text}")
                    continue  # Ir para a próxima rota
            except:
                pass  # Se a mensagem não existir, continuar normalmente

            # Agora iterar pelas datas para capturar os preços de cada dia
            for data in datas:
                # Formatar a data
                date_str = data.strftime('%d/%m')
                try:
                    dia_element = WebDriverWait(wd_chrome, 10).until(
                        EC.element_to_be_clickable((By.XPATH, f"//div[@data-js='date' and contains(text(), '{date_str}')]"))
                    )
                    dia_element.click()

                    # Após clicar, esperar 5 segundos e verificar o loader
                    wait_for_loader_after_click(wd_chrome)

                    # Verificar se a mensagem aparece após selecionar a data
                    try:
                        message_element = wd_chrome.find_element(By.CSS_SELECTOR, "span.message-val[data-js='message-validation']")
                        message_text = message_element.text.strip()
                        if "Não existe serviço para o trecho e/ou data selecionados." in message_text:
                            timestamp_scraped = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                            writer.writerow({
                                'Origem': route['origin'],
                                'Destino': route['destination'],
                                'Data': data.strftime('%d/%m/%Y'),
                                'Tipo de assento': '',
                                'Preço': '',
                                'Mensagem': message_text,
                                'Timestamp_Scraped': timestamp_scraped
                            })
                            print(f"Mensagem na data {data.strftime('%d/%m/%Y')} para rota {route['origin']} -> {route['destination']}: {message_text}")
                            continue  # Ir para a próxima data
                    except:
                        pass  # Se a mensagem não existir, continuar normalmente

                    # Esperar até que as ofertas estejam presentes
                    WebDriverWait(wd_chrome, 10).until(
                        EC.presence_of_all_elements_located((By.XPATH, "//li[contains(@data-js, 'offer-element')]"))
                    )
                
                    # Pegar as ofertas de assento e preço
                    ofertas = wd_chrome.find_elements(By.XPATH, "//li[contains(@data-js, 'offer-element')]")
                    
                    # Coletar e escrever as informações no arquivo CSV
                    for oferta in ofertas:
                        try:
                            tipo_assento = oferta.find_element(By.XPATH, ".//span[contains(@class, 'classtypeLabel')]").text.strip()
                            preco_inteiro = oferta.find_element(By.XPATH, ".//span[@data-js='priceLabel']").text.strip()
                            preco_decimal = oferta.find_element(By.XPATH, ".//span[@data-js='decimalLabel']").text.strip()
                            preco_completo = f"R${preco_inteiro}{preco_decimal}"
                            
                            timestamp_scraped = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                            
                            # Escrever as informações no arquivo CSV
                            writer.writerow({
                                'Origem': route['origin'],
                                'Destino': route['destination'],
                                'Data': data.strftime('%d/%m/%Y'),
                                'Tipo de assento': tipo_assento,
                                'Preço': preco_completo,
                                'Mensagem': '',
                                'Timestamp_Scraped': timestamp_scraped
                            })
                        except Exception as e:
                            print(f"Erro ao processar oferta na data {data.strftime('%d/%m/%Y')} para rota {route['origin']} -> {route['destination']}: {str(e)}")
                except Exception as e:
                    print(f"Erro ao selecionar data {date_str} para rota {route['origin']} -> {route['destination']}: {str(e)}")
                    continue
            # Esperar antes de processar a próxima rota
            time.sleep(2)
        except Exception as e:
            print(f"Erro ao processar rota {route['origin']} -> {route['destination']}: {str(e)}")
            continue

# Fechar o navegador
wd_chrome.quit()
