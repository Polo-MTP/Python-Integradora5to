import json
import time
import threading
from datetime import datetime
import paho.mqtt.client as mqtt
import serial
from Clases.metodos import (
    obtener_uuid,
    obtener_configuraciones,
    guardar_configuraciones_json
)

# ===============================
# 🔧 CONFIGURACIONES GLOBALES
# ===============================
puerto_serial = "COM6"  # Cambiar según tu puerto
config_file = "Jsons_DATA/user_configs.json"
broker = '13.59.132.191'
port = 1883
topic = 'conf/uuid/code'

# ===============================
# 📡 FUNCIÓN DE ENVÍO A ARDUINO
# ===============================
def enviar_comando_a_arduino(codigo, puerto=puerto_serial):
    """Enviar comando al Arduino por serial."""
    try:
        with serial.Serial(puerto, 9600, timeout=3) as arduino:
            time.sleep(3)  # Esperar inicialización
            arduino.write(f"{codigo}\n".encode())
            arduino.flush()
            print(f"⚡ Comando '{codigo}' enviado al Arduino")
    except Exception as e:
        print(f"❌ Error enviando comando a Arduino: {e}")

# ===============================
# ⏰ REVISIÓN DE CONFIGURACIONES HORARIAS
# ===============================
def revisar_configuraciones_periodicas():
    """Verifica el archivo JSON y ejecuta comandos en la fecha y hora programadas."""
    comandos_enviados = set()
    print("🕒 Iniciando revisión horaria con validación de fecha...")

    while True:
        try:
            with open(config_file, 'r', encoding='utf-8') as f:
                configuraciones = json.load(f)

            ahora_fecha = datetime.now().strftime("%Y-%m-%d")
            ahora_hora = datetime.now().strftime("%H:%M")

            for config in configuraciones:
                codigo = config.get("code")
                hora_config = config.get("config_value")
                fecha_config = config.get("config_day")

                # Convertir ISO de hora si es necesario
                if hora_config:
                    try:
                        if 'T' in hora_config or len(hora_config) > 5:
                            hora_config = datetime.fromisoformat(hora_config).strftime("%H:%M")
                    except:
                        pass

                # Comparar fecha y hora
                clave_unica = f"{codigo}_{fecha_config}_{hora_config}"
                if codigo and hora_config and fecha_config:
                    if ahora_fecha == fecha_config and ahora_hora == hora_config:
                        if clave_unica not in comandos_enviados:
                            print(f"✅ Ejecutando comando programado ({fecha_config} {hora_config}): {codigo}")
                            enviar_comando_a_arduino(codigo)
                            comandos_enviados.add(clave_unica)
                        else:
                            print(f"⏭️ Comando {codigo} ya ejecutado para {fecha_config} {hora_config}")

        except Exception as e:
            print(f"❌ Error en revisión de configuraciones: {e}")

        time.sleep(20)

# ===============================
# 📡 SISTEMA MQTT
# ===============================
def iniciar_mqtt():
    """Sistema MQTT para recibir comandos remotos."""
    def on_connect(client, userdata, flags, rc):
        if rc == 0:
            print(f'✅ Conectado a MQTT {broker}:{port}')
            client.subscribe(topic)
        else:
            print(f'❌ Error de conexión MQTT: {rc}')

    def on_message(client, userdata, msg):
        payload = msg.payload.decode().strip()
        if payload:
            print(f"📥 Comando recibido por MQTT: {payload}")
            enviar_comando_a_arduino(payload)

    client = mqtt.Client(client_id='listener-python')
    client.on_connect = on_connect
    client.on_message = on_message

    try:
        client.connect(broker, port, keepalive=60)
        client.loop_forever()
    except Exception as e:
        print(f"❌ Error en MQTT: {e}")

# ===============================
# ⚙️ ACTUALIZACIÓN DE CONFIGURACIONES DESDE API
# ===============================
def obtener_configuraciones_periodicas():
    """Actualiza configuraciones desde API cada 20 segundos."""
    print("🔄 Iniciando actualización periódica desde API...")
    while True:
        try:
            uuid = obtener_uuid()
            if uuid:
                configuraciones = obtener_configuraciones(uuid)
                if isinstance(configuraciones, list) and configuraciones:
                    guardar_configuraciones_json(configuraciones)
                    print(f"💾 {len(configuraciones)} configuraciones actualizadas desde API")
        except Exception as e:
            print(f"❌ Error actualizando configuraciones: {e}")
        time.sleep(20)

# ===============================
# 🚀 MAIN
# ===============================
def main():
    print("🚀 Sistema de configuración iniciado")
    print("="*60)
    print("🕒 Revisión horaria desde JSON cada 20s")
    print("📡 Escucha MQTT activa")
    print("🔄 Actualización desde API cada 20s")
    print("="*60)

    # Hilo: revisión horaria
    threading.Thread(target=revisar_configuraciones_periodicas, daemon=True).start()
    # Hilo: actualización desde API
    threading.Thread(target=obtener_configuraciones_periodicas, daemon=True).start()
    # Hilo: MQTT
    threading.Thread(target=iniciar_mqtt, daemon=True).start()

    # Mantener proceso vivo
    try:
        while True:
            time.sleep(10)
    except KeyboardInterrupt:
        print("\n🛑 Sistema detenido")

if __name__ == "__main__":
    main()
