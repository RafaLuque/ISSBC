from PyQt5.QtWidgets import *
from PyQt5.QtCore import *

class ConstructorDinamico:
    """
    Construye widgets dinámicamente basados en la configuración externa.
    Esta es la clave de la parametrización de las vistas.
    """
    
    def __init__(self, config):
        self.config = config
        self.campos = {}  # Diccionario para almacenar referencias a los widgets
    
    def crear_panel_sintomas(self, parent):
        """
        Crea dinámicamente los campos de entrada según la configuración
        """
        panel = QGroupBox("Síntomas y observables", parent)
        layout = QVBoxLayout(panel)
        
        self.campos = {}  # Reiniciar campos
        
        # Obtener configuración de síntomas
        sintomas_config = self.config.get('sintomas', {})
        
        # Crear categorías de síntomas
        categorias = sintomas_config.get('categorias', [])
        for categoria in categorias:
            # Título de la categoría
            label = QLabel(f"<b>{categoria['nombre']}</b>")
            label.setTextFormat(Qt.RichText)
            layout.addWidget(label)
            
            # Widget según tipo
            if categoria['tipo'] == 'seleccion_unica':
                combo = QComboBox()
                combo.addItems(categoria.get('opciones', []))
                combo.setCurrentText(categoria.get('por_defecto', ''))
                self.campos[categoria['nombre']] = combo
                layout.addWidget(combo)
            
            elif categoria['tipo'] == 'seleccion_multiple':
                grupo = QGroupBox()
                grupo_layout = QVBoxLayout(grupo)
                opciones = []
                for opcion in categoria.get('opciones', []):
                    check = QCheckBox(opcion)
                    check.setChecked(opcion == categoria.get('por_defecto', ''))
                    opciones.append(check)
                    grupo_layout.addWidget(check)
                self.campos[categoria['nombre']] = opciones
                layout.addWidget(grupo)
            
            layout.addSpacing(10)
        
        # Crear observables
        observables = sintomas_config.get('observables', [])
        for observable in observables:
            label = QLabel(f"<b>{observable['nombre']}</b>")
            label.setTextFormat(Qt.RichText)
            layout.addWidget(label)
            
            if observable['tipo'] == 'rango':
                # SpinBox para rangos numéricos
                spin = QSpinBox()
                spin.setRange(observable.get('min', 0), observable.get('max', 9999))
                spin.setValue(observable.get('por_defecto', 0))
                spin.setSuffix(" €" if "Presupuesto" in observable['nombre'] else "")
                self.campos[observable['nombre']] = spin
                layout.addWidget(spin)
                
                # Añadir slider para mejor UX
                slider = QSlider(Qt.Horizontal)
                slider.setRange(observable.get('min', 0), observable.get('max', 9999))
                slider.setValue(observable.get('por_defecto', 0))
                slider.valueChanged.connect(spin.setValue)
                spin.valueChanged.connect(slider.setValue)
                layout.addWidget(slider)
            
            elif observable['tipo'] == 'booleano':
                check = QCheckBox()
                check.setChecked(observable.get('por_defecto', False))
                self.campos[observable['nombre']] = check
                layout.addWidget(check)
            
            elif observable['tipo'] == 'texto':
                texto = QLineEdit()
                texto.setPlaceholderText(observable.get('placeholder', ''))
                self.campos[observable['nombre']] = texto
                layout.addWidget(texto)
            
            layout.addSpacing(10)
        
        # Añadir stretch al final
        layout.addStretch()
        
        return panel
    
    def obtener_datos_ingresados(self):
        """
        Recoge los valores actuales de todos los campos
        """
        datos = {}
        for nombre, widget in self.campos.items():
            if isinstance(widget, QComboBox):
                datos[nombre] = widget.currentText()
            elif isinstance(widget, QSpinBox):
                datos[nombre] = widget.value()
            elif isinstance(widget, QCheckBox):
                datos[nombre] = widget.isChecked()
            elif isinstance(widget, QLineEdit):
                datos[nombre] = widget.text()
            elif isinstance(widget, list):  # Lista de checkboxes
                valores = []
                for check in widget:
                    if check.isChecked():
                        valores.append(check.text())
                datos[nombre] = valores
        
        return datos
    
    def crear_selector_modo(self, parent):
        """
        Crea el selector de modo (Local/Web) según configuración
        """
        grupo = QGroupBox("Modo de conocimiento", parent)
        layout = QHBoxLayout(grupo)
        
        modos = self.config.get('modos_conocimiento', ["Local", "Web"])
        modo_defecto = self.config.get('modo_por_defecto', modos[0] if modos else "Local")
        
        self.modo_group = QButtonGroup(parent)
        for modo in modos:
            radio = QRadioButton(modo)
            radio.setChecked(modo == modo_defecto)
            self.modo_group.addButton(radio)
            layout.addWidget(radio)
        
        layout.addStretch()
        return grupo
    
    def obtener_modo_seleccionado(self):
        """Obtiene el modo seleccionado actualmente"""
        if hasattr(self, 'modo_group'):
            button = self.modo_group.checkedButton()
            return button.text() if button else self.config.get('modo_por_defecto', "Local")
        return self.config.get('modo_por_defecto', "Local")