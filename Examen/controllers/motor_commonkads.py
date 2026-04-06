import xml.etree.ElementTree as ET
import os
from utils.rutas import obtener_ruta_relativa

class MotorCommonKADS:
    """
    Motor de inferencia basado en reglas (CommonKADS)
    Lee reglas desde un archivo XML y aplica inferencias
    """
    
    def __init__(self, ruta_reglas="config/reglas_commonkads.xml"):
        # Usar ruta genérica
        self.ruta_reglas = obtener_ruta_relativa(ruta_reglas)
        self.reglas = []
        self.hechos = {}
        self.cargar_reglas()
    
    def cargar_reglas(self):
        """Carga las reglas desde el archivo XML"""
        try:
            if not os.path.exists(self.ruta_reglas):
                print(f"⚠️ Archivo de reglas no encontrado: {self.ruta_reglas}")
                return
            
            tree = ET.parse(self.ruta_reglas)
            root = tree.getroot()
            
            for regla_elem in root.findall('.//regla'):
                regla = {
                    'nombre': regla_elem.get('nombre', 'sin_nombre'),
                    'prioridad': int(regla_elem.get('prioridad', 0)),
                    'condiciones': [],
                    'conclusiones': []
                }
                
                # Cargar condiciones
                for cond in regla_elem.findall('condicion'):
                    cond_dict = {
                        'campo': cond.find('campo').text if cond.find('campo') is not None else '',
                        'operador': cond.find('operador').text if cond.find('operador') is not None else ''
                    }
                    
                    if cond_dict['operador'] == 'igual':
                        cond_dict['valor'] = cond.find('valor').text if cond.find('valor') is not None else ''
                    elif cond_dict['operador'] == 'entre':
                        cond_dict['valor_min'] = cond.find('valor_min').text if cond.find('valor_min') is not None else ''
                        cond_dict['valor_max'] = cond.find('valor_max').text if cond.find('valor_max') is not None else ''
                    elif cond_dict['operador'] in ['mayor_igual', 'menor_igual']:
                        cond_dict['valor'] = cond.find('valor').text if cond.find('valor') is not None else ''
                    
                    regla['condiciones'].append(cond_dict)
                
                # Cargar conclusiones
                for conc in regla_elem.findall('conclusion'):
                    conc_dict = {
                        'campo': conc.find('campo').text if conc.find('campo') is not None else '',
                        'valor': conc.find('valor').text if conc.find('valor') is not None else ''
                    }
                    regla['conclusiones'].append(conc_dict)
                
                self.reglas.append(regla)
            
            # Ordenar reglas por prioridad
            self.reglas.sort(key=lambda x: x['prioridad'], reverse=True)
            print(f"✅ Cargadas {len(self.reglas)} reglas CommonKADS")
            
        except Exception as e:
            print(f"❌ Error cargando reglas: {e}")
    
    def evaluar_condicion(self, cond, hechos):
        """Evalúa una condición individual"""
        campo = cond['campo']
        operador = cond['operador']
        
        # Obtener valor del hecho (si no existe, retornar False)
        valor_hecho = hechos.get(campo, '')
        
        if valor_hecho == '':
            return False
        
        if operador == 'igual':
            return str(valor_hecho).lower() == str(cond['valor']).lower()
        
        elif operador == 'contiene':
            return str(cond['valor']).lower() in str(valor_hecho).lower()
        
        elif operador == 'mayor_igual':
            try:
                return float(valor_hecho) >= float(cond['valor'])
            except:
                return False
        
        elif operador == 'menor_igual':
            try:
                return float(valor_hecho) <= float(cond['valor'])
            except:
                return False
        
        elif operador == 'entre':
            try:
                return float(cond['valor_min']) <= float(valor_hecho) <= float(cond['valor_max'])
            except:
                return False
        
        return False
    
    def inferir(self, hechos_iniciales):
        """
        Realiza inferencia forward chaining
        """
        self.hechos = hechos_iniciales.copy()
        reglas_aplicadas = []
        cambios = True
        
        # Forward chaining
        while cambios:
            cambios = False
            
            for regla in self.reglas:
                # Verificar si la regla ya se aplicó
                if regla['nombre'] in reglas_aplicadas:
                    continue
                
                # Evaluar todas las condiciones
                condiciones_cumplidas = True
                for cond in regla['condiciones']:
                    if not self.evaluar_condicion(cond, self.hechos):
                        condiciones_cumplidas = False
                        break
                
                # Si se cumplen, aplicar conclusiones
                if condiciones_cumplidas:
                    for conc in regla['conclusiones']:
                        campo = conc['campo']
                        valor = conc['valor']
                        
                        # Solo añadir si no existe o si el valor es diferente
                        if campo not in self.hechos or self.hechos[campo] != valor:
                            self.hechos[campo] = valor
                            cambios = True
                    
                    reglas_aplicadas.append(regla['nombre'])
                    print(f"🔍 Regla aplicada: {regla['nombre']}")
        
        return self.hechos
    
    def generar_hipotesis(self, datos_usuario):
        """
        Genera hipótesis de configuraciones posibles
        """
        # Extraer hechos iniciales del usuario
        hechos = {}
        
        if 'perfil' in datos_usuario:
            hechos['presupuesto'] = datos_usuario['perfil'].get('presupuesto', 0)
            hechos['experiencia'] = datos_usuario['perfil'].get('experiencia', '')
            hechos['prioridad'] = datos_usuario['perfil'].get('prioridad', '')
        
        if 'uso' in datos_usuario:
            hechos['uso_principal'] = datos_usuario['uso'].get('principal', '')
        
        if 'componentes_actuales' in datos_usuario:
            hechos['componentes_actuales'] = list(datos_usuario['componentes_actuales'].keys())
        
        # Realizar inferencia
        resultados = self.inferir(hechos)
        
        # Generar hipótesis según los resultados
        hipotesis = []
        
        gpu = resultados.get('gpu_recomendada', 'No determinada')
        ram = resultados.get('ram_cantidad', '16GB')
        fuente = resultados.get('fuente_potencia', '650W')
        
        # Crear configuraciones posibles
        if gpu != 'No determinada':
            hipotesis.append({
                'nombre': f"Configuración con {gpu}",
                'probabilidad': 0.85,
                'estado': 'posible',
                'detalles': {
                    'gpu': gpu,
                    'ram': ram,
                    'fuente': fuente,
                    'chipset': resultados.get('chipset_recomendado', '')
                }
            })
        
        # Segunda hipótesis alternativa
        if resultados.get('gpu_nivel') == 'Entrada':
            hipotesis.append({
                'nombre': "Configuración económica alternativa",
                'probabilidad': 0.65,
                'estado': 'posible',
                'detalles': {
                    'gpu': 'RTX 3050 / RX 6600',
                    'ram': '16GB DDR4',
                    'fuente': '500W 80+ Bronze'
                }
            })
        elif resultados.get('gpu_nivel') == 'Medio':
            hipotesis.append({
                'nombre': "Configuración calidad-precio",
                'probabilidad': 0.70,
                'estado': 'posible',
                'detalles': {
                    'gpu': 'RTX 4060 Ti / RX 7700 XT',
                    'ram': '32GB DDR5',
                    'fuente': '750W 80+ Gold'
                }
            })
        
        return hipotesis
    
    def generar_diagnostico(self, datos_usuario, hipotesis_seleccionada):
        """
        Genera diagnóstico final basado en las reglas
        """
        # Extraer hechos
        hechos = {}
        
        if 'perfil' in datos_usuario:
            hechos['presupuesto'] = datos_usuario['perfil'].get('presupuesto', 0)
        
        if 'uso' in datos_usuario:
            hechos['uso_principal'] = datos_usuario['uso'].get('principal', '')
        
        # Inferir
        resultados = self.inferir(hechos)
        
        # Construir diagnóstico
        diagnostico = f"""**COMPONENTES RECOMENDADOS (CommonKADS):**

- **CPU**: {self._recomendar_cpu(resultados)}
- **GPU**: {resultados.get('gpu_recomendada', 'RTX 4060')}
- **RAM**: {resultados.get('ram_cantidad', '16GB')} {resultados.get('ram_tipo', 'DDR5')}
- **Placa base**: Socket {resultados.get('placa_socket', 'AM5')} - Chipset {resultados.get('chipset_recomendado', 'B650')}
- **Almacenamiento**: SSD NVMe 1TB
- **Fuente**: {resultados.get('fuente_potencia', '650W')} {resultados.get('fuente_certificacion', '80+ Bronze')}

**PRECIO APROXIMADO:** {self._calcular_precio(resultados)}€
"""
        
        justificacion = f"""**JUSTIFICACIÓN (basada en reglas):**

Las siguientes reglas se aplicaron para llegar a esta configuración:

1. **Reglas de compatibilidad:** Según la CPU seleccionada, se eligió el socket y chipset compatible.
2. **Reglas de uso:** Para uso {resultados.get('uso_principal', 'Gaming')}, se priorizó {resultados.get('gpu_nivel', 'medio')} nivel de GPU.
3. **Reglas de presupuesto:** Con {resultados.get('presupuesto', 1000)}€ de presupuesto, se seleccionaron componentes equilibrados.
4. **Reglas de fuente:** La potencia de la fuente se dimensionó según la GPU recomendada.

**Evidencias consideradas:**
- Uso principal: {resultados.get('uso_principal', 'No especificado')}
- Presupuesto: {resultados.get('presupuesto', 0)}€
- Prioridad: {resultados.get('prioridad', 'Equilibrio')}
"""
        
        fuentes = []  # CommonKADS no usa fuentes web
        
        return diagnostico, justificacion, fuentes
    
    def _recomendar_cpu(self, resultados):
        """Recomienda CPU según los resultados"""
        socket = resultados.get('placa_socket', 'AM5')
        if socket == 'AM4':
            return "AMD Ryzen 5 5600X"
        elif socket == 'AM5':
            return "AMD Ryzen 5 7600X"
        elif socket == 'LGA 1700':
            return "Intel Core i5-13600K"
        else:
            return "AMD Ryzen 5 7600X"
    
    def _calcular_precio(self, resultados):
        """Calcula precio aproximado según componentes"""
        gpu_nivel = resultados.get('gpu_nivel', 'Medio')
        if gpu_nivel == 'Entrada':
            return "700-900"
        elif gpu_nivel == 'Medio':
            return "1000-1300"
        elif gpu_nivel == 'Alto':
            return "1800-2200"
        else:
            return "1000-1200"