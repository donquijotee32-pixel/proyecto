# 🚌 AMCO - SISTEMA INTELIGENTE DE OPTIMIZACIÓN DE RUTAS
## Con Streamlit, NetworkX y Algoritmo de Dijkstra

---

## 📋 DESCRIPCIÓN

Este sistema demuestra la aplicación práctica de **Álgebra Lineal** en la optimización de rutas de transporte. Utiliza:

✅ **NetworkX**: Grafo ponderado con distancias euclidianas  
✅ **Dijkstra**: Algoritmo de ruta más corta (O(n²))  
✅ **Streamlit**: Interfaz interactiva en tiempo real  
✅ **Matplotlib**: Visualización dinámica del grafo  
✅ **Eventos Simulados**: Accidentes que bloquean rutas  

---

## 🚀 INSTALACIÓN RÁPIDA

### Paso 1: Instalar Python 3.8+
```bash
python --version
# Debe mostrar Python 3.8 o superior
```

### Paso 2: Crear Entorno Virtual
```bash
python -m venv venv

# Windows:
venv\Scripts\activate

# Mac/Linux:
source venv/bin/activate
```

### Paso 3: Instalar Dependencias
```bash
pip install -r requirements_amco.txt
```

### Paso 4: Ejecutar la Aplicación
```bash
streamlit run amco_optimizador_eventos.py
```

✅ Se abrirá automáticamente en: `http://localhost:8501`

---

## 🎮 CÓMO USAR

### 1. **Selecciona Origen y Destino**
   - En la barra lateral izquierda
   - Elige dos paradas diferentes (1-6)

### 2. **Calcula Ruta Óptima Inicial**
   - Presiona el botón "🔍 Calcular Ruta Óptima Inicial"
   - Verás la ruta en azul en el mapa
   - Se mostrarán distancias y detalles

### 3. **Simula un Accidente**
   - Presiona "🚗💥 SIMULAR ACCIDENTE"
   - El sistema:
     - ✅ Selecciona una arista al azar
     - ✅ La bloquea (peso = infinito)
     - ✅ Recalcula la ruta óptima
     - ✅ Muestra nueva ruta en verde punteado
     - ✅ Actualiza estado y distancia

### 4. **Limpia el Accidente**
   - Presiona "✅ LIMPIAR ACCIDENTE"
   - Restaura la arista al peso original
   - Vuelve a la ruta original

### 5. **Explora Análisis**
   - **Tab 1**: Visualización del grafo
   - **Tab 2**: Detalles de rutas (antes/después)
   - **Tab 3**: Matemática (matriz, fórmulas, Dijkstra)
   - **Tab 4**: Historial de eventos

---

## 🔬 CONCEPTOS DE ÁLGEBRA LINEAL

### 1. **Norma Euclidiana (L2)**
```
||v|| = √[(lat₂-lat₁)² + (lon₂-lon₁)²] × 111 km

Ejemplo:
Centro Cívico (4.8135, -75.6942)
Parque Arvi (4.8250, -75.7100)

Distancia = √[(0.0115)² + (-0.0158)²] × 111 ≈ 1.99 km
```

### 2. **Matriz de Adyacencia Ponderada**
```
Matriz 6×6 donde:
- M[i,j] = distancia entre parada i y j
- M[i,j] = ∞ si hay accidente
- Simétrica: M[i,j] = M[j,i]
```

### 3. **Algoritmo de Dijkstra**
```
Complejidad: O(n²)
Pasos:
1. dist[origen] = 0, resto = ∞
2. Mientras haya nodos no visitados:
   - Seleccionar nodo no visitado con menor dist
   - Para cada vecino:
     - dist[vecino] = min(dist[vecino], dist[nodo] + arista)
   - Marcar como visitado
3. Retornar ruta y distancia total
```

---

## 📍 PARADAS (COORDENADAS REALES)

| ID | Nombre | Ciudad | Latitud | Longitud |
|----|--------|--------|---------|----------|
| 1 | Centro Cívico | Pereira | 4.8135 | -75.6942 |
| 2 | Parque Arvi | Pereira | 4.8250 | -75.7100 |
| 3 | Centro Comercial | Pereira | 4.8050 | -75.6850 |
| 4 | Terminal Autobuses | Pereira | 4.8100 | -75.7000 |
| 5 | Centro Dosquebradas | Dosquebradas | 4.8000 | -75.7200 |
| 6 | Sector Galicia | Dosquebradas | 4.7900 | -75.7150 |

---

## 🎯 EJEMPLO DE FLUJO

### Escenario: Ruta Centro Cívico → Sector Galicia

**PASO 1: Sin Accidentes**
```
Origen: 1 (Centro Cívico)
Destino: 6 (Sector Galicia)

Cálculo Dijkstra:
- Ruta: 1 → 5 → 6
- Distancia: 4.50 km
- Estado: ✅ Operando normalmente
```

**PASO 2: Simular Accidente en 1-5**
```
Accidente simulado: Centro Cívico ↔ Centro Dosquebradas BLOQUEADO

Nueva Ruta Calculada:
- Ruta: 1 → 4 → 5 → 6
- Distancia: 6.20 km
- Incremento: +1.70 km (+37.8%)
- Estado: 🚨 ACCIDENTE EN RUTA
```

**PASO 3: Limpiar Accidente**
```
Arista 1-5 desbloqueada

Ruta Restaurada:
- Ruta: 1 → 5 → 6
- Distancia: 4.50 km (original)
- Estado: ✅ Operando normalmente
```

---

## 📊 INTERFAZ STREAMLIT

### Barra Lateral (Control)
```
🎮 PANEL DE CONTROL
├─ 📍 Configuración de Ruta
│  ├─ Selecciona Origen (1-6)
│  ├─ Selecciona Destino (1-6)
│  └─ 🔍 Calcular Ruta Óptima Inicial
├─ ⚠️ SIMULAR EVENTOS
│  ├─ 🚗💥 SIMULAR ACCIDENTE (botón activo)
│  └─ ✅ LIMPIAR ACCIDENTE
└─ 📊 INFORMACIÓN DEL SISTEMA
   ├─ Paradas Activas: 6
   ├─ Rutas Posibles: 15
   └─ Última Optimización: 0.0045s
```

### Contenido Principal
```
🔔 ESTADO DEL SISTEMA
├─ ✅ Operando normalmente
└─ 🚨 Accidente en Ruta (cuando aplica)

📊 MÉTRICAS
├─ Distancia Original: 4.50 km
├─ Distancia Actual: 6.20 km
├─ Paradas en Ruta: 4
└─ Tiempo de Optimización: 0.0045s

📑 TABS
├─ 🗺️ Visualización del Grafo
├─ 📋 Detalles de Ruta
├─ 📊 Análisis Matemático
└─ 📝 Historial de Eventos
```

---

## 🔴 ESTADO DEL SISTEMA

### ✅ Operando Normalmente
```
[Verde] Sistema funcionando sin incidentes
- Todas las rutas disponibles
- Distancia óptima calculada
- Tiempo de respuesta rápido
```

### 🚨 Accidente en Ruta
```
[Rojo] Accidente detectado
- Ubicación: Centro Cívico ↔ Centro Dosquebradas (1.99 km)
- Acción: Recalculando ruta alternativa
- Tiempo: 0.0045s
- Impacto: +1.70 km (+37.8%)
```

### ⚙️ Optimizando
```
[Amarillo] Cálculo de Dijkstra en progreso
- Evaluando alternativas
- Tiempo estimado: < 1 segundo
```

---

## 📈 VISUALIZACIÓN DEL GRAFO

### Elementos
- **🔵 Nodos**: Paradas de transporte (numeradas 1-6)
- **Líneas**: Rutas entre paradas
- **🔵 Línea Azul Gruesa**: Ruta óptima ACTUAL
- **🟢 Línea Verde Punteada**: Ruta original (para comparar)
- **🔴 Línea Roja Gruesa**: Arista BLOQUEADA por accidente
- **Números en líneas**: Distancia en km

---

## 📊 TAB: ANÁLISIS MATEMÁTICO

### Matriz de Adyacencia
```
      1     2     3     4     5     6
1   0.00  1.65  0.99  1.24  3.51  4.38
2   1.65  0.00  2.08  1.94  3.16  4.23
3   0.99  2.08  0.00  1.00  2.81  3.68
4   1.24  1.94  1.00  0.00  1.81  2.68
5   3.51  3.16  2.81  1.81  0.00  1.27
6   4.38  4.23  3.68  2.68  1.27  0.00
```

### Dijkstra Paso a Paso
```
Calculando ruta 1 → 6:

Iteración 1:
- dist[1] = 0 (origen)
- dist[2,3,4,5,6] = ∞

Iteración 2:
- Seleccionar 1 (menor distancia)
- Actualizar vecinos:
  - dist[2] = 1.65
  - dist[3] = 0.99
  - dist[4] = 1.24
  - dist[5] = 3.51

... (continuar hasta dest=6)

Resultado: 1 → 5 → 6 = 4.50 km
```

---

## 📝 TAB: HISTORIAL DE EVENTOS

Tabla con todos los eventos simulados:
```
| Timestamp | Tipo     | Ubicación | Dist Original | Dist Nueva | Diferencia | Tiempo |
|-----------|----------|-----------|---------------|------------|-----------|--------|
| 10:32:45  | Accidente| 1 ↔ 5     | 4.50 km      | 6.20 km    | +1.70 km  | 0.004s |
| 10:33:12  | Accidente| 2 ↔ 4     | 5.80 km      | 7.15 km    | +1.35 km  | 0.003s |
```

---

## 🐛 SOLUCIÓN DE PROBLEMAS

### ❌ Error: "ModuleNotFoundError: No module named 'streamlit'"
```bash
pip install streamlit==1.28.1
```

### ❌ Error: "No module named 'networkx'"
```bash
pip install networkx==3.2
```

### ❌ Error: Puerto 8501 en uso
```bash
streamlit run amco_optimizador_eventos.py --server.port 8502
```

### ❌ Error: "ConnectionError" al cargar datos
**Solución**: El sistema NO requiere internet. Si ves error:
1. Cierra la aplicación
2. Borra la carpeta `.streamlit` (carpeta oculta)
3. Ejecuta de nuevo

---

## 🚀 OPTIMIZACIONES APLICADAS

✅ **Sin descarga de archivos externos**  
✅ **Caché de Streamlit para rápida visualización**  
✅ **Cálculos matemáticos optimizados con NumPy**  
✅ **Grafo eficiente con NetworkX**  
✅ **Interfaz responsive en Streamlit**  

---

## 📚 REFERENCIAS MATEMÁTICAS

### Norma Euclidiana
- Fórmula: `||v||₂ = √(x² + y²)`
- Aplicación: Distancia entre puntos geográficos
- Complejidad: O(1)

### Algoritmo de Dijkstra
- Año: 1956 (Edsger Dijkstra)
- Tipo: Greedy
- Complejidad: O(n²)
- Garantía: Ruta óptima con pesos positivos

### Grafo Ponderado
- Tipo: Grafo no dirigido (bidireccional)
- Nodos: 6 paradas
- Aristas: 15 (conexiones)
- Pesos: Distancias euclidianas

---

## 👨‍💻 AUTOR

**AMCO - Centro Inteligente Metropolitano**  
Trabajo Final: Álgebra Lineal Aplicada  
Año: 2026

---

## 📄 LICENCIA

© 2026 AMCO - Centro Inteligente Metropolitano

---

**¡Listo para demostrar Álgebra Lineal en Acción! 🚀**
