import os

def obtener_ruta_base():
    """
    Obtiene la ruta base del proyecto (donde está main.py)
    """
    # __file__ es la ruta de este archivo
    # subimos un nivel para llegar a la raíz del proyecto
    return os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

def obtener_ruta_relativa(ruta_relativa):
    """
    Convierte una ruta relativa al proyecto en ruta absoluta
    Ejemplo: obtener_ruta_relativa("pdfs_utilizados/guia.pdf")
    """
    base = obtener_ruta_base()
    return os.path.join(base, ruta_relativa)

def obtener_ruta_config(nombre_archivo):
    """Obtiene ruta a un archivo dentro de config/"""
    return obtener_ruta_relativa(f"config/{nombre_archivo}")

def obtener_ruta_pdf(nombre_archivo):
    """Obtiene ruta a un archivo dentro de pdfs_utilizados/"""
    return obtener_ruta_relativa(f"pdfs_utilizados/{nombre_archivo}")

def obtener_ruta_reglas():
    """Obtiene ruta al archivo de reglas de CommonKADS"""
    return obtener_ruta_relativa("config/reglas_commonkads.xml")