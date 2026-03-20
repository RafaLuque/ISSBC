# -*- coding: utf-8 -*-
import os

def guardar_archivo(nombre_archivo, contenido):
    """Guarda el contenido en un archivo."""
    try:
        with open(nombre_archivo, 'w', encoding='utf-8') as f:
            f.write(contenido)
        return True
    except Exception as e:
        print(f"Error al guardar: {e}")
        return False

def abrir_archivo(nombre_archivo):
    """Lee el contenido de un archivo."""
    try:
        with open(nombre_archivo, 'r', encoding='utf-8') as f:
            return f.read()
    except Exception as e:
        print(f"Error al abrir: {e}")
        return None

def listar_archivos(directorio):
    """Lista los archivos de un directorio."""
    try:
        archivos = [f for f in os.listdir(directorio) 
                   if os.path.isfile(os.path.join(directorio, f))]
        return archivos
    except Exception as e:
        print(f"Error al listar: {e}")
        return []