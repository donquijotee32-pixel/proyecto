"""
🚌 AMCO - SISTEMA AVANZADO CON MAPA EXPANSIVO DE PEREIRA Y DOSQUEBRADAS
=========================================================================

Sistema realista expandido con:
✅ 20+ Nodos estratégicos en Pereira y Dosquebradas
✅ Múltiples rutas alternas y conexiones
✅ Eventos probabilísticos en puntos críticos
✅ Red compleja realista de transporte
✅ Análisis de resilencia urbana

Ejecución: streamlit run amco_red_expandida.py

COBERTURA GEOGRÁFICA:
- Pereira Centro (norte, sur, este, oeste)
- Pereira Periferias (Arabia, Cuba, Estadio, Galicia)
- Dosquebradas (centro, norte, sur)
- Rutas intermunicipales
- Puntos críticos de congestión
"""

import sys
if sys.version_info < (3, 8):
    print(f"Error: Se requiere Python 3.8 o superior")
    sys.exit(1)

import streamlit as st
import networkx as nx
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.patches import FancyArrowPatch, Circle, Rectangle
import pandas as pd
from datetime import datetime
import time
from collections import defaultdict

# ============================================
# CONFIGURACIÓN STREAMLIT
# ============================================
st.set_page_config(
    page_title="🚌 AMCO - Red Expandida Pereira",
    page_icon="🚌",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
    <style>
    .evento-choque {
        background-color: #ff6b6b;
        color: white;
        padding: 12px;
        border-radius: 5px;
        border-left: 5px solid #c92a2a;
        font-size: 12px;
    }
    .evento-manifestacion {
        background-color: #ffd93d;
        color: #333;
        padding: 12px;
        border-radius: 5px;
        border-left: 5px solid #f08c00;
        font-size: 12px;
    }
    .evento-obra {
        background-color: #a8e6cf;
        color: #333;
        padding: 12px;
        border-radius: 5px;
        border-left: 5px solid #56ab2f;
        font-size: 12px;
    }
    .evento-lluvia {
        background-color: #74b9ff;
        color: white;
        padding: 12px;
        border-radius: 5px;
        border-left: 5px solid #0984e3;
        font-size: 12px;
    }
    .nodo-critico {
        font-weight: bold;
        color: #d63031;
    }
    .nodo-hub {
        font-weight: bold;
        color: #0984e3;
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
        "reduccion_capacidad": 0.5,
        "duracion_minutos": 30,
        "probabilidad": 0.15,
        "descripcion": "Colisión entre vehículos - 3x más lento",
        "color": "#ff6b6b"
    },
    "manifestacion": {
        "emoji": "🚧",
        "nombre": "Manifestación / Bloqueo",
        "multiplicador_peso": float('inf'),
        "reduccion_capacidad": 1.0,
        "duracion_minutos": 120,
        "probabilidad": 0.10,
        "descripcion": "Cierre total de la vía",
        "color": "#ffd93d"
    },
    "obra": {
        "emoji": "🏗️",
        "nombre": "Obras en Vía",
        "multiplicador_peso": 1.5,
        "reduccion_capacidad": 0.3,
        "duracion_minutos": 240,
        "probabilidad": 0.20,
        "descripcion": "Reducción de carriles (+50%)",
        "color": "#a8e6cf"
    },
    "lluvia": {
        "emoji": "🌧️",
        "nombre": "Lluvia Intensa",
        "multiplicador_peso": 1.8,
        "reduccion_capacidad": 0.4,
        "duracion_minutos": 45,
        "probabilidad": 0.25,
        "descripcion": "Condiciones climáticas adversas",
        "color": "#74b9ff"
    }
}

# ============================================
# NODOS EXPANDIDOS: PEREIRA Y DOSQUEBRADAS
# ============================================

NODOS_EXPANDIDOS = {
    # === PEREIRA CENTRO ===
    1: {
        "nombre": "Centro Cívico",
        "ciudad": "Pereira",
        "zona": "Centro",
        "lat": 4.8135,
        "lon": -75.6942,
        "tipo": "hub",
        "critico": False,
        "descripcion": "Zona comercial central - Banco"
    },
    2: {
        "nombre": "Intercambiador Cuba",
        "ciudad": "Pereira",
        "zona": "Centro-Oeste",
        "lat": 4.8180,
        "lon": -75.7050,
        "tipo": "hub_critico",
        "critico": True,
        "descripcion": "🔴 HUB PRINCIPAL - Centro de transporte"
    },
    3: {
        "nombre": "Gobernación",
        "ciudad": "Pereira",
        "zona": "Centro",
        "lat": 4.8100,
        "lon": -75.6950,
        "tipo": "hub",
        "critico": True,
        "descripcion": "🔴 Instituto de Movilidad"
    },
    
    # === PEREIRA NORTE ===
    4: {
        "nombre": "Estadio",
        "ciudad": "Pereira",
        "zona": "Norte",
        "lat": 4.8350,
        "lon": -75.6900,
        "tipo": "punto",
        "critico": False,
        "descripcion": "Estadio Hernando Martínez Santagertrudis"
    },
    5: {
        "nombre": "Arabia",
        "ciudad": "Pereira",
        "zona": "Norte",
        "lat": 4.8400,
        "lon": -75.7100,
        "tipo": "punto",
        "critico": False,
        "descripcion": "Barrio Arabia - Zona residencial"
    },
    
    # === PEREIRA ESTE ===
    6: {
        "nombre": "Centro Comercial",
        "ciudad": "Pereira",
        "zona": "Este",
        "lat": 4.8050,
        "lon": -75.6750,
        "tipo": "punto",
        "critico": False,
        "descripcion": "Centro Comercial Pereira"
    },
    7: {
        "nombre": "Terminal",
        "ciudad": "Pereira",
        "zona": "Este",
        "lat": 4.8000,
        "lon": -75.6800,
        "tipo": "hub",
        "critico": True,
        "descripcion": "🔴 Terminal de Buses Pereira"
    },
    
    # === PEREIRA SUR ===
    8: {
        "nombre": "Galicia",
        "ciudad": "Pereira",
        "zona": "Sur",
        "lat": 4.7900,
        "lon": -75.7050,
        "tipo": "punto",
        "critico": False,
        "descripcion": "Barrio Galicia - Sector sur"
    },
    9: {
        "nombre": "San Joaquín",
        "ciudad": "Pereira",
        "zona": "Sur",
        "lat": 4.7850,
        "lon": -75.6900,
        "tipo": "punto",
        "critico": False,
        "descripcion": "Sector San Joaquín"
    },
    
    # === PEREIRA OESTE ===
    10: {
        "nombre": "La Popa",
        "ciudad": "Pereira",
        "zona": "Oeste",
        "lat": 4.7950,
        "lon": -75.6700,
        "tipo": "alterna",
        "critico": False,
        "descripcion": "Ruta alterna La Popa"
    },
    11: {
        "nombre": "Cartago",
        "ciudad": "Pereira",
        "zona": "Oeste",
        "lat": 4.7850,
        "lon": -75.6650,
        "tipo": "alterna",
        "critico": False,
        "descripcion": "Conexión hacia Cartago"
    },
    
    # === SALIDAS PRINCIPALES ===
    12: {
        "nombre": "Viaducto (Dosquebradas)",
        "ciudad": "Pereira-Dosquebradas",
        "zona": "Salida Oeste",
        "lat": 4.8050,
        "lon": -75.7200,
        "tipo": "critica",
        "critico": True,
        "descripcion": "🔴 VIADUCTO - Salida principal"
    },
    13: {
        "nombre": "Variante (Dosquebradas)",
        "ciudad": "Pereira-Dosquebradas",
        "zona": "Salida Suroeste",
        "lat": 4.7950,
        "lon": -75.7300,
        "tipo": "critica",
        "critico": True,
        "descripcion": "🔴 VARIANTE - Salida alternativa"
    },
    14: {
        "nombre": "Salida Norte",
        "ciudad": "Pereira-Armenia",
        "zona": "Salida Norte",
        "lat": 4.8450,
        "lon": -75.6900,
        "tipo": "critica",
        "critico": True,
        "descripcion": "🔴 Salida hacia Armenia"
    },
    
    # === DOSQUEBRADAS ===
    15: {
        "nombre": "Centro Dosquebradas",
        "ciudad": "Dosquebradas",
        "zona": "Centro",
        "lat": 4.7850,
        "lon": -75.7400,
        "tipo": "hub",
        "critico": False,
        "descripcion": "Centro comercial Dosquebradas"
    },
    16: {
        "nombre": "Pereira Viejo",
        "ciudad": "Dosquebradas",
        "zona": "Norte",
        "lat": 4.7950,
        "lon": -75.7350,
        "tipo": "punto",
        "critico": False,
        "descripcion": "Sector Pereira Viejo"
    },
    17: {
        "nombre": "Sector Kennedy",
        "ciudad": "Dosquebradas",
        "zona": "Este",
        "lat": 4.7800,
        "lon": -75.7250,
        "tipo": "punto",
        "critico": False,
        "descripcion": "Barrio Kennedy"
    },
    18: {
        "nombre": "Alsino",
        "ciudad": "Dosquebradas",
        "zona": "Sur",
        "lat": 4.7700,
        "lon": -75.7300,
        "tipo": "punto",
        "critico": False,
        "descripcion": "Sector Alsino"
    },
    19: {
        "nombre": "La Bora",
        "ciudad": "Dosquebradas",
        "zona": "Oeste",
        "lat": 4.7800,
        "lon": -75.7500,
        "tipo": "alterna",
        "critico": False,
        "descripcion": "Sector La Bora - Ruta alterna"
    },
    20: {
        "nombre": "Termales Santa Rosa",
        "ciudad": "Dosquebradas",
        "zona": "Sur",
        "lat": 4.7600,
        "lon": -75.7400,
        "tipo": "punto",
        "critico": False,
        "descripcion": "Zona turística Termales"
    }
}

# ============================================
# CONEXIONES DE RED EXPANDIDA
# ============================================

CONEXIONES_EXPANDIDAS = [
    # === CENTRO PEREIRA ===
    (1, 2, "Centro → Cuba"),
    (1, 3, "Centro → Gobernación"),
    (1, 6, "Centro → CC Pereira"),
    (1, 7, "Centro → Terminal"),
    (2, 3, "Cuba → Gobernación"),
    
    # === NORTE (Arabia - Estadio) ===
    (2, 4, "Cuba → Estadio"),
    (2, 5, "Cuba → Arabia"),
    (4, 5, "Estadio ↔ Arabia"),
    (4, 1, "Estadio → Centro"),
    (5, 6, "Arabia → CC"),
    
    # === ESTE (Terminal) ===
    (3, 6, "Gobernación → CC"),
    (3, 7, "Gobernación → Terminal"),
    (6, 7, "CC ↔ Terminal"),
    (7, 1, "Terminal → Centro"),
    (7, 9, "Terminal → San Joaquín"),
    
    # === SUR (Galicia - San Joaquín) ===
    (8, 9, "Galicia ↔ San Joaquín"),
    (8, 10, "Galicia → La Popa"),
    (9, 6, "San Joaquín → CC"),
    (9, 7, "San Joaquín → Terminal"),
    (8, 1, "Galicia → Centro"),
    
    # === OESTE (La Popa) ===
    (10, 11, "La Popa ↔ Cartago"),
    (10, 1, "La Popa → Centro"),
    (10, 3, "La Popa → Gobernación"),
    (11, 8, "Cartago → Galicia"),
    
    # === SALIDAS PRINCIPALES ===
    (2, 12, "Cuba → Viaducto"),
    (3, 12, "Gobernación → Viaducto"),
    (2, 13, "Cuba → Variante"),
    (3, 13, "Gobernación → Variante"),
    (8, 13, "Galicia → Variante"),
    (10, 13, "La Popa → Variante"),
    (4, 14, "Estadio → Salida Norte"),
    (5, 14, "Arabia → Salida Norte"),
    (12, 14, "Viaducto ↔ Salida Norte (largo)"),
    
    # === DOSQUEBRADAS ===
    (12, 15, "Viaducto → Centro Dosquebradas"),
    (12, 16, "Viaducto → Pereira Viejo"),
    (13, 15, "Variante → Centro Dosquebradas"),
    (13, 18, "Variante → Alsino"),
    (13, 19, "Variante → La Bora"),
    (15, 16, "Centro Dosquebradas ↔ Pereira Viejo"),
    (15, 17, "Centro Dosquebradas → Kennedy"),
    (15, 20, "Centro Dosquebradas → Termales"),
    (16, 17, "Pereira Viejo ↔ Kennedy"),
    (17, 18, "Kennedy ↔ Alsino"),
    (18, 20, "Alsino ↔ Termales"),
    (19, 15, "La Bora → Centro Dosquebradas"),
    (19, 18, "La Bora ↔ Alsino"),
    (20, 18, "Termales ↔ Alsino"),
    
    # === RUTAS ALTERNAS INTERNAS ===
    (4, 6, "Estadio → CC (atajo)"),
    (5, 7, "Arabia → Terminal (diagonal)"),
    (6, 9, "CC → San Joaquín"),
    (8, 11, "Galicia → Cartago (atajo)"),
]

# ============================================
# CLASE: SISTEMA EXPANDIDO
# ============================================

class SistemaTransporteExpandido:
    """Sistema de transporte de Pereira/Dosquebradas expandido"""
    
    def __init__(self):
        self.nodos = NODOS_EXPANDIDOS.copy()
        self.grafo = None
        self.eventos_activos = {}
        self.historial_eventos = []
        self.crear_grafo()
    
    def distancia_euclidiana(self, p1, p2):
        """Calcula distancia euclidiana"""
        dlat = p2["lat"] - p1["lat"]
        dlon = p2["lon"] - p1["lon"]
        distancia_grados = np.sqrt(dlat**2 + dlon**2)
        distancia_km = distancia_grados * 111
        return round(distancia_km, 2)
    
    def crear_grafo(self):
        """Crea grafo expandido"""
        self.grafo = nx.Graph()
        
        # Agregar nodos
        for nodo_id, nodo_data in self.nodos.items():
            self.grafo.add_node(
                nodo_id,
                nombre=nodo_data["nombre"],
                lat=nodo_data["lat"],
                lon=nodo_data["lon"],
                critico=nodo_data["critico"],
                tipo=nodo_data["tipo"],
                zona=nodo_data["zona"]
            )
        
        # Agregar conexiones
        for nodo_i, nodo_j, descripcion in CONEXIONES_EXPANDIDAS:
            distancia = self.distancia_euclidiana(
                self.nodos[nodo_i],
                self.nodos[nodo_j]
            )
            
            self.grafo.add_edge(
                nodo_i, nodo_j,
                weight=distancia,
                peso_original=distancia,
                descripcion=descripcion,
                capacidad=100
            )
    
    def inyectar_evento(self, tipo_evento, nodo1, nodo2):
        """Inyecta evento en arista"""
        if tipo_evento not in TIPOS_EVENTOS:
            return False
        
        if nodo2 < nodo1:
            nodo1, nodo2 = nodo2, nodo1
        
        arista = (nodo1, nodo2)
        
        if not self.grafo.has_edge(nodo1, nodo2):
            return False
        
        evento_config = TIPOS_EVENTOS[tipo_evento]
        peso_original = self.grafo[nodo1][nodo2]['peso_original']
        
        if evento_config['multiplicador_peso'] == float('inf'):
            nuevo_peso = float('inf')
        else:
            nuevo_peso = peso_original * evento_config['multiplicador_peso']
        
        self.grafo[nodo1][nodo2]['weight'] = nuevo_peso
        self.grafo[nodo1][nodo2]['capacidad'] = 100 * (1 - evento_config['reduccion_capacidad'])
        
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
        """Limpia evento"""
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
        """Calcula ruta óptima"""
        try:
            if not nx.has_path(self.grafo, origen, destino):
                return None, [], None
            
            distancia = nx.dijkstra_path_length(self.grafo, origen, destino, weight='weight')
            ruta = nx.dijkstra_path(self.grafo, origen, destino, weight='weight')
            
            capacidad_min = 100
            for i in range(len(ruta) - 1):
                nodo1, nodo2 = ruta[i], ruta[i+1]
                cap = self.grafo[nodo1][nodo2]['capacidad']
                capacidad_min = min(capacidad_min, cap)
            
            return round(distancia, 2), ruta, capacidad_min
        except:
            return None, [], None
    
    def calcular_impacto(self, origen, destino):
        """Calcula impacto de eventos"""
        estado_actual = {}
        for n1, n2 in self.grafo.edges():
            estado_actual[(n1, n2)] = {
                'weight': self.grafo[n1][n2]['weight'],
                'capacidad': self.grafo[n1][n2]['capacidad']
            }
        
        for arista in list(self.eventos_activos.keys()):
            self.limpiar_evento(arista[0], arista[1])
        
        dist_original, ruta_original, cap_original = self.calcular_ruta_optima(origen, destino)
        
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
    
    def obtener_estadisticas(self):
        """Retorna estadísticas de la red"""
        criticos = sum(1 for n in self.nodos.values() if n['critico'])
        hubs = sum(1 for n in self.nodos.values() if 'hub' in n['tipo'])
        alternativos = sum(1 for n in self.nodos.values() if n['tipo'] == 'alterna')
        bloqueados = sum(1 for n1, n2 in self.grafo.edges() if self.grafo[n1][n2]['weight'] == float('inf'))
        
        return {
            'nodos_totales': len(self.nodos),
            'rutas_totales': len(list(self.grafo.edges())),
            'nodos_criticos': criticos,
            'hubs': hubs,
            'rutas_alternas': alternativos,
            'aristas_bloqueadas': bloqueados,
            'eventos_activos': len(self.eventos_activos)
        }

# ============================================
# VISUALIZACIÓN DEL GRAFO EXPANDIDO
# ============================================

def dibujar_grafo_expandido(sistema, ruta_resaltada=None, ruta_alternativa=None):
    """Dibuja el grafo expandido"""
    fig, ax = plt.subplots(figsize=(16, 13))
    
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
        
        color = '#cccccc'
        ancho = 1
        alpha = 0.4
        
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
    
    # Dibujar nodos
    for nodo_id, (x, y) in pos.items():
        nodo_data = sistema.nodos[nodo_id]
        
        if nodo_data['critico']:
            color_nodo = '#d63031'
            tamaño = 800
        elif 'hub' in nodo_data['tipo']:
            color_nodo = '#0984e3'
            tamaño = 700
        else:
            color_nodo = '#667eea'
            tamaño = 600
        
        ax.scatter(x, y, s=tamaño, c=color_nodo, edgecolors='black', 
                  linewidth=2, zorder=3, alpha=0.9)
        
        ax.text(x, y, str(nodo_id), ha='center', va='center', 
               fontweight='bold', color='white', fontsize=9, zorder=4)
        
        ax.text(x, y - 0.3, nodo_data['nombre'], ha='center', va='top', 
               fontsize=7, style='italic', zorder=4)
    
    ax.set_title('🗺️ RED EXPANDIDA PEREIRA Y DOSQUEBRADAS\n' +
                '(Rojo=Crítico | Azul=Hub | Púrpura=Normal | Verde=Alternativa)',
                fontsize=12, fontweight='bold', pad=20)
    ax.set_xlabel('Longitud', fontsize=9)
    ax.set_ylabel('Latitud', fontsize=9)
    ax.grid(True, alpha=0.2)
    ax.set_aspect('equal')
    
    plt.tight_layout()
    return fig

# ============================================
# INICIALIZACIÓN
# ============================================

if 'sistema_exp' not in st.session_state:
    st.session_state.sistema_exp = SistemaTransporteExpandido()
    st.session_state.ruta_actual = []
    st.session_state.distancia_actual = 0
    st.session_state.eventos_simulados = []

# ============================================
# INTERFAZ PRINCIPAL
# ============================================

def main():
    st.title("🚌 AMCO - RED EXPANDIDA PEREIRA & DOSQUEBRADAS")
    st.markdown("**20+ Nodos | Múltiples Rutas Alternas | Eventos Probabilísticos**")
    
    sistema = st.session_state.sistema_exp
    stats = sistema.obtener_estadisticas()
    
    # === SIDEBAR ===
    with st.sidebar:
        st.header("🎮 CONTROL AVANZADO")
        
        st.subheader("📊 Estado de la Red")
        col1, col2 = st.columns(2)
        with col1:
            st.metric("Total Nodos", stats['nodos_totales'])
            st.metric("Hubs", stats['hubs'])
        with col2:
            st.metric("Total Rutas", stats['rutas_totales'])
            st.metric("Críticos", stats['nodos_criticos'])
        
        st.divider()
        
        st.subheader("📍 Configurar Ruta")
        
        opciones = {f"{nid}. {nd['nombre'][:30]}" : nid for nid, nd in sistema.nodos.items()}
        
        col1, col2 = st.columns(2)
        with col1:
            origen_key = st.selectbox("Origen:", list(opciones.keys())[:10])
            origen = opciones[origen_key]
        
        with col2:
            destino_key = st.selectbox("Destino:", list(opciones.keys())[10:])
            destino = opciones[destino_key]
        
        if origen == destino:
            st.warning("⚠️ Origen y destino deben ser diferentes")
            return
        
        if st.button("🔍 Calcular Ruta", use_container_width=True):
            inicio = time.time()
            dist, ruta, cap = sistema.calcular_ruta_optima(origen, destino)
            
            st.session_state.ruta_actual = ruta
            st.session_state.distancia_actual = dist
            st.session_state.origen = origen
            st.session_state.destino = destino
            st.session_state.distancia_original = dist
            st.session_state.capacidad_original = cap
            st.session_state.tiempo_calculo = round(time.time() - inicio, 4)
            
            st.success("✅ Ruta calculada")
            st.rerun()
        
        st.divider()
        
        st.subheader("⚠️ INYECTAR EVENTOS")
        
        tipo_evento = st.selectbox(
            "Tipo:",
            options=list(TIPOS_EVENTOS.keys()),
            format_func=lambda x: f"{TIPOS_EVENTOS[x]['emoji']} {TIPOS_EVENTOS[x]['nombre']}"
        )
        
        evento_config = TIPOS_EVENTOS[tipo_evento]
        st.info(evento_config['descripcion'])
        
        aristas_str = []
        aristas_map = {}
        
        for n1, n2 in sistema.grafo.edges():
            arista_name = (n1, n2) if n1 < n2 else (n2, n1)
            label = f"{n1}-{n2}: {sistema.nodos[n1]['nombre'][:20]} ↔ {sistema.nodos[n2]['nombre'][:20]}"
            aristas_str.append(label)
            aristas_map[label] = arista_name
        
        arista_selected = st.selectbox("Arista:", aristas_str)
        nodo1, nodo2 = aristas_map[arista_selected]
        
        col1, col2 = st.columns(2)
        with col1:
            if st.button("💉 INYECTAR", use_container_width=True):
                sistema.inyectar_evento(tipo_evento, nodo1, nodo2)
                
                if hasattr(st.session_state, 'origen'):
                    dist, ruta, cap = sistema.calcular_ruta_optima(
                        st.session_state.origen,
                        st.session_state.destino
                    )
                    st.session_state.ruta_actual = ruta
                    st.session_state.distancia_actual = dist
                    st.session_state.capacidad_actual = cap
                
                st.rerun()
        
        with col2:
            if st.button("🧹 LIMPIAR", use_container_width=True):
                sistema.limpiar_evento(nodo1, nodo2)
                
                if hasattr(st.session_state, 'origen'):
                    dist, ruta, cap = sistema.calcular_ruta_optima(
                        st.session_state.origen,
                        st.session_state.destino
                    )
                    st.session_state.ruta_actual = ruta
                    st.session_state.distancia_actual = dist
                    st.session_state.capacidad_actual = cap
                
                st.rerun()
        
        if sistema.eventos_activos:
            st.markdown("### 🚨 Eventos Activos")
            for arista, evento in sistema.eventos_activos.items():
                st.markdown(
                    f"<div style='background-color: {evento['config']['color']}; "
                    f"color: white; padding: 10px; border-radius: 5px; margin: 5px 0;'>"
                    f"<strong>{evento['config']['emoji']}</strong> "
                    f"{evento['nodo1_nombre'][:15]} ↔ {evento['nodo2_nombre'][:15]}</div>",
                    unsafe_allow_html=True
                )
    
    # === CONTENIDO PRINCIPAL ===
    
    if not hasattr(st.session_state, 'origen'):
        st.info("👈 Configura la ruta en el panel lateral")
        return
    
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "🗺️ Mapa Red",
        "📊 Comparativa",
        "📈 Estadísticas",
        "⚠️ Eventos",
        "📋 Historial"
    ])
    
    # TAB 1
    with tab1:
        st.subheader("Red Completa de Transporte")
        
        fig = dibujar_grafo_expandido(
            sistema,
            ruta_resaltada=st.session_state.ruta_actual,
            ruta_alternativa=st.session_state.ruta_original if hasattr(st.session_state, 'ruta_original') else None
        )
        
        st.pyplot(fig, use_container_width=True)
    
    # TAB 2
    with tab2:
        st.subheader("Comparativa de Rutas")
        
        if sistema.eventos_activos:
            impacto = sistema.calcular_impacto(
                st.session_state.origen,
                st.session_state.destino
            )
            
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Distancia Original", f"{impacto['dist_original']} km")
            with col2:
                st.metric("Distancia Actual", f"{impacto['dist_actual']} km",
                         delta=f"{impacto['incremento']:+.2f} km")
            with col3:
                por = (impacto['incremento'] / impacto['dist_original'] * 100) if impacto['dist_original'] else 0
                st.metric("Impacto %", f"{por:+.1f}%")
            
            st.divider()
            
            col1, col2 = st.columns(2)
            with col1:
                st.info("**Ruta Original:**\n" + " → ".join([
                    f"{nid}. {sistema.nodos[nid]['nombre']}"
                    for nid in impacto['ruta_original']
                ]))
            
            with col2:
                st.warning("**Ruta Actual:**\n" + " → ".join([
                    f"{nid}. {sistema.nodos[nid]['nombre']}"
                    for nid in impacto['ruta_actual']
                ]))
    
    # TAB 3
    with tab3:
        st.subheader("Estadísticas Avanzadas")
        
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Nodos Totales", stats['nodos_totales'])
        with col2:
            st.metric("Rutas Totales", stats['rutas_totales'])
        with col3:
            st.metric("Nodos Críticos", stats['nodos_criticos'])
        with col4:
            st.metric("Aristas Bloqueadas", stats['aristas_bloqueadas'])
        
        st.divider()
        
        # Nodos por zona
        st.markdown("### Nodos por Zona")
        zonas = defaultdict(list)
        for nid, ndata in sistema.nodos.items():
            zonas[ndata['zona']].append(f"{nid}. {ndata['nombre']}")
        
        col1, col2, col3 = st.columns(3)
        cols = [col1, col2, col3]
        for idx, (zona, nodos) in enumerate(sorted(zonas.items())):
            with cols[idx % 3]:
                st.markdown(f"**{zona}** ({len(nodos)} nodos)")
                for nodo in nodos:
                    st.text(nodo)
    
    # TAB 4
    with tab4:
        st.subheader("Análisis de Eventos")
        
        if sistema.eventos_activos:
            for arista, evento in sistema.eventos_activos.items():
                config = evento['config']
                st.markdown(f"### {config['emoji']} {evento['nodo1_nombre']} ↔ {evento['nodo2_nombre']}")
                
                col1, col2, col3, col4 = st.columns(4)
                with col1:
                    st.metric("Peso Orig", f"{evento['peso_original']}km")
                with col2:
                    st.metric("Peso Nuevo", f"{evento['peso_nuevo']}km" if evento['peso_nuevo'] != float('inf') else "∞")
                with col3:
                    st.metric("Capacidad", f"{evento['capacidad_nueva']:.0f}%")
                with col4:
                    st.metric("Tipo", config['nombre'])
                
                st.divider()
        else:
            st.success("✅ Sin eventos activos")
    
    # TAB 5
    with tab5:
        st.subheader("Historial Completo")
        
        if sistema.historial_eventos:
            df_events = []
            for evt in sistema.historial_eventos:
                df_events.append({
                    'Hora': evt['timestamp'].strftime("%H:%M:%S"),
                    'Tipo': evt['config']['emoji'],
                    'De': evt['nodo1_nombre'][:15],
                    'A': evt['nodo2_nombre'][:15],
                    'Peso Orig': f"{evt['peso_original']}km",
                    'Peso Nuevo': f"{evt['peso_nuevo']}km" if evt['peso_nuevo'] != float('inf') else "∞",
                    'Capacidad': f"{evt['capacidad_nueva']:.0f}%"
                })
            
            df = pd.DataFrame(df_events)
            st.dataframe(df, use_container_width=True)

if __name__ == "__main__":
    main()
