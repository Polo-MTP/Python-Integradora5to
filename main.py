from Clases.metodos import obtener_uuid, obtener_dispositivos, guardar_dispositivos_json
from Clases.sensor_scheduler import SensorScheduler
from Mongo.sync import sincronizar_a_mongo

import threading
import time

# ===============================
# 🔧 CONFIGURACIONES GLOBALES
# ===============================
puerto_serial = "COM7"  # Cambiar según tu puerto

# ===============================
# 🚀 FUNCIÓN PRINCIPAL
# ===============================
def main():
    print("🚀 Iniciando Sistema de Sensores (sin configuraciones horarias/MQTT)")
    print("=" * 70)
    print("🔹 Sensores automáticos")
    print("🔹 Sincronización MongoDB")
    print("=" * 70)

    # Crear el scheduler de sensores
    scheduler = SensorScheduler(puerto_serial=puerto_serial)

    try:
        # Cargar configuración inicial desde la API
        print("🔄 Obteniendo configuración inicial...")
        uuid = obtener_uuid()
        if uuid:
            dispositivos = obtener_dispositivos(uuid)
            if dispositivos:
                guardar_dispositivos_json(dispositivos)
                print("✅ Configuración inicial de sensores cargada")
        else:
            print("⚠️ No se pudieron obtener configuraciones iniciales. Usando configuración existente.")

        # Iniciar el scheduler de sensores automáticos
        print("\n📊 Iniciando sistema de lectura automática de sensores...")
        scheduler.iniciar_programacion()

        # Hilo de actualización diaria de dispositivos
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
                    print("🔄 Configuración de sensores actualizada")
                    scheduler.recargar_dispositivos()
                else:
                    print("⚠️ No se obtuvieron dispositivos de la API")

                print("⏰ Próxima actualización de dispositivos en 24 horas")
                time.sleep(86400)

        hilo_dispositivos = threading.Thread(target=obtener_dispositivos_diariamente)
        hilo_dispositivos.daemon = True
        hilo_dispositivos.start()

        # Hilo de sincronización con MongoDB
        hilo_sync = threading.Thread(target=sincronizar_a_mongo)
        hilo_sync.daemon = True
        hilo_sync.start()

        # Mostrar estado del sistema
        time.sleep(2)
        estado = scheduler.obtener_estado()
        print("\n" + "="*70)
        print("📋 ESTADO ACTUAL DEL SISTEMA:")
        print("="*70)
        print(f"📊 Sensores automáticos activos: {estado['active_threads']}")
        print(f"🔄 Actualización dispositivos: Cada 24 horas")
        print(f"🗄️ MongoDB: Sincronización automática")

        if estado['sensors']:
            print("\n📊 SENSORES CONFIGURADOS:")
            for sensor in estado['sensors']:
                status = "✅ Activo" if sensor['active'] else "❌ Inactivo"
                print(f"   • {sensor['name']} ({sensor['code']}): {sensor['interval']}s - {status}")

        print("="*70)
        print("⌨️  Presiona Ctrl+C para detener todo el sistema")
        print("="*70)

        while True:
            time.sleep(10)

    except KeyboardInterrupt:
        print("\n🛑 Deteniendo sistema de sensores...")

    finally:
        print("🔄 Cerrando scheduler de sensores...")
        scheduler.detener_programacion()
        print("✅ Sistema detenido completamente")


if __name__ == "__main__":
    main()
