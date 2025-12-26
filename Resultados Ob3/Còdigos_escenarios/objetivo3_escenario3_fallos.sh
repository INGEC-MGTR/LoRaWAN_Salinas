#!/bin/bash
# OBJETIVO 3 - ESCENARIO 3: Fallos de Equipamiento (Gateways)
# Evalúa tolerancia a fallos variando número de GW activos

echo "════════════════════════════════════════════════════════════"
echo "  OBJETIVO 3 - ESCENARIO 3: FALLOS DE EQUIPAMIENTO"
echo "════════════════════════════════════════════════════════════"
echo ""

# Crear directorio de resultados
mkdir -p ~/ns-3-dev/objetivo3_resultados/escenario3_fallos

# Parámetros fijos
SF=7
NODES=50
TIME=3600
WEATHER=0

# ========== ARQUITECTURA TRADICIONAL ==========
echo "▶ TRADICIONAL - 3 GW activos (100% operacional)"
./ns3 run "salinas-traditional --sf=${SF} --nDevices=${NODES} --nGateways=3 --simTime=${TIME} --weatherLoss=${WEATHER}"
mv resultados_tradicional_3gw.csv objetivo3_resultados/escenario3_fallos/tradicional_gw3.csv
mv cobertura_tradicional_3gw.csv objetivo3_resultados/escenario3_fallos/cobertura_trad_gw3.csv

echo ""
echo "▶ TRADICIONAL - 2 GW activos (fallo 1 GW - 66%)"
./ns3 run "salinas-traditional --sf=${SF} --nDevices=${NODES} --nGateways=2 --simTime=${TIME} --weatherLoss=${WEATHER}"
mv resultados_tradicional_3gw.csv objetivo3_resultados/escenario3_fallos/tradicional_gw2.csv
mv cobertura_tradicional_3gw.csv objetivo3_resultados/escenario3_fallos/cobertura_trad_gw2.csv

echo ""
echo "▶ TRADICIONAL - 1 GW activo (fallo 2 GW - 33%)"
./ns3 run "salinas-traditional --sf=${SF} --nDevices=${NODES} --nGateways=1 --simTime=${TIME} --weatherLoss=${WEATHER}"
mv resultados_tradicional_3gw.csv objetivo3_resultados/escenario3_fallos/tradicional_gw1.csv
mv cobertura_tradicional_3gw.csv objetivo3_resultados/escenario3_fallos/cobertura_trad_gw1.csv

echo ""
echo "════════════════════════════════════════════════════════════"

# ========== ARQUITECTURA MÓVIL CON P2P ==========
echo "▶ MÓVIL + P2P - 3 GW activos (100% operacional)"
./ns3 run "salinas-mobile-3gw --sf=${SF} --nDevices=${NODES} --nGateways=3 --simTime=${TIME} --weatherLoss=${WEATHER} --enableP2P=true"
mv resultados_salinas_movil_3gw_p2p.csv objetivo3_resultados/escenario3_fallos/movil_p2p_gw3.csv
mv cobertura_salinas_movil_3gw.csv objetivo3_resultados/escenario3_fallos/cobertura_movil_gw3.csv

echo ""
echo "▶ MÓVIL + P2P - 2 GW activos (fallo 1 GW - 66%)"
./ns3 run "salinas-mobile-3gw --sf=${SF} --nDevices=${NODES} --nGateways=2 --simTime=${TIME} --weatherLoss=${WEATHER} --enableP2P=true"
mv resultados_salinas_movil_3gw_p2p.csv objetivo3_resultados/escenario3_fallos/movil_p2p_gw2.csv
mv cobertura_salinas_movil_3gw.csv objetivo3_resultados/escenario3_fallos/cobertura_movil_gw2.csv

echo ""
echo "▶ MÓVIL + P2P - 1 GW activo (fallo 2 GW - 33%)"
./ns3 run "salinas-mobile-3gw --sf=${SF} --nDevices=${NODES} --nGateways=1 --simTime=${TIME} --weatherLoss=${WEATHER} --enableP2P=true"
mv resultados_salinas_movil_3gw_p2p.csv objetivo3_resultados/escenario3_fallos/movil_p2p_gw1.csv
mv cobertura_salinas_movil_3gw.csv objetivo3_resultados/escenario3_fallos/cobertura_movil_gw1.csv

echo ""
echo "════════════════════════════════════════════════════════════"
echo "✅ ESCENARIO 3 COMPLETADO"
echo "📁 Resultados en: objetivo3_resultados/escenario3_fallos/"
echo "════════════════════════════════════════════════════════════"
