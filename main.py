from Clases.metodos import obtener_uuid, obtener_dispositivos, guardar_dispositivos_json, obtener_configuraciones, guardar_configuraciones_json
from Clases.sensor_scheduler import SensorScheduler
from Clases.user_config import UserConfig
from Clases.lista import Lista  # Agregar esta importación
from Mongo.sync import sincronizar_a_mongo

import threading
import time
import serial
import json
import os  # Agregar esta importación
from datetime import datetime
import paho.mqtt.client as mqtt

# ===============================
# 🔧 CONFIGURACIONES GLOBALES
# ===============================
puerto_serial = "COM6"  # Cambiar según tu puerto
config_file = "Jsons_DATA/user_configs.json"
broker = '13.59.132.191'
port = 1883
topic = 'conf/uuid/code'

# ===============================
# 📡 FUNCIÓN MEJORADA DE ARDUINO
# ===============================
def enviar_comando_a_arduino(codigo, puerto=puerto_serial):
    """Función unificada para enviar comandos al Arduino"""
    try:
        with serial.Serial(puerto, 9600, timeout=3) as arduino:
            print(f"📡 Puerto {puerto} conectado")
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

# ===============================
# ⏰ REVISIÓN DE CONFIGURACIONES HORARIAS
# ===============================
def revisar_configuraciones_periodicas():
    """Revisión mejorada de configuraciones programadas por hora"""
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
                
                # Manejar ambos formatos de hora
                if hora_config:
                    try:
                        # Si es formato ISO, convertir a HH:MM
                        if 'T' in hora_config or len(hora_config) > 5:
                            hora_config = datetime.fromisoformat(hora_config).strftime("%H:%M")
                    except:
                        pass  # Si no es ISO, usar tal como está

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
            print(f"❌ Error al revisar configuraciones periódicas: {e}")
        
        print("💤 Esperando 20 segundos...")
        time.sleep(20)

# ===============================
# 📡 SISTEMA MQTT
# ===============================
def iniciar_mqtt():
    """Sistema MQTT para recibir comandos remotos"""
    def on_connect(client, userdata, flags, rc):
        if rc == 0:
            print(f'✅ Conectado al broker MQTT en {broker}:{port}')
            client.subscribe(topic)
            print(f'📡 Suscrito al topic: {topic}')
        else:
            print(f'❌ Error de conexión MQTT. Código: {rc}')

    def on_message(client, userdata, msg):
        payload = msg.payload.decode().strip()
        print(f'📥 Mensaje MQTT recibido en "{msg.topic}": {payload}')
        if payload:
            print(f"🚀 Ejecutando comando MQTT: {payload}")
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
# 🔄 ACTUALIZACIÓN DE DISPOSITIVOS
# ===============================
def obtener_dispositivos_diariamente(scheduler):
    """Actualización diaria de dispositivos desde la API"""
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

# ===============================
# ⚙️ ACTUALIZACIÓN DE CONFIGURACIONES (CADA 5 MIN)
# ===============================
def obtener_configuraciones_periodicas():
    """Actualización de configuraciones cada 5 minutos"""
    print("⚙️ Iniciando actualización periódica de configuraciones (cada 5 min)...")
    
    while True:
        try:
            uuid = obtener_uuid()
            if not uuid:
                print("⚠️ No se encontró UUID para obtener configuraciones")
                time.sleep(300)  # 5 minutos
                continue

            # Mostrar configuraciones actuales antes de actualizar
            try:
                with open(config_file, 'r', encoding='utf-8') as f:
                    config_actual = json.load(f)
                print(f"📊 Configuraciones actuales en archivo: {len(config_actual)}")
            except Exception as e:
                print(f"📊 No hay configuraciones previas o error al leer: {e}")

            print(f"🔄 Obteniendo configuraciones desde API... UUID: {uuid}")
            configuraciones = obtener_configuraciones(uuid)

            if configuraciones:
                print(f"📋 Configuraciones recibidas de la API: {len(configuraciones)}")
                
                # Mostrar detalles de las configuraciones recibidas
                for i, config in enumerate(configuraciones):
                    codigo = config.get('code', 'N/A')
                    valor = config.get('config_value', 'N/A')
                    print(f"   {i+1}. {codigo} -> {valor}")
                
                # Verificar si tenemos datos válidos
                if isinstance(configuraciones, list) and len(configuraciones) > 0:
                    print("💾 Guardando todas las configuraciones (reemplazando archivo completo)...")
                    guardar_configuraciones_json(configuraciones)
                    print("✅ Configuraciones guardadas exitosamente")
                    
                    # Verificar que se guardó correctamente
                    try:
                        with open(config_file, 'r', encoding='utf-8') as f:
                            verificacion = json.load(f)
                        print(f"✅ Verificación: {len(verificacion)} configuraciones guardadas en {config_file}")
                        
                        # Mostrar configuraciones guardadas
                        for i, config in enumerate(verificacion):
                            codigo = config.get('code', 'N/A')
                            valor = config.get('config_value', 'N/A')
                            print(f"   ✅ {i+1}. {codigo} -> {valor}")
                            
                    except Exception as ve:
                        print(f"⚠️ Error al verificar guardado: {ve}")
                else:
                    print("⚠️ Configuraciones vacías o formato inválido - no se actualiza el archivo")
            else:
                print("⚠️ No se obtuvieron configuraciones de la API (respuesta vacía/nula)")
                print("🔄 Manteniendo configuración actual sin cambios")

        except Exception as e:
            print(f"❌ Error al obtener configuraciones periódicas: {e}")
            import traceback
            traceback.print_exc()

        print("⏰ Próxima actualización de configuraciones en 20 segundos")
        time.sleep(20)  # 20 segundos

# ===============================
# 🚀 FUNCIÓN PRINCIPAL UNIFICADA
# ===============================
def main():
    print("🚀 Iniciando Sistema Integradora de Sensores COMPLETO")
    print("=" * 70)
    print("🔹 Sensores automáticos")
    print("🔹 Configuraciones horarias")
    print("🔹 Comandos MQTT")
    print("🔹 Sincronización MongoDB")
    print("=" * 70)

    # Crear el scheduler de sensores
    scheduler = SensorScheduler(puerto_serial=puerto_serial)

    try:
        # 3. Cargar configuración inicial desde la API
        print("🔄 Obteniendo configuración inicial...")
        uuid = obtener_uuid()
        if uuid:
            # Cargar dispositivos
            dispositivos = obtener_dispositivos(uuid)
            if dispositivos:
                guardar_dispositivos_json(dispositivos)
                print("✅ Configuración inicial de sensores cargada")
            
            # Cargar configuraciones de usuario
            configuraciones = obtener_configuraciones(uuid)
            if configuraciones:
                guardar_configuraciones_json(configuraciones)
                print("✅ Configuraciones de usuario cargadas")
        else:
            print("⚠️ No se pudieron obtener configuraciones iniciales. Usando configuración existente.")

        # 2. Iniciar el scheduler de sensores automáticos
        print("\n📊 Iniciando sistema de lectura automática de sensores...")
        scheduler.iniciar_programacion()

        # 3. Hilo de actualización diaria de dispositivos
        print("🔄 Iniciando actualización diaria de dispositivos...")
        hilo_dispositivos = threading.Thread(target=obtener_dispositivos_diariamente, args=(scheduler,))
        hilo_dispositivos.daemon = True
        hilo_dispositivos.start()

        # 4. Hilo de actualización de configuraciones cada 20 segundos
        print("⚙️ Iniciando actualización periódica de configuraciones (cada 20 seg)...")
        hilo_configuraciones = threading.Thread(target=obtener_configuraciones_periodicas)
        hilo_configuraciones.daemon = True
        hilo_configuraciones.start()

        # 5. Hilo de sincronización con MongoDB
        print("🔄 Iniciando sincronización automática con MongoDB...")
        hilo_sync = threading.Thread(target=sincronizar_a_mongo)
        hilo_sync.daemon = True
        hilo_sync.start()

        # 6. Hilo para revisión de configuraciones horarias (actuadores)
        print("🕒 Iniciando verificación de configuraciones horarias...")
        hilo_config = threading.Thread(target=revisar_configuraciones_periodicas)
        hilo_config.daemon = True
        hilo_config.start()

        # 7. Hilo para MQTT (comandos remotos)
        print("📡 Iniciando escucha de comandos MQTT...")
        hilo_mqtt = threading.Thread(target=iniciar_mqtt)
        hilo_mqtt.daemon = True
        hilo_mqtt.start()

        # 8. Mostrar estado del sistema
        time.sleep(2)  # Esperar a que se inicien los hilos
        estado = scheduler.obtener_estado()
        print("\n" + "="*70)
        print("📋 ESTADO ACTUAL DEL SISTEMA:")
        print("="*70)
        print(f"📊 Sensores automáticos activos: {estado['active_threads']}")
        print(f"🔄 Actualización dispositivos: Cada 24 horas")
        print(f"⚙️ Actualización configuraciones: Cada 20 segundos")
        print(f"⏰ Configuraciones horarias: Cada 20 segundos")
        print(f"📡 MQTT: Escuchando en {broker}:{port}")
        print(f"🗄️ MongoDB: Sincronización automática")
        
        if estado['sensors']:
            print("\n📊 SENSORES CONFIGURADOS:")
            for sensor in estado['sensors']:
                status = "✅ Activo" if sensor['active'] else "❌ Inactivo"
                print(f"   • {sensor['name']} ({sensor['code']}): {sensor['interval']}s - {status}")
        
        print("="*70)
        print("⌨️  Presiona Ctrl+C para detener todo el sistema")
        print("="*70)

        # 9. Mantener el sistema vivo
        while True:
            time.sleep(10)

    except KeyboardInterrupt:
        print("\n🛑 Deteniendo sistema completo...")

    finally:
        print("🔄 Cerrando scheduler de sensores...")
        scheduler.detener_programacion()
        print("✅ Sistema detenido completamente")


if __name__ == "__main__":
    main()