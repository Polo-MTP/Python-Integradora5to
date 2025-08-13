class UserConfig:
    def __init__(self, code=None, config_type=None, config_value=None, config_day=None,
                  **kwargs):
        self.code = code  # Ej: light/on, feed, etc.
        self.config_type = config_type  # Ej: "time", "event"
        self.config_value = config_value  # Hora ISO string: "2025-07-27T17:30:00"
        self.config_day = config_day

        # Compatibilidad nombres

       
    def diccionario(self):
        return self.__dict__

    def __str__(self):
        return f"{self.code} (ID: {self.id}, Tank: {self.tankId}, Tipo: {self.config_type})"
