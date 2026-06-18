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
        self.modelo = modelo
        self._verificado = True
    
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
        self._seleccionar_modelo_disponible()
        
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
    
    def generar_hipotesis(self, prompt, contexto_pdfs="", modo="Local (solo PDFs)"):
        """Genera hipótesis usando Ollama asegurando formato JSON"""
        
        if modo == "Local (solo PDFs)":
            instruccion_fuente = """IMPORTANTE: Basa tus recomendaciones EXCLUSIVAMENTE en la información contenida en los PDFs locales proporcionados más abajo.
Solo recomienda componentes, marcas y modelos que aparezcan mencionados en dichos documentos.
Si los PDFs no contienen información suficiente, indícalo en los detalles de cada hipótesis.
NO inventes datos ni uses conocimiento externo que no esté en los PDFs."""
        else:
            instruccion_fuente = """Usa la información de los PDFs locales proporcionados como referencia principal y contrástalos con tu conocimiento general.
Si los PDFs mencionan componentes o precios, priorízalos, pero puedes complementar con información adicional."""
        
        prompt_hipotesis = f"""
Eres un experto en hardware de ordenadores.

{instruccion_fuente}

Basándote en los datos del usuario, genera 3 hipótesis sobre la configuración más adecuada.

REGLAS OBLIGATORIAS:
1. Si el usuario YA POSEE componentes, DEBES incluirlos tal cual en TODAS las configuraciones. NO los reemplaces ni los ignores.
2. Solo propón componentes NUEVOS para las categorías que el usuario NO tiene.
3. Cada configuración debe ser un PC COMPLETO (CPU, Placa Base, RAM, GPU, Fuente, Almacenamiento, Caja).
4. Indica claramente qué componentes son los que ya tiene ("[YA TIENE]") y cuáles son nuevos.
5. El presupuesto indicado es SOLO para los componentes nuevos, no para los que ya posee.

DATOS DEL USUARIO:
{prompt}

Imprime SOLO UN JSON válido. Sin explicaciones previas, sin bloques tipo ```json:
[
    {{"nombre": "Config. 1 (resumen breve de piezas clave)", "probabilidad": 0.85, "estado": "posible", "detalles": "Lista TODOS los componentes indicando [YA TIENE] o [NUEVO] y justifica brevemente"}},
    {{"nombre": "Config. 2 (resumen breve de piezas clave)", "probabilidad": 0.70, "estado": "posible", "detalles": "Lista TODOS los componentes indicando [YA TIENE] o [NUEVO] y justifica brevemente"}},
    {{"nombre": "Config. 3 (resumen breve de piezas clave)", "probabilidad": 0.50, "estado": "posible", "detalles": "Lista TODOS los componentes indicando [YA TIENE] o [NUEVO] y justifica brevemente"}}
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

        # Extraer JSON con múltiples estrategias de parseo
        try:
            hipotesis = self._parsear_json_hipotesis(respuesta)
            if hipotesis:
                return hipotesis
        except Exception as e:
            print(f"⚠️ Error extrayendo JSON de la respuesta: {e}")
        
        # Último recurso: construir hipótesis a partir del texto libre
        print("⚠️ No se pudo parsear JSON, construyendo hipótesis desde texto libre")
        return [{
            "nombre": "Configuración sugerida por IA",
            "probabilidad": 0.75,
            "estado": "posible",
            "detalles": respuesta[:1500] if len(respuesta) > 1500 else respuesta
        }]
    
    def _parsear_json_hipotesis(self, respuesta):
        """Intenta parsear la respuesta del LLM como JSON con múltiples estrategias"""
        # Limpiar bloques de pensamiento tipo <think>...</think>
        respuesta_limpia = re.sub(r'<think>.*?</think>', '', respuesta, flags=re.DOTALL).strip()
        
        # Eliminar bloques de código markdown ```json ... ```
        match_bloque = re.search(r'```(?:json)?\s*(\[.*?\])\s*```', respuesta_limpia, re.DOTALL)
        if match_bloque:
            try:
                return json.loads(match_bloque.group(1))
            except json.JSONDecodeError:
                pass
        
        # Estrategia 1: buscar el array JSON completo con regex greedy
        match = re.search(r'\[\s*\{.*\}\s*\]', respuesta_limpia, re.DOTALL)
        if match:
            try:
                return json.loads(match.group(0))
            except json.JSONDecodeError:
                # Intentar reparar JSON común (trailing commas, etc)
                texto_json = match.group(0)
                texto_json = re.sub(r',\s*([}\]])', r'\1', texto_json)  # trailing commas
                try:
                    return json.loads(texto_json)
                except json.JSONDecodeError:
                    pass
        
        # Estrategia 2: buscar objetos JSON individuales y construir array
        objetos = re.findall(r'\{[^{}]*"nombre"[^{}]*\}', respuesta_limpia, re.DOTALL)
        if objetos:
            resultado = []
            for obj_str in objetos[:3]:
                try:
                    resultado.append(json.loads(obj_str))
                except json.JSONDecodeError:
                    pass
            if resultado:
                return resultado
        
        # Estrategia 3: parseo directo
        try:
            return json.loads(respuesta_limpia)
        except json.JSONDecodeError:
            pass
        
        return None
    
    def _validar_url(self, url, timeout=5):
        """
        Verifica que una URL existe y responde con código HTTP < 400.
        Devuelve True si la URL es accesible, False en caso contrario.
        """
        import ssl
        try:
            ctx = ssl.create_default_context()
            ctx.check_hostname = False
            ctx.verify_mode = ssl.CERT_NONE

            req = urllib.request.Request(
                url,
                method='HEAD',
                headers={
                    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) '
                                  'AppleWebKit/537.36 (KHTML, like Gecko) '
                                  'Chrome/125.0.0.0 Safari/537.36'
                }
            )
            with urllib.request.urlopen(req, timeout=timeout, context=ctx) as response:
                return response.status < 400
        except Exception:
            return False

    def _filtrar_urls_validas(self, resultados, max_validos=5):
        """
        Recorre la lista de resultados y descarta los que tienen URLs rotas.
        Devuelve solo los que responden correctamente (hasta max_validos).
        """
        validos = []
        for r in resultados:
            url = r.get('url', '')
            if not url or not url.startswith('http'):
                continue
            if self._validar_url(url):
                validos.append(r)
                print(f"✅ URL válida: {url}")
                if len(validos) >= max_validos:
                    break
            else:
                print(f"❌ URL rota descartada: {url}")
        return validos

    def buscar_en_internet(self, consulta):
        """Busca fuentes reales en internet. Usa Google Search API si está configurada, si no DuckDuckGo."""
        google_cfg = self.config.get('google_search', {})
        api_key = google_cfg.get('api_key', '')
        cx = google_cfg.get('cx', '')
        habilitado = google_cfg.get('habilitado', False)
        
        if habilitado and api_key and cx:
            resultados = self._buscar_google_api(consulta, api_key, cx)
            if resultados:
                return self._filtrar_urls_validas(resultados)
            print("⚠️ Google Search API falló, usando DuckDuckGo como fallback")
        
        resultados = self._buscar_duckduckgo(consulta)
        return self._filtrar_urls_validas(resultados)
    
    def _buscar_google_api(self, consulta, api_key, cx):
        """Búsqueda real usando Google Custom Search JSON API"""
        import urllib.request
        import urllib.parse
        import ssl
        
        resultados = []
        try:
            # Construir query orientada a tiendas de componentes
            palabras = [p for p in consulta.split() if len(p) > 3]
            query_limpia = " ".join(palabras[:8]) + " precio comprar"
            q = urllib.parse.quote_plus(query_limpia)
            
            url = (f"https://www.googleapis.com/customsearch/v1"
                   f"?key={api_key}&cx={cx}&q={q}&num=5&lr=lang_es&gl=es")
            
            req = urllib.request.Request(url, headers={
                'Accept': 'application/json',
                'User-Agent': 'PCConfigExpert/1.0'
            })
            
            ctx = ssl.create_default_context()
            with urllib.request.urlopen(req, timeout=10, context=ctx) as response:
                data = json.loads(response.read().decode('utf-8'))
            
            for item in data.get('items', [])[:5]:
                titulo = item.get('title', 'Sin título')
                link = item.get('link', '')
                snippet = item.get('snippet', 'Sin descripción')
                
                # Extraer dominio
                try:
                    dominio = link.split('/')[2]
                except Exception:
                    dominio = 'Web'
                
                resultados.append({
                    "titulo": titulo,
                    "url": link,
                    "fragmento": snippet[:200],
                    "fecha": datetime.datetime.now().strftime("%d/%m/%Y"),
                    "fuente": f"Google Search ({dominio})"
                })
            
            print(f"✅ Google Search API: {len(resultados)} resultados obtenidos")
            
        except urllib.error.HTTPError as e:
            error_body = e.read().decode('utf-8') if hasattr(e, 'read') else str(e)
            print(f"❌ Error Google Search API ({e.code}): {error_body[:200]}")
        except Exception as e:
            print(f"❌ Error en Google Search API: {e}")
        
        return resultados
    
    def _buscar_duckduckgo(self, consulta):
        """Búsqueda fallback usando DuckDuckGo (sin API key)"""
        import urllib.request
        import urllib.parse
        import ssl
        
        resultados = []
        
        # Construir query
        palabras = [p for p in consulta.split() if len(p) > 3]
        query_limpia = " ".join(palabras[:6]) + " componentes pc precio"
        q = urllib.parse.quote_plus(query_limpia)
        
        ctx = ssl.create_default_context()
        ctx.check_hostname = False
        ctx.verify_mode = ssl.CERT_NONE
        
        # Estrategia 1: DuckDuckGo API (JSON, más fiable)
        try:
            req = urllib.request.Request(
                f"https://api.duckduckgo.com/?q={q}&format=json&no_redirect=1&no_html=1&skip_disambig=1",
                headers={'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36'}
            )
            with urllib.request.urlopen(req, timeout=8, context=ctx) as response:
                data = json.loads(response.read().decode('utf-8'))
                
                # Resultados relacionados
                for item in data.get('RelatedTopics', [])[:10]:
                    if 'FirstURL' in item and item['FirstURL']:
                        texto = item.get('Text', 'Sin descripción')
                        url = item['FirstURL']
                        # Descartar URLs internas de DuckDuckGo
                        if 'duckduckgo.com' in url:
                            continue
                        # Descartar URLs de Wikipedia (suelen ser irrelevantes para componentes)
                        if 'wikipedia.org' in url:
                            continue
                        try:
                            dominio = url.split('/')[2]
                        except Exception:
                            dominio = "Web"
                        resultados.append({
                            "titulo": texto[:80],
                            "url": url,
                            "fragmento": texto[:200],
                            "fecha": datetime.datetime.now().strftime("%d/%m/%Y"),
                            "fuente": f"DuckDuckGo ({dominio})"
                        })
        except Exception as e:
            print(f"⚠️ DuckDuckGo API JSON falló: {e}")
        
        # Estrategia 2: DuckDuckGo HTML con múltiples patrones regex
        if not resultados:
            try:
                req = urllib.request.Request(
                    f"https://html.duckduckgo.com/html/?q={q}",
                    headers={'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36'}
                )
                with urllib.request.urlopen(req, timeout=8, context=ctx) as response:
                    html = response.read().decode('utf-8')
                    
                    # Múltiples patrones para extraer resultados (DuckDuckGo cambia el HTML)
                    patrones_url = [
                        r'<a[^>]*class="[^"]*result__url[^"]*"[^>]*href="([^"]+)"[^>]*>(.*?)</a>',
                        r'<a[^>]*rel="nofollow"[^>]*class="[^"]*result__a[^"]*"[^>]*href="([^"]+)"[^>]*>(.*?)</a>',
                        r'<a[^>]*class="[^"]*result__a[^"]*"[^>]*href="([^"]+)"[^>]*>(.*?)</a>',
                        r'href="(https?://(?!duckduckgo)[^"]+)"[^>]*>(.*?)</a>',
                    ]
                    
                    patrones_snippet = [
                        r'<a[^>]*class="[^"]*result__snippet[^"]*"[^>]*>(.*?)</a>',
                        r'<td[^>]*class="[^"]*result__snippet[^"]*"[^>]*>(.*?)</td>',
                        r'class="[^"]*snippet[^"]*"[^>]*>(.*?)</',
                    ]
                    
                    enlaces = []
                    for patron in patrones_url:
                        enlaces = re.findall(patron, html, re.DOTALL)
                        if enlaces:
                            break
                    
                    fragmentos = []
                    for patron in patrones_snippet:
                        fragmentos = re.findall(patron, html, re.DOTALL)
                        if fragmentos:
                            break
                    
                    for idx, (url, display) in enumerate(enlaces[:5]):
                        if 'uddg=' in url:
                            real_url = urllib.parse.unquote(url.split('uddg=')[1].split('&')[0])
                        else:
                            real_url = url
                        if real_url.startswith('//'):
                            real_url = "https:" + real_url
                        
                        # Filtrar URLs internas de DuckDuckGo
                        if 'duckduckgo.com' in real_url:
                            continue
                        
                        try:
                            dominio = real_url.split('/')[2]
                        except Exception:
                            dominio = "Web"
                        
                        frag = "Resultado de búsqueda web."
                        if idx < len(fragmentos):
                            frag = re.sub(r'<[^>]+>', '', fragmentos[idx]).strip()[:200]
                        
                        titulo = re.sub(r'<[^>]+>', '', display).strip()
                        if not titulo:
                            titulo = dominio
                        
                        resultados.append({
                            "titulo": titulo,
                            "url": real_url,
                            "fragmento": frag,
                            "fecha": datetime.datetime.now().strftime("%d/%m/%Y"),
                            "fuente": f"DuckDuckGo ({dominio})"
                        })
            except Exception as e:
                print(f"⚠️ DuckDuckGo HTML falló: {e}")
        
        print(f"✅ DuckDuckGo: {len(resultados)} resultados obtenidos")
        return resultados
    
    def _recalcular_total(self, diagnostico):
        """Extrae precios de componentes NUEVOS del texto y recalcula el total correctamente"""
        # Buscar líneas con (NUEVO) y un precio en €
        precios = re.findall(r'(?:NUEVO|nuevo)\).*?(\d+)[€\s]*(?:aprox|€)', diagnostico)
        if not precios:
            # Intentar patrón alternativo: número seguido de €
            precios = re.findall(r'(?:NUEVO|nuevo).*?(\d+)\s*€', diagnostico)
        
        if precios:
            total = sum(int(p) for p in precios)
            # Eliminar cualquier línea TOTAL existente del LLM
            diagnostico = re.sub(r'\n*.*TOTAL.*(?:nuevo|€).*', '', diagnostico, flags=re.IGNORECASE).rstrip()
            diagnostico += f"\n\nTOTAL solo de componentes nuevos: {total}€"
            print(f"🧮 Total recalculado: {' + '.join(precios)} = {total}€")
        
        return diagnostico
    
    def analizar_compatibilidad(self, componentes, contexto_pdfs=""):
        """Analiza si una lista de componentes es compatible. Devuelve (es_compatible: bool, explicacion: str)"""

        # Si no hay base documental local, no se debe inventar compatibilidad.
        if (not contexto_pdfs) or ("No hay PDFs cargados" in contexto_pdfs):
            return False, (
                "VEREDICTO: NO DETERMINADO\n"
                "EXPLICACION: No hay evidencia en PDFs locales para validar compatibilidad. "
                "Carga al menos un PDF de compatibilidad para emitir veredicto técnico."
            )
        
        # Formatear el diccionario a un texto legible
        componentes_texto = "\n".join([f"- {k}: {v}" for k, v in componentes.items()])
        
        prompt = f"""
Eres un experto en hardware. El usuario indica que YA POSEE los siguientes componentes:
{componentes_texto}

Reglas obligatorias para tu análisis:
0. Debes basarte EXCLUSIVAMENTE en la información de "INFORMACION EXTRAIDA DE PDFS LOCALES". No uses conocimiento externo.
1. Si un componente parece inventado, es falso, no existe en el mercado, o en el texto dice literalmente "Modelo no especificado", ignóralo (no lo cuentes como incompatibilidad).
2. Analiza SOLO si existe alguna incompatibilidad técnica REAL entre los componentes especificados (por ejemplo: procesador con socket incompatible con la placa base, RAM DDR4 en placa DDR5, fuente de alimentación insuficiente, etc.).
3. Si solo hay 0 o 1 componentes reales especificados, no puede haber incompatibilidad entre ellos.
4. Si en los PDFs no aparece evidencia explícita para confirmar compatibilidad o incompatibilidad, responde "NO DETERMINADO".
5. En EXPLICACION cita literalmente el dato clave de los PDFs (por ejemplo socket/chipset) y relaciónalo con los componentes.

RESPONDE OBLIGATORIAMENTE con este formato exacto:
VEREDICTO: COMPATIBLE, INCOMPATIBLE o NO DETERMINADO
EXPLICACION: (breve explicación directa de por qué son compatibles o qué incompatibilidad existe)
"""
        respuesta = self.consultar(prompt, contexto_pdfs)
        
        # Parsear el veredicto
        es_compatible = True
        respuesta_up = respuesta.upper()

        # Priorizar línea explícita VEREDICTO si existe
        match_veredicto = re.search(r'VEREDICTO\s*:\s*([A-ZÁÉÍÓÚ ]+)', respuesta_up)
        if match_veredicto:
            etiqueta = match_veredicto.group(1).strip()
            es_compatible = etiqueta.startswith("COMPATIBLE")
        else:
            # Fallback por heurística textual
            cabecera = respuesta_up.split("EXPLICACION")[0] if "EXPLICACION" in respuesta_up else respuesta_up[:120]
            if "INCOMPATIBLE" in cabecera or "NO DETERMINADO" in cabecera:
                es_compatible = False
        
        return es_compatible, respuesta

    def generar_diagnostico(self, prompt, contexto_pdfs="", modo="Local (solo PDFs)"):
        """Genera diagnóstico usando Ollama con formateos explícitos"""
        
        if modo == "Local (solo PDFs)":
            instruccion_fuente = """IMPORTANTE: Basa tu diagnóstico y recomendaciones EXCLUSIVAMENTE en la información contenida en los PDFs locales proporcionados.
Solo recomienda componentes, marcas, modelos y precios que aparezcan en dichos documentos.
Si los PDFs no contienen información suficiente para algún componente, indícalo claramente.
NO inventes datos ni uses conocimiento externo que no esté en los PDFs."""
        else:
            instruccion_fuente = """Usa la información de los PDFs locales como referencia principal y contrástalos con tu conocimiento general y fuentes web.
Si los PDFs mencionan componentes o precios, priorízalos, pero puedes complementar con información adicional de internet."""
        
        prompt_diagnostico = f"""
Eres un experto en hardware español y debes proponer un presupuesto.

{instruccion_fuente}

REGLAS OBLIGATORIAS:
1. Si el usuario YA POSEE componentes, DEBES mantenerlos en la configuración final. NO los reemplaces.
2. Solo recomienda componentes NUEVOS para lo que el usuario NO tiene.
3. Marca cada componente como [YA TIENE] o [NUEVO] en el listado.
4. El presupuesto debe reflejar SOLO el coste de los componentes NUEVOS.
5. Asegura compatibilidad entre los componentes existentes y los nuevos.

DATOS DEL USUARIO E HIPÓTESIS SELECCIONADA:
{prompt}

Proporciona tu respuesta utilizando EXACTAMENTE Y SÓLO este formato:

DIAGNÓSTICO:
[Lista la configuración COMPLETA del PC: Placa base, CPU, GPU, RAM, Almacenamiento, Fuente de alimentación y Caja. Marca cada uno como [YA TIENE] o [NUEVO]. Para los nuevos, incluye precios en € con IVA aproximado. NO calcules el total, yo lo haré.]

JUSTIFICACIÓN:
[Explica por qué has elegido cada componente nuevo, asegurando compatibilidad con los que ya posee el usuario]

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
                
                # Recalcular el total de componentes NUEVOS con Python (el LLM suma mal)
                diagnostico = self._recalcular_total(diagnostico)
                
                if len(partes) > 1:
                    parte_justificacion = partes[1]
                    # Por si agregó FUENTES: extra
                    if "FUENTES:" in parte_justificacion.upper():
                        subpartes = re.split(r'FUENTES:', parte_justificacion, flags=re.IGNORECASE)
                        justificacion = subpartes[0].strip()
                        
                        # Extraer todo lo que parezca una URL y validarla antes de añadirla
                        texto_urls = subpartes[1]
                        urls = re.findall(r'(https?://[^\s\)]+)', texto_urls)
                        for idx, u in enumerate(urls[:4]):
                            if self._validar_url(u):
                                fuentes_diagnostico.append({
                                    "titulo": "URL verificada sugerida por la IA",
                                    "url": u,
                                    "fragmento": "Enlace directo verificado y recomendado por el modelo",
                                    "fecha": datetime.datetime.now().strftime("%d/%m/%Y")
                                })
                                print(f"✅ URL del LLM válida: {u}")
                            else:
                                print(f"❌ URL del LLM alucinada/rota, descartada: {u}")
                            if len(fuentes_diagnostico) >= 2:
                                break
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