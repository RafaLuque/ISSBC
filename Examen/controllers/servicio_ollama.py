import urllib.request
import urllib.error
import json
import datetime
import re

class ServicioOllama:
    """
    Servicio para interactuar con Ollama (LLMs locales) vía API REST HTTP
    """
    
    def __init__(self, config):
        self.config = config
        self.modelo = "qwen2.5:7b"  # Modelo por defecto
        self.url_base = "http://localhost:11434"
        self._verificado = False
    
    def _seleccionar_modelo_disponible(self):
        """Verifica los modelos disponibles y selecciona el mejor disponible si el por defecto no está."""
        if self._verificado:
            return
            
        try:
            req = urllib.request.Request(f"{self.url_base}/api/tags")
            with urllib.request.urlopen(req, timeout=5) as response:
                if response.status == 200:
                    raw_str = response.read().decode('utf-8')
                    data = json.loads(raw_str)
                    modelos = []
                    if 'models' in data:
                        modelos = [m.get('name', str(m)) for m in data['models']]
                        
                    if modelos:
                        if self.modelo not in modelos:
                            # Preferir modelos que sean de 7b o 8b para evitar cargar modelos pesados (como los 30b) que tiran el servidor
                            modelos_ligeros = [m for m in modelos if '7b' in m.lower() or '8b' in m.lower()]
                            
                            if modelos_ligeros:
                                # Buscar preferiblemente qwen base u otros
                                qwen_base = [m for m in modelos_ligeros if 'qwen' in m.lower() and 'coder' not in m.lower() and 'vl' not in m.lower()]
                                if qwen_base:
                                    self.modelo = qwen_base[0]
                                else:
                                    self.modelo = modelos_ligeros[0]
                            else:
                                self.modelo = modelos[0]
                            print(f"⚠️ Modelo por defecto no encontrado. Usando modelo ligero disponible: {self.modelo}")
                        else:
                            print(f"✅ Modelo {self.modelo} detectado en Ollama.")
                        self._verificado = True
                    else:
                        print(f"⚠️ Respuesta vacía de Ollama API MODO SEGURO ACTIVADO. Forzando qwen3:8b. RAW: {raw_str[:200]}")
                        self.modelo = "qwen3:8b"
                        self._verificado = True
        except Exception as e:
            print(f"⚠️ Error de red al verificar los modelos en Ollama (Forzando qwen3:8b): {e}")
            self.modelo = "qwen3:8b"
            self._verificado = True

    def cambiar_modelo(self, modelo):
        """Cambia el modelo de Ollama a usar"""
        import urllib.request
        import json
        
        # Si hay un modelo anterior, intentar descargarlo
        if hasattr(self, 'modelo') and self.modelo != modelo:
            try:
                # Llamar a la API para descargar el modelo anterior
                req = urllib.request.Request(
                    f"{self.url_base}/api/generate",
                    data=json.dumps({"model": self.modelo, "keep_alive": 0}).encode('utf-8'),
                    headers={'Content-Type': 'application/json'},
                    method='POST'
                )
                urllib.request.urlopen(req, timeout=2)
                print(f"✅ Modelo {self.modelo} descargado de memoria")
            except:
                pass
        
        self.modelo = modelo
        self._modelo_usuario = True
        self._verificado = True
        print(f"✅ Modelo cambiado a: {self.modelo}")
    
    def verificar_conexion(self):
        """Verifica que Ollama esté funcionando en el puerto HTTP"""
        try:
            req = urllib.request.Request(f"{self.url_base}/")
            with urllib.request.urlopen(req, timeout=3) as response:
                return response.status == 200
        except Exception:
            return False
            
    def obtener_modelos_disponibles(self):
        """Devuelve la lista real de modelos instalados en el sistema"""
        try:
            req = urllib.request.Request(f"{self.url_base}/api/tags")
            with urllib.request.urlopen(req, timeout=5) as response:
                if response.status == 200:
                    raw_str = response.read().decode('utf-8')
                    data = json.loads(raw_str)
                    if 'models' in data:
                        modelos = [m.get('name', str(m)) for m in data['models']]
                        if modelos:
                             return modelos
                    print(f"⚠️ API Tags vacío o sin 'models': {raw_str[:200]}")
        except Exception as e:
            print(f"⚠️ Error técnico consultando /api/tags: {e}")
            
        # Fallback a los modelos exactos que me mostraste en tu captura de pantalla
        return ["qwen3:8b", "deepseek-r1:8b", "qwen3:30b", "llama3.1:8b"]
    
    def consultar(self, prompt, contexto_pdfs=""):
        """
        Realiza una consulta post a Ollama usando la API REST
        """
        # Verificar modelo justo antes de consultar por si Ollama se arrancó después de la UI
        #self._seleccionar_modelo_disponible()
        
        prompt_completo = f"{contexto_pdfs}\n\n{prompt}" if contexto_pdfs else prompt
        
        print(f"🔍 Enviando consulta a Ollama HTTP (modelo: {self.modelo})")
        
        datos = {
            "model": self.modelo,
            "prompt": prompt_completo,
            "stream": False
        }
        
        try:
            req = urllib.request.Request(
                f"{self.url_base}/api/generate",
                data=json.dumps(datos).encode('utf-8'),
                headers={
                    'Content-Type': 'application/json',
                    'Connection': 'close'
                },
                method='POST'
            )
            with urllib.request.urlopen(req, timeout=600) as response:
                if response.status == 200:
                    resultado = json.loads(response.read().decode('utf-8'))
                    respuesta_texto = resultado.get("response", "").strip()
                    print(f"✅ Respuesta HTTP recibida ({len(respuesta_texto)} cars)")
                    return respuesta_texto
                else:
                    return f"Error HTTP {response.status}"
        except urllib.error.HTTPError as e:
            error_body = e.read().decode('utf-8')
            # Si el modelo solicitado no existe (404), forzamos una re-evaluación
            if e.code == 404 and "not found" in error_body.lower():
                print(f"⚠️ El modelo '{self.modelo}' no existe localmente. Iniciando auto-rescate...")
                self._verificado = False
                self._seleccionar_modelo_disponible()
                
                # Prevenir bucle infinito si la auto-selección vuelve a elegir el mismo por error
                if self.modelo != datos["model"]:
                    print(f"🔄 Reintentando silenciosamente con el modelo {self.modelo}...")
                    return self.consultar(prompt, contexto_pdfs)
                    
            print(f"❌ Error HTTP de Ollama: {e.code} - {error_body}")
            return f"Error HTTP {e.code}: {error_body}"
        except urllib.error.URLError as e:
            print(f"❌ Error de red con Ollama: {e.reason}")
            return f"Error de conexión con Ollama en {self.url_base}. Detalles: {e.reason}"
        except Exception as e:
            print(f"❌ Error inesperado con Ollama: {e}")
            return f"Error inesperado al conectar con Ollama: {str(e)}"
    
    def generar_hipotesis(self, prompt, contexto_pdfs=""):
        """Genera hipótesis usando Ollama asegurando formato JSON"""
        prompt_hipotesis = f"""
Eres un experto en hardware de ordenadores. Basándote en los datos del usuario, genera 3 hipótesis sobre la configuración más adecuada.

DATOS DEL USUARIO:
{prompt}

Imprime SOLO UN JSON válido. Sin explicaciones previas, sin bloques tipo ```json:
[
    {{"nombre": "Configuración sugerida 1", "probabilidad": 0.85, "estado": "posible", "detalles": "breve justificación"}},
    {{"nombre": "Configuración sugerida 2", "probabilidad": 0.70, "estado": "posible", "detalles": "breve justificación"}},
    {{"nombre": "Configuración sugerida 3", "probabilidad": 0.50, "estado": "posible", "detalles": "breve justificación"}}
]
"""
        respuesta = self.consultar(prompt_hipotesis, contexto_pdfs)
        
        # En caso de error de conexión o error no controlado
        if "Error de conexión" in respuesta or "Error HTTP" in respuesta or "Error inesperado" in respuesta:
             return [{
                 "nombre": "OLLAMA NO RESPONDE", 
                 "probabilidad": 0, 
                 "estado": "error", 
                 "detalles": respuesta
             }]

        # Extraer JSON con regex previniendo basura (Markdown etc)
        try:
            match = re.search(r'\[\s*\{.*?\}\s*\]', respuesta, re.DOTALL)
            if match:
                return json.loads(match.group(0))
            else:
                return json.loads(respuesta)
        except Exception as e:
            print(f"⚠️ Error extrayendo JSON de la respuesta: {e}")
            return [
                {
                    "nombre": "Error de parseo", 
                    "probabilidad": 0.0, 
                    "estado": "error", 
                    "detalles": "El asistente generó texto pero no pudo ser leído como JSON."
                }
            ]
    
    def buscar_en_internet(self, consulta):
        """Busca fuentes reales en internet basándose en las necesidades del usuario"""
        import urllib.request
        import urllib.parse
        import re
        import datetime
        
        resultados = []
        try:
            # Extraer algunas palabras para no hacer la query gigante
            palabras = [p for p in consulta.split() if len(p) > 3]
            query_limpia = " ".join(palabras[:6]) + " componentes pc tienda"
            q = urllib.parse.quote_plus(query_limpia)
            
            # Usar HTML simplificado de DuckDuckGo para evitar bloqueos
            req = urllib.request.Request(
                f"https://html.duckduckgo.com/html/?q={q}", 
                headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'}
            )
            
            with urllib.request.urlopen(req, timeout=5) as response:
                html = response.read().decode('utf-8')
                
                # Regex para encontrar enlaces de búsqueda orgánica en DuckDuckGo
                enlaces = re.findall(r'<a class="result__url" href="([^"]+)">(.*?)</a>', html)
                
                # Regex para los fragmentos de texto
                fragmentos = re.findall(r'<a class="result__snippet[^>]*>(.*?)</a>', html)
                
                for idx, (url, display) in enumerate(enlaces[:3]):
                    # Limpiar la URL de la redirección de DuckDuckGo si existe
                    if 'uddg=' in url:
                        real_url = urllib.parse.unquote(url.split('uddg=')[1].split('&')[0])
                    else:
                        real_url = url
                        
                    if real_url.startswith('//'):
                        real_url = "https:" + real_url
                        
                    # Extraer dominio de la URL de forma segura
                    try:
                        dominio = real_url.split('/')[2]
                    except:
                        dominio = "Fuente Web"
                        
                    # Sacar el snippet correspondiente
                    frag_limpio = "Búsqueda web automática."
                    if idx < len(fragmentos):
                        # Limpiar tags HTML (<b> tags)
                        frag_limpio = re.sub(r'<[^>]+>', '', fragmentos[idx])[:100] + "..."
                        
                    resultados.append({
                        "titulo": f"Búsqueda automática ({dominio})", 
                        "url": real_url, 
                        "fragmento": frag_limpio, 
                        "fecha": datetime.datetime.now().strftime("%d/%m/%Y")
                    })
        except Exception as e:
            print(f"⚠️ Error al buscar en internet de verdad: {e}")
            
        return resultados
    
    def generar_diagnostico(self, prompt, contexto_pdfs="", modo="Local (solo PDFs)"):
        """Genera diagnóstico usando Ollama con formateos explícitos"""
        
        prompt_diagnostico = f"""
Eres un experto en hardware español y debes proponer un presupuesto. Usa los datos del usuario y PDFs para tu respuesta.

DATOS DEL USUARIO E HIPÓTESIS SELECCIONADA:
{prompt}

Proporciona tu respuesta utilizando EXACTAMENTE Y SÓLO este formato:

DIAGNÓSTICO:
[Lista componentes propuestos. Si es en España, precios en € con IVA aproximado]

JUSTIFICACIÓN:
[Explica por qué has elegido cada parte asegurando compatibilidad]

FUENTES:
[Añade 1 o 2 URLs reales de tiendas como pccomponentes o amazon si lo sabes]
"""
        respuesta = self.consultar(prompt_diagnostico, contexto_pdfs)
        
        # Parseo de respuestas tolerantes a formato libre usando regex simple
        diagnostico = ""
        justificacion = ""
        fuentes_diagnostico = []
        
        if "Error de conexión" in respuesta or "Error HTTP" in respuesta or "Error inesperado" in respuesta:
            return respuesta, "No se generó justificación por un error en Ollama o la red.", []

        if "DIAGNÓSTICO:" in respuesta.upper():
            try:
                # Partimos de forma ignóstica a mayúsculas
                partes = re.split(r'JUSTIFICACI[ÓO]N:', respuesta, flags=re.IGNORECASE)
                diag_part = re.split(r'DIAGN[ÓO]STICO:', partes[0], flags=re.IGNORECASE)
                diagnostico = diag_part[1].strip() if len(diag_part) > 1 else partes[0].strip()
                
                if len(partes) > 1:
                    parte_justificacion = partes[1]
                    # Por si agregó FUENTES: extra
                    if "FUENTES:" in parte_justificacion.upper():
                        subpartes = re.split(r'FUENTES:', parte_justificacion, flags=re.IGNORECASE)
                        justificacion = subpartes[0].strip()
                        
                        # Extraer todo lo que parezca una URL
                        texto_urls = subpartes[1]
                        urls = re.findall(r'(https?://[^\s\)]+)', texto_urls)
                        for idx, u in enumerate(urls[:2]):
                            fuentes_diagnostico.append({
                                "titulo": "URL sugerida por la Inteligencia Artificial",
                                "url": u,
                                "fragmento": "Enlace directo recomendado por el modelo",
                                "fecha": datetime.datetime.now().strftime("%d/%m/%Y")
                            })
                    else:
                        justificacion = parte_justificacion.strip()
            except Exception as e:
                import traceback
                traza = traceback.format_exc()
                print(f"⚠️ Error partiendo la respuesta: {traza}")
                diagnostico = respuesta
                justificacion = f"Error en regex: {str(e)}\n\n{traza}"
        else:
            diagnostico = respuesta
            justificacion = "El LLM no adjuntó una sección de JUSTIFICACIÓN estructurada."
        
        fuentes_web = []
        if modo == "Web (PDFs + Internet)":
            fuentes_web = self.buscar_en_internet(prompt[:100])
        
        todas_fuentes = fuentes_diagnostico + fuentes_web
        return diagnostico, justificacion, todas_fuentes