from Clases.metodos import *

def main():
    uuid = obtener_uuid()
    if not uuid:
        print("⚠️ No se encontró UUID en el archivo .env")
        return

    dispositivos = obtener_dispositivos(uuid)

    if dispositivos:
        guardar_dispositivos_json(dispositivos)
    else:
        print("⚠️ No se obtuvieron dispositivos.")

if __name__ == "__main__":
    main()
