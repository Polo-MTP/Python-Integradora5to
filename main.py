from Clases.metodos import obtener_uuid, obtener_dispositivos, guardar_dispositivos_json
from Clases.sensor_scheduler import SensorScheduler
from Mongo.sync import sincronizar_a_mongo

import threading
import time
import serial
import json
from datetime import datetime

# 🔁 NUEVA FUNCIÓN: Revisión periódica de configuraciones horarias
def revisar_configuraciones_periodicas(puerto_serial="COM5", config_file="Jsons_DATA/user_configs.json"):
    while True:
        try:
            with open(config_file, 'r', encoding='utf-8') as f:
                configuraciones = json.load(f)

            ahora = datetime.now().strftime("%H:%M")

            for config in configuraciones:
                codigo = config["code"]  # Ej: "light/on"
                hora = datetime.fromisoformat(config["config_value"]).strftime("%H:%M")

                if ahora == hora:
                    comando = f"{codigo}"
                    with serial.Serial(puerto_serial, 115200, timeout=2) as arduino:
                        arduino.write(f"{comando}\n".encode())
                        print(f"⚡ Enviado a Arduino: {comando}")
        except Exception as e:
            print(f"❌ Error al revisar configuraciones periódicas: {e}")
        
        time.sleep(60)  # Revisar cada minuto


# 🔄 Actualización diaria de dispositivos
def obtener_dispositivos_diariamente(scheduler):
    """Función que actualiza los dispositivos cada 24 horas y recarga el scheduler"""
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
            if scheduler:
                print("🔄 Recargando configuración de sensores...")
                scheduler.recargar_dispositivos()
        else:
            print("⚠️ No se obtuvieron dispositivos de la API. Continuando con configuración actual.")

        print("⏰ Próxima actualización de dispositivos en 24 horas")
        time.sleep(86400)


# 🚀 Punto de entrada principal
def main():
    print("🚀 Iniciando Sistema Integradora de Sensores")
    print("=" * 60)

    # Crear el scheduler
    scheduler = SensorScheduler(puerto_serial="COM5")

    try:
        # 1. Cargar configuración inicial de dispositivos desde la API
        print("🔄 Obteniendo configuración inicial de dispositivos...")
        uuid = obtener_uuid()
        if uuid:
            dispositivos = obtener_dispositivos(uuid)
            if dispositivos:
                guardar_dispositivos_json(dispositivos)
                print("✅ Configuración inicial cargada")
            else:
                print("⚠️ No se pudieron obtener dispositivos. Usando configuración existente.")

        # 2. Iniciar el scheduler de sensores
        print("\n📊 Iniciando sistema de lectura de sensores...")
        scheduler.iniciar_programacion()

        # 3. Hilo de actualización diaria de dispositivos
        hilo_dispositivos = threading.Thread(target=obtener_dispositivos_diariamente, args=(scheduler,))
        hilo_dispositivos.daemon = True
        hilo_dispositivos.start()

        # 4. Hilo de sincronización con MongoDB
        print("🔄 Iniciando sincronización automática con MongoDB...")
        hilo_sync = threading.Thread(target=sincronizar_a_mongo)
        hilo_sync.daemon = True
        hilo_sync.start()

        # 5. Hilo para revisión de configuraciones horarias (luz, comida, etc.)
        print("🕒 Iniciando verificación de configuraciones horarias...")
        hilo_config = threading.Thread(target=revisar_configuraciones_periodicas)
        hilo_config.daemon = True
        hilo_config.start()

        # 6. Mostrar estado
        estado = scheduler.obtener_estado()
        print("\n📋 Estado del sistema:")
        print(f"📊 Total sensores activos: {estado['active_threads']}")
        print(f"🔄 Sync dispositivos: Cada 24 horas")

        for sensor in estado['sensors']:
            status = "✅ Activo" if sensor['active'] else "❌ Inactivo"
            print(f"   • {sensor['name']} ({sensor['code']}): {sensor['interval']}s - {status}")

        print("\n⌨️  Presiona Ctrl+C para detener el sistema")

        # 7. Mantener vivo
        while True:
            time.sleep(10)

    except KeyboardInterrupt:
        print("\n🛹 Deteniendo sistema...")

    finally:
        scheduler.detener_programacion()
        print("🚀 Sistema detenido completamente")


if __name__ == "__main__":
    main()
