from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi
import os
from dotenv import load_dotenv

# 📦 Cargar variables del archivo .env
load_dotenv()

class MongoDb:
    def __init__(self):
        self.uri = os.getenv("MONGO_URI")
        self.db_name = os.getenv("DB_DATABASE")
        self.client = None
        self.db = None
        self.collection = None

        if not self.verificar_conexion():
            print("❌ No se pudo conectar a MongoDB")
            raise Exception("Error de conexión a MongoDB")

        print("✅ Conexión a MongoDB establecida correctamente")

    def verificar_conexion(self):
        try:
            server_api = ServerApi("1", strict=True, deprecation_errors=True)
            self.client = MongoClient(self.uri, server_api=server_api)

            self.client.admin.command("ping")

            self.db = self.client[self.db_name]
            self.collection = self.db["dataSensores"]

            print(f"🎯 Conectado a la base de datos '{self.db_name}' y colección 'dataSensores'")
            return True
        except Exception as e:
            print(f"🔌 Error de conexión: {e}")
            return False

    def insertar_documento(self, documento):
        if self.collection is None:
            print("⚠️ Colección no inicializada. Verifique la conexión.")
            return
        try:
            self.collection.insert_one(documento)
            print(f"📄 Documento insertado con éxito: {documento}")
        except Exception as e:
            print(f"❌ Error al insertar documento: {e}")

    def insertar_documentos(self, documentos):
        if self.collection is None:
            print("⚠️ Colección no inicializada. Verifique la conexión.")
            return
        try:
            self.collection.insert_many(documentos)
            print(f"📄 Documentos insertados con éxito: {documentos}")
        except Exception as e:
            print(f"❌ Error al insertar documentos: {e}")

# 🚀 Punto de entrada
if __name__ == "__main__":
    try:
        mongo = MongoDb()
        mongo.insertar_documento({"nombre": "prueba", "edad": 20})
    except Exception as e:
        print(f"⛔ Error en la ejecución: {e}")