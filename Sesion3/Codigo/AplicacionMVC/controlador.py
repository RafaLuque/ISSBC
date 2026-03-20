# -*- coding: utf-8 -*-

import modelo as mod

def guardar_archivo(nombre_archivo, contenido):
    """Guarda el archivo a través del modelo."""
    return mod.guardar_archivo(nombre_archivo, contenido)

def abrir_archivo(nombre_archivo):
    """Abre el archivo a través del modelo."""
    return mod.abrir_archivo(nombre_archivo)

def listar_archivos(directorio):
    """Lista los archivos del directorio."""
    return mod.listar_archivos(directorio)
