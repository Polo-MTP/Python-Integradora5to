class Device:
    def __init__(self, id, tank_id=None, tankId=None, code=None, name=None, createdAt=None, updatedAt=None, 
                 sensor_type_id=None, created_at=None, updated_at=None, sensor_type=None, reading_interval=300, **kwargs):
        self.id = id
        # Manejar ambos nombres para compatibilidad
        self.tankId = tank_id or tankId
        self.tank_id = tank_id or tankId
        self.code = code
        self.name = name
        self.createdAt = createdAt or created_at
        self.updatedAt = updatedAt or updated_at
        self.created_at = createdAt or created_at
        self.updated_at = updatedAt or updated_at
        self.sensor_type_id = sensor_type_id
        self.sensor_type = sensor_type or {}
        
        # Extraer reading_interval del sensor_type si está disponible
        if isinstance(sensor_type, dict) and 'reading_interval' in sensor_type:
            self.reading_interval = sensor_type['reading_interval']
        else:
            self.reading_interval = reading_interval

    def diccionario(self):
        return self.__dict__

    def __str__(self):
        return f"{self.name} (ID: {self.id}, Tank: {self.tankId})"
