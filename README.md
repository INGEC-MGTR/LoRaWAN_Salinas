# Arquitecturas LoRaWAN para Emergencias Marítimas

## Descripción
Simulación NS-3 de arquitecturas LoRaWAN para comunicaciones de emergencia marítima en Salinas, Ecuador.

**Autores:** Ing. Erika Michelle Chiriguayo Rodríguez | Ing. Fernando Vinicio Chamba Macas, Mgtr.
**Institución:** UPSE - Maestría en Telecomunicaciones

## Estructura del Proyecto

```
LoRaWAN_Tesis/
├── Resultados Ob1/              # Objetivo 1: Diseño y modelado
│   ├── Animacion_gif/           # Animaciones de red
│   ├── Resultados_Movil_10gw/   # Resultados 10 gateways móviles
│   ├── Resultados_mòvil_3gw/    # Resultados 3 gateways móviles
│   ├── Resultados_tradicional_3gw/  # Arquitectura tradicional (fija)
│   └── Script_graficas/         # Scripts de visualización
│
├── Resultados Ob2/              # Objetivo 2: Validación P2P
│   ├── Analisis_objetivo2/      # Análisis de datos
│   └── Resultado_simulaciones_SF_Ptx/  # Resultados SF/Potencia
│
├── Resultados Ob3/              # Objetivo 3: Escalabilidad
│   ├── Analisis_objetivo3/      # Análisis comparativo
│   ├── Còdigos_escenarios/      # Scripts de escenarios
│   └── Resultados_escenarios/   # Datos de simulaciones
│
├── *.cc                         # Códigos de simulación NS-3
└── *.sh                         # Scripts de validación
```

## Archivos de Simulación

- `salinas-traditional_original.cc` - Arquitectura tradicional (gateways fijos)
- `salinas-mobile-3gw_original.cc` - 3 gateways móviles + P2P
- `salinas-mobile-10gw-p2p.cc` - 10 gateways móviles
- `validacion_simulacion_objetivo2.sh` - Script de validación

## Resultados Principales

- **PDR Móvil**: 99.20% vs Tradicional: 97.71% (+1.49%)
- **Cobertura**: 100% vs ~95% (+5%)
- **Resiliencia**: Móvil tolera 66% fallos, Tradicional 0%

## Uso

```bash
# Compilar en NS-3
./ns3 run "salinas-mobile-3gw_original --nDevices=50 --simTime=3600"
```

## 📧 Contacto
e.chiriguarodrigue@upse.edu.ec
f.chamba@upse.edu.ec
