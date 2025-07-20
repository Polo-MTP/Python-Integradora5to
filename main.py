from Clases.metodos import obtener_uuid, obtener_dispositivos, guardar_dispositivos_json
from Clases.arduino import leer_serial_y_guardar

def main():
    # Obtener el UUID desde .env
    uuid = obtener_uuid()
    if not uuid:
        print("⚠️ No se encontró UUID en el archivo .env")
        return

    print(f"🔑 UUID obtenido: {uuid}")

    dispositivos = obtener_dispositivos(uuid)

    if dispositivos:
        guardar_dispositivos_json(dispositivos)
    else:
        print("⚠️ No se obtuvieron dispositivos de la API. No se puede continuar.")
        return


    # Ahora que tenemos los dispositivos, empezamos a leer el puerto serial
    # y guardar datos usando el mapa cargado
    leer_serial_y_guardar(puerto="COM6")

if __name__ == "__main__":
    main()
