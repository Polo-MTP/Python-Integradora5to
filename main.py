from Clases.metodos import obtener_uuid, obtener_dispositivos, guardar_dispositivos_json
from Clases.sensor_scheduler import SensorScheduler
from Mongo.sync import sincronizar_a_mongo
import threading
import time

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
            # Recargar el scheduler con los nuevos dispositivos
            if scheduler:
                print("🔄 Recargando configuración de sensores...")
                scheduler.recargar_dispositivos()
        else:
            print("⚠️ No se obtuvieron dispositivos de la API. Continuando con configuración actual.")

        # Esperar 24 horas antes de la próxima actualización
        print("⏰ Próxima actualización de dispositivos en 24 horas")
        time.sleep(86400)

def main():
    print("🚀 Iniciando Sistema Integradora de Sensores")
    print("="*60)
    
    # Crear el scheduler de sensores
    scheduler = SensorScheduler(puerto_serial="COM5")
    
    try:
        # 1. Primero obtener dispositivos iniciales
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
        
        # 3. Iniciar hilo para actualizar dispositivos cada 24 horas
        hilo_dispositivos = threading.Thread(target=obtener_dispositivos_diariamente, args=(scheduler,))
        hilo_dispositivos.daemon = True
        hilo_dispositivos.start()
        
        # 4. Iniciar hilo de sincronización con MongoDB
        print("🔄 Iniciando sincronización automática con MongoDB...")
        hilo_sync = threading.Thread(target=sincronizar_a_mongo)
        hilo_sync.daemon = True
        hilo_sync.start()
        
        # 5. Mostrar estado del sistema
        estado = scheduler.obtener_estado()
        print("\n📋 Estado del sistema:")
        print(f"📊 Total sensores activos: {estado['active_threads']}")
        print(f"🔄 Sync dispositivos: Cada 24 horas")
        
        for sensor in estado['sensors']:
            status = "✅ Activo" if sensor['active'] else "❌ Inactivo"
            print(f"   • {sensor['name']} ({sensor['code']}): {sensor['interval']}s - {status}")
        
        print("\n⌨️  Presiona Ctrl+C para detener el sistema")
        
        # 6. Mantener el programa ejecutándose
        while True:
            time.sleep(10)  # Verificar cada 10 segundos
            
            # Opcional: mostrar estado periódicamente
            # estado_actual = scheduler.obtener_estado()
            # if estado_actual['active_threads'] == 0:
            #     print("⚠️ Advertencia: No hay hilos activos")
                
    except KeyboardInterrupt:
        print("\n🛹 Deteniendo sistema...")
    finally:
        # Limpiar recursos
        scheduler.detener_programacion()
        print("🚀 Sistema detenido completamente")

if __name__ == "__main__":
    main()
