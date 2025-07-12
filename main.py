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

dato = leer_datos_serial('COM6')  
if dato:
    print("Lectura del Arduino:", dato)

if __name__ == "__main__":
    main()
