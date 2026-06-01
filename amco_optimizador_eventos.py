"""
🚌 AMCO - SISTEMA DE OPTIMIZACIÓN DE RUTAS CON EVENTOS
=========================================================

Sistema avanzado que demuestra:
✅ Álgebra Lineal: Matrices de distancias, Dijkstra
✅ NetworkX: Grafo dinámico, cálculo de rutas óptimas
✅ Streamlit: Interfaz interactiva en tiempo real
✅ Optimización: Respuesta inmediata a eventos

Ejecución: streamlit run amco_optimizador_eventos.py

NOTA: Sin descarga de archivos externos. TODO integrado.
"""

import sys
import os

# Verificar Python 3.8+
if sys.version_info < (3, 8):
    print(f"Error: Se requiere Python 3.8 o superior")
    sys.exit(1)

import streamlit as st
import networkx as nx
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.patches import FancyArrowPatch
import time
from datetime import datetime

# ============================================
# CONFIGURACIÓN DE STREAMLIT
# ============================================
st.set_page_config(
    page_title="🚌 AMCO - Optimización de Rutas",
    page_icon="🚌",
    layout="wide",
    initial_sidebar_state="expanded"
)

# CSS personalizado
st.markdown("""
    <style>
    .stMetric {
        background-color: #f0f2f6;
        padding: 20px;
        border-radius: 10px;
        border-left: 5px solid #667eea;
    }
    .estado-normal {
        background-color: #d4edda;
        color: #155724;
        padding: 15px;
        border-radius: 5px;
        border-left: 5px solid #28a745;
    }
    .estado-alerta {
        background-color: #f8d7da;
        color: #721c24;
        padding: 15px;
        border-radius: 5px;
        border-left: 5px solid #dc3545;
    }
    .estado-optimizando {
        background-color: #fff3cd;
        color: #856404;
        padding: 15px;
        border-radius: 5px;
        border-left: 5px solid #ffc107;
    }
    </style>
""", unsafe_allow_html=True)

# ============================================
# VARIABLES DE SESIÓN
# ============================================
if 'grafo_original' not in st.session_state:
    st.session_state.grafo_original = None
    st.session_state.grafo_actual = None
    st.session_state.ruta_actual = []
    st.session_state.ruta_original = []
    st.session_state.estado = "Inicializando..."
    st.session_state.historial_eventos = []
    st.session_state.arista_bloqueada = None
    st.session_state.tiempo_calculo = 0
    st.session_state.paradas = []

# ============================================
# CLASE: SISTEMA DE TRANSPORTE
# ============================================
class SistemaTransporte:
    """
    Sistema de optimización de rutas con NetworkX y Dijkstra.
    Demuestra Álgebra Lineal aplicada a optimización.
    """
    
    def __init__(self):
        """Inicializa el sistema con paradas reales de Pereira y Dosquebradas"""
        
        # Paradas con coordenadas reales (lat, lon)
        self.paradas = {
            1: {"nombre": "Centro Cívico", "lat": 4.8135, "lon": -75.6942, "ciudad": "Pereira"},
            2: {"nombre": "Parque Arvi", "lat": 4.8250, "lon": -75.7100, "ciudad": "Pereira"},
            3: {"nombre": "Centro Comercial", "lat": 4.8050, "lon": -75.6850, "ciudad": "Pereira"},
            4: {"nombre": "Terminal Autobuses", "lat": 4.8100, "lon": -75.7000, "ciudad": "Pereira"},
            5: {"nombre": "Centro Dosquebradas", "lat": 4.8000, "lon": -75.7200, "ciudad": "Dosquebradas"},
            6: {"nombre": "Sector Galicia", "lat": 4.7900, "lon": -75.7150, "ciudad": "Dosquebradas"},
        }
        
        self.grafo = None
        self.crear_grafo()
    
    def distancia_euclidiana(self, p1, p2):
        """
        Calcula distancia euclidiana entre dos paradas.
        ÁLGEBRA LINEAL: Norma L2
        
        Fórmula: ||v|| = sqrt((lat2-lat1)² + (lon2-lon1)²) × 111 km
        """
        dlat = p2["lat"] - p1["lat"]
        dlon = p2["lon"] - p1["lon"]
        distancia_grados = np.sqrt(dlat**2 + dlon**2)
        distancia_km = distancia_grados * 111
        return round(distancia_km, 2)
    
    def crear_grafo(self):
        """
        Crea grafo completo (todos conectados con todos).
        Cada arista tiene peso = distancia euclidiana.
        
        ÁLGEBRA LINEAL: Matriz de adyacencia ponderada
        """
        self.grafo = nx.Graph()
        
        # Agregar nodos
        for nodo_id, parada in self.paradas.items():
            self.grafo.add_node(nodo_id, 
                              nombre=parada["nombre"],
                              lat=parada["lat"],
                              lon=parada["lon"])
        
        # Agregar aristas con pesos (distancias)
        parada_ids = list(self.paradas.keys())
        for i in range(len(parada_ids)):
            for j in range(i + 1, len(parada_ids)):
                nodo_i = parada_ids[i]
                nodo_j = parada_ids[j]
                
                distancia = self.distancia_euclidiana(
                    self.paradas[nodo_i],
                    self.paradas[nodo_j]
                )
                
                self.grafo.add_edge(nodo_i, nodo_j, weight=distancia)
    
    def calcular_ruta_optima(self, origen, destino):
        """
        Calcula la ruta más corta usando Dijkstra.
        
        ALGORITMO: Dijkstra (O(n²))
        Retorna: (distancia_total, lista_de_nodos)
        """
        try:
            if not nx.has_path(self.grafo, origen, destino):
                return None, []
            
            # Dijkstra nativo de NetworkX
            distancia = nx.dijkstra_path_length(self.grafo, origen, destino, weight='weight')
            ruta = nx.dijkstra_path(self.grafo, origen, destino, weight='weight')
            
            return round(distancia, 2), ruta
        except nx.exception.NodeNotFound:
            return None, []
    
    def bloquear_arista(self):
        """
        Selecciona una arista al azar y la bloquea (peso infinito).
        
        SIMULACIÓN DE EVENTO: Accidente
        """
        aristas = list(self.grafo.edges())
        if not aristas:
            return None, None
        
        # Seleccionar arista aleatoria
        arista = aristas[np.random.randint(0, len(aristas))]
        nodo1, nodo2 = arista
        
        # Guardar peso original
        peso_original = self.grafo[nodo1][nodo2]['weight']
        
        # Bloquear (peso infinito)
        self.grafo[nodo1][nodo2]['weight'] = float('inf')
        
        parada1 = self.paradas[nodo1]["nombre"]
        parada2 = self.paradas[nodo2]["nombre"]
        
        return (nodo1, nodo2), f"{parada1} ↔ {parada2} ({peso_original} km)"
    
    def desbloquear_arista(self, arista):
        """Desbloquea una arista (restaura peso original)"""
        if arista is None:
            return
        
        nodo1, nodo2 = arista
        
        # Recalcular distancia original
        distancia = self.distancia_euclidiana(
            self.paradas[nodo1],
            self.paradas[nodo2]
        )
        
        self.grafo[nodo1][nodo2]['weight'] = distancia
    
    def obtener_matriz_adyacencia(self):
        """
        Retorna matriz de adyacencia ponderada.
        ÁLGEBRA LINEAL: Matriz n×n de pesos
        """
        return nx.to_numpy_array(self.grafo, weight='weight')

# ============================================
# FUNCIONES AUXILIARES
# ============================================

def crear_sistema():
    """Crea o recupera el sistema de transporte"""
    if st.session_state.grafo_original is None:
        sistema = SistemaTransporte()
        st.session_state.sistema = sistema
        st.session_state.grafo_original = sistema.grafo.copy()
        st.session_state.grafo_actual = sistema.grafo.copy()
        st.session_state.paradas = sistema.paradas
    return st.session_state.sistema

def dibujar_grafo(grafo, ruta_principal, ruta_alternativa=None, arista_bloqueada=None):
    """
    Dibuja el grafo con las rutas.
    Usa Matplotlib + NetworkX.
    """
    fig, ax = plt.subplots(figsize=(12, 10))
    
    # Posiciones basadas en coordenadas reales
    pos = {}
    for nodo, data in grafo.nodes(data=True):
        # Normalizar coordenadas para visualización
        lat = data.get('lat', 0)
        lon = data.get('lon', 0)
        # Invertir lon porque en mapas va hacia la izquierda
        pos[nodo] = (lon * 100, lat * 100)
    
    # Dibujar aristas
    for nodo1, nodo2, data in grafo.edges(data=True):
        peso = data['weight']
        
        # Determinar color de arista
        color = '#cccccc'
        ancho = 1
        
        if (nodo1, nodo2) == arista_bloqueada or (nodo2, nodo1) == arista_bloqueada:
            color = '#ff0000'  # Rojo para arista bloqueada
            ancho = 3
        elif [nodo1, nodo2] in [[ruta_principal[i], ruta_principal[i+1]] 
                                 for i in range(len(ruta_principal)-1)] or \
             [nodo2, nodo1] in [[ruta_principal[i], ruta_principal[i+1]] 
                                 for i in range(len(ruta_principal)-1)]:
            color = '#667eea'  # Azul para ruta actual
            ancho = 3
        elif ruta_alternativa and ([nodo1, nodo2] in [[ruta_alternativa[i], ruta_alternativa[i+1]] 
                                     for i in range(len(ruta_alternativa)-1)] or \
             [nodo2, nodo1] in [[ruta_alternativa[i], ruta_alternativa[i+1]] 
                                 for i in range(len(ruta_alternativa)-1)]):
            color = '#27ae60'  # Verde para ruta alternativa
            ancho = 3
        
        x = [pos[nodo1][0], pos[nodo2][0]]
        y = [pos[nodo1][1], pos[nodo2][1]]
        
        ax.plot(x, y, color=color, linewidth=ancho, alpha=0.6, zorder=1)
        
        # Etiqueta de distancia
        if peso != float('inf'):
            mid_x = (pos[nodo1][0] + pos[nodo2][0]) / 2
            mid_y = (pos[nodo1][1] + pos[nodo2][1]) / 2
            ax.text(mid_x, mid_y, f"{peso}km", fontsize=8, alpha=0.7,
                   bbox=dict(boxstyle='round,pad=0.3', facecolor='white', alpha=0.7))
    
    # Dibujar nodos
    for nodo, (x, y) in pos.items():
        color_nodo = '#667eea'
        if nodo in ruta_principal:
            color_nodo = '#667eea' if nodo == ruta_principal[0] else '#667eea'
        
        ax.scatter(x, y, s=500, c=color_nodo, edgecolors='black', 
                  linewidth=2, zorder=3, alpha=0.9)
        
        # Etiqueta del nodo
        nombre = grafo.nodes[nodo]['nombre']
        ax.text(x, y, str(nodo), ha='center', va='center', 
               fontweight='bold', color='white', fontsize=10, zorder=4)
        ax.text(x, y - 0.15, nombre, ha='center', va='top', 
               fontsize=8, style='italic', zorder=4)
    
    # Resaltar ruta principal
    if len(ruta_principal) > 1:
        for i in range(len(ruta_principal) - 1):
            nodo1 = ruta_principal[i]
            nodo2 = ruta_principal[i + 1]
            x = [pos[nodo1][0], pos[nodo2][0]]
            y = [pos[nodo1][1], pos[nodo2][1]]
            ax.plot(x, y, color='#667eea', linewidth=4, alpha=0.9, zorder=2)
    
    # Resaltar ruta alternativa si existe
    if ruta_alternativa and len(ruta_alternativa) > 1:
        for i in range(len(ruta_alternativa) - 1):
            nodo1 = ruta_alternativa[i]
            nodo2 = ruta_alternativa[i + 1]
            x = [pos[nodo1][0], pos[nodo2][0]]
            y = [pos[nodo1][1], pos[nodo2][1]]
            ax.plot(x, y, color='#27ae60', linewidth=3, alpha=0.8, 
                   linestyle='--', zorder=2)
    
    ax.set_title('🗺️ MAPA DE RUTAS - PEREIRA Y DOSQUEBRADAS', 
                fontsize=14, fontweight='bold', pad=20)
    ax.set_xlabel('Longitud (x100)', fontsize=10)
    ax.set_ylabel('Latitud (x100)', fontsize=10)
    ax.grid(True, alpha=0.2)
    ax.set_aspect('equal')
    
    plt.tight_layout()
    return fig

def mostrar_estado(estado_texto, tipo="normal"):
    """Muestra el estado del sistema"""
    if tipo == "normal":
        st.markdown(f'<div class="estado-normal"><strong>✅ Estado:</strong> {estado_texto}</div>', 
                   unsafe_allow_html=True)
    elif tipo == "alerta":
        st.markdown(f'<div class="estado-alerta"><strong>🚨 Estado:</strong> {estado_texto}</div>', 
                   unsafe_allow_html=True)
    elif tipo == "optimizando":
        st.markdown(f'<div class="estado-optimizando"><strong>⚙️ Estado:</strong> {estado_texto}</div>', 
                   unsafe_allow_html=True)

# ============================================
# INTERFAZ PRINCIPAL
# ============================================

def main():
    st.title("🚌 AMCO - SISTEMA INTELIGENTE DE OPTIMIZACIÓN DE RUTAS")
    st.markdown("**Demuestra: Álgebra Lineal, NetworkX y Algoritmo de Dijkstra**")
    
    # Crear sistema
    sistema = crear_sistema()
    
    # ============================================
    # SIDEBAR: CONTROLES
    # ============================================
    with st.sidebar:
        st.header("🎮 PANEL DE CONTROL")
        
        # Selección de origen y destino
        st.subheader("📍 Configuración de Ruta")
        
        col1, col2 = st.columns(2)
        with col1:
            origen = st.selectbox(
                "Origen:",
                options=list(sistema.paradas.keys()),
                format_func=lambda x: f"{x}. {sistema.paradas[x]['nombre']}"
            )
        
        with col2:
            destino = st.selectbox(
                "Destino:",
                options=list(sistema.paradas.keys()),
                format_func=lambda x: f"{x}. {sistema.paradas[x]['nombre']}",
                index=5
            )
        
        # Validar que origen != destino
        if origen == destino:
            st.warning("⚠️ El origen y destino deben ser diferentes")
            return
        
        # Botón calcular ruta inicial
        if st.button("🔍 Calcular Ruta Óptima Inicial", use_container_width=True):
            inicio = time.time()
            
            st.session_state.grafo_actual = st.session_state.grafo_original.copy()
            distancia, ruta = sistema.calcular_ruta_optima(origen, destino)
            
            st.session_state.ruta_original = ruta
            st.session_state.ruta_actual = ruta
            st.session_state.tiempo_calculo = round(time.time() - inicio, 4)
            st.session_state.estado = "Operando normalmente"
            st.session_state.arista_bloqueada = None
            st.session_state.historial_eventos = []
            
            st.session_state.distancia_original = distancia
            st.session_state.distancia_actual = distancia
            st.session_state.origen = origen
            st.session_state.destino = destino
            
            st.success("✅ Ruta inicial calculada")
            st.rerun()
        
        st.divider()
        
        # Sección de eventos
        st.subheader("⚠️ SIMULAR EVENTOS")
        
        if st.button("🚗💥 SIMULAR ACCIDENTE", use_container_width=True, 
                    key="btn_accidente"):
            
            if not hasattr(st.session_state, 'ruta_original') or len(st.session_state.ruta_original) == 0:
                st.error("❌ Calcula una ruta inicial primero")
            else:
                inicio = time.time()
                
                # Crear copia del grafo actual
                st.session_state.grafo_actual = st.session_state.grafo_original.copy()
                
                # Bloquear arista aleatoria
                arista, descripcion = sistema.bloquear_arista()
                st.session_state.arista_bloqueada = arista
                
                # Mostrar estado de alerta
                st.session_state.estado = f"🚨 ACCIDENTE EN RUTA: {descripcion}"
                
                # Recalcular ruta alternativa
                distancia_alt, ruta_alt = sistema.calcular_ruta_optima(
                    st.session_state.origen, 
                    st.session_state.destino
                )
                
                st.session_state.tiempo_calculo = round(time.time() - inicio, 4)
                
                # Guardar ruta actual
                st.session_state.ruta_actual = ruta_alt
                st.session_state.distancia_actual = distancia_alt
                
                # Registrar en historial
                evento = {
                    "timestamp": datetime.now().strftime("%H:%M:%S"),
                    "tipo": "Accidente",
                    "ubicacion": descripcion,
                    "ruta_original_dist": st.session_state.distancia_original,
                    "ruta_nueva_dist": distancia_alt,
                    "diferencia": round(distancia_alt - st.session_state.distancia_original, 2),
                    "tiempo_calculo": st.session_state.tiempo_calculo
                }
                st.session_state.historial_eventos.append(evento)
                
                st.rerun()
        
        if st.button("✅ LIMPIAR ACCIDENTE", use_container_width=True):
            if st.session_state.arista_bloqueada is not None:
                sistema.desbloquear_arista(st.session_state.arista_bloqueada)
                st.session_state.grafo_actual = st.session_state.grafo_original.copy()
                st.session_state.arista_bloqueada = None
                st.session_state.ruta_actual = st.session_state.ruta_original
                st.session_state.distancia_actual = st.session_state.distancia_original
                st.session_state.estado = "Operando normalmente"
                
                st.success("✅ Accidente resuelto - Ruta restaurada")
                st.rerun()
        
        st.divider()
        
        # Información del sistema
        st.subheader("📊 INFORMACIÓN DEL SISTEMA")
        
        st.metric("Paradas Activas", len(sistema.paradas))
        st.metric("Rutas Posibles", len(list(sistema.grafo.edges())))
        
        if hasattr(st.session_state, 'tiempo_calculo'):
            st.metric("Última Optimización", f"{st.session_state.tiempo_calculo}s")
    
    # ============================================
    # CONTENIDO PRINCIPAL
    # ============================================
    
    # Estado del sistema
    st.subheader("🔔 ESTADO DEL SISTEMA")
    
    if hasattr(st.session_state, 'estado'):
        if "Accidente" in st.session_state.estado:
            mostrar_estado(st.session_state.estado, tipo="alerta")
        else:
            mostrar_estado(st.session_state.estado, tipo="normal")
    else:
        mostrar_estado("Esperando configuración...", tipo="normal")
    
    # Métricas principales
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        if hasattr(st.session_state, 'distancia_original'):
            st.metric(
                "Distancia Original",
                f"{st.session_state.distancia_original} km",
                delta=None
            )
        else:
            st.metric("Distancia Original", "—")
    
    with col2:
        if hasattr(st.session_state, 'distancia_actual'):
            delta = st.session_state.distancia_actual - st.session_state.distancia_original
            st.metric(
                "Distancia Actual",
                f"{st.session_state.distancia_actual} km",
                delta=f"{delta:+.2f} km" if delta != 0 else "Sin cambios"
            )
        else:
            st.metric("Distancia Actual", "—")
    
    with col3:
        if hasattr(st.session_state, 'ruta_original'):
            st.metric(
                "Paradas en Ruta",
                len(st.session_state.ruta_original)
            )
        else:
            st.metric("Paradas en Ruta", "—")
    
    with col4:
        if hasattr(st.session_state, 'tiempo_calculo'):
            st.metric(
                "Tiempo de Optimización",
                f"{st.session_state.tiempo_calculo}s"
            )
        else:
            st.metric("Tiempo de Optimización", "—")
    
    # Tabs para visualización
    tab1, tab2, tab3, tab4 = st.tabs([
        "🗺️ Visualización del Grafo",
        "📋 Detalles de Ruta",
        "📊 Análisis Matemático",
        "📝 Historial de Eventos"
    ])
    
    # Tab 1: Visualización
    with tab1:
        st.subheader("Mapa de Rutas Optimizadas")
        
        if hasattr(st.session_state, 'ruta_original') and len(st.session_state.ruta_original) > 0:
            fig = dibujar_grafo(
                st.session_state.grafo_actual,
                st.session_state.ruta_actual,
                ruta_alternativa=st.session_state.ruta_original if st.session_state.arista_bloqueada else None,
                arista_bloqueada=st.session_state.arista_bloqueada
            )
            st.pyplot(fig, use_container_width=True)
            
            # Leyenda
            st.markdown("""
            **Leyenda:**
            - 🔵 **Nodos**: Paradas de transporte
            - 🔵 **Línea Azul**: Ruta óptima actual
            - 🟢 **Línea Verde Punteada**: Ruta original (antes del accidente)
            - 🔴 **Línea Roja**: Arista bloqueada (accidente)
            """)
        else:
            st.info("👆 Selecciona origen y destino en el panel lateral, luego presiona 'Calcular Ruta Óptima Inicial'")
    
    # Tab 2: Detalles de Ruta
    with tab2:
        st.subheader("Información Detallada de Rutas")
        
        if hasattr(st.session_state, 'ruta_original') and len(st.session_state.ruta_original) > 0:
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("### 📍 Ruta Original (Sin Accidente)")
                st.info(f"**Distancia:** {st.session_state.distancia_original} km")
                
                ruta_text = " → ".join([
                    f"{nodo}. {sistema.paradas[nodo]['nombre']}"
                    for nodo in st.session_state.ruta_original
                ])
                st.markdown(f"**Camino:** {ruta_text}")
                
                # Detalles de segmentos
                st.markdown("**Segmentos:**")
                for i in range(len(st.session_state.ruta_original) - 1):
                    nodo1 = st.session_state.ruta_original[i]
                    nodo2 = st.session_state.ruta_original[i + 1]
                    distancia = st.session_state.grafo_original[nodo1][nodo2]['weight']
                    
                    st.text(
                        f"  {sistema.paradas[nodo1]['nombre']} → "
                        f"{sistema.paradas[nodo2]['nombre']}: {distancia} km"
                    )
            
            with col2:
                st.markdown("### 🚨 Ruta Actual (Con Accidentes)")
                st.warning(f"**Distancia:** {st.session_state.distancia_actual} km")
                
                if st.session_state.arista_bloqueada:
                    delta = st.session_state.distancia_actual - st.session_state.distancia_original
                    st.error(f"**Incremento:** {delta:+.2f} km ({(delta/st.session_state.distancia_original*100):+.1f}%)")
                
                ruta_text = " → ".join([
                    f"{nodo}. {sistema.paradas[nodo]['nombre']}"
                    for nodo in st.session_state.ruta_actual
                ])
                st.markdown(f"**Camino:** {ruta_text}")
                
                # Detalles de segmentos
                st.markdown("**Segmentos:**")
                for i in range(len(st.session_state.ruta_actual) - 1):
                    nodo1 = st.session_state.ruta_actual[i]
                    nodo2 = st.session_state.ruta_actual[i + 1]
                    
                    if st.session_state.grafo_actual[nodo1][nodo2]['weight'] == float('inf'):
                        st.error(
                            f"  ❌ {sistema.paradas[nodo1]['nombre']} → "
                            f"{sistema.paradas[nodo2]['nombre']}: BLOQUEADO"
                        )
                    else:
                        distancia = st.session_state.grafo_actual[nodo1][nodo2]['weight']
                        st.text(
                            f"  {sistema.paradas[nodo1]['nombre']} → "
                            f"{sistema.paradas[nodo2]['nombre']}: {distancia} km"
                        )
        else:
            st.info("👆 Calcula una ruta primero")
    
    # Tab 3: Análisis Matemático
    with tab3:
        st.subheader("🔬 ANÁLISIS DE ÁLGEBRA LINEAL")
        
        st.markdown("#### 1️⃣ Matriz de Adyacencia Ponderada")
        st.markdown("""
        La matriz representa las distancias (pesos) entre todas las paradas.
        
        **Fórmula:** `D[i,j] = ||parada_i - parada_j||₂ × 111 km`
        
        Donde `||·||₂` es la norma euclidiana (L2).
        """)
        
        matriz = sistema.obtener_matriz_adyacencia()
        
        # Crear DataFrame para mejor visualización
        import pandas as pd
        df_matriz = pd.DataFrame(
            matriz,
            index=[f"{i}. {sistema.paradas[i]['nombre']}" for i in range(1, 7)],
            columns=[f"{i}" for i in range(1, 7)]
        )
        
        st.dataframe(df_matriz.style.format("{:.2f}"), use_container_width=True)
        
        st.markdown("#### 2️⃣ Algoritmo de Dijkstra")
        st.markdown("""
        Encuentra la ruta más corta en un grafo ponderado.
        
        **Complejidad:** O(n²) donde n = número de paradas
        
        **Pasos:**
        1. Inicializar distancias a infinito (excepto origen = 0)
        2. Seleccionar nodo no visitado con menor distancia
        3. Actualizar distancias de sus vecinos
        4. Repetir hasta llegar al destino
        
        **Propiedades:**
        - ✅ Garantiza encontrar la ruta óptima
        - ✅ Funciona con pesos positivos
        - ✅ Se recalcula automáticamente ante cambios (accidentes)
        """)
        
        if hasattr(st.session_state, 'tiempo_calculo'):
            st.success(f"✅ Última optimización completada en {st.session_state.tiempo_calculo}s")
        
        st.markdown("#### 3️⃣ Norma Euclidiana")
        st.markdown("""
        Calcula la distancia entre dos puntos en el plano geográfico.
        
        **Fórmula:** 
        ```
        distancia = √[(lat₂-lat₁)² + (lon₂-lon₁)²] × 111 km
        ```
        
        El factor 111 convierte grados a kilómetros (aprox 1° ≈ 111 km)
        """)
    
    # Tab 4: Historial de Eventos
    with tab4:
        st.subheader("📝 Historial de Eventos y Optimizaciones")
        
        if len(st.session_state.historial_eventos) > 0:
            # Tabla con eventos
            df_eventos = pd.DataFrame(st.session_state.historial_eventos)
            st.dataframe(df_eventos, use_container_width=True)
            
            # Estadísticas
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.metric(
                    "Total de Eventos",
                    len(st.session_state.historial_eventos)
                )
            
            with col2:
                avg_diferencia = df_eventos['diferencia'].mean()
                st.metric(
                    "Incremento Promedio",
                    f"{avg_diferencia:+.2f} km"
                )
            
            with col3:
                max_tiempo = df_eventos['tiempo_calculo'].max()
                st.metric(
                    "Tiempo Max. de Optimización",
                    f"{max_tiempo}s"
                )
        else:
            st.info("No hay eventos registrados aún")

if __name__ == "__main__":
    main()
