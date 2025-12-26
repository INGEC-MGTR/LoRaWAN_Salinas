#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Animación Comparativa de Arquitecturas LoRaWAN
Tradicional (Fijos) vs Propuesta (Móviles + P2P)
"""

import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from matplotlib.patches import Circle
import numpy as np

# Configuración
plt.rcParams['font.family'] = 'DejaVu Sans'
plt.rcParams['font.size'] = 10

print("=" * 80)
print("GENERANDO ANIMACIONES COMPARATIVAS DE ARQUITECTURAS")
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
    exit(1)

# Obtener tiempos comunes
times_fixed = sorted(df_fixed['time'].unique())
times_mobile = sorted(df_mobile['time'].unique())

# Usar los primeros N tiempos comunes (para animación más rápida)
max_frames = 60  # 60 frames = ~12 segundos a 5 fps
times = sorted(set(times_fixed) & set(times_mobile))[:max_frames]

print(f"\n✓ Tiempos para animación: {len(times)} frames")
print(f"  Rango: {times[0]:.0f}s - {times[-1]:.0f}s")

# ========== ANIMACIÓN LADO A LADO ==========
print("\nCreando animación comparativa lado a lado...")

fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(18, 8))

def init():
    for ax in [ax1, ax2]:
        ax.clear()
        ax.set_facecolor('#E3F2FD')
        ax.fill_between([0, 25000], -1000, 0, color='#D7CCC8', alpha=0.7)
        ax.set_xlim(0, 25000)
        ax.set_ylim(0, 15000)
        ax.grid(True, alpha=0.3, linestyle='--')
    return []

def animate(frame_idx):
    for ax in [ax1, ax2]:
        ax.clear()
        ax.set_facecolor('#E3F2FD')
        ax.fill_between([0, 25000], -1000, 0, color='#D7CCC8', alpha=0.7)
    
    current_time = times[frame_idx]
    
    # ===== PANEL IZQUIERDO: TRADICIONAL =====
    current_fixed = df_fixed[df_fixed['time'] == current_time]
    
    boats_f = current_fixed[current_fixed['type'] == 'boat']
    gateways_f = current_fixed[current_fixed['type'] == 'gateway']
    server_f = current_fixed[current_fixed['type'] == 'server']
    
    # Cobertura fija
    for _, gw in gateways_f.iterrows():
        coverage = Circle((gw['x'], gw['y']), 15000, 
                         color='#E74C3C', fill=True, alpha=0.08, 
                         linewidth=2, edgecolor='#E74C3C', linestyle='--')
        ax1.add_patch(coverage)
    
    # Enlaces
    connected_f = 0
    for _, boat in boats_f.iterrows():
        min_dist = float('inf')
        closest_gw = None
        for _, gw in gateways_f.iterrows():
            dist = np.sqrt((boat['x'] - gw['x'])**2 + (boat['y'] - gw['y'])**2)
            if dist < min_dist:
                min_dist = dist
                closest_gw = gw
        if closest_gw is not None and min_dist <= 15000:
            ax1.plot([boat['x'], closest_gw['x']], 
                   [boat['y'], closest_gw['y']], 
                   color='#95A5A6', linewidth=0.8, alpha=0.4)
            connected_f += 1
    
    # Backhaul
    if len(server_f) > 0:
        srv = server_f.iloc[0]
        for _, gw in gateways_f.iterrows():
            ax1.plot([gw['x'], srv['x']], [gw['y'], srv['y']], 
                   color='#F39C12', linewidth=1.5, alpha=0.6, linestyle=':')
    
    # Nodos
    ax1.scatter(boats_f['x'], boats_f['y'], c='#3498DB', s=100, marker='o', 
               label=f'Embarcaciones ({len(boats_f)})', alpha=0.8, 
               edgecolors='#2874A6', linewidths=1.5, zorder=5)
    ax1.scatter(gateways_f['x'], gateways_f['y'], c='#E74C3C', s=400, marker='s', 
               label=f'GW Fijos ({len(gateways_f)})', alpha=0.9, 
               edgecolors='#C0392B', linewidths=2.5, zorder=6)
    if len(server_f) > 0:
        ax1.scatter(server_f['x'], server_f['y'], c='#F39C12', s=500, marker='D', 
                   label='Network Server', alpha=0.9, 
                   edgecolors='#D68910', linewidths=2.5, zorder=7)
    
    ax1.set_xlim(0, 25000)
    ax1.set_ylim(0, 15000)
    ax1.set_xlabel('Distancia Este (m)', fontweight='bold', fontsize=11)
    ax1.set_ylabel('Distancia Norte (m)', fontweight='bold', fontsize=11)
    ax1.set_title(f'⚓ ARQUITECTURA TRADICIONAL\nTiempo: {current_time:.0f}s', 
                 fontweight='bold', fontsize=12, color='#E74C3C')
    ax1.grid(True, alpha=0.3, linestyle='--')
    ax1.legend(loc='upper right', fontsize=9, framealpha=0.9)
    
    # Stats tradicional
    coverage_pct_f = (connected_f / len(boats_f) * 100) if len(boats_f) > 0 else 0
    stats_f = f'Cobertura: {coverage_pct_f:.0f}%\nConectadas: {connected_f}/{len(boats_f)}'
    ax1.text(0.02, 0.98, stats_f, transform=ax1.transAxes,
            fontsize=10, verticalalignment='top', fontweight='bold',
            bbox=dict(boxstyle='round', facecolor='white', alpha=0.85, 
                     edgecolor='#E74C3C', linewidth=2),
            color='#E74C3C')
    
    # ===== PANEL DERECHO: MÓVIL + P2P =====
    current_mobile = df_mobile[df_mobile['time'] == current_time]
    
    boats_m = current_mobile[current_mobile['type'] == 'boat']
    gateways_m = current_mobile[current_mobile['type'] == 'gateway']
    server_m = current_mobile[current_mobile['type'] == 'server']
    
    # Cobertura móvil
    for _, gw in gateways_m.iterrows():
        coverage = Circle((gw['x'], gw['y']), 15000, 
                         color='#27AE60', fill=True, alpha=0.08, 
                         linewidth=2, edgecolor='#27AE60', linestyle='--')
        ax2.add_patch(coverage)
    
    # Enlaces
    connected_m = 0
    for _, boat in boats_m.iterrows():
        min_dist = float('inf')
        closest_gw = None
        for _, gw in gateways_m.iterrows():
            dist = np.sqrt((boat['x'] - gw['x'])**2 + (boat['y'] - gw['y'])**2)
            if dist < min_dist:
                min_dist = dist
                closest_gw = gw
        if closest_gw is not None and min_dist <= 15000:
            ax2.plot([boat['x'], closest_gw['x']], 
                   [boat['y'], closest_gw['y']], 
                   color='#52BE80', linewidth=0.8, alpha=0.5)
            connected_m += 1
    
    # Backhaul
    if len(server_m) > 0:
        srv = server_m.iloc[0]
        for _, gw in gateways_m.iterrows():
            ax2.plot([gw['x'], srv['x']], [gw['y'], srv['y']], 
                   color='#F39C12', linewidth=1.5, alpha=0.6, linestyle=':')
    
    # Nodos
    ax2.scatter(boats_m['x'], boats_m['y'], c='#3498DB', s=100, marker='o', 
               label=f'Embarcaciones ({len(boats_m)})', alpha=0.8, 
               edgecolors='#2874A6', linewidths=1.5, zorder=5)
    ax2.scatter(gateways_m['x'], gateways_m['y'], c='#27AE60', s=400, marker='^', 
               label=f'GW Móviles ({len(gateways_m)})', alpha=0.9, 
               edgecolors='#1E8449', linewidths=2.5, zorder=6)
    if len(server_m) > 0:
        ax2.scatter(server_m['x'], server_m['y'], c='#F39C12', s=500, marker='D', 
                   label='Network Server', alpha=0.9, 
                   edgecolors='#D68910', linewidths=2.5, zorder=7)
    
    ax2.set_xlim(0, 25000)
    ax2.set_ylim(0, 15000)
    ax2.set_xlabel('Distancia Este (m)', fontweight='bold', fontsize=11)
    ax2.set_ylabel('Distancia Norte (m)', fontweight='bold', fontsize=11)
    ax2.set_title(f'🚢 ARQUITECTURA PROPUESTA\nTiempo: {current_time:.0f}s', 
                 fontweight='bold', fontsize=12, color='#27AE60')
    ax2.grid(True, alpha=0.3, linestyle='--')
    ax2.legend(loc='upper right', fontsize=9, framealpha=0.9)
    
    # Stats móvil
    coverage_pct_m = (connected_m / len(boats_m) * 100) if len(boats_m) > 0 else 0
    stats_m = f'Cobertura: {coverage_pct_m:.0f}%\nConectadas: {connected_m}/{len(boats_m)}'
    ax2.text(0.02, 0.98, stats_m, transform=ax2.transAxes,
            fontsize=10, verticalalignment='top', fontweight='bold',
            bbox=dict(boxstyle='round', facecolor='white', alpha=0.85, 
                     edgecolor='#27AE60', linewidth=2),
            color='#27AE60')
    
    return []

# Crear animación
print("Generando animación (esto puede tardar varios minutos)...")
anim = animation.FuncAnimation(fig, animate, init_func=init,
                              frames=len(times), interval=200, 
                              blit=True, repeat=True)

# Guardar como GIF
output_gif = 'Animacion_Comparacion_Arquitecturas.gif'
print(f"Guardando animación como GIF ({len(times)} frames a 5 fps)...")
anim.save(output_gif, writer='pillow', fps=5, dpi=100)
print(f"✓ Animación guardada: {output_gif}")

plt.close()

# ========== CAPTURAS CLAVE ==========
print("\nGenerando capturas de momentos clave...")

key_frames = [0, len(times)//4, len(times)//2, 3*len(times)//4, -1]
frame_names = ['inicio', 'cuarto', 'mitad', 'tres_cuartos', 'final']

for idx, (frame_idx, name) in enumerate(zip(key_frames, frame_names)):
    fig_static, (ax1, ax2) = plt.subplots(1, 2, figsize=(18, 8))
    
    current_time = times[frame_idx]
    
    # Panel izquierdo - Tradicional
    ax1.set_facecolor('#E3F2FD')
    ax1.fill_between([0, 25000], -1000, 0, color='#D7CCC8', alpha=0.7)
    
    current_fixed = df_fixed[df_fixed['time'] == current_time]
    boats_f = current_fixed[current_fixed['type'] == 'boat']
    gateways_f = current_fixed[current_fixed['type'] == 'gateway']
    server_f = current_fixed[current_fixed['type'] == 'server']
    
    for _, gw in gateways_f.iterrows():
        coverage = Circle((gw['x'], gw['y']), 15000, 
                         color='#E74C3C', fill=True, alpha=0.08, 
                         linewidth=2, edgecolor='#E74C3C', linestyle='--')
        ax1.add_patch(coverage)
    
    connected_f = 0
    for _, boat in boats_f.iterrows():
        min_dist = float('inf')
        closest_gw = None
        for _, gw in gateways_f.iterrows():
            dist = np.sqrt((boat['x'] - gw['x'])**2 + (boat['y'] - gw['y'])**2)
            if dist < min_dist:
                min_dist = dist
                closest_gw = gw
        if closest_gw is not None and min_dist <= 15000:
            ax1.plot([boat['x'], closest_gw['x']], 
                   [boat['y'], closest_gw['y']], 
                   color='#95A5A6', linewidth=0.8, alpha=0.4)
            connected_f += 1
    
    if len(server_f) > 0:
        srv = server_f.iloc[0]
        for _, gw in gateways_f.iterrows():
            ax1.plot([gw['x'], srv['x']], [gw['y'], srv['y']], 
                   color='#F39C12', linewidth=1.5, alpha=0.6, linestyle=':')
    
    ax1.scatter(boats_f['x'], boats_f['y'], c='#3498DB', s=100, marker='o', 
               label=f'Embarcaciones ({len(boats_f)})', alpha=0.8, 
               edgecolors='#2874A6', linewidths=1.5, zorder=5)
    ax1.scatter(gateways_f['x'], gateways_f['y'], c='#E74C3C', s=400, marker='s', 
               label=f'GW Fijos ({len(gateways_f)})', alpha=0.9, 
               edgecolors='#C0392B', linewidths=2.5, zorder=6)
    if len(server_f) > 0:
        ax1.scatter(server_f['x'], server_f['y'], c='#F39C12', s=500, marker='D', 
                   label='Network Server', alpha=0.9, zorder=7)
    
    ax1.set_xlim(0, 25000)
    ax1.set_ylim(0, 15000)
    ax1.set_xlabel('Distancia Este (m)', fontweight='bold', fontsize=11)
    ax1.set_ylabel('Distancia Norte (m)', fontweight='bold', fontsize=11)
    ax1.set_title(f'⚓ ARQUITECTURA TRADICIONAL\nTiempo: {current_time:.0f}s', 
                 fontweight='bold', fontsize=12, color='#E74C3C')
    ax1.grid(True, alpha=0.3, linestyle='--')
    ax1.legend(loc='upper right', fontsize=9, framealpha=0.9)
    
    # Panel derecho - Móvil
    ax2.set_facecolor('#E8F5E9')
    ax2.fill_between([0, 25000], -1000, 0, color='#D7CCC8', alpha=0.7)
    
    current_mobile = df_mobile[df_mobile['time'] == current_time]
    boats_m = current_mobile[current_mobile['type'] == 'boat']
    gateways_m = current_mobile[current_mobile['type'] == 'gateway']
    server_m = current_mobile[current_mobile['type'] == 'server']
    
    for _, gw in gateways_m.iterrows():
        coverage = Circle((gw['x'], gw['y']), 15000, 
                         color='#27AE60', fill=True, alpha=0.08, 
                         linewidth=2, edgecolor='#27AE60', linestyle='--')
        ax2.add_patch(coverage)
    
    connected_m = 0
    for _, boat in boats_m.iterrows():
        min_dist = float('inf')
        closest_gw = None
        for _, gw in gateways_m.iterrows():
            dist = np.sqrt((boat['x'] - gw['x'])**2 + (boat['y'] - gw['y'])**2)
            if dist < min_dist:
                min_dist = dist
                closest_gw = gw
        if closest_gw is not None and min_dist <= 15000:
            ax2.plot([boat['x'], closest_gw['x']], 
                   [boat['y'], closest_gw['y']], 
                   color='#52BE80', linewidth=0.8, alpha=0.5)
            connected_m += 1
    
    if len(server_m) > 0:
        srv = server_m.iloc[0]
        for _, gw in gateways_m.iterrows():
            ax2.plot([gw['x'], srv['x']], [gw['y'], srv['y']], 
                   color='#F39C12', linewidth=1.5, alpha=0.6, linestyle=':')
    
    ax2.scatter(boats_m['x'], boats_m['y'], c='#3498DB', s=100, marker='o', 
               label=f'Embarcaciones ({len(boats_m)})', alpha=0.8, 
               edgecolors='#2874A6', linewidths=1.5, zorder=5)
    ax2.scatter(gateways_m['x'], gateways_m['y'], c='#27AE60', s=400, marker='^', 
               label=f'GW Móviles ({len(gateways_m)})', alpha=0.9, 
               edgecolors='#1E8449', linewidths=2.5, zorder=6)
    if len(server_m) > 0:
        ax2.scatter(server_m['x'], server_m['y'], c='#F39C12', s=500, marker='D', 
                   label='Network Server', alpha=0.9, zorder=7)
    
    ax2.set_xlim(0, 25000)
    ax2.set_ylim(0, 15000)
    ax2.set_xlabel('Distancia Este (m)', fontweight='bold', fontsize=11)
    ax2.set_ylabel('Distancia Norte (m)', fontweight='bold', fontsize=11)
    ax2.set_title(f'🚢 ARQUITECTURA PROPUESTA\nTiempo: {current_time:.0f}s', 
                 fontweight='bold', fontsize=12, color='#27AE60')
    ax2.grid(True, alpha=0.3, linestyle='--')
    ax2.legend(loc='upper right', fontsize=9, framealpha=0.9)
    
    # Título general
    fig_static.suptitle(f'Comparación de Arquitecturas LoRaWAN - cantón Salinas\n',
                       fontsize=14, fontweight='bold', y=0.98)
    
    plt.tight_layout(rect=[0, 0.02, 1, 0.96])
    
    output_img = f'Captura_{idx+1}_{name}.png'
    plt.savefig(output_img, dpi=300, bbox_inches='tight', facecolor='white')
    plt.close()
    print(f"✓ Captura {idx+1} guardada: {output_img}")

print("\n" + "=" * 80)
print("ARCHIVOS GENERADOS:")
print("=" * 80)
print(f"  1. {output_gif} (animación completa)")
print("  2. Captura_1_inicio.png")
print("  3. Captura_2_cuarto.png")
print("  4. Captura_3_mitad.png")
print("  5. Captura_4_tres_cuartos.png")
print("  6. Captura_5_final.png")
print("=" * 80)
print("\n✓ Proceso completado exitosamente!")
