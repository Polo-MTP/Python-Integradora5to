# main.py
from Clases.metodos import *
from Clases.user_config import UserConfig
import json
from datetime import datetime
import serial
import time
import threading
import paho.mqtt.client as mqtt

# Configuraciones
puerto_serial = "COM6"
config_file = "Jsons_DATA/user_configs.json"
broker = '13.59.132.191'
port = 1883
topic = 'conf/uuid/code'

# Función para enviar comando al Arduino
def enviar_comando_a_arduino(codigo):
    try:
        with serial.Serial(puerto_serial, 115200, timeout=3) as arduino:
            print(f"📡 Puerto {puerto_serial} conectado")
            time.sleep(3)  # Esperar a que Arduino se inicialice
            arduino.write(f"{codigo}\n".encode())
            arduino.flush()
            print(f"⚡ Comando '{codigo}' enviado al Arduino")

            time.sleep(2)
            while arduino.in_waiting > 0:
                respuesta = arduino.readline().decode().strip()
                if respuesta:
                    print(f"📨 Arduino: {respuesta}")
    except serial.SerialException as e:
        print(f"❌ ERROR DE PUERTO SERIAL: {e}")
    except Exception as e:
        print(f"❌ ERROR GENERAL: {e}")

# -----------------------------
# ⏰ TAREA 1: POR HORA PROGRAMADA
# -----------------------------
def revisar_configuraciones_periodicas():
    print("⚙️ Iniciando revisión de configuraciones de actuadores (por hora)...")
    comandos_enviados = set()

    while True:
        try:
            with open(config_file, 'r', encoding='utf-8') as f:
                configuraciones = json.load(f)

            ahora = datetime.now().strftime("%H:%M")
            print(f"⏰ Hora actual: {ahora}")

            for config in configuraciones:
                codigo = config.get("code")
                hora_config = config.get("config_value")
                clave_unica = f"{codigo}_{hora_config}"

                print(f"🔍 Verificando: {codigo} programado para {hora_config}")

                if codigo and hora_config and ahora == hora_config:
                    if clave_unica not in comandos_enviados:
                        print(f"✅ Ejecutando comando programado: {codigo}")
                        enviar_comando_a_arduino(codigo)
                        comandos_enviados.add(clave_unica)
                    else:
                        print(f"⏭️ Comando {codigo} ya ejecutado")
        except Exception as e:
            print(f"❌ Error al revisar configuraciones: {e}")

        print("💤 Esperando 30 segundos...")
        time.sleep(30)

# -----------------------------
# 📡 TAREA 2: ESCUCHAR MQTT
# -----------------------------
def iniciar_mqtt():
    def on_connect(client, userdata, flags, rc):
        if rc == 0:
            print(f'✅ Conectado al broker MQTT en {broker}:{port}')
            client.subscribe(topic)
            print(f'📡 Suscrito al topic: {topic}')
        else:
            print(f'❌ Error de conexión. Código: {rc}')

    def on_message(client, userdata, msg):
        payload = msg.payload.decode().strip()
        print(f'📥 Mensaje MQTT recibido en "{msg.topic}": {payload}')
        if payload:
            print(f"🚀 Ejecutando comando MQTT: {payload}")
            enviar_comando_a_arduino(payload)

    client = mqtt.Client(client_id='listener-python')
    client.on_connect = on_connect
    client.on_message = on_message

    client.connect(broker, port, keepalive=60)
    client.loop_forever()

# -----------------------------
# 🧵 EJECUTAR AMBAS TAREAS A LA VEZ
# -----------------------------
if __name__ == "__main__":
    print("🚀 Iniciando sistema...")

    # Iniciar el hilo de revisión de horas
    hilo_horas = threading.Thread(target=revisar_configuraciones_periodicas)
    hilo_horas.daemon = True
    hilo_horas.start()

    # Iniciar MQTT (queda en loop_forever)
    iniciar_mqtt()
