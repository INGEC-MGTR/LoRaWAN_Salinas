#!/bin/bash
# OBJETIVO 3 - ESCENARIO 1: Condiciones Meteorológicas Adversas
# Evalúa el impacto de pérdidas adicionales por clima

echo "════════════════════════════════════════════════════════════"
echo "  OBJETIVO 3 - ESCENARIO 1: CONDICIONES METEOROLÓGICAS"
echo "════════════════════════════════════════════════════════════"
echo ""

# Crear directorio de resultados
mkdir -p ~/ns-3-dev/objetivo3_resultados/escenario1_meteorologico

# Parámetros fijos
SF=7
NODES=50
TIME=3600

# ========== ARQUITECTURA TRADICIONAL ==========
echo "▶ TRADICIONAL - Condiciones Ideales (0 dB)"
./ns3 run "salinas-traditional --sf=${SF} --nDevices=${NODES} --simTime=${TIME} --weatherLoss=0"
mv resultados_tradicional_3gw.csv objetivo3_resultados/escenario1_meteorologico/tradicional_weather0.csv
mv cobertura_tradicional_3gw.csv objetivo3_resultados/escenario1_meteorologico/cobertura_trad_weather0.csv

echo ""
echo "▶ TRADICIONAL - Condiciones Moderadas (5 dB)"
./ns3 run "salinas-traditional --sf=${SF} --nDevices=${NODES} --simTime=${TIME} --weatherLoss=5"
mv resultados_tradicional_3gw.csv objetivo3_resultados/escenario1_meteorologico/tradicional_weather5.csv
mv cobertura_tradicional_3gw.csv objetivo3_resultados/escenario1_meteorologico/cobertura_trad_weather5.csv

echo ""
echo "▶ TRADICIONAL - Condiciones Severas (10 dB)"
./ns3 run "salinas-traditional --sf=${SF} --nDevices=${NODES} --simTime=${TIME} --weatherLoss=10"
mv resultados_tradicional_3gw.csv objetivo3_resultados/escenario1_meteorologico/tradicional_weather10.csv
mv cobertura_tradicional_3gw.csv objetivo3_resultados/escenario1_meteorologico/cobertura_trad_weather10.csv

echo ""
echo "════════════════════════════════════════════════════════════"

# ========== ARQUITECTURA MÓVIL CON P2P ==========
echo "▶ MÓVIL + P2P - Condiciones Ideales (0 dB)"
./ns3 run "salinas-mobile-3gw --sf=${SF} --nDevices=${NODES} --simTime=${TIME} --weatherLoss=0 --enableP2P=true"
mv resultados_salinas_movil_3gw_p2p.csv objetivo3_resultados/escenario1_meteorologico/movil_p2p_weather0.csv
mv cobertura_salinas_movil_3gw.csv objetivo3_resultados/escenario1_meteorologico/cobertura_movil_weather0.csv

echo ""
echo "▶ MÓVIL + P2P - Condiciones Moderadas (5 dB)"
./ns3 run "salinas-mobile-3gw --sf=${SF} --nDevices=${NODES} --simTime=${TIME} --weatherLoss=5 --enableP2P=true"
mv resultados_salinas_movil_3gw_p2p.csv objetivo3_resultados/escenario1_meteorologico/movil_p2p_weather5.csv
mv cobertura_salinas_movil_3gw.csv objetivo3_resultados/escenario1_meteorologico/cobertura_movil_weather5.csv

echo ""
echo "▶ MÓVIL + P2P - Condiciones Severas (10 dB)"
./ns3 run "salinas-mobile-3gw --sf=${SF} --nDevices=${NODES} --simTime=${TIME} --weatherLoss=10 --enableP2P=true"
mv resultados_salinas_movil_3gw_p2p.csv objetivo3_resultados/escenario1_meteorologico/movil_p2p_weather10.csv
mv cobertura_salinas_movil_3gw.csv objetivo3_resultados/escenario1_meteorologico/cobertura_movil_weather10.csv

echo ""
echo "════════════════════════════════════════════════════════════"
echo "✅ ESCENARIO 1 COMPLETADO"
echo "📁 Resultados en: objetivo3_resultados/escenario1_meteorologico/"
echo "════════════════════════════════════════════════════════════"
