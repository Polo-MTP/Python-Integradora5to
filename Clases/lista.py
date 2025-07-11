import json

class Lista:
    def __init__(self, tipo_dato=None, datos=None):
        self.elementos = []
        self.tipo_dato = tipo_dato or self.__class__

        if datos is not None:
            self.agregar_elementos(datos)

    def agregar_elementos(self, datos):
        if isinstance(datos, list):
            for elemento in datos:
                self.agregar_elemento(elemento)
        else:
            self.agregar_elemento(datos)

    def agregar_elemento(self, elemento):
        if isinstance(elemento, self.tipo_dato):
            self.elementos.append(elemento)
        elif isinstance(elemento, dict):
            try:
                obj = self.tipo_dato(**elemento)
                self.elementos.append(obj)
            except TypeError as e:
                print(f"Error al construir el objeto desde dict: {e}")
        else:
            print(f"Error: {elemento} no es del tipo {self.tipo_dato.__name__} y no se agregó.")

    def mostrar_elementos(self):
        if not self.elementos:
            print("La lista está vacía.")
        else:
            for elemento in self.elementos:
                print(elemento)

    def diccionario(self):
        return [e.diccionario() if hasattr(e, 'diccionario') else e.__dict__ for e in self.elementos]

    def guardar(self, archivo):
        with open(archivo, "w", encoding="utf-8") as f:
            json.dump(self.diccionario(), f, indent=4, ensure_ascii=False)

    def cargar(self, archivo):
        with open(archivo, "r", encoding="utf-8") as f:
            datos = json.load(f)
        self.elementos.clear()
        self.agregar_elementos(datos)
