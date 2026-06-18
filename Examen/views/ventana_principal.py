from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *

from views.componentes_dinamicos import ConstructorDinamico
from views.ventana_hipotesis import VentanaHipotesis
from views.ventana_diagnostico import VentanaDiagnostico
from views.ventana_justificacion import VentanaJustificacion
from views.ventana_pdfs import VentanaPDFs
from views.ventana_fuentes import VentanaFuentes

class VentanaPrincipal(QMainWindow):
    """
    Vista principal - Asesor de Configuración de PC
    """
    
    def __init__(self, controlador, config):
        super().__init__()
        self.controlador = controlador
        self.config = config
        self.constructor = ConstructorDinamico(config)
        
        self.controlador.set_vista_principal(self) 
        
        self.ventana_hipotesis = None
    
        self.ventana_diagnostico = None
        self.ventana_justificacion = None
        self.ventana_pdfs = None
        self.ventana_fuentes = None
        self.btn_fuentes_web = None  # Inicializar como None
        
        self.contador_ventanas = 0
        
        self.init_ui()
        
        # Conectar señal de PDFs para actualizar el label de estado
        self.controlador.modelo.pdfs_actualizados.connect(self._actualizar_label_pdfs)
        
        # Actualizar label con los PDFs ya cargados desde el caché
        self._actualizar_label_pdfs()
        
        # Después de init_ui, el botón ya existe, ahora podemos actualizar su estado
        self._cambiar_opciones_modelo()
        self._actualizar_info_modo()
    
    def init_ui(self):
        """Inicializa la interfaz - Enfoque en asesoramiento PC"""
        self.setWindowTitle("Asesor Experto en Configuración de PC")
        self.setGeometry(100, 100, 1000, 700)
        
        # Widget central con scroll
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.NoFrame)
        self.setCentralWidget(scroll)
        
        central_widget = QWidget()
        scroll.setWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        main_layout.setSpacing(20)
        
        # Cabecera con logo/icono
        cabecera = self._crear_cabecera()
        main_layout.addWidget(cabecera)
        
        # Panel de perfil del usuario (quién es el cliente)
        panel_perfil = self._crear_panel_perfil_usuario()
        main_layout.addWidget(panel_perfil)
        
        # Panel de componentes actuales (hardware existente)
        panel_componentes_actuales = self._crear_panel_componentes_actuales()
        main_layout.addWidget(panel_componentes_actuales)
        
        # Panel de necesidades y uso
        panel_necesidades = self._crear_panel_necesidades()
        main_layout.addWidget(panel_necesidades)
        
        # Panel de modos de conocimiento
        panel_modos = self._crear_panel_modos_conocimiento()
        main_layout.addWidget(panel_modos)
        
        # Panel de acciones
        panel_acciones = self._crear_panel_acciones()
        main_layout.addWidget(panel_acciones)
        
        # Barra de estado
        self._crear_barra_estado()
    
    def _crear_cabecera(self):
        """Cabecera con título y descripción del servicio"""
        widget = QWidget()
        layout = QHBoxLayout(widget)
        
        # Icono (simulado)
        icono = QLabel("🖥️")
        icono.setStyleSheet("font-size: 48px;")
        layout.addWidget(icono)
        
        # Texto
        texto = QLabel()
        texto.setText(
            "<h1>Asesor Experto en Configuración de PC</h1>"
            "<p style='color: #666;'>Analizamos tu hardware actual y necesidades "
            "para recomendar la configuración óptima</p>"
        )
        layout.addWidget(texto)
        
        return widget
    
    def _crear_panel_perfil_usuario(self):
        """Panel con información del usuario/cliente"""
        panel = QGroupBox("👤 Perfil del usuario")
        panel.setStyleSheet("""
            QGroupBox { 
                font-size: 14px; 
                font-weight: bold;
                margin-top: 8px;
                padding-top: 8px;
            }
        """)
        
        # Crear layout para el panel
        layout = QGridLayout(panel)  # <-- ESTA LÍNEA FALTABA
        
        # Presupuesto disponible
        layout.addWidget(QLabel("Presupuesto disponible (€):"), 0, 0)
        self.spin_presupuesto = QSpinBox()
        self.spin_presupuesto.setRange(300, 10000)
        self.spin_presupuesto.setValue(1000)
        self.spin_presupuesto.setSingleStep(100)
        self.spin_presupuesto.setSuffix(" €")
        layout.addWidget(self.spin_presupuesto, 0, 1)
        
        # Prioridad
        layout.addWidget(QLabel("Prioridad principal:"), 1, 0)
        self.combo_prioridad = QComboBox()
        self.combo_prioridad.addItems([
            "Rendimiento máximo",
            "Mejor relación calidad-precio",
            "Eficiencia energética",
            "Presupuesto ajustado",
            "Future-proof (duradero)"
        ])
        layout.addWidget(self.combo_prioridad, 1, 1)
        
        return panel
    
    def _crear_panel_componentes_actuales(self):
        """Panel para especificar los componentes que ya tiene el cliente"""
        panel = QGroupBox("🖱️ Componentes actuales (los que ya posees)")
        panel.setCheckable(True)
        panel.setChecked(False)
        layout = QGridLayout(panel)  # <-- ESTO DEBE ESTAR
        
        fila = 0
        self.componentes_actuales = {}
        
        componentes = [
            ("CPU", "Ej: Intel i5-11400"),
            ("GPU", "Ej: NVIDIA GTX 1660"),
            ("RAM", "Ej: 16GB DDR4"),
            ("Placa base", "Ej: B560M"),
            ("Fuente", "Ej: 650W 80+ Bronze"),
            ("Almacenamiento", "Ej: SSD 500GB"),
            ("Caja", "Ej: ATX")
        ]
        
        for componente, placeholder in componentes:
            layout.addWidget(QLabel(componente + ":"), fila, 0)
            
            # Checkbox para indicar si lo tiene
            check = QCheckBox()
            check.setChecked(False)
            layout.addWidget(check, fila, 1)
            
            # Campo de texto para especificar modelo
            texto = QLineEdit()
            texto.setPlaceholderText(placeholder)
            texto.setEnabled(False)
            check.toggled.connect(texto.setEnabled)
            layout.addWidget(texto, fila, 2)
            
            self.componentes_actuales[componente] = {
                'check': check,
                'texto': texto
            }
            
            fila += 1
        
        return panel
    
    def _crear_panel_necesidades(self):
        """Panel con el uso previsto del PC"""
        panel = QGroupBox("🎮 Uso principal del equipo")
        layout = QVBoxLayout(panel)
        
        # Usos principales con iconos
        usos_layout = QHBoxLayout()
        
        self.uso_seleccionado = None
        self.botones_uso = []
        
        usos = [
            ("🎮 Gaming", "Gaming"),
            ("🎬 Edición vídeo", "Edición vídeo"),
            ("💻 Programación", "Programación"),
            ("🎨 Diseño 3D", "Diseño 3D"),
            ("📊 Ofimática", "Ofimática"),
            ("📡 Streaming", "Streaming")
        ]
        
        for texto, valor in usos:
            btn = QPushButton(texto)
            btn.setCheckable(True)
            btn.setStyleSheet("QPushButton { padding: 8px; border: 2px solid #ddd; border-radius: 5px; } QPushButton:checked { background: #3498db; color: white; border-color: #2980b9; }")
            btn.clicked.connect(lambda checked, v=valor: self._seleccionar_uso(v))
            usos_layout.addWidget(btn)
            self.botones_uso.append((btn, valor))
        
        layout.addLayout(usos_layout)
        
        # Detalles adicionales según uso
        self.detalles_uso = QTextEdit()
        self.detalles_uso.setPlaceholderText("Detalles adicionales... (ej: juegos específicos, software, resolución deseada)")
        self.detalles_uso.setMaximumHeight(80)
        layout.addWidget(self.detalles_uso)
        
        return panel
    def _seleccionar_uso(self, valor):
        """Maneja la selección del uso principal"""
        for btn, v in self.botones_uso:
            btn.setChecked(v == valor)
        self.uso_seleccionado = valor
    

    
    def _crear_panel_modos_conocimiento(self):
        """
        Panel para seleccionar el modo de conocimiento según el examen:
        - Modelo: qué modelo de conocimiento usar (CommonKADS/LLM)
        - Modo Local: solo PDFs locales
        - Modo Web: PDFs + Internet
        """
        panel = QGroupBox("🧠 Configuración del conocimiento")
        panel.setStyleSheet("QGroupBox { font-size: 14px; font-weight: bold; border: 2px solid #9b59b6; margin-top: 10px; padding-top: 10px; } QGroupBox::title { subcontrol-origin: margin; left: 10px; padding: 0 5px 0 5px; }")
        
        layout = QVBoxLayout(panel)
        layout.setSpacing(15)
        layout.setContentsMargins(10, 10, 10, 10)
        
        # ============================================
        # PARTE 1: MODELO DE CONOCIMIENTO A UTILIZAR
        # ============================================
        grupo_modelo = QGroupBox("1. Modelo de conocimiento")
        grupo_modelo.setStyleSheet("QGroupBox { font-weight: bold; margin-top: 8px; padding-top: 8px; } QGroupBox::title { subcontrol-origin: margin; left: 10px; padding: 0 5px 0 5px; }")
        
        modelo_layout = QVBoxLayout(grupo_modelo)
        modelo_layout.setSpacing(10)
        modelo_layout.setContentsMargins(10, 15, 10, 10)
        
        # Explicación
        info_modelo = QLabel("<b>Selecciona el enfoque para el razonamiento:</b><br><span style='color: #666; font-size: 11px;'>Comparativa entre metodología estructurada (CommonKADS) y modelos de lenguaje (LLM)</span>")
        info_modelo.setWordWrap(True)
        info_modelo.setStyleSheet("margin-bottom: 8px;")
        modelo_layout.addWidget(info_modelo)
        
        # Radio buttons para selección de modelo
        radios_widget = QWidget()
        radios_layout = QHBoxLayout(radios_widget)
        radios_layout.setContentsMargins(0, 5, 0, 5)
        radios_layout.setSpacing(20)
        
        self.radio_commonkads = QRadioButton("📊 CommonKADS (basado en reglas)")
        self.radio_commonkads.setChecked(True)
        radios_layout.addWidget(self.radio_commonkads)
        
        self.radio_llm = QRadioButton("🤖 LLM (Modelo de Lenguaje)")
        radios_layout.addWidget(self.radio_llm)
        
        radios_layout.addStretch()
        modelo_layout.addWidget(radios_widget)
        
        # Opciones específicas para LLM
        self.llm_options = QWidget()
        llm_layout = QHBoxLayout(self.llm_options)
        llm_layout.setContentsMargins(20, 10, 5, 5)
        llm_layout.setSpacing(10)
        
        llm_layout.addWidget(QLabel("Modelo Ollama:"))
        self.combo_llm = QComboBox()
        
        # Obtener los modelos instalados de verdad o bien una lista default si está capado
        modelos_reales = self.controlador.servicio_ollama.obtener_modelos_disponibles()
        self.combo_llm.addItems(modelos_reales)
        
        # Tratar de autoseleccionar un modelo eficiente de entre los que se encuentren (ej 7b o 8b)
        for i, m in enumerate(modelos_reales):
            m_low = m.lower()
            if ('8b' in m_low or '7b' in m_low) and '30b' not in m_low:
                self.combo_llm.setCurrentIndex(i)
                break
                
        self.combo_llm.setMinimumWidth(150)
        llm_layout.addWidget(self.combo_llm)

        # Cambiar el modelo en Ollama cada vez que el usuario cambia la selección del combo
        self.combo_llm.currentIndexChanged.connect(self._al_cambiar_modelo_llm)

        btn_verificar = QPushButton("🔌 Verificar Ollama")
        btn_verificar.clicked.connect(self.verificar_ollama)
        llm_layout.addWidget(btn_verificar)
        
        llm_layout.addStretch()
        modelo_layout.addWidget(self.llm_options)
        
        # Conectar señal para cambiar visibilidad
        self.radio_llm.toggled.connect(self._cambiar_opciones_modelo)
        self.radio_commonkads.toggled.connect(self._cambiar_opciones_modelo)
        
        layout.addWidget(grupo_modelo)
        
        # Añadir separador visual
        line = QFrame()
        line.setFrameShape(QFrame.HLine)
        line.setFrameShadow(QFrame.Sunken)
        line.setStyleSheet("background-color: #ccc; max-height: 1px; margin: 5px 0;")
        layout.addWidget(line)
        
        # ============================================
        # PARTE 2: MODO DE CONOCIMIENTO (LOCAL/WEB)
        # ============================================
        grupo_modo = QGroupBox("2. Modo de conocimiento")
        grupo_modo.setStyleSheet("QGroupBox { font-weight: bold; margin-top: 8px; padding-top: 8px; } QGroupBox::title { subcontrol-origin: margin; left: 10px; padding: 0 5px 0 5px; }")
        
        modo_layout = QVBoxLayout(grupo_modo)
        modo_layout.setSpacing(10)
        modo_layout.setContentsMargins(10, 15, 10, 10)
        
        # Explicación
        info_modo = QLabel("<b>Selecciona las fuentes de información:</b><br><span style='color: #666; font-size: 11px;'>Local: solo PDFs del usuario | Web: PDFs + búsqueda en internet</span>")
        info_modo.setWordWrap(True)
        info_modo.setStyleSheet("margin-bottom: 8px;")
        modo_layout.addWidget(info_modo)
        
        # Radio buttons para modo
        modos_widget = QWidget()
        modos_layout = QHBoxLayout(modos_widget)
        modos_layout.setContentsMargins(0, 5, 0, 5)
        modos_layout.setSpacing(20)
        
        self.radio_local = QRadioButton("📁 Modo Local (solo PDFs)")
        self.radio_local.setChecked(True)
        modos_layout.addWidget(self.radio_local)
        
        self.radio_web = QRadioButton("🌐 Modo Web (PDFs + Internet)")
        modos_layout.addWidget(self.radio_web)
        
        modos_layout.addStretch()
        modo_layout.addWidget(modos_widget)
        
        # Información adicional según modo
        self.info_modo = QLabel()
        self.info_modo.setStyleSheet("color: #666; font-size: 11px; padding: 8px; background: #f0f0f0; border-radius: 3px; margin-top: 5px; margin-bottom: 5px;")
        self.info_modo.setWordWrap(True)
        modo_layout.addWidget(self.info_modo)
        
        # Conectar señal para actualizar info
        self.radio_local.toggled.connect(self._actualizar_info_modo)
        self.radio_web.toggled.connect(self._actualizar_info_modo)
        
        layout.addWidget(grupo_modo)
        
        # Añadir separador visual
        line2 = QFrame()
        line2.setFrameShape(QFrame.HLine)
        line2.setFrameShadow(QFrame.Sunken)
        line2.setStyleSheet("background-color: #ccc; max-height: 1px; margin: 5px 0;")
        layout.addWidget(line2)
        
        # ============================================
        # PARTE 3: ESTADO ACTUAL
        # ============================================
        grupo_estado = QGroupBox("Estado actual")
        grupo_estado.setStyleSheet("QGroupBox { font-weight: bold; margin-top: 8px; padding-top: 8px; } QGroupBox::title { subcontrol-origin: margin; left: 10px; padding: 0 5px 0 5px; }")
        
        estado_layout = QHBoxLayout(grupo_estado)
        estado_layout.setContentsMargins(10, 15, 10, 10)
        estado_layout.setSpacing(10)
        
        self.label_pdfs_cargados = QLabel("📄 PDFs cargados: 0")
        self.label_pdfs_cargados.setStyleSheet("font-weight: normal;")
        estado_layout.addWidget(self.label_pdfs_cargados)
        
        estado_layout.addStretch()
        
        self.label_estado_conocimiento = QLabel("✅ Configuración válida")
        self.label_estado_conocimiento.setStyleSheet("font-weight: normal; color: #27ae60;")
        estado_layout.addWidget(self.label_estado_conocimiento)
        
        layout.addWidget(grupo_estado)
        
        # Inicializar visibilidad
        self._cambiar_opciones_modelo()
        self._actualizar_info_modo()
        
        return panel
    def _cambiar_opciones_modelo(self):
        """Muestra/oculta opciones y botones según el modelo seleccionado"""
        usando_llm = self.radio_llm.isChecked()

        if usando_llm:
            self.llm_options.setVisible(True)

            # Cambiar modelo en el controlador
            texto_combo = self.combo_llm.currentText()
            if texto_combo.strip():
                modelo_llm = texto_combo.split()[0]
                self.controlador.servicio_ollama.cambiar_modelo(modelo_llm)

            # Fuentes web: disponibles solo en modo Web
            if hasattr(self, 'btn_fuentes_web') and self.btn_fuentes_web is not None:
                self.btn_fuentes_web.setEnabled(self.radio_web.isChecked())

            # Habilitar selector de modo de conocimiento
            if hasattr(self, 'radio_local'):
                self.radio_local.setEnabled(True)
                self.radio_web.setEnabled(True)
        else:
            self.llm_options.setVisible(False)

            # Con CommonKADS las fuentes web no aplican
            if hasattr(self, 'btn_fuentes_web') and self.btn_fuentes_web is not None:
                self.btn_fuentes_web.setEnabled(False)

            # Deshabilitar selector de modo de conocimiento (sin sentido con CommonKADS)
            if hasattr(self, 'radio_local'):
                self.radio_local.setEnabled(False)
                self.radio_web.setEnabled(False)

        # Habilitar/deshabilitar botones de acción según modelo
        solo_compatibilidad = not usando_llm
        if hasattr(self, 'btn_configuraciones'):
            self.btn_configuraciones.setEnabled(not solo_compatibilidad)
            self.btn_configuraciones.setToolTip(
                "" if not solo_compatibilidad
                else "Solo disponible con LLM. CommonKADS realiza únicamente análisis de compatibilidad."
            )
        if hasattr(self, 'btn_recomendacion'):
            self.btn_recomendacion.setEnabled(not solo_compatibilidad)
            self.btn_recomendacion.setToolTip(
                "" if not solo_compatibilidad
                else "Solo disponible con LLM. CommonKADS realiza únicamente análisis de compatibilidad."
            )
        
    def _al_cambiar_modelo_llm(self):
        """Notifica al servicio Ollama cuando el usuario cambia el modelo en el combo."""
        texto = self.combo_llm.currentText().strip()
        if texto and self.radio_llm.isChecked():
            modelo = texto.split()[0]
            self.controlador.servicio_ollama.cambiar_modelo(modelo)
            print(f"🔄 Modelo Ollama cambiado a: {modelo}")
            if hasattr(self, 'label_estado'):
                self.label_estado.setText(f"✅ Modelo Ollama: {modelo}")

    def _actualizar_info_modo(self):
        """Actualiza la información según el modo seleccionado"""
        if self.radio_web.isChecked():
            self.info_modo.setText(
                "🌐 MODO WEB: El sistema consultará información en internet además de tus PDFs. "
                "Las fuentes utilizadas quedarán registradas en la ventana de fuentes web."
            )
            # Habilitar botón de fuentes web
            if hasattr(self, 'btn_fuentes_web') and self.btn_fuentes_web is not None:
                self.btn_fuentes_web.setEnabled(True)
        else:
            self.info_modo.setText(
                "📁 MODO LOCAL: El diagnóstico se basará exclusivamente en los PDFs que cargues "
                "y en los datos que introduzcas. No se realizarán búsquedas en internet."
            )
            # Deshabilitar botón de fuentes web
            if hasattr(self, 'btn_fuentes_web') and self.btn_fuentes_web is not None:
                self.btn_fuentes_web.setEnabled(False)
        
        # También actualizar el label de estado del modelo
        if hasattr(self, 'label_estado_conocimiento'):
            modelo_usado = "CommonKADS" if self.radio_commonkads.isChecked() else f"LLM ({self.combo_llm.currentText()})"
            modo_usado = "Web" if self.radio_web.isChecked() else "Local"
            self.label_estado_conocimiento.setText(f"✅ {modelo_usado} | Modo {modo_usado}")
    
    def verificar_ollama(self):
        """Verifica la conexión con Ollama y muestra los modelos disponibles reales"""
        self.label_estado.setText("⏳ Verificando conexión con Ollama...")
        QApplication.processEvents()

        # Comprobar si Ollama está corriendo
        conectado = self.controlador.servicio_ollama.verificar_conexion()

        if not conectado:
            self.label_estado.setText("❌ Ollama no disponible")
            QMessageBox.warning(self, "Verificación Ollama",
                "❌ No se pudo conectar con Ollama\n\n"
                f"URL: {self.controlador.servicio_ollama.url_base}\n\n"
                "Asegúrate de que Ollama esté instalado y ejecutándose:\n"
                "  1. Instala Ollama desde https://ollama.com\n"
                "  2. Ejecuta 'ollama serve' en una terminal\n"
                "  3. Pulsa de nuevo 'Verificar Ollama'")
            return

        # Obtener modelos disponibles reales
        modelos = self.controlador.servicio_ollama.obtener_modelos_disponibles()

        # Actualizar el combo de modelos con los datos reales
        modelo_previo = self.combo_llm.currentText()
        self.combo_llm.clear()
        self.combo_llm.addItems(modelos)

        # Intentar mantener la selección previa si sigue disponible
        idx = self.combo_llm.findText(modelo_previo)
        if idx >= 0:
            self.combo_llm.setCurrentIndex(idx)

        modelo_actual = self.combo_llm.currentText()
        self.label_estado.setText(f"✅ Ollama conectado — {len(modelos)} modelo(s)")

        lista_modelos = "\n".join([f"  • {m}" for m in modelos]) if modelos else "  (ninguno)"
        QMessageBox.information(self, "Verificación Ollama",
            f"✅ Conexión exitosa con Ollama\n\n"
            f"Modelos instalados ({len(modelos)}):\n{lista_modelos}\n\n"
            f"Modelo seleccionado: {modelo_actual}")
    
    def cargar_reglas_commonkads(self):
        """Carga un archivo de reglas para CommonKADS"""
        ruta, _ = QFileDialog.getOpenFileName(
            self, "Cargar archivo de reglas CommonKADS", "",
            "Archivos de reglas (*.xml *.kads *.rules);;Todos los archivos (*.*)"
        )
        
        if ruta:
            self.txt_reglas.setText(ruta)
            self.label_estado.setText(f"✅ Reglas cargadas: {ruta.split('/')[-1]}")
            
            # Mostrar información del archivo
            QMessageBox.information(self, "Reglas cargadas",
                f"Archivo: {ruta}\n\n"
                "Reglas disponibles:\n"
                "• 15 reglas de compatibilidad socket CPU-Placa\n"
                "• 8 reglas de requisitos de memoria\n"
                "• 12 reglas de equilibrio de rendimiento\n"
                "• 5 reglas de dimensionamiento de fuente")
    
    def _crear_panel_acciones(self):
        """Panel con botones de acción específicos del dominio"""
        panel = QGroupBox("🚀 Acciones de asesoramiento")
        layout = QHBoxLayout(panel)
        
        # Botón para análisis de compatibilidad
        self.btn_compatibilidad = QPushButton("🔍 Analizar compatibilidad")
        self.btn_compatibilidad.clicked.connect(self.analizar_compatibilidad)
        self.btn_compatibilidad.setStyleSheet("background-color: #3498db;")
        layout.addWidget(self.btn_compatibilidad)
        
        # Botón para generar configuraciones
        self.btn_configuraciones = QPushButton("⚡ Generar configuraciones posibles")
        self.btn_configuraciones.clicked.connect(self.generar_configuraciones)
        self.btn_configuraciones.setStyleSheet("background-color: #27ae60;")
        layout.addWidget(self.btn_configuraciones)
        
        # Botón para recomendación final
        self.btn_recomendacion = QPushButton("✅ Obtener recomendación final")
        self.btn_recomendacion.clicked.connect(self.obtener_recomendacion)
        self.btn_recomendacion.setStyleSheet("background-color: #e67e22;")
        layout.addWidget(self.btn_recomendacion)
        
        # Gestión de conocimiento (PDFs)
        btn_pdfs = QPushButton("📁 Manuales/Guías (PDF)")
        btn_pdfs.clicked.connect(self.mostrar_ventana_pdfs)
        layout.addWidget(btn_pdfs)
        
        # BOTÓN DE FUENTES WEB
        self.btn_fuentes_web = QPushButton("🌐 Ver fuentes web")
        self.btn_fuentes_web.clicked.connect(self.mostrar_ventana_fuentes)
        self.btn_fuentes_web.setEnabled(False)  # Inicialmente deshabilitado
        self.btn_fuentes_web.setStyleSheet("background-color: #9b59b6;")
        layout.addWidget(self.btn_fuentes_web)
        
        return panel
    
    def _crear_barra_estado(self):
        """Barra de estado con información relevante"""
        self.statusBar().showMessage("Listo para asesorar")
        
        # Etiquetas permanentes en la barra de estado
        self.label_estado = QLabel("✅ Sistema listo")
        self.statusBar().addPermanentWidget(self.label_estado)
        
        self.label_compatibilidad = QLabel("🔄 Compatibilidad: No analizada")
        self.statusBar().addPermanentWidget(self.label_compatibilidad)

        # Log de archivos de reglas cargados al inicio
        reglas_xml = getattr(self.controlador.motor_commonkads, 'ruta_reglas', '')
        ontologia = getattr(self.controlador.motor_commonkads, 'ruta_ontologia', '')
        num_reglas = len(getattr(self.controlador.motor_commonkads, 'reglas', []))
        tiene_ontologia = bool(getattr(self.controlador.motor_commonkads, 'ontologia', {}))

        import os
        partes = []
        if reglas_xml and os.path.exists(reglas_xml):
            partes.append(f"📋 {os.path.basename(reglas_xml)} ({num_reglas} reglas)")
        if ontologia and os.path.exists(ontologia):
            partes.append(f"🧠 {os.path.basename(ontologia)}{'  ✅' if tiene_ontologia else '  ❌'}")

        texto_log = "  |  ".join(partes) if partes else "⚠️ Sin archivos de reglas"
        self.label_reglas_log = QLabel(texto_log)
        self.label_reglas_log.setStyleSheet("color: #555; font-size: 10px; padding-right: 6px;")
        self.statusBar().addPermanentWidget(self.label_reglas_log)
    
    def analizar_compatibilidad(self):
        """Analiza la compatibilidad de los componentes actuales"""
        componentes = self._recoger_componentes_actuales()
        if not componentes:
            QMessageBox.information(self, "Información", 
                "Marca los componentes que tienes para analizar su compatibilidad")
            return
        
        modelo_usado = "CommonKADS" if self.radio_commonkads.isChecked() else f"LLM ({self.combo_llm.currentText()})"
        self.label_estado.setText(f"⏳ Analizando compatibilidad con {modelo_usado} (Ejecutando en 2º plano, por favor espera...)")
        QApplication.processEvents()
        
        usar_llm = self.radio_llm.isChecked()
        # Llamar al controlador de manera asíncrona
        self.controlador.evaluar_compatibilidad(componentes, usar_llm, lambda ok, res: self._mostrar_resultado_compatibilidad(componentes, ok, res))
    
    def _mostrar_resultado_compatibilidad(self, componentes, es_compatible, resultado_analisis):
        """Muestra el resultado del análisis de compatibilidad"""
        if es_compatible:
            self.label_compatibilidad.setText("✅ Compatibilidad: Los componentes son compatibles")
            self.label_estado.setText("✅ Análisis completado - Componentes compatibles")
            icono = QMessageBox.Information
        else:
            self.label_compatibilidad.setText("❌ Compatibilidad: Se detectaron incompatibilidades")
            self.label_estado.setText("⚠️ Análisis completado - Incompatibilidades detectadas")
            icono = QMessageBox.Warning
        
        dialogo = QMessageBox(self)
        dialogo.setWindowTitle("Análisis de compatibilidad")
        dialogo.setIcon(icono)
        dialogo.setText(
            "Resultados del análisis:\n\n" +
            str(resultado_analisis) + "\n\n" +
            "Componentes analizados:\n" +
            "\n".join([f"• {comp}: {val}" for comp, val in componentes.items()]))
        dialogo.exec_()
    
    def generar_configuraciones(self):
        """Genera posibles configuraciones basadas en necesidades, verificando compatibilidad primero"""
        datos = self._recoger_todos_datos()
        
        # Actualizar el modo directamente en el modelo del controlador
        modo_texto = "Web (PDFs + Internet)" if self.radio_web.isChecked() else "Local (solo PDFs)"
        self.controlador.modelo.modo_actual = modo_texto
        self.controlador.modelo.sintomas = datos
        
        modelo_usado = "CommonKADS" if self.radio_commonkads.isChecked() else f"LLM ({self.combo_llm.currentText()})"

        self._verificar_compatibilidad_previa(
            datos,
            modelo_usado,
            callback_si_compatible=lambda: self._continuar_generacion(datos, modelo_usado)
        )
    
    def _continuar_generacion(self, datos, modelo_usado):
        """Continúa la generación de configuraciones tras pasar la verificación de compatibilidad"""
        self.label_estado.setText(f"⏳ Generando configuraciones con {modelo_usado} (Ejecutando en 2º plano, por favor espera...)")
        QApplication.processEvents()
        self.controlador.evaluar_hipotesis(datos)
    
    def _mostrar_incompatibilidad(self, mensaje):
        """Muestra un diálogo de incompatibilidad y detiene el proceso"""
        self.label_estado.setText("❌ Se detectaron incompatibilidades entre los componentes existentes")
        
        dialogo = QMessageBox(self)
        dialogo.setWindowTitle("⚠️ Incompatibilidad detectada")
        dialogo.setIcon(QMessageBox.Warning)
        dialogo.setText("Se han detectado incompatibilidades entre los componentes que ya posees.\n\n"
                        "Debes revisar y quitar alguno de los componentes marcados antes de volver a generar configuraciones.")
        dialogo.setDetailedText(mensaje)
        dialogo.setStandardButtons(QMessageBox.Ok)
        dialogo.exec_()
    
    def obtener_recomendacion(self):
        """Obtiene la recomendación final"""
        datos = self._recoger_todos_datos()

        # Actualizar el modo directamente en el modelo del controlador
        modo_texto = "Web (PDFs + Internet)" if self.radio_web.isChecked() else "Local (solo PDFs)"
        self.controlador.modelo.modo_actual = modo_texto  # <-- Acceso directo al modelo
        self.controlador.modelo.sintomas = datos
        
        modelo_usado = "CommonKADS" if self.radio_commonkads.isChecked() else f"LLM ({self.combo_llm.currentText()})"
        self._verificar_compatibilidad_previa(
            datos,
            modelo_usado,
            callback_si_compatible=lambda: self._continuar_recomendacion(modelo_usado)
        )
        
    def _continuar_recomendacion(self, modelo_usado):
        """Continúa con el veredicto final tras pasar la verificación de compatibilidad"""
        self.label_estado.setText(f"⏳ Calculando recomendación con {modelo_usado} (Ejecutando en 2º plano, no cierres la app...)")
        QApplication.processEvents()

        self.controlador.diagnosticar()
        # Las ventanas se mostrarán automáticamente desde el QThread al terminar.

    def _verificar_compatibilidad_previa(self, datos, modelo_usado, callback_si_compatible):
        """Verifica compatibilidad de componentes existentes antes de continuar con una acción crítica."""
        componentes = datos.get('componentes_actuales', {})
        componentes_reales = {k: v for k, v in componentes.items()
                              if v and v != "Modelo no especificado"}

        if len(componentes_reales) >= 2:
            self.label_estado.setText(f"⏳ Verificando compatibilidad de componentes existentes con {modelo_usado}...")
            QApplication.processEvents()

            usar_llm = self.radio_llm.isChecked()
            self.controlador.evaluar_compatibilidad(
                componentes_reales,
                usar_llm,
                lambda ok, res: callback_si_compatible() if ok else self._mostrar_incompatibilidad(res)
            )
        else:
            callback_si_compatible()
        
    def _recoger_componentes_actuales(self):
        """Recoge los componentes que el usuario ha marcado"""
        componentes = {}
        for nombre, widgets in self.componentes_actuales.items():
            if widgets['check'].isChecked():
                modelo = widgets['texto'].text().strip()
                componentes[nombre] = modelo if modelo else "Modelo no especificado"
        return componentes
    
    def _recoger_todos_datos(self):
        """Recoge todos los datos del formulario"""
        # Determinar el modo como string exacto
        modo_texto = "Web (PDFs + Internet)" if self.radio_web.isChecked() else "Local (solo PDFs)"
        
        datos = {
            'perfil': {
                'presupuesto': self.spin_presupuesto.value(),
                'prioridad': self.combo_prioridad.currentText()
            },
            'componentes_actuales': self._recoger_componentes_actuales(),
            'uso': {
                'principal': self.uso_seleccionado,
                'detalles': self.detalles_uso.toPlainText()
            },
            'conocimiento': {
                'modelo': {
                    'tipo': 'commonkads' if self.radio_commonkads.isChecked() else 'llm',
                    'llm_modelo': self.combo_llm.currentText() if self.radio_llm.isChecked() else None,
                    'archivo_reglas': self.txt_reglas.text() if self.radio_commonkads.isChecked() else None
                },
                'modo': {
                    'tipo': 'local' if self.radio_local.isChecked() else 'web',
                    'texto': modo_texto,  # Guardar el texto exacto
                    'usar_pdfs': True,
                    'usar_web': self.radio_web.isChecked()
                }
            }
        }
        return datos
    
    # Métodos para ventanas secundarias (con manejo de errores)
    def mostrar_ventana_hipotesis(self):
        """Muestra la ventana de configuraciones posibles"""
        if self.ventana_hipotesis is not None:
            try:
                if self.ventana_hipotesis.isVisible():
                    self.ventana_hipotesis.raise_()
                    self.ventana_hipotesis.activateWindow()
                    return
            except RuntimeError:
                self.ventana_hipotesis = None
        
        self.ventana_hipotesis = VentanaHipotesis(self.controlador)
        self._posicionar_ventana_cascada(self.ventana_hipotesis)
        self.ventana_hipotesis.setWindowTitle("Configuraciones posibles")
        self.ventana_hipotesis.show()
    
    def mostrar_ventana_diagnostico(self):
        """Muestra la ventana de recomendación final"""
        if self.ventana_diagnostico is not None:
            try:
                if self.ventana_diagnostico.isVisible():
                    self.ventana_diagnostico.raise_()
                    self.ventana_diagnostico.activateWindow()
                    return
            except RuntimeError:
                self.ventana_diagnostico = None
        
        self.ventana_diagnostico = VentanaDiagnostico(self.controlador)
        self._posicionar_ventana_cascada(self.ventana_diagnostico)
        self.ventana_diagnostico.setWindowTitle("Recomendación final de componentes")
        self.ventana_diagnostico.show()
    
    def mostrar_ventana_justificacion(self):
        """Muestra la ventana de justificación"""
        if self.ventana_justificacion is not None:
            try:
                if self.ventana_justificacion.isVisible():
                    self.ventana_justificacion.raise_()
                    self.ventana_justificacion.activateWindow()
                    return
            except RuntimeError:
                self.ventana_justificacion = None
        
        self.ventana_justificacion = VentanaJustificacion(self.controlador)
        self._posicionar_ventana_cascada(self.ventana_justificacion)
        self.ventana_justificacion.setWindowTitle("Por qué estos componentes")
        self.ventana_justificacion.show()
    
    def mostrar_ventana_pdfs(self):
        """Muestra la ventana de gestión de PDFs"""
        if self.ventana_pdfs is not None:
            try:
                if self.ventana_pdfs.isVisible():
                    self.ventana_pdfs.raise_()
                    self.ventana_pdfs.activateWindow()
                    return
            except RuntimeError:
                self.ventana_pdfs = None
        
        self.ventana_pdfs = VentanaPDFs(self.controlador)
        self._posicionar_ventana_cascada(self.ventana_pdfs)
        self.ventana_pdfs.setWindowTitle("Manuales y guías de referencia")
        self.ventana_pdfs.show()
    
    def mostrar_ventana_fuentes(self):
        """Muestra la ventana de fuentes web"""
        if self.ventana_fuentes is not None:
            try:
                if self.ventana_fuentes.isVisible():
                    self.ventana_fuentes.raise_()
                    self.ventana_fuentes.activateWindow()
                    return
            except RuntimeError:
                self.ventana_fuentes = None
        
        self.ventana_fuentes = VentanaFuentes(self.controlador)
        self._posicionar_ventana_cascada(self.ventana_fuentes)
        self.ventana_fuentes.setWindowTitle("Fuentes consultadas")
        self.ventana_fuentes.show()
    
    def _posicionar_ventana_cascada(self, ventana):
        """Posiciona una ventana en cascada respecto a la principal"""
        main_geo = self.geometry()
        main_pos = main_geo.topLeft()
        offset = 30 * (self.contador_ventanas % 10)
        ventana.move(main_pos.x() + 50 + offset, main_pos.y() + 50 + offset)
        self.contador_ventanas += 1
    
    def _actualizar_label_pdfs(self):
        """Actualiza el label de PDFs cargados en la sección Estado actual"""
        n = len(self.controlador.modelo.pdfs)
        self.label_pdfs_cargados.setText(f"📄 PDFs cargados: {n}")
        if n > 0:
            nombres = ", ".join(p['nombre'] for p in self.controlador.modelo.pdfs)
            self.label_pdfs_cargados.setToolTip(f"Archivos: {nombres}")
            self.label_estado_conocimiento.setText("✅ Base de conocimiento lista")
            self.label_estado_conocimiento.setStyleSheet("font-weight: normal; color: #27ae60;")
        else:
            self.label_pdfs_cargados.setToolTip("")
            self.label_estado_conocimiento.setText("⚠️ Sin PDFs cargados")
            self.label_estado_conocimiento.setStyleSheet("font-weight: normal; color: #e67e22;")

    def actualizar_vistas(self):
        """Actualiza vistas cuando el modelo cambia"""  
        ventanas = [
            ('ventana_hipotesis', 'actualizar_datos'),
            ('ventana_diagnostico', 'actualizar_datos'),
            ('ventana_justificacion', 'actualizar_datos'),
            ('ventana_pdfs', 'actualizar_lista'),
            ('ventana_fuentes', 'actualizar_tabla')
        ]
        
        for attr_name, metodo in ventanas:
            ventana = getattr(self, attr_name, None)
            if ventana is not None:
                try:
                    if ventana.isVisible():
                        getattr(ventana, metodo)()
                except RuntimeError:
                    setattr(self, attr_name, None)
    
    def closeEvent(self, event):
        """Maneja el cierre de la aplicación"""
        ventanas = [
            self.ventana_hipotesis,
            self.ventana_diagnostico,
            self.ventana_justificacion,
            self.ventana_pdfs,
            self.ventana_fuentes
        ]
        for ventana in ventanas:
            if ventana is not None:
                try:
                    ventana.close()
                except RuntimeError:
                    pass
        event.accept()