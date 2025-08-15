class Alerta:
    def __init__(self, id, tankId, deviceId, code, value, message, date, synced=False):
        self.id = id
        self.tankId = tankId
        self.deviceId = deviceId
        self.code = code
        self.value = value
        self.message = message
        self.date = date
        self.synced = synced
        
    def diccionario(self):
        return self.__dict__

    def __str__(self):
        return f"Alerta - {self.code}: {self.value} - {self.message} ({self.date})"
