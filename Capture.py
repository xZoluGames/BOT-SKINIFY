import undetected_chromedriver as uc
import json
import os
import time
import winsound
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from threading import Thread

base_path = os.path.dirname(os.path.abspath(__file__))

def cargar_configuracion():
    config_file = os.path.join(base_path, 'Config.txt')
    configuracion = {}
    try:
        with open(config_file, 'r', encoding='utf-8') as file:
            for line in file:
                if line.strip() and not line.startswith('#'):
                    key, value = line.split('=')
                    configuracion[key.strip()] = value.strip()
    except FileNotFoundError:
        print("File 'Config.txt' not found.")
    return configuracion

# Configuración de undetected_chromedriver
def iniciar_navegador_con_perfil():
    options = uc.ChromeOptions()
    user_data_dir = os.path.join(base_path, 'UserData')
    options.add_argument(f"user-data-dir={user_data_dir}")
    options.add_argument(r'--profile-directory=Default')
    driver_path = os.path.join(base_path, 'Chromedriver', 'chromedriver.exe')
    driver = uc.Chrome(options=options, executable_path=driver_path)
    return driver

# Función para emitir un pitido al encontrar el objeto
def emitir_sonido():
    frequency = 1000
    duration = 500
    winsound.Beep(frequency, duration)

# Función para obtener datos de la página de Skinify
def obtener_datos_inventario(driver):
    try:
        pre_element = WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.TAG_NAME, "pre")))
        json_data = pre_element.text
        data = json.loads(json_data)
        return data.get("inventory", [])
    except json.JSONDecodeError:
        print("Error decoding JSON.")
        return []
    except Exception as e:
        print(f"An error occurred: {e}")
        return []

# Función para manejar la pestaña de Skinify
def actualizar_skinify(driver, item_name):
    while True:
        driver.switch_to.window(driver.window_handles[0])  # Asegurarse de estar en la pestaña de Skinify
        driver.get("https://skinify.io/account/inventory?gameid=1")
        print(f"Loading the inventory page and searching for the item: {item_name}...")
        inventory = obtener_datos_inventario(driver)
        
        for item in inventory:
            if item.get("name") == item_name:
                price = item.get("price", "0.00")
                print(f"{item['name']}\n$ {price}")
                emitir_sonido()
                break
        else:
            print("Item not found, reloading in 15 seconds.")
        
        time.sleep(15)

# Función para gestionar la pestaña de Rustyloot
def gestionar_pestana_rustyloot(driver):
    while True:
        driver.switch_to.window(driver.window_handles[1])  # Cambiar a la pestaña de Rustyloot
        driver.get("https://rustyloot.gg/?deposit=true")
        time.sleep(5)  # Esperar a que la página cargue

        try:
            element = WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.XPATH, "//div[@id='root']/div/div[2]/div[3]/div/div/div/div[2]/div[2]/div/div/div[3]/img")))
            element.click()
            print("Elemento clickeado, esperando 20 segundos antes de cerrar la ventana emergente...")

            # Esperar a que se genere la nueva pestaña
            time.sleep(20)

            # Cerrar todas las ventanas emergentes
            for handle in driver.window_handles[2:]:
                driver.switch_to.window(handle)
                driver.close()

            # Volver a la pestaña de Rustyloot
            driver.switch_to.window(driver.window_handles[1])
        except Exception as e:
            print(f"Error al intentar hacer clic o cerrar la pestaña: {e}")

        # Esperar 60 segundos antes de repetir el clic en Rustyloot
        time.sleep(60)

if __name__ == "__main__":
    configuracion = cargar_configuracion()
    item_name = configuracion.get('name', 'Sticker | fitch | Katowice 2019')

    driver = iniciar_navegador_con_perfil()

    # Abrir la pestaña de Skinify inicialmente
    driver.get("https://skinify.io/account/inventory?gameid=1")

    # Abrir una nueva pestaña para Rustyloot
    driver.execute_script("window.open('https://rustyloot.gg/?deposit=true', '_blank');")

    # Iniciar la gestión de la pestaña de Rustyloot en un hilo separado
    thread_rustyloot = Thread(target=gestionar_pestana_rustyloot, args=(driver,))
    thread_rustyloot.start()

    # Operación normal en la pestaña principal de Skinify
    actualizar_skinify(driver, item_name)