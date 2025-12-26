#!/usr/bin/env python3
"""
Generador de Gráficas - Objetivo 1
Comparación de Arquitecturas LoRaWAN
"""

import matplotlib.pyplot as plt
import numpy as np
import seaborn as sns

# Configuración de estilo profesional
plt.style.use('seaborn-v0_8-darkgrid')
sns.set_palette("husl")
plt.rcParams['font.family'] = 'DejaVu Sans'
plt.rcParams['font.size'] = 11
plt.rcParams['axes.labelsize'] = 12
plt.rcParams['axes.titlesize'] = 14
plt.rcParams['xtick.labelsize'] = 10
plt.rcParams['ytick.labelsize'] = 10
plt.rcParams['legend.fontsize'] = 10
plt.rcParams['figure.titlesize'] = 16

# Colores profesionales
COLORS = {
    'tradicional': '#E74C3C',  # Rojo
    'movil_3': '#3498DB',       # Azul
    'movil_3_p2p': '#9B59B6',   # Morado
    'movil_10': '#2ECC71',      # Verde
    'movil_10_p2p': '#1ABC9C'   # Verde azulado
}

# DATOS REALES DE LAS SIMULACIONES
datos = {
    'Tradicional\n(3 GW Fijos)': {
        'pdr': 99.30,
        'latencia': 53,
        'cobertura': 68.0,  # Del análisis anterior
        'distancia': 10314,  # Del análisis anterior
        'embarcaciones_cubiertas': 34,
        'p2p_exitosos': 0,
        'p2p_total': 0,
        'color': COLORS['tradicional']
    },
    'Móvil\n(3 GW sin P2P)': {
        'pdr': 99.43,
        'latencia': 53,
        'cobertura': 99.39,
        'distancia': 6900,
        'embarcaciones_cubiertas': 50,
        'p2p_exitosos': 0,
        'p2p_total': 0,
        'color': COLORS['movil_3']
    },
    'Móvil\n(3 GW con P2P)': {
        'pdr': 99.43,
        'latencia': 53,
        'cobertura': 99.39,
        'distancia': 6900,
        'embarcaciones_cubiertas': 50,
        'p2p_exitosos': 214,
        'p2p_total': 287,
        'color': COLORS['movil_3_p2p']
    },
    'Móvil\n(10 GW sin P2P)': {
        'pdr': 100.00,
        'latencia': 53,
        'cobertura': 100.0,
        'distancia': 2789,
        'embarcaciones_cubiertas': 50,
        'p2p_exitosos': 0,
        'p2p_total': 0,
        'color': COLORS['movil_10']
    },
    'Móvil\n(10 GW con P2P)': {
        'pdr': 100.00,
        'latencia': 53,
        'cobertura': 100.0,
        'distancia': 2789,
        'embarcaciones_cubiertas': 50,
        'p2p_exitosos': 218,
        'p2p_total': 286,
        'color': COLORS['movil_10_p2p']
    }
}

def crear_grafica_pdr():
    """Gráfica de PDR comparativa"""
    arquitecturas = list(datos.keys())
    pdrs = [datos[arq]['pdr'] for arq in arquitecturas]
    colors = [datos[arq]['color'] for arq in arquitecturas]
    
    fig, ax = plt.subplots(figsize=(12, 6))
    bars = ax.bar(arquitecturas, pdrs, color=colors, alpha=0.8, edgecolor='black', linewidth=1.5)
    
    # Añadir valores en las barras
    for bar, value in zip(bars, pdrs):
        height = bar.get_height()
        ax.text(bar.get_x() + bar.get_width()/2., height,
                f'{value:.2f}%',
                ha='center', va='bottom', fontweight='bold', fontsize=11)
    
    ax.set_ylabel('PDR (%)', fontweight='bold')
    ax.set_title('Comparación de Packet Delivery Ratio (PDR)\nObjetivo 1: Evaluación de Arquitecturas LoRaWAN', 
                 fontweight='bold', pad=20)
    ax.set_ylim(98.5, 101)
    ax.grid(axis='y', alpha=0.3)
    ax.axhline(y=99, color='red', linestyle='--', linewidth=1, alpha=0.5, label='Objetivo 99%')
    ax.legend(loc='lower right')
    
    plt.xticks(rotation=0, ha='center')
    plt.tight_layout()
    plt.savefig('grafica_pdr_objetivo1.png', dpi=300, bbox_inches='tight')
    print("✅ Gráfica guardada: grafica_pdr_objetivo1.png")
    plt.close()

def crear_grafica_cobertura():
    """Gráfica de cobertura comparativa"""
    arquitecturas = list(datos.keys())
    coberturas = [datos[arq]['cobertura'] for arq in arquitecturas]
    colors = [datos[arq]['color'] for arq in arquitecturas]
    
    fig, ax = plt.subplots(figsize=(12, 6))
    bars = ax.bar(arquitecturas, coberturas, color=colors, alpha=0.8, 
                   edgecolor='black', linewidth=1.5)
    
    # Añadir valores
    for bar, value in zip(bars, coberturas):
        height = bar.get_height()
        ax.text(bar.get_x() + bar.get_width()/2., height,
                f'{value:.1f}%',
                ha='center', va='bottom', fontweight='bold', fontsize=11)
    
    ax.set_ylabel('Cobertura (%)', fontweight='bold')
    ax.set_title('Comparación de Cobertura Dinámica\nObjetivo 1: Evaluación de Arquitecturas LoRaWAN',
                 fontweight='bold', pad=20)
    ax.set_ylim(0, 110)
    ax.grid(axis='y', alpha=0.3)
    ax.axhline(y=90, color='red', linestyle='--', linewidth=1, alpha=0.5, label='Objetivo 90%')
    ax.legend(loc='lower right')
    
    plt.xticks(rotation=0, ha='center')
    plt.tight_layout()
    plt.savefig('grafica_cobertura_objetivo1.png', dpi=300, bbox_inches='tight')
    print("✅ Gráfica guardada: grafica_cobertura_objetivo1.png")
    plt.close()

def crear_grafica_distancia():
    """Gráfica de distancia promedio al gateway"""
    arquitecturas = list(datos.keys())
    distancias = [datos[arq]['distancia'] for arq in arquitecturas]
    colors = [datos[arq]['color'] for arq in arquitecturas]
    
    fig, ax = plt.subplots(figsize=(12, 6))
    bars = ax.bar(arquitecturas, distancias, color=colors, alpha=0.8, 
                   edgecolor='black', linewidth=1.5)
    
    # Añadir valores
    for bar, value in zip(bars, distancias):
        height = bar.get_height()
        ax.text(bar.get_x() + bar.get_width()/2., height,
                f'{value:,.0f} m',
                ha='center', va='bottom', fontweight='bold', fontsize=10)
    
    ax.set_ylabel('Distancia Promedio al Gateway (m)', fontweight='bold')
    ax.set_title('Distancia Promedio al Gateway Más Cercano\nObjetivo 1: Evaluación de Arquitecturas LoRaWAN',
                 fontweight='bold', pad=20)
    ax.set_ylim(0, 12000)
    ax.grid(axis='y', alpha=0.3)
    ax.axhline(y=15000, color='red', linestyle='--', linewidth=2, alpha=0.7, 
               label='Alcance Máximo LoRa (15 km)')
    ax.legend(loc='upper right')
    
    plt.xticks(rotation=0, ha='center')
    plt.tight_layout()
    plt.savefig('grafica_distancia_objetivo1.png', dpi=300, bbox_inches='tight')
    print("✅ Gráfica guardada: grafica_distancia_objetivo1.png")
    plt.close()

def crear_grafica_embarcaciones_cubiertas():
    """Gráfica de embarcaciones cubiertas"""
    arquitecturas = list(datos.keys())
    cubiertas = [datos[arq]['embarcaciones_cubiertas'] for arq in arquitecturas]
    colors = [datos[arq]['color'] for arq in arquitecturas]
    total = 50
    
    fig, ax = plt.subplots(figsize=(12, 6))
    bars = ax.bar(arquitecturas, cubiertas, color=colors, alpha=0.8,
                   edgecolor='black', linewidth=1.5)
    
    # Añadir valores
    for bar, value in zip(bars, cubiertas):
        height = bar.get_height()
        porcentaje = (value / total) * 100
        ax.text(bar.get_x() + bar.get_width()/2., height,
                f'{value}/{total}\n({porcentaje:.0f}%)',
                ha='center', va='bottom', fontweight='bold', fontsize=10)
    
    ax.set_ylabel('Embarcaciones Cubiertas', fontweight='bold')
    ax.set_title('Embarcaciones con Cobertura LoRaWAN\nObjetivo 1: Evaluación de Arquitecturas LoRaWAN',
                 fontweight='bold', pad=20)
    ax.set_ylim(0, 55)
    ax.grid(axis='y', alpha=0.3)
    ax.axhline(y=total, color='green', linestyle='--', linewidth=2, alpha=0.7,
               label='Total: 50 embarcaciones')
    ax.legend(loc='lower right')
    
    plt.xticks(rotation=0, ha='center')
    plt.tight_layout()
    plt.savefig('grafica_embarcaciones_objetivo1.png', dpi=300, bbox_inches='tight')
    print("✅ Gráfica guardada: grafica_embarcaciones_objetivo1.png")
    plt.close()

def crear_grafica_p2p_relay():
    """Gráfica específica de relay P2P"""
    # Solo arquitecturas con P2P
    arqs_p2p = ['Móvil\n(3 GW con P2P)', 'Móvil\n(10 GW con P2P)']
    exitosos = [datos[arq]['p2p_exitosos'] for arq in arqs_p2p]
    totales = [datos[arq]['p2p_total'] for arq in arqs_p2p]
    fallidos = [totales[i] - exitosos[i] for i in range(len(totales))]
    colors = [datos[arq]['color'] for arq in arqs_p2p]
    
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))
    
    # Gráfica 1: Mensajes relay
    x = np.arange(len(arqs_p2p))
    width = 0.35
    
    bars1 = ax1.bar(x - width/2, exitosos, width, label='Exitoso', 
                   color='#2ECC71', alpha=0.8, edgecolor='black')
    bars2 = ax1.bar(x + width/2, fallidos, width, label='Fallido',
                   color='#E74C3C', alpha=0.8, edgecolor='black')
    
    ax1.set_ylabel('Cantidad de Mensajes', fontweight='bold')
    ax1.set_title('Mensajes Relay P2P\n(Protocolo de Emergencia)', fontweight='bold')
    ax1.set_xticks(x)
    ax1.set_xticklabels(arqs_p2p)
    ax1.legend()
    ax1.grid(axis='y', alpha=0.3)
    
    # Añadir valores
    for bars in [bars1, bars2]:
        for bar in bars:
            height = bar.get_height()
            ax1.text(bar.get_x() + bar.get_width()/2., height,
                    f'{int(height)}', ha='center', va='bottom', fontsize=9)
    
    # Gráfica 2: Eficiencia P2P
    eficiencias = [(exitosos[i]/totales[i])*100 for i in range(len(totales))]
    bars = ax2.bar(range(len(arqs_p2p)), eficiencias, color=colors, 
                   alpha=0.8, edgecolor='black', linewidth=1.5)
    
    ax2.set_ylabel('Eficiencia P2P (%)', fontweight='bold')
    ax2.set_title('Eficiencia del Protocolo P2P\n(Tasa de Éxito)', fontweight='bold')
    ax2.set_xticks(range(len(arqs_p2p)))
    ax2.set_xticklabels(arqs_p2p)
    ax2.set_ylim(0, 100)
    ax2.grid(axis='y', alpha=0.3)
    
    # Añadir valores
    for bar, value in zip(bars, eficiencias):
        height = bar.get_height()
        ax2.text(bar.get_x() + bar.get_width()/2., height,
                f'{value:.1f}%', ha='center', va='bottom', fontweight='bold', fontsize=11)
    
    plt.tight_layout()
    plt.savefig('grafica_relay_p2p_objetivo1.png', dpi=300, bbox_inches='tight')
    print("✅ Gráfica guardada: grafica_relay_p2p_objetivo1.png")
    plt.close()

def crear_grafica_comparativa_general():
    """Gráfica de radar comparativa general (solo 3 arquitecturas principales)"""
    # Seleccionar arquitecturas principales para claridad
    arqs_principales = [
        'Tradicional\n(3 GW Fijos)',
        'Móvil\n(3 GW con P2P)',
        'Móvil\n(10 GW con P2P)'
    ]
    
    categorias = ['PDR\n(%)', 'Cobertura\n(%)', 'Embarcaciones\nCubiertas']
    
    # Normalizar valores a escala 0-100
    valores = []
    for arq in arqs_principales:
        pdr_norm = datos[arq]['pdr']
        cob_norm = datos[arq]['cobertura']
        emb_norm = (datos[arq]['embarcaciones_cubiertas'] / 50) * 100
        valores.append([pdr_norm, cob_norm, emb_norm])
    
    # Número de variables
    N = len(categorias)
    angles = np.linspace(0, 2 * np.pi, N, endpoint=False).tolist()
    
    # Cerrar el polígono
    for i in range(len(valores)):
        valores[i] += valores[i][:1]
    angles += angles[:1]
    
    fig, ax = plt.subplots(figsize=(10, 10), subplot_kw=dict(projection='polar'))
    
    colors_radar = [datos[arq]['color'] for arq in arqs_principales]
    
    for i, arq in enumerate(arqs_principales):
        ax.plot(angles, valores[i], 'o-', linewidth=2, label=arq, color=colors_radar[i])
        ax.fill(angles, valores[i], alpha=0.15, color=colors_radar[i])
    
    ax.set_xticks(angles[:-1])
    ax.set_xticklabels(categorias, fontweight='bold')
    ax.set_ylim(0, 100)
    ax.set_title('Comparación General de Rendimiento\nObjetivo 1: Arquitecturas LoRaWAN',
                 fontweight='bold', pad=30, fontsize=16)
    ax.legend(loc='upper right', bbox_to_anchor=(1.3, 1.1))
    ax.grid(True)
    
    plt.tight_layout()
    plt.savefig('grafica_radar_objetivo1.png', dpi=300, bbox_inches='tight')
    print("✅ Gráfica guardada: grafica_radar_objetivo1.png")
    plt.close()

def main():
    print("\n╔════════════════════════════════════════════════════════╗")
    print("║    GENERADOR DE GRÁFICAS - OBJETIVO 1                ║")
    print("╚════════════════════════════════════════════════════════╝\n")
    
    print("📊 Generando gráficas profesionales...\n")
    
    crear_grafica_pdr()
    crear_grafica_cobertura()
    crear_grafica_distancia()
    crear_grafica_embarcaciones_cubiertas()
    crear_grafica_p2p_relay()
    crear_grafica_comparativa_general()
    
    print("\n" + "="*60)
    print("✅ GRÁFICAS GENERADAS EXITOSAMENTE")
    print("="*60)
    print("\n📁 Archivos generados:")
    print("  1. grafica_pdr_objetivo1.png")
    print("  2. grafica_cobertura_objetivo1.png")
    print("  3. grafica_distancia_objetivo1.png")
    print("  4. grafica_embarcaciones_objetivo1.png")
    print("  5. grafica_relay_p2p_objetivo1.png")
    print("  6. grafica_radar_objetivo1.png")
    print("\n💡 Resolución: 300 DPI (calidad publicación)")
    print("="*60 + "\n")

if __name__ == "__main__":
    main()
