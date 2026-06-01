"""
🚌 AMCO - SISTEMA AVANZADO DE OPTIMIZACIÓN CON EVENTOS PROBABILÍSTICOS
=======================================================================

Sistema realista de Pereira con:
✅ Nodos críticos de la ciudad (Intercambiador Cuba, Gobernación, Viaducto)
✅ Eventos probabilísticos (Choques, Manifestaciones, Obras, Lluvia)
✅ Impacto dinámico en pesos y capacidad
✅ Selector de eventos en Streamlit
✅ Ruteo automático bajo estrés

Ejecución: streamlit run amco_eventos_probabilisticos.py

REALISMO PEREIRA:
- Intercambiador de Cuba (Hub principal)
- Gobernación / Instituto de Movilidad
- Viaducto (salida Dosquebradas)
- La Popa (ruta alterna)
"""

import sys
if sys.version_info < (3, 8):
    print(f"Error: Se requiere Python 3.8 o superior")
    sys.exit(1)

import streamlit as st
import networkx as nx
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.patches import FancyArrowPatch, Circle
import pandas as pd
from datetime import datetime
import time

# ============================================
# CONFIGURACIÓN STREAMLIT
# ============================================
st.set_page_config(
    page_title="🚌 AMCO - Eventos Probabilísticos",
    page_icon="🚌",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
    <style>
    .evento-choque {
        background-color: #ff6b6b;
        color: white;
        padding: 15px;
        border-radius: 5px;
        border-left: 5px solid #c92a2a;
    }
    .evento-manifestacion {
        background-color: #ffd93d;
        color: #333;
        padding: 15px;
        border-radius: 5px;
        border-left: 5px solid #f08c00;
    }
    .evento-obra {
        background-color: #a8e6cf;
        color: #333;
        padding: 15px;
        border-radius: 5px;
        border-left: 5px solid #56ab2f;
    }
    .evento-lluvia {
        background-color: #74b9ff;
        color: white;
        padding: 15px;
        border-radius: 5px;
        border-left: 5px solid #0984e3;
    }
    .nodo-critico {
        font-weight: bold;
        color: #d63031;
    }
    .estadisticas-evento {
        background-color: #f1f1f1;
        padding: 15px;
        border-radius: 5px;
        margin-top: 10px;
    }
    </style>
""", unsafe_allow_html=True)

# ============================================
# DEFINICIÓN DE EVENTOS PROBABILÍSTICOS
# ============================================

TIPOS_EVENTOS = {
    "choque": {
        "emoji": "🚗💥",
        "nombre": "Choque Vehicular",
        "multiplicador_peso": 3.0,
        "reduccion_capacidad": 0.5,  # 50% de reducción
        "duracion_minutos": 30,
        "probabilidad": 0.15,
        "descripcion": "Colisión entre vehículos que reduce capacidad al 50%",
        "color": "#ff6b6b"
    },
    "manifestacion": {
        "emoji": "🚧",
        "nombre": "Manifestación / Bloqueo",
        "multiplicador_peso": float('inf'),
        "reduccion_capacidad": 1.0,  # Cierre total
        "duracion_minutos": 120,
        "probabilidad": 0.10,
        "descripcion": "Cierre total de la vía (peso infinito)",
        "color": "#ffd93d"
    },
    "obra": {
        "emoji": "🏗️",
        "nombre": "Obras en Vía",
        "multiplicador_peso": 1.5,
        "reduccion_capacidad": 0.3,  # 30% de reducción
        "duracion_minutos": 240,
        "probabilidad": 0.20,
        "descripcion": "Reducción de carriles (+50% en tiempo)",
        "color": "#a8e6cf"
    },
    "lluvia": {
        "emoji": "🌧️",
        "nombre": "Lluvia Intensa",
        "multiplicador_peso": 1.8,
        "reduccion_capacidad": 0.4,  # 40% de reducción
        "duracion_minutos": 45,
        "probabilidad": 0.25,
        "descripcion": "Condiciones climáticas adversas (+80% en tiempo)",
        "color": "#74b9ff"
    }
}

# ============================================
# NODOS CRÍTICOS DE PEREIRA
# ============================================

NODOS_PEREIRA = {
    1: {
        "nombre": "Centro Cívico",
        "ciudad": "Pereira",
        "lat": 4.8135,
        "lon": -75.6942,
        "tipo": "hub",
        "critico": False,
        "descripcion": "Zona comercial central"
    },
    2: {
        "nombre": "Intercambiador de Cuba",
        "ciudad": "Pereira",
        "lat": 4.8180,
        "lon": -75.6850,
        "tipo": "hub",
        "critico": True,
        "descripcion": "🔴 HUB CRÍTICO - Nodo principal de transporte"
    },
    3: {
        "nombre": "Gobernación",
        "ciudad": "Pereira",
        "lat": 4.8100,
        "lon": -75.6950,
        "tipo": "hub",
        "critico": True,
        "descripcion": "🔴 Instituto de Movilidad - Centro administrativo"
    },
    4: {
        "nombre": "Viaducto (Dosquebradas)",
        "ciudad": "Pereira",
        "lat": 4.8050,
        "lon": -75.7100,
        "tipo": "critica",
        "critico": True,
        "descripcion": "🔴 VIADUCTO CRÍTICO - Única salida hacia Dosquebradas"
    },
    5: {
        "nombre": "La Popa (Ruta Alterna)",
        "ciudad": "Pereira",
        "lat": 4.7950,
        "lon": -75.6800,
        "tipo": "alterna",
        "critico": False,
        "descripcion": "Ruta alterna por La Popa"
    },
    6: {
        "nombre": "Variante",
        "ciudad": "Pereira",
        "lat": 4.8250,
        "lon": -75.7200,
        "tipo": "alterna",
        "critico": False,
        "descripcion": "Ruta alterna por Variante"
    },
    7: {
        "nombre": "Centro Dosquebradas",
        "ciudad": "Dosquebradas",
        "lat": 4.7850,
        "lon": -75.7300,
        "tipo": "destino",
        "critico": False,
        "descripcion": "Destino principal en Dosquebradas"
    }
}

# ============================================
# CLASE: SISTEMA TRANSPORTE REALISTA
# ============================================

class SistemaTransportePereira:
    """
    Sistema de transporte de Pereira con eventos probabilísticos.
    Incluye nodos críticos y ruteo inteligente bajo estrés.
    """
    
    def __init__(self):
        self.nodos = NODOS_PEREIRA.copy()
        self.grafo = None
        self.eventos_activos = {}
        self.historial_eventos = []
        self.crear_grafo()
    
    def distancia_euclidiana(self, p1, p2):
        """Calcula distancia euclidiana entre dos puntos"""
        dlat = p2["lat"] - p1["lat"]
        dlon = p2["lon"] - p1["lon"]
        distancia_grados = np.sqrt(dlat**2 + dlon**2)
        distancia_km = distancia_grados * 111
        return round(distancia_km, 2)
    
    def crear_grafo(self):
        """Crea grafo de Pereira con conexiones realistas"""
        self.grafo = nx.Graph()
        
        # Agregar nodos
        for nodo_id, nodo_data in self.nodos.items():
            self.grafo.add_node(
                nodo_id,
                nombre=nodo_data["nombre"],
                lat=nodo_data["lat"],
                lon=nodo_data["lon"],
                critico=nodo_data["critico"]
            )
        
        # Crear conexiones realistas de Pereira
        # Basadas en la geografía y red de transporte
        conexiones = [
            (1, 2, "Centro → Intercambiador Cuba"),
            (1, 3, "Centro → Gobernación"),
            (2, 3, "Cuba → Gobernación"),
            (2, 4, "Cuba → Viaducto"),
            (3, 4, "Gobernación → Viaducto"),
            (3, 5, "Gobernación → La Popa (alterna)"),
            (2, 5, "Cuba → La Popa"),
            (4, 6, "Viaducto → Variante"),
            (5, 6, "La Popa → Variante (alterna)"),
            (4, 7, "Viaducto → Dosquebradas"),
            (6, 7, "Variante → Dosquebradas"),
            (5, 7, "La Popa → Dosquebradas (alterna larga)")
        ]
        
        for nodo_i, nodo_j, descripcion in conexiones:
            distancia = self.distancia_euclidiana(
                self.nodos[nodo_i],
                self.nodos[nodo_j]
            )
            
            self.grafo.add_edge(
                nodo_i, nodo_j,
                weight=distancia,
                peso_original=distancia,
                descripcion=descripcion,
                capacidad=100  # Capacidad base
            )
    
    def inyectar_evento(self, tipo_evento, nodo1, nodo2):
        """
        Inyecta un evento probabilístico en una arista.
        
        Modifica:
        - El peso (tiempo de viaje)
        - La capacidad del bus
        """
        if tipo_evento not in TIPOS_EVENTOS:
            return False
        
        # Normalizar arista
        if nodo2 < nodo1:
            nodo1, nodo2 = nodo2, nodo1
        
        arista = (nodo1, nodo2)
        
        if not self.grafo.has_edge(nodo1, nodo2):
            return False
        
        evento_config = TIPOS_EVENTOS[tipo_evento]
        peso_original = self.grafo[nodo1][nodo2]['peso_original']
        
        # Calcular nuevo peso
        if evento_config['multiplicador_peso'] == float('inf'):
            nuevo_peso = float('inf')
        else:
            nuevo_peso = peso_original * evento_config['multiplicador_peso']
        
        # Actualizar grafo
        self.grafo[nodo1][nodo2]['weight'] = nuevo_peso
        self.grafo[nodo1][nodo2]['capacidad'] = 100 * (1 - evento_config['reduccion_capacidad'])
        
        # Registrar evento
        evento = {
            "arista": arista,
            "tipo": tipo_evento,
            "timestamp": datetime.now(),
            "nodo1_nombre": self.nodos[nodo1]["nombre"],
            "nodo2_nombre": self.nodos[nodo2]["nombre"],
            "peso_original": peso_original,
            "peso_nuevo": nuevo_peso,
            "capacidad_nueva": self.grafo[nodo1][nodo2]['capacidad'],
            "config": evento_config
        }
        
        self.eventos_activos[arista] = evento
        self.historial_eventos.append(evento)
        
        return True
    
    def limpiar_evento(self, nodo1, nodo2):
        """Limpia un evento y restaura valores originales"""
        if nodo2 < nodo1:
            nodo1, nodo2 = nodo2, nodo1
        
        arista = (nodo1, nodo2)
        
        if arista in self.eventos_activos:
            peso_original = self.grafo[nodo1][nodo2]['peso_original']
            self.grafo[nodo1][nodo2]['weight'] = peso_original
            self.grafo[nodo1][nodo2]['capacidad'] = 100
            del self.eventos_activos[arista]
            return True
        
        return False
    
    def calcular_ruta_optima(self, origen, destino):
        """Calcula ruta óptima usando Dijkstra"""
        try:
            if not nx.has_path(self.grafo, origen, destino):
                return None, [], None
            
            distancia = nx.dijkstra_path_length(self.grafo, origen, destino, weight='weight')
            ruta = nx.dijkstra_path(self.grafo, origen, destino, weight='weight')
            
            # Calcular capacidad mínima en la ruta
            capacidad_min = 100
            for i in range(len(ruta) - 1):
                nodo1, nodo2 = ruta[i], ruta[i+1]
                cap = self.grafo[nodo1][nodo2]['capacidad']
                capacidad_min = min(capacidad_min, cap)
            
            return round(distancia, 2), ruta, capacidad_min
        except:
            return None, [], None
    
    def calcular_impacto(self, origen, destino):
        """
        Calcula impacto de eventos en la ruta.
        Compara ruta original vs actual.
        """
        # Guardar estado actual
        estado_actual = {}
        for n1, n2 in self.grafo.edges():
            estado_actual[(n1, n2)] = {
                'weight': self.grafo[n1][n2]['weight'],
                'capacidad': self.grafo[n1][n2]['capacidad']
            }
        
        # Limpiar todos los eventos
        for arista in list(self.eventos_activos.keys()):
            self.limpiar_evento(arista[0], arista[1])
        
        dist_original, ruta_original, cap_original = self.calcular_ruta_optima(origen, destino)
        
        # Restaurar estado
        for (n1, n2), valores in estado_actual.items():
            self.grafo[n1][n2]['weight'] = valores['weight']
            self.grafo[n1][n2]['capacidad'] = valores['capacidad']
        
        dist_actual, ruta_actual, cap_actual = self.calcular_ruta_optima(origen, destino)
        
        return {
            'dist_original': dist_original,
            'dist_actual': dist_actual,
            'ruta_original': ruta_original,
            'ruta_actual': ruta_actual,
            'incremento': dist_actual - dist_original if dist_actual else 0,
            'capacidad_original': cap_original,
            'capacidad_actual': cap_actual
        }
    
    def obtener_aristas_bloqueadas(self):
        """Retorna aristas con peso infinito"""
        return [
            (n1, n2) for n1, n2 in self.grafo.edges()
            if self.grafo[n1][n2]['weight'] == float('inf')
        ]

# ============================================
# FUNCIONES AUXILIARES
# ============================================

def dibujar_grafo_pereira(sistema, ruta_resaltada=None, ruta_alternativa=None):
    """Dibuja el grafo realista de Pereira"""
    fig, ax = plt.subplots(figsize=(14, 11))
    
    # Posiciones basadas en coordenadas reales
    pos = {}
    for nodo_id, nodo_data in sistema.nodos.items():
        lat = nodo_data["lat"]
        lon = nodo_data["lon"]
        pos[nodo_id] = (lon * 100, lat * 100)
    
    # Dibujar aristas
    for nodo1, nodo2, data in sistema.grafo.edges(data=True):
        peso = data['weight']
        x = [pos[nodo1][0], pos[nodo2][0]]
        y = [pos[nodo1][1], pos[nodo2][1]]
        
        # Determinar color
        color = '#cccccc'
        ancho = 1.5
        alpha = 0.6
        
        if peso == float('inf'):
            color = '#ff0000'
            ancho = 3
            alpha = 1.0
        elif ruta_resaltada and ([nodo1, nodo2] in [[ruta_resaltada[i], ruta_resaltada[i+1]] 
                                  for i in range(len(ruta_resaltada)-1)] or
                                 [nodo2, nodo1] in [[ruta_resaltada[i], ruta_resaltada[i+1]] 
                                  for i in range(len(ruta_resaltada)-1)]):
            color = '#667eea'
            ancho = 3
            alpha = 0.9
        elif ruta_alternativa and ([nodo1, nodo2] in [[ruta_alternativa[i], ruta_alternativa[i+1]] 
                                    for i in range(len(ruta_alternativa)-1)] or
                                   [nodo2, nodo1] in [[ruta_alternativa[i], ruta_alternativa[i+1]] 
                                    for i in range(len(ruta_alternativa)-1)]):
            color = '#27ae60'
            ancho = 2.5
            alpha = 0.8
        
        ax.plot(x, y, color=color, linewidth=ancho, alpha=alpha, zorder=1)
        
        # Etiqueta de distancia
        if peso != float('inf'):
            mid_x = (pos[nodo1][0] + pos[nodo2][0]) / 2
            mid_y = (pos[nodo1][1] + pos[nodo2][1]) / 2
            etiqueta = f"{peso}km"
            
            # Si hay evento, mostrar impacto
            if (nodo1, nodo2) in sistema.eventos_activos or (nodo2, nodo1) in sistema.eventos_activos:
                peso_original = sistema.grafo[nodo1][nodo2]['peso_original']
                etiqueta = f"{peso}km (era {peso_original}km)"
            
            ax.text(mid_x, mid_y, etiqueta, fontsize=7, alpha=0.7,
                   bbox=dict(boxstyle='round,pad=0.3', facecolor='white', alpha=0.8))
        else:
            mid_x = (pos[nodo1][0] + pos[nodo2][0]) / 2
            mid_y = (pos[nodo1][1] + pos[nodo2][1]) / 2
            ax.text(mid_x, mid_y, "BLOQUEADO", fontsize=7, color='red', fontweight='bold',
                   bbox=dict(boxstyle='round,pad=0.3', facecolor='yellow', alpha=0.9))
    
    # Dibujar nodos
    for nodo_id, (x, y) in pos.items():
        nodo_data = sistema.nodos[nodo_id]
        
        # Color según tipo
        if nodo_data['critico']:
            color_nodo = '#d63031'  # Rojo para nodos críticos
            tamaño = 700
        else:
            color_nodo = '#667eea'
            tamaño = 600
        
        ax.scatter(x, y, s=tamaño, c=color_nodo, edgecolors='black', 
                  linewidth=2, zorder=3, alpha=0.9)
        
        # Etiqueta del nodo
        ax.text(x, y, str(nodo_id), ha='center', va='center', 
               fontweight='bold', color='white', fontsize=11, zorder=4)
        
        # Nombre
        ax.text(x, y - 0.25, nodo_data['nombre'], ha='center', va='top', 
               fontsize=8, style='italic', zorder=4, fontweight='bold' if nodo_data['critico'] else 'normal')
    
    # Título
    ax.set_title('🗺️ MAPA INTELIGENTE DE TRANSPORTE - PEREIRA Y DOSQUEBRADAS\n' + 
                '(Rojo = Nodos Críticos | Azul = Ruta Actual | Verde = Ruta Alternativa)',
                fontsize=12, fontweight='bold', pad=20)
    ax.set_xlabel('Longitud (x100)', fontsize=10)
    ax.set_ylabel('Latitud (x100)', fontsize=10)
    ax.grid(True, alpha=0.2)
    ax.set_aspect('equal')
    
    plt.tight_layout()
    return fig

# ============================================
# INICIALIZACIÓN
# ============================================

if 'sistema' not in st.session_state:
    st.session_state.sistema = SistemaTransportePereira()
    st.session_state.ruta_actual = []
    st.session_state.distancia_actual = 0
    st.session_state.eventos_simulados = []
    st.session_state.comparativa = None

# ============================================
# INTERFAZ PRINCIPAL
# ============================================

def main():
    st.title("🚌 AMCO - SISTEMA CON EVENTOS PROBABILÍSTICOS")
    st.markdown("**Pereira & Dosquebradas | Optimización Inteligente bajo Estrés**")
    
    sistema = st.session_state.sistema
    
    # ============================================
    # SIDEBAR
    # ============================================
    with st.sidebar:
        st.header("🎮 CONTROL Y SIMULACIÓN")
        
        st.subheader("📍 Configuración de Ruta")
        
        # Opciones de nodos
        opciones_nodos = {
            f"{nid}. {nd['nombre']} {'🔴' if nd['critico'] else ''}": nid
            for nid, nd in sistema.nodos.items()
        }
        
        col1, col2 = st.columns(2)
        with col1:
            origen_key = st.selectbox("Origen:", list(opciones_nodos.keys())[:4])
            origen = opciones_nodos[origen_key]
        
        with col2:
            destino_key = st.selectbox("Destino:", list(opciones_nodos.keys())[3:])
            destino = opciones_nodos[destino_key]
        
        if origen == destino:
            st.warning("⚠️ Origen y destino deben ser diferentes")
            return
        
        # Botón calcular ruta
        if st.button("🔍 Calcular Ruta Inicial", use_container_width=True):
            inicio = time.time()
            dist, ruta, cap = sistema.calcular_ruta_optima(origen, destino)
            
            st.session_state.ruta_actual = ruta
            st.session_state.distancia_actual = dist
            st.session_state.origen = origen
            st.session_state.destino = destino
            st.session_state.distancia_original = dist
            st.session_state.capacidad_original = cap
            st.session_state.tiempo_calculo = round(time.time() - inicio, 4)
            
            st.success("✅ Ruta inicial calculada")
            st.rerun()
        
        st.divider()
        
        # ============================================
        # INYECCIÓN DE EVENTOS
        # ============================================
        st.subheader("⚠️ INYECTAR EVENTOS PROBABILÍSTICOS")
        
        tipo_evento = st.selectbox(
            "Tipo de Evento:",
            options=list(TIPOS_EVENTOS.keys()),
            format_func=lambda x: f"{TIPOS_EVENTOS[x]['emoji']} {TIPOS_EVENTOS[x]['nombre']}"
        )
        
        evento_config = TIPOS_EVENTOS[tipo_evento]
        
        # Mostrar descripción del evento
        st.info(f"**{evento_config['emoji']} {evento_config['nombre']}**\n\n"
               f"{evento_config['descripcion']}\n\n"
               f"⏱️ Duración típica: {evento_config['duracion_minutos']} min\n"
               f"📊 Probabilidad real: {evento_config['probabilidad']*100:.0f}%")
        
        # Seleccionar arista
        st.markdown("**Selecciona donde inyectar el evento:**")
        
        aristas_str = []
        aristas_map = {}
        
        for n1, n2 in sistema.grafo.edges():
            arista_name = (n1, n2) if n1 < n2 else (n2, n1)
            label = f"{sistema.nodos[n1]['nombre']} ↔ {sistema.nodos[n2]['nombre']}"
            aristas_str.append(label)
            aristas_map[label] = arista_name
        
        arista_selected = st.selectbox("Arista:", aristas_str)
        nodo1, nodo2 = aristas_map[arista_selected]
        
        # Botón inyectar evento
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button(f"💉 INYECTAR {evento_config['emoji']}", use_container_width=True):
                sistema.inyectar_evento(tipo_evento, nodo1, nodo2)
                
                # Recalcular ruta
                if hasattr(st.session_state, 'origen'):
                    dist, ruta, cap = sistema.calcular_ruta_optima(
                        st.session_state.origen,
                        st.session_state.destino
                    )
                    
                    st.session_state.ruta_actual = ruta
                    st.session_state.distancia_actual = dist
                    st.session_state.capacidad_actual = cap
                    
                    # Guardar evento
                    st.session_state.eventos_simulados.append({
                        'tipo': tipo_evento,
                        'arista': (nodo1, nodo2),
                        'timestamp': datetime.now()
                    })
                
                st.rerun()
        
        with col2:
            if st.button("🧹 LIMPIAR EVENTO", use_container_width=True):
                sistema.limpiar_evento(nodo1, nodo2)
                
                # Recalcular ruta
                if hasattr(st.session_state, 'origen'):
                    dist, ruta, cap = sistema.calcular_ruta_optima(
                        st.session_state.origen,
                        st.session_state.destino
                    )
                    
                    st.session_state.ruta_actual = ruta
                    st.session_state.distancia_actual = dist
                    st.session_state.capacidad_actual = cap
                
                st.rerun()
        
        st.divider()
        
        # Eventos activos
        st.subheader("🚨 Eventos Activos")
        if sistema.eventos_activos:
            for arista, evento in sistema.eventos_activos.items():
                config = evento['config']
                st.markdown(
                    f"<div class='evento-{evento['tipo']}'>"
                    f"<strong>{config['emoji']} {evento['nodo1_nombre']} ↔ {evento['nodo2_nombre']}</strong><br>"
                    f"Peso: {evento['peso_original']}km → {evento['peso_nuevo']}km<br>"
                    f"Capacidad: {evento['capacidad_nueva']:.0f}%"
                    f"</div>",
                    unsafe_allow_html=True
                )
        else:
            st.success("✅ Sin eventos activos - Sistema operando normalmente")
    
    # ============================================
    # CONTENIDO PRINCIPAL
    # ============================================
    
    if not hasattr(st.session_state, 'origen'):
        st.info("👈 Configura la ruta en el panel lateral")
        return
    
    # Tabs
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "🗺️ Mapa Interactivo",
        "📊 Comparativa de Rutas",
        "⚠️ Análisis de Eventos",
        "📈 Estadísticas",
        "📋 Historial"
    ])
    
    # TAB 1: Mapa
    with tab1:
        st.subheader("Mapa de Rutas en Tiempo Real")
        
        fig = dibujar_grafo_pereira(
            sistema,
            ruta_resaltada=st.session_state.ruta_actual,
            ruta_alternativa=st.session_state.ruta_original if hasattr(st.session_state, 'ruta_original') else None
        )
        
        st.pyplot(fig, use_container_width=True)
        
        st.markdown("""
        **Legendas:**
        - 🔴 **Nodos Rojos**: Nodos críticos (Cuba, Gobernación, Viaducto)
        - 🔵 **Nodos Azules**: Nodos normales
        - 🔵 **Línea Azul**: Ruta actual
        - 🟢 **Línea Verde**: Ruta alterna (si hay cambios)
        - 🔴 **Línea Roja**: Arista bloqueada
        """)
    
    # TAB 2: Comparativa
    with tab2:
        st.subheader("Comparativa: Antes vs Después del Evento")
        
        if sistema.eventos_activos:
            impacto = sistema.calcular_impacto(
                st.session_state.origen,
                st.session_state.destino
            )
            
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.metric(
                    "Distancia Original",
                    f"{impacto['dist_original']} km",
                    delta=None
                )
            
            with col2:
                st.metric(
                    "Distancia Actual",
                    f"{impacto['dist_actual']} km",
                    delta=f"{impacto['incremento']:+.2f} km" if impacto['incremento'] != 0 else "Sin cambios"
                )
            
            with col3:
                porcentaje = (impacto['incremento'] / impacto['dist_original'] * 100) if impacto['dist_original'] else 0
                st.metric(
                    "Impacto %",
                    f"{porcentaje:+.1f}%",
                    delta=None
                )
            
            st.divider()
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("### 📍 Ruta Original")
                ruta_orig_text = " → ".join([
                    f"{nid}. {sistema.nodos[nid]['nombre']}"
                    for nid in impacto['ruta_original']
                ])
                st.info(ruta_orig_text)
            
            with col2:
                st.markdown("### 🚨 Ruta Actual (Optimizada)")
                ruta_act_text = " → ".join([
                    f"{nid}. {sistema.nodos[nid]['nombre']}"
                    for nid in impacto['ruta_actual']
                ])
                st.warning(ruta_act_text)
        else:
            st.info("Inyecta un evento para ver la comparativa")
    
    # TAB 3: Análisis de Eventos
    with tab3:
        st.subheader("⚠️ Análisis Detallado de Eventos")
        
        if sistema.eventos_activos:
            for arista, evento in sistema.eventos_activos.items():
                config = evento['config']
                
                st.markdown(f"### {config['emoji']} {evento['nodo1_nombre']} ↔ {evento['nodo2_nombre']}")
                
                col1, col2, col3, col4 = st.columns(4)
                
                with col1:
                    st.metric("Tipo", config['nombre'])
                
                with col2:
                    st.metric("Peso Orig", f"{evento['peso_original']}km")
                
                with col3:
                    st.metric("Peso Nuevo", f"{evento['peso_nuevo']}km" if evento['peso_nuevo'] != float('inf') else "∞ BLOQUEADO")
                
                with col4:
                    st.metric("Capacidad", f"{evento['capacidad_nueva']:.0f}%")
                
                # Impacto
                st.markdown(f"**📊 Impacto:**")
                
                col1, col2 = st.columns(2)
                with col1:
                    if evento['peso_nuevo'] == float('inf'):
                        st.error("🚫 Esta ruta está completamente bloqueada")
                    else:
                        multiplicador = evento['peso_nuevo'] / evento['peso_original']
                        st.info(f"⏱️ Tiempo de viaje: +{(multiplicador-1)*100:.0f}%")
                
                with col2:
                    reduccion = (1 - evento['capacidad_nueva']/100) * 100
                    st.warning(f"👥 Capacidad reducida: -{reduccion:.0f}%")
                
                st.divider()
        else:
            st.info("🟢 Sistema sin eventos - Operando normalmente")
    
    # TAB 4: Estadísticas
    with tab4:
        st.subheader("📈 Estadísticas del Sistema")
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Nodos Críticos", sum(1 for n in sistema.nodos.values() if n['critico']))
        
        with col2:
            st.metric("Total de Rutas", len(list(sistema.grafo.edges())))
        
        with col3:
            st.metric("Eventos Activos", len(sistema.eventos_activos))
        
        with col4:
            bloqueadas = len(sistema.obtener_aristas_bloqueadas())
            st.metric("Aristas Bloqueadas", bloqueadas, delta=-bloqueadas if bloqueadas > 0 else None)
        
        st.divider()
        
        st.markdown("### Eventos en Nodos Críticos")
        
        criticos_con_eventos = {}
        for arista, evento in sistema.eventos_activos.items():
            n1, n2 = arista
            if sistema.nodos[n1]['critico']:
                if n1 not in criticos_con_eventos:
                    criticos_con_eventos[n1] = []
                criticos_con_eventos[n1].append(evento)
            if sistema.nodos[n2]['critico']:
                if n2 not in criticos_con_eventos:
                    criticos_con_eventos[n2] = []
                criticos_con_eventos[n2].append(evento)
        
        if criticos_con_eventos:
            for nodo_id, eventos in criticos_con_eventos.items():
                nodo_name = sistema.nodos[nodo_id]['nombre']
                st.error(f"🔴 {nodo_name}: {len(eventos)} evento(s) activo(s)")
        else:
            st.success("✅ Nodos críticos operando normalmente")
    
    # TAB 5: Historial
    with tab5:
        st.subheader("📋 Historial de Eventos")
        
        if sistema.historial_eventos:
            df_eventos = []
            for evt in sistema.historial_eventos:
                df_eventos.append({
                    'Timestamp': evt['timestamp'].strftime("%H:%M:%S"),
                    'Tipo': f"{evt['config']['emoji']} {evt['config']['nombre']}",
                    'Ubicación': f"{evt['nodo1_nombre']} ↔ {evt['nodo2_nombre']}",
                    'Peso Original': f"{evt['peso_original']}km",
                    'Peso Nuevo': f"{evt['peso_nuevo']}km" if evt['peso_nuevo'] != float('inf') else "∞",
                    'Capacidad': f"{evt['capacidad_nueva']:.0f}%"
                })
            
            df = pd.DataFrame(df_eventos)
            st.dataframe(df, use_container_width=True)
            
            st.markdown("### Estadísticas de Eventos")
            
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.metric("Total de Eventos", len(sistema.historial_eventos))
            
            with col2:
                choques = sum(1 for e in sistema.historial_eventos if e['tipo'] == 'choque')
                st.metric("Choques", choques)
            
            with col3:
                bloqueos = sum(1 for e in sistema.historial_eventos if e['tipo'] == 'manifestacion')
                st.metric("Bloqueos", bloqueos)
        else:
            st.info("No hay eventos registrados aún")

if __name__ == "__main__":
    main()
