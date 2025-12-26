#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Animación de Arquitectura LoRaWAN Propuesta
Gateways Móviles + Topología Híbrida (Estrella + P2P)
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
print("GENERANDO ANIMACIÓN - ARQUITECTURA PROPUESTA (MÓVIL + P2P)")
print("=" * 80)

# Leer datos
print("\nCargando datos de posiciones...")
try:
    df_mobile = pd.read_csv('positions_mobile.csv')
    print(f"✓ Datos cargados: {len(df_mobile)} registros")
except FileNotFoundError:
    print("❌ ERROR: No se encontró positions_mobile.csv")
    print("Asegúrate de ejecutar este script en ~/ns-3-dev/")
    exit(1)

# Obtener tiempos únicos
times = sorted(df_mobile['time'].unique())
print(f"✓ Total de frames disponibles: {len(times)}")

# Usar solo los primeros 60 frames (para animación más rápida)
max_frames = min(60, len(times))
times = times[:max_frames]
print(f"✓ Usando {max_frames} frames para animación")
print(f"  Rango de tiempo: {times[0]:.0f}s - {times[-1]:.0f}s")

# Configurar figura
fig, ax = plt.subplots(figsize=(14, 9))

def init():
    ax.clear()
    ax.set_facecolor('#E8F5E9')
    ax.fill_between([0, 25000], -1000, 0, color='#D7CCC8', alpha=0.7)
    ax.set_xlim(0, 25000)
    ax.set_ylim(0, 15000)
    ax.set_xlabel('Distancia Este (m)', fontweight='bold', fontsize=12)
    ax.set_ylabel('Distancia Norte (m)', fontweight='bold', fontsize=12)
    ax.set_title('🚢 Red LoRaWAN Marítima - Arquitectura Propuesta\nGateways Móviles + P2P', 
                fontweight='bold', fontsize=14, pad=15, color='#27AE60')
    ax.grid(True, alpha=0.3, linestyle='--')
    return []

def animate(frame_idx):
    ax.clear()
    
    # Fondo
    ax.set_facecolor('#E8F5E9')
    ax.fill_between([0, 25000], -1000, 0, color='#D7CCC8', alpha=0.7, label='Costa')
    
    current_time = times[frame_idx]
    
    # Filtrar datos del tiempo actual
    current_data = df_mobile[df_mobile['time'] == current_time]
    
    # Separar por tipo
    boats = current_data[current_data['type'] == 'boat']
    gateways = current_data[current_data['type'] == 'gateway']
    server = current_data[current_data['type'] == 'server']
    
    # Dibujar círculos de cobertura DINÁMICA de gateways móviles (15 km de radio)
    for _, gw in gateways.iterrows():
        coverage = Circle((gw['x'], gw['y']), 15000, 
                         color='#27AE60', fill=True, alpha=0.10,
                         linewidth=2, edgecolor='#27AE60', linestyle='--')
        ax.add_patch(coverage)
    
    # Dibujar trayectorias de gateways móviles (últimos 5 puntos)
    if frame_idx >= 5:
        for gw_id in gateways.index:
            past_times = times[max(0, frame_idx-5):frame_idx+1]
            past_data = df_mobile[
                (df_mobile['time'].isin(past_times)) & 
                (df_mobile['type'] == 'gateway')
            ]
            if len(past_data) > 1:
                ax.plot(past_data['x'], past_data['y'], 
                       color='#27AE60', linewidth=1.5, alpha=0.3, 
                       linestyle=':', zorder=3)
    
    # Dibujar enlaces de comunicación directa
    connected_boats = 0
    p2p_links = 0
    
    for _, boat in boats.iterrows():
        # Encontrar gateway más cercano
        min_dist = float('inf')
        closest_gw = None
        
        for _, gw in gateways.iterrows():
            dist = np.sqrt((boat['x'] - gw['x'])**2 + (boat['y'] - gw['y'])**2)
            if dist < min_dist:
                min_dist = dist
                closest_gw = gw
        
        # Enlace directo si está en rango
        if closest_gw is not None and min_dist <= 15000:  # Dentro del rango LoRa
            ax.plot([boat['x'], closest_gw['x']], 
                   [boat['y'], closest_gw['y']], 
                   color='#52BE80', linewidth=0.8, alpha=0.5)
            connected_boats += 1
        # Simular enlace P2P si está fuera de rango directo
        elif closest_gw is not None and 15000 < min_dist <= 20000:
            # Buscar embarcación intermedia para relay P2P
            for _, relay_boat in boats.iterrows():
                dist_to_relay = np.sqrt((boat['x'] - relay_boat['x'])**2 + (boat['y'] - relay_boat['y'])**2)
                dist_relay_to_gw = np.sqrt((relay_boat['x'] - closest_gw['x'])**2 + (relay_boat['y'] - closest_gw['y'])**2)
                
                # Si la embarcación relay está en rango de ambos
                if dist_to_relay < 5000 and dist_relay_to_gw <= 15000:
                    # Enlace P2P embarcación -> relay (línea punteada morada)
                    ax.plot([boat['x'], relay_boat['x']], 
                           [boat['y'], relay_boat['y']], 
                           color='#9B59B6', linewidth=1.2, alpha=0.6, 
                           linestyle='--', zorder=4)
                    # Enlace relay -> gateway
                    ax.plot([relay_boat['x'], closest_gw['x']], 
                           [relay_boat['y'], closest_gw['y']], 
                           color='#52BE80', linewidth=0.8, alpha=0.5)
                    p2p_links += 1
                    connected_boats += 1
                    break
    
    # Dibujar enlaces de gateways a servidor (backhaul)
    if len(server) > 0:
        srv = server.iloc[0]
        for _, gw in gateways.iterrows():
            ax.plot([gw['x'], srv['x']], 
                   [gw['y'], srv['y']], 
                   color='#F39C12', linewidth=1.5, alpha=0.6, linestyle=':')
    
    # Dibujar nodos
    ax.scatter(boats['x'], boats['y'], 
              c='#3498DB', s=100, marker='o', 
              label=f'Embarcaciones ({len(boats)})', 
              alpha=0.8, edgecolors='#2874A6', linewidths=1.5, zorder=5)
    
    ax.scatter(gateways['x'], gateways['y'], 
              c='#27AE60', s=400, marker='^', 
              label=f'Gateways Móviles ({len(gateways)})', 
              alpha=0.9, edgecolors='#1E8449', linewidths=2.5, zorder=6)
    
    if len(server) > 0:
        ax.scatter(server['x'], server['y'], 
                  c='#F39C12', s=500, marker='D', 
                  label='Network Server', 
                  alpha=0.95, edgecolors='#D68910', linewidths=2.5, zorder=7)
    
    # Configuración del gráfico
    ax.set_xlim(0, 25000)
    ax.set_ylim(0, 15000)
    ax.set_xlabel('Distancia Este (metros)', fontweight='bold', fontsize=12)
    ax.set_ylabel('Distancia Norte (metros)', fontweight='bold', fontsize=12)
    ax.set_title(f'🚢 Arquitectura Propuesta - LoRaWAN\nTiempo: {current_time:.0f}s', 
                fontweight='bold', fontsize=14, pad=15, color='#27AE60')
    ax.grid(True, alpha=0.3, linestyle='--')
    ax.legend(loc='upper right', fontsize=10, framealpha=0.9, 
             edgecolor='#27AE60', fancybox=True)
    
    # Estadísticas en tiempo real
    coverage_pct = (connected_boats / len(boats) * 100) if len(boats) > 0 else 0
    stats_text = f'Cobertura: {coverage_pct:.0f}%\n' \
                 f'Conectadas: {connected_boats}/{len(boats)}\n' \
                 f'Enlaces P2P: {p2p_links}\n' \
                 f'Topología: Híbrida'
    ax.text(0.02, 0.98, stats_text, transform=ax.transAxes,
           fontsize=11, verticalalignment='top', fontweight='bold',
           bbox=dict(boxstyle='round', facecolor='white', alpha=0.9, 
                    edgecolor='#27AE60', linewidth=2.5),
           color='#27AE60')
    
    # Información adicional
    info_text = f'Cantón Salinas | Área: 375 km² | SF: 7-12 | UPSE'
    ax.text(0.5, 0.02, info_text, transform=ax.transAxes,
           fontsize=9, verticalalignment='bottom', ha='center',
           bbox=dict(boxstyle='round', facecolor='white', alpha=0.8),
           style='italic', color='#7F8C8D')
    
    return []

print("\nCreando animación de arquitectura propuesta...")
print("(Esto puede tardar 1-3 minutos)")

anim = animation.FuncAnimation(fig, animate, init_func=init,
                              frames=len(times), interval=200, 
                              blit=True, repeat=True)

# Guardar como GIF
output_gif = 'Animacion_Arquitectura_Movil.gif'
print(f"\nGuardando animación como GIF ({len(times)} frames a 5 fps)...")
anim.save(output_gif, writer='pillow', fps=5, dpi=100)
print(f"✓ Animación guardada: {output_gif}")

plt.close()

# ========== CAPTURAS CLAVE ==========
print("\nGenerando capturas de momentos clave...")

key_frames = [0, len(times)//4, len(times)//2, 3*len(times)//4, -1]
frame_names = ['inicio', 'cuarto', 'mitad', 'tres_cuartos', 'final']

for idx, (frame_idx, name) in enumerate(zip(key_frames, frame_names)):
    fig_static, ax_static = plt.subplots(figsize=(14, 9))
    
    current_time = times[frame_idx]
    current_data = df_mobile[df_mobile['time'] == current_time]
    
    # Fondo
    ax_static.set_facecolor('#E8F5E9')
    ax_static.fill_between([0, 25000], -1000, 0, color='#D7CCC8', alpha=0.7)
    
    boats = current_data[current_data['type'] == 'boat']
    gateways = current_data[current_data['type'] == 'gateway']
    server = current_data[current_data['type'] == 'server']
    
    # Círculos de cobertura dinámica
    for _, gw in gateways.iterrows():
        coverage = Circle((gw['x'], gw['y']), 15000, 
                         color='#27AE60', fill=True, alpha=0.10,
                         linewidth=2, edgecolor='#27AE60', linestyle='--')
        ax_static.add_patch(coverage)
    
    # Trayectorias de gateways
    if frame_idx >= 5:
        past_times = times[max(0, frame_idx-5):frame_idx+1]
        past_data = df_mobile[
            (df_mobile['time'].isin(past_times)) & 
            (df_mobile['type'] == 'gateway')
        ]
        if len(past_data) > 1:
            ax_static.plot(past_data['x'], past_data['y'], 
                          color='#27AE60', linewidth=1.5, alpha=0.3, 
                          linestyle=':', zorder=3)
    
    # Enlaces
    connected_boats = 0
    p2p_links = 0
    
    for _, boat in boats.iterrows():
        min_dist = float('inf')
        closest_gw = None
        for _, gw in gateways.iterrows():
            dist = np.sqrt((boat['x'] - gw['x'])**2 + (boat['y'] - gw['y'])**2)
            if dist < min_dist:
                min_dist = dist
                closest_gw = gw
        
        if closest_gw is not None and min_dist <= 15000:
            ax_static.plot([boat['x'], closest_gw['x']], 
                          [boat['y'], closest_gw['y']], 
                          color='#52BE80', linewidth=0.8, alpha=0.5)
            connected_boats += 1
        elif closest_gw is not None and 15000 < min_dist <= 20000:
            for _, relay_boat in boats.iterrows():
                dist_to_relay = np.sqrt((boat['x'] - relay_boat['x'])**2 + (boat['y'] - relay_boat['y'])**2)
                dist_relay_to_gw = np.sqrt((relay_boat['x'] - closest_gw['x'])**2 + (relay_boat['y'] - closest_gw['y'])**2)
                if dist_to_relay < 5000 and dist_relay_to_gw <= 15000:
                    ax_static.plot([boat['x'], relay_boat['x']], 
                                  [boat['y'], relay_boat['y']], 
                                  color='#9B59B6', linewidth=1.2, alpha=0.6, 
                                  linestyle='--', zorder=4)
                    ax_static.plot([relay_boat['x'], closest_gw['x']], 
                                  [relay_boat['y'], closest_gw['y']], 
                                  color='#52BE80', linewidth=0.8, alpha=0.5)
                    p2p_links += 1
                    connected_boats += 1
                    break
    
    # Backhaul
    if len(server) > 0:
        srv = server.iloc[0]
        for _, gw in gateways.iterrows():
            ax_static.plot([gw['x'], srv['x']], 
                          [gw['y'], srv['y']], 
                          color='#F39C12', linewidth=1.5, alpha=0.6, linestyle=':')
    
    # Nodos
    ax_static.scatter(boats['x'], boats['y'], c='#3498DB', s=100, marker='o', 
                     label=f'Embarcaciones ({len(boats)})', alpha=0.8, 
                     edgecolors='#2874A6', linewidths=1.5, zorder=5)
    ax_static.scatter(gateways['x'], gateways['y'], c='#27AE60', s=400, marker='^', 
                     label=f'Gateways Móviles ({len(gateways)})', alpha=0.9, 
                     edgecolors='#1E8449', linewidths=2.5, zorder=6)
    if len(server) > 0:
        ax_static.scatter(server['x'], server['y'], c='#F39C12', s=500, marker='D', 
                         label='Network Server', alpha=0.95, 
                         edgecolors='#D68910', linewidths=2.5, zorder=7)
    
    ax_static.set_xlim(0, 25000)
    ax_static.set_ylim(0, 15000)
    ax_static.set_xlabel('Distancia Este (metros)', fontweight='bold', fontsize=12)
    ax_static.set_ylabel('Distancia Norte (metros)', fontweight='bold', fontsize=12)
    ax_static.set_title(f'🚢 Arquitectura Propuesta - LoRaWAN\nTiempo: {current_time:.0f}s', 
                       fontweight='bold', fontsize=14, pad=15, color='#27AE60')
    ax_static.grid(True, alpha=0.3, linestyle='--')
    ax_static.legend(loc='upper right', fontsize=10, framealpha=0.9,
                    edgecolor='#27AE60', fancybox=True)
    
    # Stats
    coverage_pct = (connected_boats / len(boats) * 100) if len(boats) > 0 else 0
    stats_text = f'Cobertura: {coverage_pct:.0f}%\n' \
                 f'Conectadas: {connected_boats}/{len(boats)}\n' \
                 f'Enlaces P2P: {p2p_links}\n' \
                 f'Topología: Híbrida'
    ax_static.text(0.02, 0.98, stats_text, transform=ax_static.transAxes,
                  fontsize=11, verticalalignment='top', fontweight='bold',
                  bbox=dict(boxstyle='round', facecolor='white', alpha=0.9, 
                           edgecolor='#27AE60', linewidth=2.5),
                  color='#27AE60')
    
    # Info
    info_text = f'cantón Salinas, Ecuador | Área: 25×15 km'
    ax_static.text(0.5, 0.02, info_text, transform=ax_static.transAxes,
                  fontsize=9, verticalalignment='bottom', ha='center',
                  bbox=dict(boxstyle='round', facecolor='white', alpha=0.8),
                  style='italic', color='#7F8C8D')
    
    plt.tight_layout()
    
    output_img = f'Movil_Captura_{idx+1}_{name}.png'
    plt.savefig(output_img, dpi=300, bbox_inches='tight', facecolor='white')
    plt.close()
    print(f"✓ Captura {idx+1} guardada: {output_img}")

print("\n" + "=" * 80)
print("ARCHIVOS GENERADOS - ARQUITECTURA PROPUESTA:")
print("=" * 80)
print(f"  1. {output_gif} (animación)")
print("  2. Movil_Captura_1_inicio.png")
print("  3. Movil_Captura_2_cuarto.png")
print("  4. Movil_Captura_3_mitad.png")
print("  5. Movil_Captura_4_tres_cuartos.png")
print("  6. Movil_Captura_5_final.png")
print("=" * 80)
print("\n✓ Proceso completado exitosamente!")
print("\n📊 COMPARACIÓN:")
print("Ahora tienes ambas animaciones para comparar:")
print("  • Animacion_Arquitectura_Tradicional.gif")
print("  • Animacion_Arquitectura_Movil.gif")
