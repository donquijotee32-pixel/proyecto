"""
🛠️ UTILIDADES Y FUNCIONES AUXILIARES REUTILIZABLES
Módulo de funciones compartidas para todo el proyecto
"""

import numpy as np
import pandas as pd
from typing import List, Dict, Tuple, Optional, Any
from datetime import datetime, timedelta
import json
import os
import math
from math import radians, sin, cos, sqrt, atan2


# ==================== FUNCIONES GEOGRÁFICAS ====================

def haversine(lat1, lon1, lat2, lon2):
    """Calcula distancia en KM entre dos puntos geográficos"""
    R = 6371
    lat1_rad = radians(lat1)
    lat2_rad = radians(lat2)
    delta_lat = radians(lat2 - lat1)
    delta_lon = radians(lon2 - lon1)
    
    a = sin(delta_lat / 2) ** 2 + cos(lat1_rad) * cos(lat2_rad) * sin(delta_lon / 2) ** 2
    c = 2 * atan2(sqrt(a), sqrt(1 - a))
    
    return R * c


def calcular_distancia_ruta(path):
    """Calcula distancia total de una ruta"""
    if not path or len(path) < 2:
        return 0.0
    
    distancia_total = 0.0
    
    for i in range(len(path) - 1):
        lon1, lat1 = path[i]
        lon2, lat2 = path[i + 1]
        distancia_total += haversine(lat1, lon1, lat2, lon2)
    
    return round(distancia_total, 2)


def calcular_tiempo_estimado(distancia_km, velocidad_promedio_kmh=30):
    """Calcula tiempo estimado de una ruta"""
    if distancia_km == 0 or velocidad_promedio_kmh == 0:
        return 0.0
    
    horas = distancia_km / velocidad_promedio_kmh
    minutos = horas * 60
    
    return round(minutos, 1)


def calcular_demanda_promedio(personas_list: List[int]) -> float:
    """Calcula demanda promedio de personas esperando en paradas"""
    if not personas_list:
        return 0.0
    
    return round(sum(personas_list) / len(personas_list), 2)


def path_json_a_lista(path_json: str) -> List[list]:
    """Convierte path JSON string a lista de coordenadas"""
    try:
        return json.loads(path_json)
    except:
        return []


# ==================== UTILIDADES GENERALES ====================

class UtilsGenerales:
    """Funciones auxiliares generales"""
    
    @staticmethod
    def formato_hora(minutos: int) -> str:
        """Convierte minutos a formato HH:MM"""
        horas = minutos // 60
        mins = minutos % 60
        return f"{horas:02d}:{mins:02d}"
    
    @staticmethod
    def porcentaje_a_color(valor: float) -> str:
        """Convierte porcentaje a código de color hexadecimal"""
        if valor < 25:
            return "#2ecc71"  # Verde
        elif valor < 50:
            return "#f39c12"  # Naranja
        elif valor < 75:
            return "#e67e22"  # Naranja oscuro
        else:
            return "#e74c3c"  # Rojo
    
    @staticmethod
    def estado_a_emoji(estado: str) -> str:
        """Convierte estado a emoji descriptivo"""
        estados = {
            "excelente": "🟢",
            "bueno": "🟢",
            "normal": "🟡",
            "malo": "🟠",
            "critico": "🔴",
            "alerta": "⚠️",
            "error": "❌",
            "mantenimiento": "🔧",
            "activo": "✅",
            "inactivo": "⏸️"
        }
        return estados.get(estado.lower(), "❓")
    
    @staticmethod
    def redondear(valor: float, decimales: int = 2) -> float:
        """Redondea valor a n decimales"""
        return round(valor, decimales)


class ValidacionDatos:
    """Validación de datos y parámetros"""
    
    @staticmethod
    def validar_rango(valor: float, min_val: float, max_val: float) -> bool:
        """Valida que valor esté en rango"""
        return min_val <= valor <= max_val
    
    @staticmethod
    def validar_coordenadas(lat: float, lon: float) -> bool:
        """Valida coordenadas geográficas"""
        return -90 <= lat <= 90 and -180 <= lon <= 180
    
    @staticmethod
    def validar_datos_df(df: pd.DataFrame, columnas_requeridas: List[str]) -> bool:
        """Valida que DataFrame tenga columnas requeridas"""
        return all(col in df.columns for col in columnas_requeridas)


class OperacionesDataFrame:
    """Operaciones comunes con pandas DataFrames"""
    
    @staticmethod
    def filtrar_por_rango_fecha(df: pd.DataFrame, col_fecha: str, 
                                fecha_inicio: datetime, 
                                fecha_fin: datetime) -> pd.DataFrame:
        """Filtra DataFrame por rango de fechas"""
        df_copia = df.copy()
        df_copia[col_fecha] = pd.to_datetime(df_copia[col_fecha])
        return df_copia[(df_copia[col_fecha] >= fecha_inicio) & 
                        (df_copia[col_fecha] <= fecha_fin)]
    
    @staticmethod
    def estadisticas_basicas(df: pd.DataFrame, columnas: List[str]) -> Dict:
        """Calcula estadísticas básicas de columnas"""
        stats = {}
        for col in columnas:
            if col in df.columns:
                stats[col] = {
                    "media": df[col].mean(),
                    "mediana": df[col].median(),
                    "std": df[col].std(),
                    "min": df[col].min(),
                    "max": df[col].max()
                }
        return stats
    
    @staticmethod
    def agrupar_y_contar(df: pd.DataFrame, columna_grupo: str) -> pd.DataFrame:
        """Agrupa y cuenta registros por columna"""
        return df.groupby(columna_grupo).size().reset_index(name='cantidad')


class CacheSimple:
    """Sistema simple de cache en memoria con expiración"""
    
    def __init__(self, ttl_segundos: int = 300):
        self.cache = {}
        self.ttl = ttl_segundos
    
    def set(self, clave: str, valor: Any, segundos: Optional[int] = None):
        """Almacena valor en cache"""
        expiracion = datetime.now() + timedelta(seconds=segundos or self.ttl)
        self.cache[clave] = {
            "valor": valor,
            "expiracion": expiracion
        }
    
    def get(self, clave: str, default: Any = None) -> Any:
        """Obtiene valor del cache si no ha expirado"""
        if clave not in self.cache:
            return default
        
        item = self.cache[clave]
        
        if datetime.now() > item["expiracion"]:
            del self.cache[clave]
            return default
        
        return item["valor"]
    
    def limpiar(self):
        """Limpia todo el cache"""
        self.cache.clear()


class GeneradorReportes:
    """Genera reportes en diferentes formatos"""
    
    @staticmethod
    def generar_reporte_texto(titulo: str, datos: Dict) -> str:
        """Genera reporte en formato texto"""
        reporte = f"\n{'='*50}\n"
        reporte += f"{titulo}\n"
        reporte += f"{'='*50}\n"
        reporte += f"Generado: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n"
        
        for clave, valor in datos.items():
            reporte += f"{clave}: {valor}\n"
        
        return reporte
    
    @staticmethod
    def generar_reporte_json(datos: Dict) -> str:
        """Genera reporte en JSON"""
        return json.dumps(datos, indent=2, default=str)
    
    @staticmethod
    def generar_reporte_csv(df: pd.DataFrame) -> str:
        """Genera reporte en CSV"""
        return df.to_csv(index=False)


class LoggerSimple:
    """Sistema simple de logging"""
    
    def __init__(self):
        self.logs = []
    
    def log(self, nivel: str, mensaje: str):
        """Registra un log"""
        entrada = {
            "timestamp": datetime.now().isoformat(),
            "nivel": nivel,
            "mensaje": mensaje
        }
        self.logs.append(entrada)
    
    def obtener_logs(self, nivel: Optional[str] = None, limite: int = 100) -> List[Dict]:
        """Obtiene logs filtrados"""
        logs = self.logs
        
        if nivel:
            logs = [l for l in logs if l["nivel"] == nivel]
        
        return logs[-limite:]
    
    def limpiar(self):
        """Limpia logs"""
        self.logs.clear()


class NormalizadorDatos:
    """Normaliza datos para procesamiento"""
    
    @staticmethod
    def normalizar_0_1(valores: List[float]) -> List[float]:
        """Normaliza a rango [0, 1]"""
        if not valores:
            return []
        
        min_val = min(valores)
        max_val = max(valores)
        
        if min_val == max_val:
            return [0.5] * len(valores)
        
        return [(v - min_val) / (max_val - min_val) for v in valores]
    
    @staticmethod
    def normalizar_m1_1(valores: List[float]) -> List[float]:
        """Normaliza a rango [-1, 1]"""
        normalizados = NormalizadorDatos.normalizar_0_1(valores)
        return [2 * v - 1 for v in normalizados]


class TiemposUtiles:
    """Utilidades para manejo de tiempos"""
    
    @staticmethod
    def tiempo_hasta_ahora(fecha: datetime) -> str:
        """Retorna tiempo transcurrido legible"""
        diferencia = datetime.now() - fecha
        segundos = diferencia.total_seconds()
        
        if segundos < 60:
            return f"hace {int(segundos)}s"
        elif segundos < 3600:
            return f"hace {int(segundos/60)}m"
        elif segundos < 86400:
            return f"hace {int(segundos/3600)}h"
        else:
            return f"hace {int(segundos/86400)}d"


if __name__ == "__main__":
    print("✅ Módulo de utilidades cargado correctamente")
    print(f"Hora: {UtilsGenerales.formato_hora(125)}")
    print(f"Color 75%: {UtilsGenerales.porcentaje_a_color(75)}")
