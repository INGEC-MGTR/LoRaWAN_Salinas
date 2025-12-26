#!/usr/bin/env python3
"""
Análisis de Protocolos P2P de Emergencia - Objetivo 1
Evaluación de comunicación peer-to-peer como protocolo de emergencia
"""

import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

def analizar_p2p():
    """Analiza métricas P2P de todas las arquitecturas"""
    
    print("\n╔════════════════════════════════════════════════════════╗")
    print("║    ANÁLISIS PROTOCOLOS P2P DE EMERGENCIA             ║")
    print("╚════════════════════════════════════════════════════════╝\n")
    
    # Leer datos
    datos = []
    
    # Tradicional (sin P2P)
    try:
        df = pd.read_csv('resultados-salinas-traditional-gw.csv')
        datos.append({
            'Arquitectura': 'Tradicional (3 GW)',
            'P2P': 'No',
            'PDR': df['PDR'].iloc[0],
            'Cobertura': 68.0,  # De análisis anterior
            'TotalP2P': 0,
            'RelayExitoso': 0,
            'RelayFallido': 0,
            'EficienciaP2P': 0
        })
    except:
        pass
    
    # Móvil 3 GW sin P2P
    try:
        df = pd.read_csv('resultados_movil_3gw.csv')
        datos.append({
            'Arquitectura': 'Móvil (3 GW)',
            'P2P': 'No',
            'PDR': df['PDR'].iloc[0],
            'Cobertura': 99.39,
            'TotalP2P': df['TotalP2PPackets'].iloc[0] if 'TotalP2PPackets' in df.columns else 0,
            'RelayExitoso': df['SuccessfulRelays'].iloc[0] if 'SuccessfulRelays' in df.columns else 0,
            'RelayFallido': df['FailedRelays'].iloc[0] if 'FailedRelays' in df.columns else 0,
            'EficienciaP2P': df['P2PEfficiency'].iloc[0] if 'P2PEfficiency' in df.columns else 0
        })
    except:
        pass
    
    # Móvil 3 GW CON P2P
    try:
        df = pd.read_csv('resultados_salinas_movil_3gw_p2p.csv')
        datos.append({
            'Arquitectura': 'Móvil (3 GW) + P2P',
            'P2P': 'Sí',
            'PDR': df['PDR'].iloc[0],
            'Cobertura': 99.39,  # Estimado
            'TotalP2P': df['TotalP2PPackets'].iloc[0] if 'TotalP2PPackets' in df.columns else 0,
            'RelayExitoso': df['SuccessfulRelays'].iloc[0] if 'SuccessfulRelays' in df.columns else 0,
            'RelayFallido': df['FailedRelays'].iloc[0] if 'FailedRelays' in df.columns else 0,
            'EficienciaP2P': df['P2PEfficiency'].iloc[0] if 'P2PEfficiency' in df.columns else 0
        })
        print("✅ Datos P2P de 3 GW cargados")
    except Exception as e:
        print(f"⚠️  No se encontró resultados_salinas_movil_3gw_p2p.csv")
        print(f"   Ejecuta: ./ns3 run \"salinas-mobile-3gw --enableP2P=true\"\n")
    
    # Móvil 10 GW CON P2P
    try:
        df = pd.read_csv('resultados_salinas_gw10_p2p.csv')
        # Verificar si tiene datos P2P
        if 'TotalP2PPackets' in df.columns and df['TotalP2PPackets'].iloc[0] > 0:
            datos.append({
                'Arquitectura': 'Móvil (10 GW) + P2P',
                'P2P': 'Sí',
                'PDR': df['PDR'].iloc[0],
                'Cobertura': 100.0,
                'TotalP2P': df['TotalP2PPackets'].iloc[0],
                'RelayExitoso': df['SuccessfulRelays'].iloc[0],
                'RelayFallido': df['FailedRelays'].iloc[0],
                'EficienciaP2P': df['P2PEfficiency'].iloc[0]
            })
            print("✅ Datos P2P de 10 GW cargados")
    except Exception as e:
        print(f"⚠️  No se encontró resultados_salinas_gw10_p2p.csv con P2P habilitado")
        print(f"   Ejecuta: ./ns3 run \"salinas-mobile-gw-p2p --nGateways=10 --enableP2P=true\"\n")
    
    if len(datos) == 0:
        print("\n❌ No se encontraron datos para análisis P2P")
        return
    
    # Crear DataFrame
    df_p2p = pd.DataFrame(datos)
    
    # TABLA 1: Comparación general con P2P
    print("\n" + "="*100)
    print("TABLA 1: COMPARACIÓN DE ARQUITECTURAS CON PROTOCOLO P2P")
    print("="*100)
    print(df_p2p.to_string(index=False))
    print("="*100)
    
    # Guardar tabla
    df_p2p.to_csv('objetivo1_tabla_protocolos_p2p.csv', index=False, encoding='utf-8-sig')
    print("\n✅ Tabla guardada: objetivo1_tabla_protocolos_p2p.csv")
    
    # TABLA 2: Métricas específicas de relay
    datos_relay = []
    for dato in datos:
        if dato['TotalP2P'] > 0:
            tasa_exito = (dato['RelayExitoso'] / dato['TotalP2P'] * 100) if dato['TotalP2P'] > 0 else 0
            datos_relay.append({
                'Arquitectura': dato['Arquitectura'],
                'Total Mensajes P2P': int(dato['TotalP2P']),
                'Relay Exitoso': int(dato['RelayExitoso']),
                'Relay Fallido': int(dato['RelayFallido']),
                'Tasa Éxito (%)': f"{tasa_exito:.2f}",
                'Eficiencia P2P (%)': f"{dato['EficienciaP2P']:.2f}"
            })
    
    if datos_relay:
        df_relay = pd.DataFrame(datos_relay)
        print("\n" + "="*100)
        print("TABLA 2: MÉTRICAS DE PROTOCOLO P2P (RELAY DE EMERGENCIA)")
        print("="*100)
        print(df_relay.to_string(index=False))
        print("="*100)
        
        df_relay.to_csv('objetivo1_tabla_metricas_relay.csv', index=False, encoding='utf-8-sig')
        print("\n✅ Tabla guardada: objetivo1_tabla_metricas_relay.csv")
    
    # ANÁLISIS: Mejora por P2P
    print("\n" + "="*100)
    print("ANÁLISIS: IMPACTO DEL PROTOCOLO P2P DE EMERGENCIA")
    print("="*100)
    
    # Comparar móvil sin P2P vs móvil con P2P (3 GW)
    movil_sin_p2p = [d for d in datos if d['Arquitectura'] == 'Móvil (3 GW)']
    movil_con_p2p = [d for d in datos if d['Arquitectura'] == 'Móvil (3 GW) + P2P']
    
    if movil_sin_p2p and movil_con_p2p:
        sin = movil_sin_p2p[0]
        con = movil_con_p2p[0]
        
        mejora_pdr = con['PDR'] - sin['PDR']
        print(f"\n📊 Efecto de P2P en arquitectura móvil (3 GW):")
        print(f"   • PDR sin P2P: {sin['PDR']:.2f}%")
        print(f"   • PDR con P2P: {con['PDR']:.2f}%")
        print(f"   • Mejora: {mejora_pdr:+.2f}%")
        print(f"\n   • Mensajes relay exitosos: {int(con['RelayExitoso'])}")
        print(f"   • Eficiencia P2P: {con['EficienciaP2P']:.2f}%")
        
        if con['TotalP2P'] > 0:
            print(f"\n   ✅ El protocolo P2P actuó {int(con['RelayExitoso'])} veces como")
            print(f"      mecanismo de emergencia cuando no había gateway directo disponible")
    else:
        print("\n⚠️  Falta ejecutar simulación con P2P=true para comparación completa")
    
    print("\n" + "="*100)
    
    # Crear gráfica si hay datos P2P
    if datos_relay:
        crear_grafica_relay(df_p2p, df_relay)

def crear_grafica_relay(df_general, df_relay):
    """Crea gráficas de métricas P2P"""
    
    # Filtrar solo arquitecturas con P2P
    df_p2p = df_general[df_general['P2P'] == 'Sí']
    
    if len(df_p2p) == 0:
        return
    
    fig, axes = plt.subplots(2, 2, figsize=(14, 10))
    fig.suptitle('Análisis de Protocolos P2P de Emergencia\nObjetivo 1', 
                 fontweight='bold', fontsize=16)
    
    # Gráfica 1: PDR con y sin P2P
    ax1 = axes[0, 0]
    arquitecturas = df_general['Arquitectura'].tolist()
    pdrs = df_general['PDR'].tolist()
    colors = ['#E74C3C' if 'Tradicional' in a else '#3498DB' if 'P2P' not in a else '#2ECC71' 
              for a in arquitecturas]
    
    bars = ax1.bar(range(len(arquitecturas)), pdrs, color=colors, alpha=0.8, edgecolor='black')
    ax1.set_xticks(range(len(arquitecturas)))
    ax1.set_xticklabels([a.replace(' + P2P', '\n+P2P').replace('Móvil', 'M') 
                          for a in arquitecturas], fontsize=9)
    ax1.set_ylabel('PDR (%)', fontweight='bold')
    ax1.set_title('PDR: Comparación con/sin P2P', fontweight='bold')
    ax1.grid(axis='y', alpha=0.3)
    
    # Añadir valores
    for bar, value in zip(bars, pdrs):
        height = bar.get_height()
        ax1.text(bar.get_x() + bar.get_width()/2., height,
                f'{value:.2f}%', ha='center', va='bottom', fontsize=9)
    
    # Gráfica 2: Mensajes relay
    ax2 = axes[0, 1]
    if len(df_relay) > 0:
        arqs = df_relay['Arquitectura'].tolist()
        relay_exitoso = [int(r) for r in df_relay['Relay Exitoso'].tolist()]
        relay_fallido = [int(r) for r in df_relay['Relay Fallido'].tolist()]
        
        x = np.arange(len(arqs))
        width = 0.35
        
        bars1 = ax2.bar(x - width/2, relay_exitoso, width, label='Exitoso', 
                       color='#2ECC71', alpha=0.8)
        bars2 = ax2.bar(x + width/2, relay_fallido, width, label='Fallido',
                       color='#E74C3C', alpha=0.8)
        
        ax2.set_xticks(x)
        ax2.set_xticklabels([a.replace(' + P2P', '\n+P2P').replace('Móvil', 'M') 
                             for a in arqs], fontsize=9)
        ax2.set_ylabel('Cantidad de Mensajes', fontweight='bold')
        ax2.set_title('Mensajes Relay (Protocolo P2P)', fontweight='bold')
        ax2.legend()
        ax2.grid(axis='y', alpha=0.3)
    
    # Gráfica 3: Eficiencia P2P
    ax3 = axes[1, 0]
    if len(df_relay) > 0:
        arqs = df_relay['Arquitectura'].tolist()
        eficiencias = [float(e) for e in df_relay['Eficiencia P2P (%)'].tolist()]
        
        bars = ax3.bar(range(len(arqs)), eficiencias, color='#9B59B6', alpha=0.8, edgecolor='black')
        ax3.set_xticks(range(len(arqs)))
        ax3.set_xticklabels([a.replace(' + P2P', '\n+P2P').replace('Móvil', 'M') 
                             for a in arqs], fontsize=9)
        ax3.set_ylabel('Eficiencia P2P (%)', fontweight='bold')
        ax3.set_title('Eficiencia del Protocolo P2P', fontweight='bold')
        ax3.grid(axis='y', alpha=0.3)
        
        for bar, value in zip(bars, eficiencias):
            height = bar.get_height()
            ax3.text(bar.get_x() + bar.get_width()/2., height,
                    f'{value:.1f}%', ha='center', va='bottom', fontsize=9)
    
    # Gráfica 4: Tasa de éxito
    ax4 = axes[1, 1]
    if len(df_relay) > 0:
        arqs = df_relay['Arquitectura'].tolist()
        tasas = [float(t) for t in df_relay['Tasa Éxito (%)'].tolist()]
        
        bars = ax4.bar(range(len(arqs)), tasas, color='#16A085', alpha=0.8, edgecolor='black')
        ax4.set_xticks(range(len(arqs)))
        ax4.set_xticklabels([a.replace(' + P2P', '\n+P2P').replace('Móvil', 'M') 
                             for a in arqs], fontsize=9)
        ax4.set_ylabel('Tasa de Éxito (%)', fontweight='bold')
        ax4.set_title('Tasa de Éxito de Relay P2P', fontweight='bold')
        ax4.set_ylim(0, 110)
        ax4.grid(axis='y', alpha=0.3)
        
        for bar, value in zip(bars, tasas):
            height = bar.get_height()
            ax4.text(bar.get_x() + bar.get_width()/2., height,
                    f'{value:.1f}%', ha='center', va='bottom', fontsize=9)
    
    plt.tight_layout()
    plt.savefig('grafica_protocolo_p2p_objetivo1.png', dpi=300, bbox_inches='tight')
    print("\n✅ Gráfica guardada: grafica_protocolo_p2p_objetivo1.png")
    plt.close()

if __name__ == "__main__":
    analizar_p2p()
