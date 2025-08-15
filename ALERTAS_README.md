# 🚨 Sistema de Alertas - Documentación

## 📋 Descripción

El sistema de alertas está integrado automáticamente con la captura de datos de sensores. Cuando un sensor envía un valor que está fuera del rango definido, se genera automáticamente una alerta que se guarda localmente y se sincroniza con MongoDB.

## 🏗️ Arquitectura

```
Arduino → Sensor Data → Verificación Automática → Alerta (si fuera de rango)
    ↓                                                   ↓
    Data Online/Local                          Alertas Online
    ↓                                                   ↓
    MongoDB (dataSensores)                     MongoDB (alertas)
```

## 📊 Configuración de Rangos

Los rangos de alertas se configuran en el archivo `Jsons_DATA/alertasMapa.json`:

```json
{
  "phh/1": {
    "min": 5.0,
    "max": 9.0
  },
  "niv/1": {
    "min": 200.0,
    "max": 2000.0
  },
  "tmp/1": {
    "min": 17.0,
    "max": 26.0
  },
  "tbz/1": {
    "min": 300.0,
    "max": 900.0
  },
  "tds/1": {
    "min": null,
    "max": null
  }
}
```

### Reglas de Configuración:
- **min/max = null**: No hay restricción en ese extremo
- **min/max = número**: Valor límite para generar alerta
- Si ambos son null, el sensor nunca generará alertas

## 🔄 Flujo Automático

### 1. Captura de Datos
Cuando llegan datos del Arduino (formato: `sensor_code:valor`):

```python
# Ejemplo: "tmp/1:15.2"
sensor_code = "tmp/1"
valor = 15.2
```

### 2. Verificación Automática
La función `guardar_dato()` automáticamente:
1. Guarda los datos normales (online + historial)
2. Carga el mapa de alertas
3. Verifica si el valor está fuera de rango
4. Si está fuera de rango → Genera alerta automáticamente

### 3. Generación de Alerta
Si el valor está fuera de rango:

```python
# Se crea automáticamente una alerta con:
{
    "id": 1,
    "tankId": 2,
    "deviceId": 6,
    "code": "tmp/1",
    "value": 15.2,
    "message": "Temperatura muy baja: 15.2 (mínimo: 17.0)",
    "date": "2025-08-15T06:37:30.123456",
    "synced": false
}
```

### 4. Sincronización con MongoDB
- Las alertas se sincronizan cada **30 segundos**
- Van a la colección **"alertas"** en MongoDB
- Después de sincronizar, el archivo local se limpia
- El campo `synced` se usa para control local

## 📁 Archivos Involucrados

### Configuración
- `Jsons_DATA/alertasMapa.json` - Rangos de alertas por sensor

### Datos
- `Jsons_DATA/data_sesnsoresalerta_online.json` - Alertas pendientes de sync
- `Jsons_DATA/data_sensores_online.json` - Datos normales pendientes
- `Jsons_DATA/data_sensores_local.json` - Historial local permanente

### Código
- `Clases/alerta.py` - Clase modelo para alertas
- `Clases/arduino.py` - Lógica de captura y verificación automática
- `Mongo/sync.py` - Sincronización con MongoDB (datos + alertas)
- `Mongo/mongo.py` - Cliente MongoDB

## 🧪 Pruebas

### Script de Prueba
```bash
python test_alertas.py
```

Este script:
1. Simula datos del Arduino
2. Prueba valores normales y fuera de rango
3. Muestra las alertas generadas
4. Predice comportamiento esperado

### Casos de Prueba Incluidos
- ✅ Valores normales (NO generan alertas)
- 🚨 Valores por debajo del mínimo (SÍ generan alertas)
- 🚨 Valores por encima del máximo (SÍ generan alertas)
- ➰ Sensores sin límites (TDS - nunca generan alertas)

## 🚀 Uso en Producción

### Inicio Normal
```bash
python main.py
```

El sistema se ejecuta automáticamente:
1. ✅ Lee datos del puerto serial (COM6)
2. 🔍 Verifica alertas automáticamente
3. 💾 Guarda datos + alertas localmente
4. 🔄 Sincroniza con MongoDB cada 30 segundos
5. 🧹 Limpia archivos después de sincronizar

### Configuración de Nuevos Sensores

Para agregar un nuevo sensor:

1. **Agregar al mapa de dispositivos** (se hace automáticamente desde la API)
2. **Configurar rangos de alerta** en `alertasMapa.json`:
```json
{
  "nuevo_sensor/1": {
    "min": 10.0,
    "max": 50.0
  }
}
```

### Sin Configuración de Alertas
Si un sensor no está en `alertasMapa.json`:
- ✅ Los datos se capturan normalmente
- ❌ NO se generan alertas (comportamiento seguro)

## 🗄️ MongoDB

### Colecciones
- **dataSensores**: Datos normales de sensores
- **alertas**: Alertas generadas automáticamente

### Estructura de Alerta en MongoDB
```json
{
  "_id": ObjectId("..."),
  "id": 1,
  "tankId": 2,
  "deviceId": 6,
  "code": "tmp/1",
  "value": 15.2,
  "message": "Temperatura muy baja: 15.2 (mínimo: 17.0)",
  "date": "2025-08-15T06:37:30.123456"
}
```

## 🔧 Configuración Avanzada

### Variables de Entorno (.env)
```
UUID=tu_uuid_aqui
MONGO_URI=tu_conexion_mongodb
DB_DATABASE=nombre_base_datos
```

### Personalización de Mensajes
En `Clases/arduino.py`, función `generar_mensaje_alerta()`:

```python
nombres_sensores = {
    "tmp": "Temperatura",
    "phh": "pH", 
    "niv": "Nivel de agua",
    "tbz": "Turbidez",
    "tds": "TDS"
}
```

### Intervalos de Sincronización
En `Mongo/sync.py`, línea ~228:
```python
time.sleep(30)  # Cambiar por el intervalo deseado en segundos
```

## 🐛 Diagnóstico

### Logs del Sistema
El sistema muestra logs detallados:
- 📨 Datos recibidos del Arduino
- ✅ Datos guardados correctamente
- 🚨 Alertas generadas
- 🔄 Estados de sincronización
- ❌ Errores y advertencias

### Verificación Manual
```python
# Ver alertas pendientes
import json
with open("Jsons_DATA/data_sesnsoresalerta_online.json", "r") as f:
    alertas = json.load(f)
print(f"Alertas pendientes: {len(alertas)}")
```

### Problemas Comunes
1. **No se generan alertas**: Verificar `alertasMapa.json`
2. **No se sincronizan**: Verificar conexión MongoDB
3. **Valores no numéricos**: Se ignoran automáticamente
4. **Sensores desconocidos**: Se registran pero no generan alertas

## 📈 Monitoreo

### Estadísticas en Tiempo Real
El sistema muestra cada 30 segundos:
- 📊 Datos sincronizados vs pendientes
- 🚨 Alertas procesadas
- 🔄 Estado de conexiones
- 🗄️ Resultados de MongoDB

### Dashboard Recomendado
Para monitoreo en producción, considera:
- Grafana + MongoDB para visualización
- Alertas por email/SMS cuando se generen alertas críticas
- Logs centralizados (ELK Stack)

---
**Nota**: Este sistema está diseñado para funcionar 24/7 de manera autónoma, generando alertas automáticamente sin intervención manual.
