#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Universidad Estatal Península de Santa Elena (UPSE)
Comparación Visual Geográfica de Arquitecturas LoRaWAN
Arquitectura Tradicional (Fijos) vs Arquitectura Propuesta (Móviles + P2P)
"""

import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.patches import Circle
import numpy as np

# Configuración
plt.rcParams['font.family'] = 'DejaVu Sans'
plt.rcParams['font.size'] = 10

print("=" * 80)
print("COMPARACIÓN VISUAL GEOGRÁFICA DE ARQUITECTURAS")
print("=" * 80)

# Leer datos
print("\nCargando datos de posiciones...")
try:
    df_fixed = pd.read_csv('positions_fixed.csv')
    df_mobile = pd.read_csv('positions_mobile.csv')
    print(f"✓ Datos tradicionales: {len(df_fixed)} registros")
    print(f"✓ Datos móviles: {len(df_mobile)} registros")
except FileNotFoundError as e:
    print(f"❌ ERROR: No se encontró {e.filename}")
    print("Asegúrate de ejecutar este script en ~/ns-3-dev/")
    exit(1)

# Ver tiempos disponibles
print(f"\n📊 Tiempos disponibles:")
print(f"  - Tradicional: {sorted(df_fixed['time'].unique())[:10]}...")
print(f"  - Móvil: {sorted(df_mobile['time'].unique())[:10]}...")

# Buscar tiempo cercano a 300s (o el más cercano disponible)
target_time = 300.0
available_times_fixed = df_fixed['time'].unique()
available_times_mobile = df_mobile['time'].unique()

# Encontrar tiempo más cercano
closest_time_fixed = min(available_times_fixed, key=lambda x: abs(x - target_time))
closest_time_mobile = min(available_times_mobile, key=lambda x: abs(x - target_time))

print(f"\n✓ Tiempo objetivo: {target_time}s")
print(f"✓ Tiempo real tradicional: {closest_time_fixed}s")
print(f"✓ Tiempo real móvil: {closest_time_mobile}s")

# Usar el tiempo más cercano para ambos
time_to_use = max(closest_time_fixed, closest_time_mobile)
print(f"✓ Usando tiempo: {time_to_use}s")

# Filtrar datos
fixed_data = df_fixed[df_fixed['time'] == time_to_use]
mobile_data = df_mobile[df_mobile['time'] == time_to_use]

# Si aún está vacío, usar el primer tiempo disponible
if len(fixed_data) == 0:
    time_to_use = sorted(df_fixed['time'].unique())[10] if len(df_fixed['time'].unique()) > 10 else df_fixed['time'].unique()[0]
    fixed_data = df_fixed[df_fixed['time'] == time_to_use]
    print(f"⚠️  Ajustando a tiempo tradicional: {time_to_use}s")

if len(mobile_data) == 0:
    time_to_use = sorted(df_mobile['time'].unique())[10] if len(df_mobile['time'].unique()) > 10 else df_mobile['time'].unique()[0]
    mobile_data = df_mobile[df_mobile['time'] == time_to_use]
    print(f"⚠️  Ajustando a tiempo móvil: {time_to_use}s")

print(f"\n✓ Nodos encontrados:")
print(f"  - Tradicionales: {len(fixed_data)}")
print(f"  - Móviles: {len(mobile_data)}")

if len(fixed_data) == 0 or len(mobile_data) == 0:
    print("\n❌ ERROR: No hay datos suficientes en los CSV")
    print("Verifica que los archivos positions_fixed.csv y positions_mobile.csv tengan datos")
    exit(1)

# Crear figura con 2 subplots lado a lado
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(18, 9))

# ========== PANEL IZQUIERDO: ARQUITECTURA TRADICIONAL ==========
print("\nGenerando visualización de arquitectura tradicional...")
ax1.set_facecolor('#E3F2FD')  # Azul claro para el mar
ax1.fill_between([0, 25000], -1000, 0, color='#D7CCC8', alpha=0.8)

# Separar nodos por tipo
boats_f = fixed_data[fixed_data['type'] == 'boat']
gateways_f = fixed_data[fixed_data['type'] == 'gateway']
server_f = fixed_data[fixed_data['type'] == 'server']

print(f"  - Embarcaciones: {len(boats_f)}")
print(f"  - Gateways: {len(gateways_f)}")
print(f"  - Servidor: {len(server_f)}")

# Cobertura estática de gateways fijos
for idx, gw in gateways_f.iterrows():
    coverage = Circle((gw['x'], gw['y']), 15000,  # 15 km alcance LoRa
                     color='#E74C3C', fill=True, 
                     alpha=0.10, linewidth=2, edgecolor='#E74C3C', linestyle='--')
    ax1.add_patch(coverage)

# Enlaces entre embarcaciones y gateways
connected_boats = 0
for _, boat in boats_f.iterrows():
    min_dist = float('inf')
    closest_gw = None
    for _, gw in gateways_f.iterrows():
        dist = np.sqrt((boat['x'] - gw['x'])**2 + (boat['y'] - gw['y'])**2)
        if dist < min_dist:
            min_dist = dist
            closest_gw = gw
    if closest_gw is not None and min_dist <= 15000:  # Dentro de rango LoRa
        ax1.plot([boat['x'], closest_gw['x']], 
               [boat['y'], closest_gw['y']], 
               color='#95A5A6', linewidth=0.8, alpha=0.4)
        connected_boats += 1

# Enlaces gateway-servidor
if len(server_f) > 0:
    srv = server_f.iloc[0]
    for idx, gw in gateways_f.iterrows():
        ax1.plot([gw['x'], srv['x']], [gw['y'], srv['y']], 
               color='#F39C12', linewidth=2, alpha=0.7, linestyle=':')

# Dibujar nodos
ax1.scatter(boats_f['x'], boats_f['y'], c='#3498DB', s=120, marker='o', 
           label=f'Embarcaciones ({len(boats_f)})', alpha=0.8, 
           edgecolors='#2874A6', linewidths=2, zorder=5)
ax1.scatter(gateways_f['x'], gateways_f['y'], c='#E74C3C', s=500, marker='s', 
           label=f'GW Fijos Costeros ({len(gateways_f)})', alpha=0.9, 
           edgecolors='#C0392B', linewidths=3, zorder=6)
if len(server_f) > 0:
    ax1.scatter(server_f['x'], server_f['y'], c='#F39C12', s=600, marker='D', 
               label='Network Server', alpha=0.95, 
               edgecolors='#D68910', linewidths=3, zorder=7)

ax1.set_xlim(-500, 25500)
ax1.set_ylim(-1000, 15500)
ax1.set_xlabel('Distancia Este (metros)', fontweight='bold', fontsize=12)
ax1.set_ylabel('Distancia Norte (metros)', fontweight='bold', fontsize=12)
ax1.set_title('⚓ ARQUITECTURA TRADICIONAL\nGateways Fijos Costeros + Topología Estrella', 
             fontweight='bold', fontsize=14, pad=15, color='#E74C3C')
ax1.grid(True, alpha=0.3, linestyle='--', linewidth=0.8)
ax1.legend(loc='upper right', fontsize=10, framealpha=0.95, edgecolor='#E74C3C', fancybox=True)

# Estadísticas panel izquierdo
coverage_pct = (connected_boats / len(boats_f)) * 100 if len(boats_f) > 0 else 0
stats_text = f'Cobertura: {coverage_pct:.0f}%\n' \
             f'Conectadas: {connected_boats}/{len(boats_f)}\n' \
             f'Topología: Estrella\n' \
             f'P2P: No'
ax1.text(0.02, 0.98, stats_text, transform=ax1.transAxes,
        fontsize=11, verticalalignment='top', fontweight='bold',
        bbox=dict(boxstyle='round', facecolor='white', alpha=0.9, 
                 edgecolor='#E74C3C', linewidth=3),
        color='#E74C3C')

# ========== PANEL DERECHO: ARQUITECTURA PROPUESTA ==========
print("\nGenerando visualización de arquitectura propuesta...")
ax2.set_facecolor('#E8F5E9')  # Verde claro para el mar
ax2.fill_between([0, 25000], -1000, 0, color='#D7CCC8', alpha=0.8)

# Separar nodos por tipo
boats_m = mobile_data[mobile_data['type'] == 'boat']
gateways_m = mobile_data[mobile_data['type'] == 'gateway']
server_m = mobile_data[mobile_data['type'] == 'server']

print(f"  - Embarcaciones: {len(boats_m)}")
print(f"  - Gateways: {len(gateways_m)}")
print(f"  - Servidor: {len(server_m)}")

# Cobertura dinámica de gateways móviles
for idx, gw in gateways_m.iterrows():
    coverage = Circle((gw['x'], gw['y']), 15000,  # 15 km alcance LoRa
                     color='#27AE60', fill=True, 
                     alpha=0.10, linewidth=2, edgecolor='#27AE60', linestyle='--')
    ax2.add_patch(coverage)

# Enlaces entre embarcaciones y gateways
connected_boats_m = 0
p2p_links = 0

for _, boat in boats_m.iterrows():
    min_dist = float('inf')
    closest_gw = None
    for _, gw in gateways_m.iterrows():
        dist = np.sqrt((boat['x'] - gw['x'])**2 + (boat['y'] - gw['y'])**2)
        if dist < min_dist:
            min_dist = dist
            closest_gw = gw
    
    # Enlace directo si está en rango
    if closest_gw is not None and min_dist <= 15000:
        ax2.plot([boat['x'], closest_gw['x']], 
               [boat['y'], closest_gw['y']], 
               color='#52BE80', linewidth=0.8, alpha=0.5)
        connected_boats_m += 1

# Enlaces gateway-servidor
if len(server_m) > 0:
    srv = server_m.iloc[0]
    for idx, gw in gateways_m.iterrows():
        ax2.plot([gw['x'], srv['x']], [gw['y'], srv['y']], 
               color='#F39C12', linewidth=2, alpha=0.7, linestyle=':')

# Dibujar nodos
ax2.scatter(boats_m['x'], boats_m['y'], c='#3498DB', s=120, marker='o', 
           label=f'Embarcaciones ({len(boats_m)})', alpha=0.8, 
           edgecolors='#2874A6', linewidths=2, zorder=5)
ax2.scatter(gateways_m['x'], gateways_m['y'], c='#27AE60', s=500, marker='^', 
           label=f'GW Móviles ({len(gateways_m)})', alpha=0.9, 
           edgecolors='#1E8449', linewidths=3, zorder=6)
if len(server_m) > 0:
    ax2.scatter(server_m['x'], server_m['y'], c='#F39C12', s=600, marker='D', 
               label='Network Server', alpha=0.95, 
               edgecolors='#D68910', linewidths=3, zorder=7)

ax2.set_xlim(-500, 25500)
ax2.set_ylim(-1000, 15500)
ax2.set_xlabel('Distancia Este (metros)', fontweight='bold', fontsize=12)
ax2.set_ylabel('Distancia Norte (metros)', fontweight='bold', fontsize=12)
ax2.set_title('🚢 ARQUITECTURA PROPUESTA\nGateways Móviles + Topología Híbrida (Estrella + P2P)', 
             fontweight='bold', fontsize=14, pad=15, color='#27AE60')
ax2.grid(True, alpha=0.3, linestyle='--', linewidth=0.8)
ax2.legend(loc='upper right', fontsize=10, framealpha=0.95, edgecolor='#27AE60', fancybox=True)

# Estadísticas panel derecho
coverage_pct_m = (connected_boats_m / len(boats_m)) * 100 if len(boats_m) > 0 else 0
stats_text_m = f'Cobertura: {coverage_pct_m:.0f}%\n' \
               f'Conectadas: {connected_boats_m}/{len(boats_m)}\n' \
               f'Topología: Híbrida\n' \
               f'P2P: Sí'
ax2.text(0.02, 0.98, stats_text_m, transform=ax2.transAxes,
        fontsize=11, verticalalignment='top', fontweight='bold',
        bbox=dict(boxstyle='round', facecolor='white', alpha=0.9, 
                 edgecolor='#27AE60', linewidth=3),
        color='#27AE60')

# Título general
fig.suptitle('Comparación Geográfica de Arquitecturas LoRaWAN\n' +
            'Comunicaciones de Emergencia Marítima - cantón Salinas, Ecuador',
            fontsize=16, fontweight='bold', y=0.98, color='#2C3E50')

# Nota al pie
metadata_text = f'Embarcaciones: 50 | Área: 25×15 km (375 km²) | ' \
                f'Alcance LoRa: 15 km'
fig.text(0.5, 0.01, metadata_text,
         ha='center', fontsize=10, style='italic', color='#7F8C8D',
         bbox=dict(boxstyle='round', facecolor='white', alpha=0.8, edgecolor='#BDC3C7'))

plt.tight_layout(rect=[0, 0.03, 1, 0.96])

# Guardar
output_file = 'Comparacion_Geografica_Arquitecturas.png'
plt.savefig(output_file, dpi=300, bbox_inches='tight', facecolor='white')
print(f"\n✓ Comparación geográfica guardada: {output_file}")

# Resumen
print("\n" + "=" * 80)
print("RESUMEN DE VISUALIZACIÓN")
print("=" * 80)
print(f"\n📍 ARQUITECTURA TRADICIONAL:")
print(f"   • Gateways fijos: {len(gateways_f)}")
print(f"   • Embarcaciones: {len(boats_f)}")
print(f"   • Conectadas: {connected_boats}/{len(boats_f)} ({coverage_pct:.1f}%)")

print(f"\n📍 ARQUITECTURA PROPUESTA:")
print(f"   • Gateways móviles: {len(gateways_m)}")
print(f"   • Embarcaciones: {len(boats_m)}")
print(f"   • Conectadas: {connected_boats_m}/{len(boats_m)} ({coverage_pct_m:.1f}%)")

print("\n" + "=" * 80)
print(f"✓ ARCHIVO GENERADO: {output_file}")
print("=" * 80)

plt.show()
