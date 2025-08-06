# metodos.py
import requests
import os
from Clases.lista import Lista
from Clases.device import Device
from Clases.user_config import UserConfig
import serial
import time

from dotenv import load_dotenv

load_dotenv()

def obtener_uuid():
    return os.getenv("UUID")

def obtener_dispositivos(uuid: str):
    url = 'http://localhost:3333/getdevices'
    payload = {'uuid': uuid}

    try:
        response = requests.post(url, json=payload)

        if response.status_code == 200:
            return response.json()
        else:
            print(f"❌ Error {response.status_code}: {response.text}")
            return None

    except requests.exceptions.RequestException as e:
        print(f"❌ Error en la conexión: {e}")
        return None

def guardar_dispositivos_json(dispositivos: list, archivo: str = 'Jsons_DATA/devices.json'):
    lista_dispositivos = Lista(Device)
    lista_dispositivos.agregar_elementos(dispositivos)
    
    os.makedirs(os.path.dirname(archivo), exist_ok=True)
    lista_dispositivos.guardar(archivo)
    print(f"✅ Dispositivos guardados exitosamente en {archivo}")

def obtener_configuraciones(uuid: str):
    url = 'https://761ad39b8f57.ngrok-free.app/getconfig'
    payload = {'uuid': uuid}

    try:
        response = requests.post(url, json=payload)

        if response.status_code == 200:
            return response.json()
        else:
            print(f"❌ Error {response.status_code}: {response.text}")
            return None

    except requests.exceptions.RequestException as e:
        print(f"❌ Error en la conexión: {e}")
        return None

# Corregido: función renombrada y sin coma al final
def guardar_configuraciones_json(configuraciones: list, archivo: str = 'Jsons_DATA/user_configs.json'):
    lista_configuraciones = Lista(UserConfig)
    lista_configuraciones.agregar_elementos(configuraciones)
    
    os.makedirs(os.path.dirname(archivo), exist_ok=True)
    lista_configuraciones.guardar(archivo)
    print(f"✅ Configuraciones guardadas exitosamente en {archivo}")