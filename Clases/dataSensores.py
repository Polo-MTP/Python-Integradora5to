class dataSensores:
    def __init__(self, id, id_tank, sensor, value, unit, date, deviceId=None, code=None):
        self.id = id
        self.tankId = id_tank
        self.name = sensor
        self.deviceId = deviceId
        self.code = code
        self.value = value
        self.unit = unit
        self.date = date

    def diccionario(self):
        return self.__dict__

    def __str__(self):
        return f"Sensor: {self.name}, Value: {self.value} {self.unit}, Date: {self.date}"
