class Device:
    def __init__(self, id, tankId, code, name, createdAt=None, updatedAt=None):
        self.id = id
        self.tankId = tankId
        self.code= code
        self.name = name
        self.createdAt = createdAt
        self.updatedAt = updatedAt

    def diccionario(self):
        return self.__dict__

    def __str__(self):
        return f"{self.name} (ID: {self.id}, Tank: {self.tankId})"
