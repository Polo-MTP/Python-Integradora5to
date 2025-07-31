# main.py
from Clases.metodos import *
from Clases.user_config import UserConfig
import json
from datetime import datetime
import serial
import time

def revisar_configuraciones_periodicas(puerto_serial="COM6", config_file="Jsons_DATA/user_configs.json"):
    print("⚙️ Iniciando revisión de configuraciones de actuadores...")
    
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
                        print(f"✅ EJECUTANDO comando: {codigo}")
                        try:
                            with serial.Serial(puerto_serial, 115200, timeout=3) as arduino:
                                print(f"📡 Puerto {puerto_serial} conectado")
                                time.sleep(3)  # Esperar que Arduino termine de inicializar
                                arduino.write(f"{codigo}\n".encode())
                                arduino.flush()
                                print(f"⚡ Comando '{codigo}' enviado al Arduino")
                                
                                # Verificar si Arduino responde
                                time.sleep(2)  # Más tiempo para que procese
                                respuestas = []
                                while arduino.in_waiting > 0:
                                    respuesta = arduino.readline().decode().strip()
                                    if respuesta:
                                        respuestas.append(respuesta)
                                        print(f"📨 Arduino: {respuesta}")
                                
                                if not respuestas:
                                    print("⚠️ No hay más respuestas del Arduino")
                                
                                comandos_enviados.add(clave_unica)
                        except serial.SerialException as e:
                            print(f"❌ ERROR DE PUERTO SERIAL: {e}")
                        except Exception as e:
                            print(f"❌ ERROR GENERAL: {e}")
                    else:
                        print(f"⏭️ Comando {codigo} ya ejecutado")
        
        except Exception as e:
            print(f"❌ Error al revisar configuraciones: {e}")
        
        print("💤 Esperando 30 segundos...")
        time.sleep(30)

if __name__ == "__main__":
    revisar_configuraciones_periodicas()
    print("🚀 Proceso iniciado correctamente")