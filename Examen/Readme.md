# Sistema de Diagnóstico para Configuración de PC

## Descripción del dominio
El dominio seleccionado es el asesoramiento para la configuración de ordenadores personales, una tarea de diagnóstico técnico que consiste en recomendar componentes hardware compatibles y ajustados a las necesidades y presupuesto del usuario.

## Arquitectura MVC

### Modelo (`models/modelo_datos.py`)
- Mantiene el estado de la aplicación: síntomas, PDFs, hipótesis, diagnóstico, justificación y fuentes web
- Notifica cambios mediante señales PyQt
- Getters/setters para encapsulación

### Vista (`views/`)
- **Ventana principal**: Interfaz principal con panel de síntomas dinámico
- **Ventana hipótesis**: Muestra ranking de posibles configuraciones
- **Ventana diagnóstico**: Presenta la configuración final recomendada
- **Ventana justificación**: Explica el razonamiento y evidencias
- **Ventana PDFs**: Gestión de conocimiento local
- **Ventana fuentes**: Muestra fuentes web consultadas (modo Web)

### Controlador (`controllers/controlador_principal.py`)
- Coordina el flujo de la aplicación
- Procesa eventos de la vista
- Actualiza el modelo
- Invoca al servicio LLM

## Parametrización externa
La aplicación lee `config/config_diagnostico.json` para definir:
- Categorías de síntomas y sus opciones
- Observables (rangos, booleanos, texto)
- Modos de conocimiento disponibles
- Colores de la interfaz

## Instrucciones de ejecución

### Requisitos
```bash
pip install PyQt5