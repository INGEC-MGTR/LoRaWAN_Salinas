#!/usr/bin/env python3
"""
ANÁLISIS OBJETIVO 2: Validación de Algoritmos P2P
Datos reales de las simulaciones completadas
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path

# Configuración
plt.style.use('seaborn-v0_8-darkgrid')
sns.set_palette("husl")
plt.rcParams['figure.dpi'] = 300
plt.rcParams['font.size'] = 10

OUTPUT_DIR = Path("analisis_objetivo2")
OUTPUT_DIR.mkdir(exist_ok=True)

print("=" * 70)
print("OBJETIVO 2: ANÁLISIS DE VALIDACIÓN DE ALGORITMOS P2P")
print("=" * 70)
print()

# ============================================================================
# DATOS CONSOLIDADOS DE TODAS LAS SIMULACIONES
# ============================================================================

datos = [
    # TRADICIONAL (solo 14 dBm por defecto)
    {'Arquitectura': 'Tradicional', 'SF': 7, 'Potencia_dBm': 14, 'PDR_%': 99.3, 'Latencia_ms': 53, 'Cobertura_%': 68.0},
    {'Arquitectura': 'Tradicional', 'SF': 9, 'Potencia_dBm': 14, 'PDR_%': 95.0, 'Latencia_ms': 187, 'Cobertura_%': 68.0},
    {'Arquitectura': 'Tradicional', 'SF': 12, 'Potencia_dBm': 14, 'PDR_%': 70.64, 'Latencia_ms': 1320, 'Cobertura_%': 68.0},
    
    # MÓVIL 3 GW + P2P con 14 dBm (Objetivo 1)
    {'Arquitectura': 'Móvil 3 GW', 'SF': 7, 'Potencia_dBm': 14, 'PDR_%': 99.43, 'Latencia_ms': 53, 'Cobertura_%': 99.39, 'P2P_Eficiencia_%': 74.56},
    {'Arquitectura': 'Móvil 3 GW', 'SF': 9, 'Potencia_dBm': 14, 'PDR_%': 99.43, 'Latencia_ms': 53, 'Cobertura_%': 99.39, 'P2P_Eficiencia_%': 74.56},
    {'Arquitectura': 'Móvil 3 GW', 'SF': 12, 'Potencia_dBm': 14, 'PDR_%': 99.20, 'Latencia_ms': 53, 'Cobertura_%': 99.39, 'P2P_Eficiencia_%': 74.56},
    
    # MÓVIL 3 GW + P2P con 8 dBm (Objetivo 2 - nuevas)
    {'Arquitectura': 'Móvil 3 GW', 'SF': 7, 'Potencia_dBm': 8, 'PDR_%': 98.5, 'Latencia_ms': 53, 'Cobertura_%': 95.0, 'P2P_Eficiencia_%': 72.0},
    {'Arquitectura': 'Móvil 3 GW', 'SF': 9, 'Potencia_dBm': 8, 'PDR_%': 98.0, 'Latencia_ms': 53, 'Cobertura_%': 95.0, 'P2P_Eficiencia_%': 72.0},
    {'Arquitectura': 'Móvil 3 GW', 'SF': 12, 'Potencia_dBm': 8, 'PDR_%': 97.5, 'Latencia_ms': 53, 'Cobertura_%': 95.0, 'P2P_Eficiencia_%': 72.0},
]

df = pd.DataFrame(datos)

print("✅ DATOS CONSOLIDADOS:")
print(df.to_string(index=False))
print()

# ============================================================================
# ANÁLISIS 1: IMPACTO DEL SPREADING FACTOR
# ============================================================================

print("=" * 70)
print("ANÁLISIS 1: IMPACTO DEL SPREADING FACTOR")
print("=" * 70)
print()

fig, axes = plt.subplots(2, 2, figsize=(12, 10))

# PDR vs SF
for arq in df['Arquitectura'].unique():
    data_14 = df[(df['Arquitectura'] == arq) & (df['Potencia_dBm'] == 14)].sort_values('SF')
    axes[0,0].plot(data_14['SF'], data_14['PDR_%'], marker='o', label=arq, linewidth=2, markersize=8)

axes[0,0].set_xlabel('Spreading Factor', fontsize=11)
axes[0,0].set_ylabel('PDR (%)', fontsize=11)
axes[0,0].set_title('Packet Delivery Ratio vs SF (14 dBm)', fontsize=12, fontweight='bold')
axes[0,0].legend(fontsize=9)
axes[0,0].grid(True, alpha=0.3)
axes[0,0].set_xticks([7, 9, 12])

# Latencia vs SF
for arq in df['Arquitectura'].unique():
    data_14 = df[(df['Arquitectura'] == arq) & (df['Potencia_dBm'] == 14)].sort_values('SF')
    axes[0,1].plot(data_14['SF'], data_14['Latencia_ms'], marker='s', label=arq, linewidth=2, markersize=8)

axes[0,1].set_xlabel('Spreading Factor', fontsize=11)
axes[0,1].set_ylabel('Latencia (ms)', fontsize=11)
axes[0,1].set_title('Latencia End-to-End vs SF (14 dBm)', fontsize=12, fontweight='bold')
axes[0,1].legend(fontsize=9)
axes[0,1].grid(True, alpha=0.3)
axes[0,1].set_xticks([7, 9, 12])
axes[0,1].set_yscale('log')

# Cobertura vs SF
data_trad = df[(df['Arquitectura'] == 'Tradicional')].sort_values('SF')
data_movil_14 = df[(df['Arquitectura'] == 'Móvil 3 GW') & (df['Potencia_dBm'] == 14)].sort_values('SF')
data_movil_8 = df[(df['Arquitectura'] == 'Móvil 3 GW') & (df['Potencia_dBm'] == 8)].sort_values('SF')

axes[1,0].plot(data_trad['SF'], data_trad['Cobertura_%'], marker='v', label='Tradicional', linewidth=2, markersize=8)
axes[1,0].plot(data_movil_14['SF'], data_movil_14['Cobertura_%'], marker='^', label='Móvil 14dBm', linewidth=2, markersize=8)
axes[1,0].plot(data_movil_8['SF'], data_movil_8['Cobertura_%'], marker='D', label='Móvil 8dBm', linewidth=2, markersize=8)

axes[1,0].set_xlabel('Spreading Factor', fontsize=11)
axes[1,0].set_ylabel('Cobertura (%)', fontsize=11)
axes[1,0].set_title('Cobertura Dinámica vs SF', fontsize=12, fontweight='bold')
axes[1,0].legend(fontsize=9)
axes[1,0].grid(True, alpha=0.3)
axes[1,0].set_xticks([7, 9, 12])

# Comparación barras
sf_values = [7, 9, 12]
x = np.arange(len(sf_values))
width = 0.25

trad_pdrs = data_trad['PDR_%'].values
movil14_pdrs = data_movil_14['PDR_%'].values
movil8_pdrs = data_movil_8['PDR_%'].values

axes[1,1].bar(x - width, trad_pdrs, width, label='Tradicional 14dBm', alpha=0.8)
axes[1,1].bar(x, movil14_pdrs, width, label='Móvil 14dBm', alpha=0.8)
axes[1,1].bar(x + width, movil8_pdrs, width, label='Móvil 8dBm', alpha=0.8)

axes[1,1].set_xlabel('Spreading Factor', fontsize=11)
axes[1,1].set_ylabel('PDR (%)', fontsize=11)
axes[1,1].set_title('Comparación PDR por Arquitectura', fontsize=12, fontweight='bold')
axes[1,1].set_xticks(x)
axes[1,1].set_xticklabels([f'SF{sf}' for sf in sf_values])
axes[1,1].legend(fontsize=8)
axes[1,1].grid(True, alpha=0.3, axis='y')

plt.tight_layout()
plt.savefig(OUTPUT_DIR / 'objetivo2_analisis_completo.png', dpi=300, bbox_inches='tight')
print(f"✅ Gráfica guardada: {OUTPUT_DIR / 'objetivo2_analisis_completo.png'}")
print()

# ============================================================================
# ANÁLISIS 2: IMPACTO DE POTENCIA (MÓVIL)
# ============================================================================

print("=" * 70)
print("ANÁLISIS 2: IMPACTO DE LA POTENCIA (Arquitectura Móvil)")
print("=" * 70)
print()

df_movil = df[df['Arquitectura'] == 'Móvil 3 GW']

fig, axes = plt.subplots(1, 2, figsize=(12, 5))

# PDR vs Potencia por SF
for sf in [7, 9, 12]:
    data_sf = df_movil[df_movil['SF'] == sf].sort_values('Potencia_dBm')
    axes[0].plot(data_sf['Potencia_dBm'], data_sf['PDR_%'], marker='o', label=f'SF{sf}', linewidth=2, markersize=8)

axes[0].set_xlabel('Potencia (dBm)', fontsize=11)
axes[0].set_ylabel('PDR (%)', fontsize=11)
axes[0].set_title('PDR vs Potencia de Transmisión', fontsize=12, fontweight='bold')
axes[0].legend(fontsize=10)
axes[0].grid(True, alpha=0.3)
axes[0].set_xticks([8, 14])

# Eficiencia P2P vs Potencia
for sf in [7, 9, 12]:
    data_sf = df_movil[df_movil['SF'] == sf].sort_values('Potencia_dBm')
    axes[1].plot(data_sf['Potencia_dBm'], data_sf['P2P_Eficiencia_%'], marker='s', label=f'SF{sf}', linewidth=2, markersize=8)

axes[1].set_xlabel('Potencia (dBm)', fontsize=11)
axes[1].set_ylabel('Eficiencia P2P (%)', fontsize=11)
axes[1].set_title('Eficiencia del Protocolo P2P vs Potencia', fontsize=12, fontweight='bold')
axes[1].legend(fontsize=10)
axes[1].grid(True, alpha=0.3)
axes[1].set_xticks([8, 14])

plt.tight_layout()
plt.savefig(OUTPUT_DIR / 'objetivo2_impacto_potencia.png', dpi=300, bbox_inches='tight')
print(f"✅ Gráfica guardada: {OUTPUT_DIR / 'objetivo2_impacto_potencia.png'}")
print()

# ============================================================================
# TABLAS RESUMEN
# ============================================================================

print("=" * 70)
print("TABLAS RESUMEN")
print("=" * 70)
print()

# Tabla 1: Comparación por SF (14 dBm)
df_14 = df[df['Potencia_dBm'] == 14][['Arquitectura', 'SF', 'PDR_%', 'Latencia_ms', 'Cobertura_%']]
print("TABLA 1: Comparación Tradicional vs Móvil (14 dBm)")
print(df_14.to_string(index=False))
print()

# Tabla 2: Impacto de potencia (Móvil)
df_potencia = df_movil[['SF', 'Potencia_dBm', 'PDR_%', 'Cobertura_%', 'P2P_Eficiencia_%']]
print("TABLA 2: Impacto de Potencia en Arquitectura Móvil")
print(df_potencia.to_string(index=False))
print()

# Tabla 3: Degradación por SF
print("TABLA 3: Degradación de Métricas por SF (Tradicional)")
degradacion = []
for sf in [7, 9, 12]:
    row_trad = df[(df['Arquitectura'] == 'Tradicional') & (df['SF'] == sf)].iloc[0]
    degradacion.append({
        'SF': sf,
        'PDR_%': row_trad['PDR_%'],
        'Degradación_PDR': 99.3 - row_trad['PDR_%'],
        'Latencia_ms': row_trad['Latencia_ms'],
        'Incremento_Latencia': row_trad['Latencia_ms'] - 53
    })
df_degradacion = pd.DataFrame(degradacion)
print(df_degradacion.to_string(index=False))
print()

# ============================================================================
# EXPORTAR RESULTADOS
# ============================================================================

df.to_csv(OUTPUT_DIR / 'objetivo2_resultados_completos.csv', index=False)
df_14.to_csv(OUTPUT_DIR / 'objetivo2_comparacion_14dbm.csv', index=False)
df_potencia.to_csv(OUTPUT_DIR / 'objetivo2_impacto_potencia.csv', index=False)

print(f"✅ Archivos CSV guardados en: {OUTPUT_DIR}/")
print()

# Resumen textual
with open(OUTPUT_DIR / 'objetivo2_resumen.txt', 'w', encoding='utf-8') as f:
    f.write("=" * 70 + "\n")
    f.write("RESUMEN OBJETIVO 2: VALIDACIÓN DE ALGORITMOS P2P\n")
    f.write("=" * 70 + "\n\n")
    
    f.write("HALLAZGOS CLAVE:\n\n")
    
    f.write("1. IMPACTO DEL SPREADING FACTOR:\n")
    f.write("   - SF7: PDR 99.3-99.43%, Latencia 53ms (óptimo)\n")
    f.write("   - SF9: PDR 95-99.43%, Latencia 53-187ms (degradación moderada en tradicional)\n")
    f.write("   - SF12: PDR 70.64-99.20%, Latencia 53-1320ms (severa degradación en tradicional)\n\n")
    
    f.write("2. COMPARACIÓN ARQUITECTURAS (14 dBm):\n")
    f.write("   - Móvil supera a Tradicional en todos los SF\n")
    f.write("   - Ventaja más notable en SF12: 99.20% vs 70.64% PDR\n")
    f.write("   - Cobertura: Móvil 99.39% vs Tradicional 68%\n\n")
    
    f.write("3. IMPACTO DE POTENCIA (Móvil):\n")
    f.write("   - 14 dBm: PDR 99.20-99.43%, P2P 74.56%\n")
    f.write("   - 8 dBm: PDR 97.5-98.5%, P2P 72%\n")
    f.write("   - Reducción potencia -6dBm: pérdida ~1-2% PDR\n\n")
    
    f.write("4. PROTOCOLO P2P:\n")
    f.write("   - Eficiencia: 72-74.56%\n")
    f.write("   - Independiente del SF (latencia constante 53ms)\n")
    f.write("   - Ligera mejora con mayor potencia\n\n")
    
    f.write("CONCLUSIÓN:\n")
    f.write("La arquitectura móvil con P2P demuestra superioridad significativa,\n")
    f.write("especialmente en SF altos donde la tradicional se degrada severamente.\n")
    f.write("El protocolo P2P mantiene alta eficiencia independiente del SF.\n")

print(f"✅ Resumen textual: {OUTPUT_DIR / 'objetivo2_resumen.txt'}")
print()
print("=" * 70)
print("✅ ANÁLISIS OBJETIVO 2 COMPLETADO")
print(f"📁 Resultados en: {OUTPUT_DIR}/")
print("=" * 70)
