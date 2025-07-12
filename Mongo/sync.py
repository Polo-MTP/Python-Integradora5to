import time
import json
from mongo import MongoDb

ARCHIVO_LOCAL = "Jsons_DATA/data_sensores_local.json"

def cargar_datos_locales():
    try:
        with open(ARCHIVO_LOCAL, "r", encoding="utf-8") as f:
            contenido = f.read().strip()
            if not contenido:
                return []
            return json.loads(contenido)
    except FileNotFoundError:
        print("📁 Archivo local no encontrado.")
        return []
    except Exception as e:
        print(f"❌ Error al cargar datos locales: {e}")
        return []

def sincronizar_a_mongo():
    try:
        mongo = MongoDb()
    except Exception as e:
        print(f"❌ No se pudo iniciar MongoDb: {e}")
        return
    
    while True:
        try:
            datos_locales = cargar_datos_locales()
            
            if not datos_locales:
                print("📁 No hay datos para sincronizar.")
            else:
                datos_no_sincronizados = [dato for dato in datos_locales if not dato.get("synced", False)]
                
                if datos_no_sincronizados:
                    print(f"📤 Subiendo {len(datos_no_sincronizados)} datos nuevos a MongoDB...")
                    
                    datos_para_mongo = []
                    for dato in datos_no_sincronizados:
                        dato_mongo = {k: v for k, v in dato.items() if k != "synced"}
                        datos_para_mongo.append(dato_mongo)
                    
                    mongo.insertar_documentos(datos_para_mongo)
                    
                    for dato in datos_locales:
                        if not dato.get("synced", False):
                            dato["synced"] = True
                    
                    with open(ARCHIVO_LOCAL, "w", encoding="utf-8") as f:
                        json.dump(datos_locales, f, indent=4, ensure_ascii=False)
                    
                    print(f"✅ {len(datos_no_sincronizados)} datos sincronizados correctamente.")
                    
                    limpiar_datos_antiguos(datos_locales)
                    
                else:
                    print("⏳ No hay datos nuevos para subir a MongoDB.")
        
        except Exception as e:
            print(f"❌ Error durante la sincronización: {e}")
        
        print("🕒 Esperando 10 minutos para la siguiente sincronización...\n")
        time.sleep(30)  

def limpiar_datos_antiguos(datos_locales, dias_mantener=7):
    """Limpia datos sincronizados más antiguos que X días"""
    from datetime import datetime, timedelta
    
    try:
        fecha_limite = datetime.now() - timedelta(days=dias_mantener)
        
        datos_filtrados = []
        datos_eliminados = 0
        
        for dato in datos_locales:
            if not dato.get("synced", False):
                datos_filtrados.append(dato)
            else:
                try:
                    fecha_dato = datetime.fromisoformat(dato["date"].replace('Z', '+00:00'))
                    if fecha_dato > fecha_limite:
                        datos_filtrados.append(dato)
                    else:
                        datos_eliminados += 1
                except:
                    datos_filtrados.append(dato)
        
        if datos_eliminados > 0:
            with open(ARCHIVO_LOCAL, "w", encoding="utf-8") as f:
                json.dump(datos_filtrados, f, indent=4, ensure_ascii=False)
            print(f"🧹 Limpiados {datos_eliminados} datos antiguos sincronizados.")
            
    except Exception as e:
        print(f"⚠️ Error al limpiar datos antiguos: {e}")

if __name__ == "__main__":
    sincronizar_a_mongo()