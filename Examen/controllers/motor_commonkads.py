import xml.etree.ElementTree as ET
import os
import json
import re
from utils.rutas import obtener_ruta_relativa

class MotorCommonKADS:
    """
    Motor de inferencia basado en reglas (CommonKADS)
    Lee reglas desde un archivo XML y aplica inferencias
    """
    
    def __init__(self, ruta_reglas="config/reglas_commonkads.xml"):
        # Usar ruta genérica
        self.ruta_reglas = obtener_ruta_relativa(ruta_reglas)
        self.ruta_ontologia = obtener_ruta_relativa("config/ontologia_compatibilidad.json")
        self.reglas = []
        self.ontologia = {}
        self.hechos = {}
        self.cargar_reglas()
        self.cargar_ontologia()

    def cargar_ontologia(self):
        """Carga la ontología JSON de compatibilidad."""
        try:
            if not os.path.exists(self.ruta_ontologia):
                print(f"⚠️ Ontología no encontrada: {self.ruta_ontologia}")
                self.ontologia = {}
                return

            with open(self.ruta_ontologia, 'r', encoding='utf-8') as f:
                self.ontologia = json.load(f)

            print("✅ Ontología de compatibilidad cargada correctamente")
        except Exception as e:
            print(f"❌ Error cargando ontología: {e}")
            self.ontologia = {}
    
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

    def _normalizar(self, texto):
        if not texto:
            return ""
        return str(texto).strip().lower()

    def _extraer_w(self, texto):
        if not texto:
            return None
        m = re.search(r'(\d{3,4})\s*w', self._normalizar(texto))
        if m:
            try:
                return int(m.group(1))
            except ValueError:
                return None
        return None

    def _extraer_gb(self, texto):
        if not texto:
            return None
        m = re.search(r'(\d{1,3})\s*gb', self._normalizar(texto))
        if m:
            try:
                return int(m.group(1))
            except ValueError:
                return None
        return None

    def _detectar_tipo_ram(self, ram_texto):
        t = self._normalizar(ram_texto)
        if 'ddr5' in t:
            return 'DDR5'
        if 'ddr4' in t:
            return 'DDR4'
        return None

    def _detectar_chipset_placa(self, placa_texto):
        placa = self._normalizar(placa_texto)
        if not placa:
            return None

        for item in self.ontologia.get('cpu_socket_chipset', []):
            for chipset in item.get('chipsets_compatibles', []):
                if self._normalizar(chipset) in placa:
                    return chipset
        return None

    def _detectar_familia_cpu(self, cpu_texto):
        cpu = self._normalizar(cpu_texto)
        if not cpu:
            return None

        if 'ryzen 9' in cpu and ('7950' in cpu or '7900' in cpu):
            return 'AMD Ryzen 7000 series'
        if 'ryzen' in cpu and ('9000' in cpu or '9700' in cpu or '9900' in cpu):
            return 'AMD Ryzen 9000 series'
        if 'ryzen' in cpu and ('7600' in cpu or '7700' in cpu or '7800' in cpu):
            return 'AMD Ryzen 7000 series'
        if 'ryzen' in cpu and ('5600' in cpu or '5700' in cpu or '5800' in cpu or '5900' in cpu):
            return 'AMD Ryzen 5000 series'

        if 'intel' in cpu or re.search(r'\bi[3579]-\d{4,5}', cpu):
            if any(x in cpu for x in ['10', '11']) and re.search(r'\bi[3579]-1\d{4}', cpu):
                return 'Intel Core 10th/11th Gen'
            if re.search(r'\bi[3579]-1[234]\d{3}', cpu):
                return 'Intel Core 12th/13th/14th Gen'
            if any(x in cpu for x in ['12400', '13400', '13600', '13700', '13900', '14700', '14900']):
                return 'Intel Core 12th/13th/14th Gen'

        return None

    def _socket_por_familia(self, familia_cpu):
        if not familia_cpu:
            return None
        for item in self.ontologia.get('cpu_socket_chipset', []):
            if item.get('familia_cpu') == familia_cpu:
                return item.get('socket')
        return None

    def _socket_por_chipset(self, chipset):
        if not chipset:
            return None
        c_norm = self._normalizar(chipset)
        for item in self.ontologia.get('cpu_socket_chipset', []):
            for ch in item.get('chipsets_compatibles', []):
                if self._normalizar(ch) == c_norm:
                    return item.get('socket')
        return None

    def _gpu_minima_fuente(self, gpu_texto):
        g = self._normalizar(gpu_texto)
        if not g:
            return None

        reglas = self.ontologia.get('reglas_compatibilidad_adicionales', {}).get('gpu_fuente_minima', [])
        for regla in reglas:
            for gpu_ref in regla.get('gpus', []):
                if self._normalizar(gpu_ref) in g:
                    return regla.get('fuente_minima_w')
        return None

    def analizar_compatibilidad(self, componentes):
        """
        Analiza compatibilidad usando reglas CommonKADS + ontología JSON.
        """
        if not componentes:
            return "No hay componentes para analizar."

        if not self.ontologia:
            return "VEREDICTO: COMPATIBLE\nEXPLICACION: No se pudo cargar la ontología de compatibilidad; se asume compatibilidad general como fallback."

        cpu = componentes.get('CPU', '')
        placa = componentes.get('Placa base', '')
        ram = componentes.get('RAM', '')
        gpu = componentes.get('GPU', '')
        fuente = componentes.get('Fuente', '')

        incompatibilidades = []
        advertencias = []

        familia_cpu = self._detectar_familia_cpu(cpu)
        socket_cpu = self._socket_por_familia(familia_cpu)
        chipset_placa = self._detectar_chipset_placa(placa)
        socket_placa = self._socket_por_chipset(chipset_placa)
        tipo_ram = self._detectar_tipo_ram(ram)
        gb_ram = self._extraer_gb(ram)
        fuente_w = self._extraer_w(fuente)
        fuente_min_gpu = self._gpu_minima_fuente(gpu)

        # Regla 1: CPU vs Placa (familia/socket/chipset)
        validacion_cpu_placa_posible = False
        if familia_cpu and chipset_placa:
            validacion_cpu_placa_posible = True
            fila_cpu = next((x for x in self.ontologia.get('cpu_socket_chipset', []) if x.get('familia_cpu') == familia_cpu), None)
            if fila_cpu and chipset_placa not in fila_cpu.get('chipsets_compatibles', []):
                incompatibilidades.append(
                    f"CPU '{cpu}' ({familia_cpu}) no es compatible con chipset '{chipset_placa}'. "
                    f"Chipsets válidos: {', '.join(fila_cpu.get('chipsets_compatibles', []))}."
                )
        elif familia_cpu and placa and not chipset_placa:
            # Se identificó la CPU pero no el chipset de la placa: no se puede confirmar compatibilidad
            socket_requerido = socket_cpu or '?'
            advertencias.append(
                f"Se identificó la CPU '{cpu}' ({familia_cpu}, socket {socket_requerido}) "
                f"pero no se pudo reconocer el chipset de la placa base '{placa}'. "
                f"No es posible confirmar compatibilidad de socket."
            )
        elif cpu and not familia_cpu and placa:
            advertencias.append(
                f"No se pudo identificar la familia de CPU de '{cpu}'. "
                f"Introduce el modelo completo (ej: 'Intel i5-13600K' o 'AMD Ryzen 5 7600') para validar socket/chipset."
            )
        elif cpu and placa and not familia_cpu and not chipset_placa:
            advertencias.append("No se pudo identificar ni la familia de CPU ni el chipset de placa para validar socket/chipset.")

        # Regla 2: Socket de plataforma vs tipo de RAM
        socket_referencia = socket_placa or socket_cpu
        if socket_referencia and tipo_ram:
            ram_ok = False
            for regla_ram in self.ontologia.get('ram_compatibilidad', []):
                if regla_ram.get('tipo_ram') == tipo_ram and socket_referencia in regla_ram.get('sockets_compatibles', []):
                    ram_ok = True
                    break
            if not ram_ok:
                incompatibilidades.append(
                    f"RAM '{ram}' ({tipo_ram}) incompatible con plataforma '{socket_referencia}'."
                )

        # Regla 3: RAM máxima por chipset
        if chipset_placa and gb_ram:
            limites_ram = self.ontologia.get('reglas_compatibilidad_adicionales', {}).get('ram_maxima_por_chipset', [])
            for regla in limites_ram:
                if chipset_placa in regla.get('chipsets', []):
                    maximo = regla.get('ram_maxima_gb')
                    max_num = None
                    if isinstance(maximo, int):
                        max_num = maximo
                    elif isinstance(maximo, str) and '-' in maximo:
                        try:
                            max_num = int(maximo.split('-')[-1])
                        except Exception:
                            max_num = None
                    if max_num and gb_ram > max_num:
                        incompatibilidades.append(
                            f"RAM instalada ({gb_ram}GB) supera el máximo de '{chipset_placa}' ({maximo}GB)."
                        )
                    break

        # Regla 4: GPU vs potencia mínima de fuente
        if fuente_min_gpu and fuente_w:
            if fuente_w < fuente_min_gpu:
                incompatibilidades.append(
                    f"Fuente insuficiente para GPU '{gpu}': {fuente_w}W < mínimo {fuente_min_gpu}W."
                )
        elif gpu and fuente and (fuente_min_gpu is None or fuente_w is None):
            advertencias.append("No se pudo validar completamente GPU vs fuente por falta de identificación exacta de modelo o potencia.")

        if incompatibilidades:
            explicacion = "VEREDICTO: INCOMPATIBLE\n"
            explicacion += "EXPLICACION: Se detectaron incompatibilidades técnicas reales:\n"
            for i, inc in enumerate(incompatibilidades, 1):
                explicacion += f"{i}. {inc}\n"
            if advertencias:
                explicacion += "\nObservaciones:\n"
                for a in advertencias:
                    explicacion += f"- {a}\n"
            return explicacion.strip()

        # Si hay advertencias que impiden validar correctamente → NO DETERMINADO
        if advertencias:
            explicacion = "VEREDICTO: NO DETERMINADO\n"
            explicacion += "EXPLICACION: No fue posible confirmar ni descartar la compatibilidad porque falta información:\n"
            for a in advertencias:
                explicacion += f"- {a}\n"
            return explicacion.strip()

        explicacion = "VEREDICTO: COMPATIBLE\n"
        explicacion += "EXPLICACION: No se encontraron incompatibilidades técnicas con las reglas CommonKADS de ontología."
        return explicacion.strip()