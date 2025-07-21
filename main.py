from Clases.metodos import obtener_uuid, obtener_dispositivos, guardar_dispositivos_json
from Clases.arduino import leer_serial_una_vez
import threading
import time

def obtener_dispositivos_diariamente():
    while True:
        uuid = obtener_uuid()
        if not uuid:
            print("⚠️ No se encontró UUID en el archivo .env")
            time.sleep(86400)
            continue

        print(f"🔑 UUID obtenido: {uuid}")

        dispositivos = obtener_dispositivos(uuid)

        if dispositivos:
            guardar_dispositivos_json(dispositivos)
        else:
            print("⚠️ No se obtuvieron dispositivos de la API. No se puede continuar.")

        # Espera 24 horas
        time.sleep(86400)

def leer_sensores_periodicamente(puerto):
    while True:
        print("🔄 Iniciando lectura de sensores...")
        leer_serial_una_vez(puerto=puerto)
        print(f"⏰ Esperando 5 minutos antes de la próxima lectura...")
        # Espera 5 minutos (300 segundos)
        time.sleep(300)

def main():
    # Iniciar hilo para obtener dispositivos diariamente
    hilo_dispositivos = threading.Thread(target=obtener_dispositivos_diariamente)
    hilo_dispositivos.start()

    # Iniciar lectura de sensores cada 5 minutos
    hilo_sensores = threading.Thread(target=leer_sensores_periodicamente, args=("COM6",))
    hilo_sensores.start()

    # Mantener el hilo principal vivo
    hilo_dispositivos.join()
    hilo_sensores.join()

if __name__ == "__main__":
    main()
