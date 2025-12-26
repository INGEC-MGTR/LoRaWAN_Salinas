#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Universidad Estatal Península de Santa Elena (UPSE)
Facultad de Sistemas y Telecomunicaciones
Carrera de Telecomunicaciones

Visualización Animada de Red LoRaWAN Marítima
Autora: Emi
Fecha: Diciembre 2024
"""

import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from matplotlib.patches import Circle
import numpy as np

# Configuración de estilo
plt.rcParams['font.family'] = 'serif'
plt.rcParams['font.size'] = 10

# Leer datos
print("Cargando datos de posiciones...")
df_pos = pd.read_csv('positions_mobile.csv')

# Obtener tiempos únicos
times = sorted(df_pos['time'].unique())
print(f"✓ Datos cargados: {len(times)} frames de tiempo")

# Configurar figura
fig, ax = plt.subplots(figsize=(14, 9))

def init():
    ax.clear()
    # Fondo océano
    ax.set_facecolor('#87CEEB')
    
    # Costa
    ax.fill_between([0, 25000], -1000, 0, color='#D2B48C', alpha=0.7, label='Costa')
    
    # Configuración de ejes
    ax.set_xlim(0, 25000)
    ax.set_ylim(0, 15000)
    ax.set_xlabel('Distancia Este (m)', fontweight='bold', fontsize=12)
    ax.set_ylabel('Distancia Norte (m)', fontsize=12, fontweight='bold')
    ax.set_title('Red LoRaWAN Marítima - Cantón Salinas\nGateways Móviles', 
                fontweight='bold', fontsize=14, pad=15)
    ax.grid(True, alpha=0.3, linestyle='--')
    
    return []

def animate(frame_idx):
    ax.clear()
    
    # Fondo
    ax.set_facecolor('#87CEEB')
    ax.fill_between([0, 25000], -1000, 0, color='#D2B48C', alpha=0.7)
    
    current_time = times[frame_idx]
    
    # Filtrar datos del tiempo actual
    current_data = df_pos[df_pos['time'] == current_time]
    
    # Separar por tipo
    boats = current_data[current_data['type'] == 'boat']
    gateways = current_data[current_data['type'] == 'gateway']
    server = current_data[current_data['type'] == 'server']
    
    # Dibujar círculos de cobertura de gateways (5 km de radio)
    for _, gw in gateways.iterrows():
        coverage = Circle((gw['x'], gw['y']), 5000, 
                         color='red', fill=False, 
                         linestyle='--', alpha=0.3, linewidth=1.5)
        ax.add_patch(coverage)
    
    # Dibujar enlaces de comunicación (líneas de embarcaciones a gateways más cercanos)
    for _, boat in boats.iterrows():
        # Encontrar gateway más cercano
        min_dist = float('inf')
        closest_gw = None
        
        for _, gw in gateways.iterrows():
            dist = np.sqrt((boat['x'] - gw['x'])**2 + (boat['y'] - gw['y'])**2)
            if dist < min_dist:
                min_dist = dist
                closest_gw = gw
        
        if closest_gw is not None and min_dist < 5000:  # Dentro del rango
            ax.plot([boat['x'], closest_gw['x']], 
                   [boat['y'], closest_gw['y']], 
                   color='white', linewidth=0.8, alpha=0.4)
    
    # Dibujar enlaces de gateways a servidor
    if len(server) > 0:
        srv = server.iloc[0]
        for _, gw in gateways.iterrows():
            ax.plot([gw['x'], srv['x']], 
                   [gw['y'], srv['y']], 
                   color='yellow', linewidth=1.2, alpha=0.5, linestyle=':')
    
    # Dibujar nodos
    ax.scatter(boats['x'], boats['y'], 
              c='#3498db', s=80, marker='o', 
              label=f'Embarcaciones ({len(boats)})', 
              alpha=0.8, edgecolors='darkblue', linewidths=1.5, zorder=5)
    
    ax.scatter(gateways['x'], gateways['y'], 
              c='#e74c3c', s=250, marker='^', 
              label=f'Gateways Móviles ({len(gateways)})', 
              alpha=0.9, edgecolors='darkred', linewidths=2, zorder=6)
    
    if len(server) > 0:
        ax.scatter(server['x'], server['y'], 
                  c='#2ecc71', s=400, marker='s', 
                  label='Servidor de Red', 
                  alpha=0.9, edgecolors='darkgreen', linewidths=2, zorder=7)
    
    # Configuración
    ax.set_xlim(0, 25000)
    ax.set_ylim(0, 15000)
    ax.set_xlabel('Distancia Este (m)', fontweight='bold', fontsize=11)
    ax.set_ylabel('Distancia Norte (m)', fontweight='bold', fontsize=11)
    ax.set_title(f'Red LoRaWAN Marítima - Gateways Móviles\nTiempo: {current_time:.1f}s', 
                fontweight='bold', fontsize=13, pad=15)
    ax.grid(True, alpha=0.3, linestyle='--')
    ax.legend(loc='upper right', fontsize=10, framealpha=0.9)
    
    # Información adicional
    info_text = f'Área: 375 km² | Cobertura dinámica | SF: 7-12'
    ax.text(0.02, 0.02, info_text, transform=ax.transAxes,
           fontsize=9, verticalalignment='bottom',
           bbox=dict(boxstyle='round', facecolor='white', alpha=0.8))
    
    return []

print("Creando animación...")
anim = animation.FuncAnimation(fig, animate, init_func=init,
                              frames=len(times), interval=200, 
                              blit=True, repeat=True)

print("Guardando animación como GIF...")
anim.save('lorawan_mobile_network.gif', writer='pillow', fps=5, dpi=100)
print("✓ Animación guardada: lorawan_mobile_network.gif")

print("Guardando frames clave como imágenes estáticas...")
# Guardar algunos frames importantes
key_frames = [0, len(times)//4, len(times)//2, 3*len(times)//4]
for i, frame_idx in enumerate(key_frames):
    fig_static, ax_static = plt.subplots(figsize=(14, 9))
    
    current_time = times[frame_idx]
    current_data = df_pos[df_pos['time'] == current_time]
    
    ax_static.set_facecolor('#87CEEB')
    ax_static.fill_between([0, 25000], -1000, 0, color='#D2B48C', alpha=0.7)
    
    boats = current_data[current_data['type'] == 'boat']
    gateways = current_data[current_data['type'] == 'gateway']
    server = current_data[current_data['type'] == 'server']
    
    # Círculos de cobertura
    for _, gw in gateways.iterrows():
        coverage = Circle((gw['x'], gw['y']), 5000, 
                         color='red', fill=False, 
                         linestyle='--', alpha=0.3, linewidth=1.5)
        ax_static.add_patch(coverage)
    
    # Enlaces
    for _, boat in boats.iterrows():
        min_dist = float('inf')
        closest_gw = None
        for _, gw in gateways.iterrows():
            dist = np.sqrt((boat['x'] - gw['x'])**2 + (boat['y'] - gw['y'])**2)
            if dist < min_dist:
                min_dist = dist
                closest_gw = gw
        if closest_gw is not None and min_dist < 5000:
            ax_static.plot([boat['x'], closest_gw['x']], 
                          [boat['y'], closest_gw['y']], 
                          color='white', linewidth=0.8, alpha=0.4)
    
    if len(server) > 0:
        srv = server.iloc[0]
        for _, gw in gateways.iterrows():
            ax_static.plot([gw['x'], srv['x']], 
                          [gw['y'], srv['y']], 
                          color='yellow', linewidth=1.2, alpha=0.5, linestyle=':')
    
    # Nodos
    ax_static.scatter(boats['x'], boats['y'], c='#3498db', s=80, marker='o', 
                     label=f'Embarcaciones ({len(boats)})', alpha=0.8, 
                     edgecolors='darkblue', linewidths=1.5, zorder=5)
    ax_static.scatter(gateways['x'], gateways['y'], c='#e74c3c', s=250, marker='^', 
                     label=f'Gateways Móviles ({len(gateways)})', alpha=0.9, 
                     edgecolors='darkred', linewidths=2, zorder=6)
    if len(server) > 0:
        ax_static.scatter(server['x'], server['y'], c='#2ecc71', s=400, marker='s', 
                         label='Servidor de Red', alpha=0.9, 
                         edgecolors='darkgreen', linewidths=2, zorder=7)
    
    ax_static.set_xlim(0, 25000)
    ax_static.set_ylim(0, 15000)
    ax_static.set_xlabel('Distancia Este (m)', fontweight='bold', fontsize=11)
    ax_static.set_ylabel('Distancia Norte (m)', fontweight='bold', fontsize=11)
    ax_static.set_title(f'Red LoRaWAN Marítima - Gateways Móviles\nTiempo: {current_time:.1f}s', 
                       fontweight='bold', fontsize=13, pad=15)
    ax_static.grid(True, alpha=0.3, linestyle='--')
    ax_static.legend(loc='upper right', fontsize=10, framealpha=0.9)
    
    plt.savefig(f'network_snapshot_{i+1}.png', dpi=300, bbox_inches='tight')
    plt.close()
    print(f"✓ Frame {i+1} guardado: network_snapshot_{i+1}.png")

print("\n✓ ¡Visualizaciones completadas!")
print("  - lorawan_mobile_network.gif (animación)")
print("  - network_snapshot_1.png hasta network_snapshot_4.png (capturas)")
