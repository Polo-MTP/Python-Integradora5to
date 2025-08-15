#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Script de prueba para verificar el sistema de alertas
Este script simula datos del Arduino para probar la generación automática de alertas
"""

import sys
import os

# Agregar el path para importar las clases
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from Clases.arduino import guardar_dato
import json

def leer_alertas_generadas():
    """Lee y muestra las alertas generadas"""
    archivo_alertas = "Jsons_DATA/data_sesnsoresalerta_online.json"
    try:
        with open(archivo_alertas, "r", encoding="utf-8") as f:
            alertas = json.load(f)
        
        if alertas:
            print(f"\n🚨 === ALERTAS GENERADAS ({len(alertas)}) ===")
            for alerta in alertas:
                print(f"ID: {alerta['id']}")
                print(f"Sensor: {alerta['code']}")
                print(f"Valor: {alerta['value']}")
                print(f"Mensaje: {alerta['message']}")
                print(f"Fecha: {alerta['date']}")
                print(f"Sincronizado: {alerta['synced']}")
                print("-" * 50)
        else:
            print("\n✅ No hay alertas generadas")
            
    except FileNotFoundError:
        print("\n📁 No se encontró archivo de alertas")
    except Exception as e:
        print(f"\n❌ Error leyendo alertas: {e}")

def test_alertas():
    """Función principal de prueba"""
    print("🧪 === PRUEBA DEL SISTEMA DE ALERTAS ===")
    print("Este script simula datos del Arduino para probar la generación de alertas")
    print("Basándose en los rangos definidos en alertasMapa.json:")
    
    # Mostrar rangos configurados
    try:
        with open("Jsons_DATA/alertasMapa.json", "r", encoding="utf-8") as f:
            rangos = json.load(f)
        
        print("\n📊 RANGOS CONFIGURADOS:")
        for sensor, rango in rangos.items():
            print(f"  {sensor}: min={rango['min']}, max={rango['max']}")
    except Exception as e:
        print(f"❌ Error leyendo rangos: {e}")
        return
    
    print("\n" + "="*60)
    
    # Limpiar archivo de alertas previo
    try:
        with open("Jsons_DATA/data_sesnsoresalerta_online.json", "w", encoding="utf-8") as f:
            json.dump([], f, indent=4, ensure_ascii=False)
        print("🗑️ Archivo de alertas limpiado para la prueba")
    except:
        pass
    
    # Casos de prueba
    casos_prueba = [
        # Valores normales (NO deben generar alertas)
        ("tmp/1", 20.5, "Temperatura normal"),
        ("phh/1", 7.0, "pH normal"),
        ("niv/1", 1500.0, "Nivel normal"),
        
        # Valores fuera de rango (SÍ deben generar alertas)
        ("tmp/1", 10.0, "Temperatura MUY BAJA (min: 17.0)"),
        ("tmp/1", 30.0, "Temperatura MUY ALTA (max: 26.0)"),
        ("phh/1", 3.0, "pH MUY BAJO (min: 5.0)"),
        ("phh/1", 12.0, "pH MUY ALTO (max: 9.0)"),
        ("niv/1", 100.0, "Nivel MUY BAJO (min: 200.0)"),
        ("niv/1", 3000.0, "Nivel MUY ALTO (max: 2000.0)"),
        
        # TDS no tiene límites (no debe generar alertas)
        ("tds/1", 50.0, "TDS sin límites"),
        ("tds/1", 5000.0, "TDS sin límites alto"),
    ]
    
    print("\n🧪 EJECUTANDO CASOS DE PRUEBA:")
    print("="*60)
    
    alertas_esperadas = 0
    
    for sensor_code, valor, descripcion in casos_prueba:
        print(f"\n📊 Probando: {descripcion}")
        print(f"   Sensor: {sensor_code}, Valor: {valor}")
        
        # Predecir si debe generar alerta
        debe_generar_alerta = False
        if sensor_code in rangos:
            rango = rangos[sensor_code]
            if (rango['min'] is not None and valor < rango['min']) or \
               (rango['max'] is not None and valor > rango['max']):
                debe_generar_alerta = True
                alertas_esperadas += 1
        
        print(f"   Expectativa: {'🚨 DEBE generar alerta' if debe_generar_alerta else '✅ NO debe generar alerta'}")
        
        # Ejecutar la función
        guardar_dato(sensor_code, valor)
    
    print("\n" + "="*60)
    print("🧪 PRUEBA COMPLETADA")
    print(f"📈 Alertas esperadas: {alertas_esperadas}")
    
    # Mostrar alertas generadas
    leer_alertas_generadas()
    
    print("\n🔍 Para probar la sincronización:")
    print("1. Ejecuta el script principal (main.py)")
    print("2. Las alertas se sincronizarán automáticamente con MongoDB cada 30 segundos")
    print("3. Las alertas se guardarán en la colección 'alertas'")

if __name__ == "__main__":
    test_alertas()
