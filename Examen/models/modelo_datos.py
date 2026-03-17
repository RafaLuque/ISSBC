from PyQt5.QtCore import QObject, pyqtSignal

class ModeloDiagnostico(QObject):
    """
    Modelo MVC: Mantiene el estado y datos de la aplicación.
    Notifica cambios a las vistas mediante señales.
    """
    
    # Señales para notificar cambios
    datos_actualizados = pyqtSignal()
    pdfs_actualizados = pyqtSignal()
    hipotesis_actualizadas = pyqtSignal()
    diagnostico_actualizado = pyqtSignal()
    
    def __init__(self):
        super().__init__()
        self._sintomas = {}           # Datos ingresados por usuario
        self._pdfs = []                # Lista de rutas de PDFs [{'ruta': '', 'nombre': '', 'tamaño': 0}]
        self._hipotesis = []            # Lista de hipótesis [{'nombre': '', 'probabilidad': 0, 'estado': ''}]
        self._diagnostico_final = ""    # Diagnóstico seleccionado
        self._justificacion = ""        # Justificación del diagnóstico
        self._fuentes_web = []           # Fuentes consultadas [{'titulo': '', 'url': '', 'fragmento': '', 'fecha': ''}]
        self._modo_actual = "Local (solo PDFs)"  # Modo de conocimiento
    
    # Propiedades con getters y setters para encapsulación
    @property
    def sintomas(self):
        return self._sintomas.copy()
    
    @sintomas.setter
    def sintomas(self, valor):
        self._sintomas = valor.copy() if valor else {}
        self.datos_actualizados.emit()
    
    @property
    def pdfs(self):
        return self._pdfs.copy()
    
    def agregar_pdf(self, ruta, nombre, tamaño):
       """Añade un PDF a la lista"""
       self._pdfs.append({
           'ruta': ruta,
           'nombre': nombre,
           'tamaño': tamaño,
           'fecha': ''  # Se podría añadir fecha
           })
       self.pdfs_actualizados.emit()  # Esta señal es importante
    
    def eliminar_pdf(self, indice):
        """Elimina un PDF por índice"""
        if 0 <= indice < len(self._pdfs):
            del self._pdfs[indice]
            self.pdfs_actualizados.emit()
    
    def vaciar_pdfs(self):
        """Elimina todos los PDFs"""
        self._pdfs.clear()
        self.pdfs_actualizados.emit()
    
    @property
    def hipotesis(self):
        return self._hipotesis.copy()
    
    @hipotesis.setter
    def hipotesis(self, valor):
        self._hipotesis = valor.copy() if valor else []
        self.hipotesis_actualizadas.emit()
    
    @property
    def diagnostico_final(self):
        return self._diagnostico_final
    
    @diagnostico_final.setter
    def diagnostico_final(self, valor):
        self._diagnostico_final = valor
        self.diagnostico_actualizado.emit()
    
    @property
    def justificacion(self):
        return self._justificacion
    
    @justificacion.setter
    def justificacion(self, valor):
        self._justificacion = valor
        self.datos_actualizados.emit()
    
    @property
    def fuentes_web(self):
        return self._fuentes_web.copy()
    
    def agregar_fuente_web(self, titulo, url, fragmento, fecha):
        """Añade una fuente web consultada"""
        self._fuentes_web.append({
            'titulo': titulo,
            'url': url,
            'fragmento': fragmento,
            'fecha': fecha
        })
        self.datos_actualizados.emit()
    
    @property
    def modo_actual(self):
        return self._modo_actual
    
    @modo_actual.setter
    def modo_actual(self, valor):
        self._modo_actual = valor
        self.datos_actualizados.emit()