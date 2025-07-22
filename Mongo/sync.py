import time
import json
import os
import sys

# Agregar el directorio padre al path para importar las clases
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from mongo import MongoDb
from Clases.lista import Lista
from Clases.dataSensores import dataSensores

ARCHIVO_LOCAL = "Jsons_DATA/data_sensores_local.json"

class SyncManager:
    def __init__(self, archivo_local=ARCHIVO_LOCAL):
        self.archivo_local = archivo_local
        self.lista_sensores = Lista(dataSensores)
        self.mongo = None
        self._inicializar_mongo()
    
    def _inicializar_mongo(self):
        try:
            self.mongo = MongoDb()
            print("✅ Conexión a MongoDB inicializada")
        except Exception as e:
            print(f"❌ Error al inicializar MongoDB: {e}")
            self.mongo = None
    
    def cargar_datos_locales(self):
        try:
            if not os.path.exists(self.archivo_local):
                print("📁 Archivo local no encontrado, creando lista vacía")
                return Lista(dataSensores)
            
            lista_datos = Lista(dataSensores)
            lista_datos.cargar(self.archivo_local)
            
            print(f"📊 Cargados {len(lista_datos.elementos)} datos locales")
            return lista_datos
            
        except Exception as e:
            print(f"❌ Error al cargar datos locales: {e}")
            return Lista(dataSensores)
    
    def filtrar_datos_no_sincronizados(self, lista_datos):
        """Filtra datos que no han sido sincronizados"""
        datos_no_sync = []
        for elemento in lista_datos.elementos:
            dato_dict = elemento.diccionario() if hasattr(elemento, 'diccionario') else elemento.__dict__
            if not dato_dict.get("synced", False):
                datos_no_sync.append(dato_dict)
        
        print(f"🔍 Encontrados {len(datos_no_sync)} datos no sincronizados")
        return datos_no_sync
    
    def preparar_datos_para_mongo(self, datos_no_sync):
        """Prepara datos para inserción en MongoDB removiendo campos locales"""
        datos_mongo = []
        for dato in datos_no_sync:
            dato_limpio = {k: v for k, v in dato.items() if k not in ["synced"]}
            datos_mongo.append(dato_limpio)
        
        return datos_mongo
    
    def marcar_como_sincronizados(self, lista_datos):
        datos_modificados = 0
        
        datos_dict = []
        for elemento in lista_datos.elementos:
            dato_dict = elemento.diccionario() if hasattr(elemento, 'diccionario') else elemento.__dict__
            if not dato_dict.get("synced", False):
                dato_dict["synced"] = True
                datos_modificados += 1
            datos_dict.append(dato_dict)
        
        with open(self.archivo_local, "w", encoding="utf-8") as f:
            json.dump(datos_dict, f, indent=4, ensure_ascii=False)
        
        print(f"✅ {datos_modificados} datos marcados como sincronizados")
        return datos_modificados
    
    def limpiar_datos_antiguos(self, dias_mantener=7):
        from datetime import datetime, timedelta
        
        try:
            fecha_limite = datetime.now() - timedelta(days=dias_mantener)
            
            with open(self.archivo_local, "r", encoding="utf-8") as f:
                datos_actuales = json.load(f)
            
            datos_filtrados = []
            datos_eliminados = 0
            
            for dato in datos_actuales:
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
                with open(self.archivo_local, "w", encoding="utf-8") as f:
                    json.dump(datos_filtrados, f, indent=4, ensure_ascii=False)
                print(f"🧹 Limpiados {datos_eliminados} datos antiguos (>{dias_mantener} días)")
            else:
                print("🧹 No hay datos antiguos para limpiar")
                
        except Exception as e:
            print(f"⚠️ Error al limpiar datos antiguos: {e}")
    
    def obtener_estadisticas(self, lista_datos):
        try:
            total_datos = len(lista_datos.elementos)
            sincronizados = 0
            no_sincronizados = 0
            
            for elemento in lista_datos.elementos:
                dato_dict = elemento.diccionario() if hasattr(elemento, 'diccionario') else elemento.__dict__
                if dato_dict.get("synced", False):
                    sincronizados += 1
                else:
                    no_sincronizados += 1
            
            print(f"📊 Estadísticas: {total_datos} total | {sincronizados} sync | {no_sincronizados} pendientes")
            return {
                "total": total_datos,
                "sincronizados": sincronizados,
                "no_sincronizados": no_sincronizados
            }
            
        except Exception as e:
            print(f"⚠️ Error al obtener estadísticas: {e}")
            return {"total": 0, "sincronizados": 0, "no_sincronizados": 0}

def cargar_datos_locales():
    sync_manager = SyncManager()
    return sync_manager.cargar_datos_locales()

def sincronizar_a_mongo(archivo_online="Jsons_DATA/data_sensores_online.json"):
    print("🚀 Iniciando servicio de sincronización con SyncManager...")
    
    sync_manager = SyncManager()
    
    if not sync_manager.mongo:
        print("❌ No se pudo inicializar MongoDB. Terminando...")
        return
    
    print("✅ SyncManager inicializado correctamente")
    
    while True:
        try:
            print("\n" + "="*60)
            print("🔄 Iniciando ciclo de sincronización")
            
            lista_datos = Lista(dataSensores)
            lista_datos.cargar(archivo_online)
            
            stats = sync_manager.obtener_estadisticas(lista_datos)
            
            if stats["total"] == 0:
                print("📁 No hay datos para sincronizar.")
            else:
                datos_no_sync = sync_manager.filtrar_datos_no_sincronizados(lista_datos)
                
                if datos_no_sync:
                    print(f"📤 Subiendo {len(datos_no_sync)} datos nuevos a MongoDB...")
                    
                    datos_mongo = sync_manager.preparar_datos_para_mongo(datos_no_sync)
                    
                    try:
                        sync_manager.mongo.insertar_documentos(datos_mongo)
                        print(f"✅ {len(datos_mongo)} datos insertados en MongoDB")
                        
                        sync_manager.marcar_como_sincronizados(lista_datos)
                        
                        sync_manager.limpiar_datos_antiguos()
                        
                    except Exception as e:
                        print(f"❌ Error al insertar en MongoDB: {e}")
                        print("⚠️ Datos no marcados como sincronizados")
                        
                    # Borrar datos del archivo online después de subir
                    with open(archivo_online, "w", encoding="utf-8") as f:
                        json.dump([], f, indent=4, ensure_ascii=False)
                    
                else:
                    print("⏳ No hay datos nuevos para subir a MongoDB.")
        
        except Exception as e:
            print(f"❌ Error durante la sincronización: {e}")
        
        print("🕒 Esperando 30 segundos para la siguiente sincronización...")
        print("="*60)
        time.sleep(30)

def limpiar_datos_antiguos(datos_locales, dias_mantener=7):
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