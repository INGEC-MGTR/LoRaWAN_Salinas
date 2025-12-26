#!/bin/bash
# OBJETIVO 3 - ESCENARIO 2: Densidad Variable de Embarcaciones
# Evalúa escalabilidad con diferentes números de nodos

echo "════════════════════════════════════════════════════════════"
echo "  OBJETIVO 3 - ESCENARIO 2: DENSIDAD VARIABLE"
echo "════════════════════════════════════════════════════════════"
echo ""

# Crear directorio de resultados
mkdir -p ~/ns-3-dev/objetivo3_resultados/escenario2_densidad

# Parámetros fijos
SF=7
TIME=3600
WEATHER=0

# ========== ARQUITECTURA TRADICIONAL ==========
echo "▶ TRADICIONAL - 50 embarcaciones"
./ns3 run "salinas-traditional --sf=${SF} --nDevices=50 --simTime=${TIME} --weatherLoss=${WEATHER}"
mv resultados_tradicional_3gw.csv objetivo3_resultados/escenario2_densidad/tradicional_nodes50.csv
mv cobertura_tradicional_3gw.csv objetivo3_resultados/escenario2_densidad/cobertura_trad_nodes50.csv

echo ""
echo "▶ TRADICIONAL - 75 embarcaciones"
./ns3 run "salinas-traditional --sf=${SF} --nDevices=75 --simTime=${TIME} --weatherLoss=${WEATHER}"
mv resultados_tradicional_3gw.csv objetivo3_resultados/escenario2_densidad/tradicional_nodes75.csv
mv cobertura_tradicional_3gw.csv objetivo3_resultados/escenario2_densidad/cobertura_trad_nodes75.csv

echo ""
echo "▶ TRADICIONAL - 100 embarcaciones"
./ns3 run "salinas-traditional --sf=${SF} --nDevices=100 --simTime=${TIME} --weatherLoss=${WEATHER}"
mv resultados_tradicional_3gw.csv objetivo3_resultados/escenario2_densidad/tradicional_nodes100.csv
mv cobertura_tradicional_3gw.csv objetivo3_resultados/escenario2_densidad/cobertura_trad_nodes100.csv

echo ""
echo "════════════════════════════════════════════════════════════"

# ========== ARQUITECTURA MÓVIL CON P2P ==========
echo "▶ MÓVIL + P2P - 50 embarcaciones"
./ns3 run "salinas-mobile-3gw --sf=${SF} --nDevices=50 --simTime=${TIME} --weatherLoss=${WEATHER} --enableP2P=true"
mv resultados_salinas_movil_3gw_p2p.csv objetivo3_resultados/escenario2_densidad/movil_p2p_nodes50.csv
mv cobertura_salinas_movil_3gw.csv objetivo3_resultados/escenario2_densidad/cobertura_movil_nodes50.csv

echo ""
echo "▶ MÓVIL + P2P - 75 embarcaciones"
./ns3 run "salinas-mobile-3gw --sf=${SF} --nDevices=75 --simTime=${TIME} --weatherLoss=${WEATHER} --enableP2P=true"
mv resultados_salinas_movil_3gw_p2p.csv objetivo3_resultados/escenario2_densidad/movil_p2p_nodes75.csv
mv cobertura_salinas_movil_3gw.csv objetivo3_resultados/escenario2_densidad/cobertura_movil_nodes75.csv

echo ""
echo "▶ MÓVIL + P2P - 100 embarcaciones"
./ns3 run "salinas-mobile-3gw --sf=${SF} --nDevices=100 --simTime=${TIME} --weatherLoss=${WEATHER} --enableP2P=true"
mv resultados_salinas_movil_3gw_p2p.csv objetivo3_resultados/escenario2_densidad/movil_p2p_nodes100.csv
mv cobertura_salinas_movil_3gw.csv objetivo3_resultados/escenario2_densidad/cobertura_movil_nodes100.csv

echo ""
echo "════════════════════════════════════════════════════════════"
echo "✅ ESCENARIO 2 COMPLETADO"
echo "📁 Resultados en: objetivo3_resultados/escenario2_densidad/"
echo "════════════════════════════════════════════════════════════"
