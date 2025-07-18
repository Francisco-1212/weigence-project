# lector_peso.py
import random

def iniciar_sensor():
    # Esta función inicializará el sensor
    pass

def leer_peso():
    """
    Lee el peso desde el sensor HX711 y lo devuelve como float.
    """
    peso = 0.0  # simulado por ahora
    return peso

if __name__ == "__main__":
    print("Peso actual:", leer_peso(), "g")

def leer_peso():
    return round(random.uniform(500.0, 1000.0), 2) 