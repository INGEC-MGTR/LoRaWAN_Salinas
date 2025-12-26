#!/bin/bash
##############################################################################
# SCRIPT CORREGIDO - OBJETIVO 2
# Comparación: Tradicional vs Móvil con variación de SF y Potencia
##############################################################################

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

BASE_DIR="$HOME/ns-3-dev"
RESULTADOS_DIR="$BASE_DIR/resultados_objetivo2_corregido"
LOG_FILE="$RESULTADOS_DIR/simulaciones_log.txt"

mkdir -p "$RESULTADOS_DIR"

log_mensaje() {
    echo -e "${BLUE}[$(date '+%Y-%m-%d %H:%M:%S')]${NC} $1" | tee -a "$LOG_FILE"
}

log_exito() {
    echo -e "${GREEN}[$(date '+%Y-%m-%d %H:%M:%S')] ✅ $1${NC}" | tee -a "$LOG_FILE"
}

log_error() {
    echo -e "${RED}[$(date '+%Y-%m-%d %H:%M:%S')] ❌ $1${NC}" | tee -a "$LOG_FILE"
}

log_advertencia() {
    echo -e "${YELLOW}[$(date '+%Y-%m-%d %H:%M:%S')] ⚠️  $1${NC}" | tee -a "$LOG_FILE"
}

clear
echo "╔════════════════════════════════════════════════════════════════╗"
echo "║           OBJETIVO 2: VALIDACIÓN ALGORITMOS P2P                ║"
echo "║     Comparación: Tradicional vs Móvil (SF y Potencia)         ║"
echo "╚════════════════════════════════════════════════════════════════╝"
echo ""
log_mensaje "Iniciando simulaciones del Objetivo 2 (CORREGIDO)"
log_mensaje "Potencias válidas: 8, 14, 16 dBm"
log_mensaje "Spreading Factors: SF7, SF9, SF12"
echo ""

cd "$BASE_DIR" || { log_error "No se pudo acceder a $BASE_DIR"; exit 1; }

TOTAL_SIMS=18
COMPLETADAS=0
FALLIDAS=0

ejecutar_simulacion() {
    local NUM=$1
    local ARQUITECTURA=$2
    local SCRIPT=$3
    local SF=$4
    local TX_POWER=$5
    local NOMBRE_SALIDA=$6
    local ENABLE_P2P=$7
    
    echo ""
    echo "════════════════════════════════════════════════════════════════"
    log_mensaje "Simulación $NUM/$TOTAL_SIMS: $NOMBRE_SALIDA"
    log_mensaje "  Arquitectura: $ARQUITECTURA"
    log_mensaje "  SF: $SF | Potencia: ${TX_POWER} dBm | P2P: $ENABLE_P2P"
    echo "════════════════════════════════════════════════════════════════"
    
    local CMD="./ns3 run \"$SCRIPT --sf=$SF --txPower=$TX_POWER --simTime=3600 --enableP2P=$ENABLE_P2P\""
    
    log_mensaje "Ejecutando: $CMD"
    
    eval $CMD
    
    local EXIT_CODE=$?
    
    if [ $EXIT_CODE -eq 0 ]; then
        log_exito "Simulación completada exitosamente"
        
        # Renombrar archivos según arquitectura
        if [[ "$SCRIPT" == "salinas-traditional" ]]; then
            if [ -f "resultados_tradicional_3gw.csv" ]; then
                mv "resultados_tradicional_3gw.csv" "$RESULTADOS_DIR/${NOMBRE_SALIDA}_resultados.csv"
                log_exito "Archivo renombrado: ${NOMBRE_SALIDA}_resultados.csv"
            fi
            if [ -f "cobertura_tradicional_3gw.csv" ]; then
                mv "cobertura_tradicional_3gw.csv" "$RESULTADOS_DIR/${NOMBRE_SALIDA}_cobertura.csv"
            fi
        elif [[ "$SCRIPT" == "salinas-mobile-3gw" ]]; then
            if [ -f "resultados_salinas_movil_3gw_p2p.csv" ]; then
                mv "resultados_salinas_movil_3gw_p2p.csv" "$RESULTADOS_DIR/${NOMBRE_SALIDA}_resultados.csv"
                log_exito "Archivo renombrado: ${NOMBRE_SALIDA}_resultados.csv"
            fi
            if [ -f "cobertura_salinas_movil_3gw.csv" ]; then
                mv "cobertura_salinas_movil_3gw.csv" "$RESULTADOS_DIR/${NOMBRE_SALIDA}_cobertura.csv"
            fi
        fi
        
        ((COMPLETADAS++))
    else
        log_error "Simulación falló con código de error: $EXIT_CODE"
        ((FALLIDAS++))
    fi
    
    local PROGRESO=$((($COMPLETADAS * 100) / $TOTAL_SIMS))
    echo ""
    log_mensaje "Progreso: $COMPLETADAS/$TOTAL_SIMS completadas ($PROGRESO%)"
    echo ""
    
    sleep 2
}

# ═══════════════════════════════════════════════════════════════════════════
# GRUPO 1: TRADICIONAL 3 GW - SF7
# ═══════════════════════════════════════════════════════════════════════════
echo ""
echo "╔════════════════════════════════════════════════════════════════╗"
echo "║  GRUPO 1: Tradicional 3 GW - SF7 variación de potencia        ║"
echo "╚════════════════════════════════════════════════════════════════╝"

log_advertencia "Simulación 1 (SF7, 14dBm) ya ejecutada en Objetivo 1 - OMITIDA"
((COMPLETADAS++))

ejecutar_simulacion 2 "Tradicional 3 GW" "salinas-traditional" 7 8 "tradicional_3gw_sf7_tx8" "false"
ejecutar_simulacion 3 "Tradicional 3 GW" "salinas-traditional" 7 16 "tradicional_3gw_sf7_tx16" "false"

# ═══════════════════════════════════════════════════════════════════════════
# GRUPO 2: TRADICIONAL 3 GW - SF9
# ═══════════════════════════════════════════════════════════════════════════
echo ""
echo "╔════════════════════════════════════════════════════════════════╗"
echo "║  GRUPO 2: Tradicional 3 GW - SF9 variación de potencia        ║"
echo "╚════════════════════════════════════════════════════════════════╝"

ejecutar_simulacion 4 "Tradicional 3 GW" "salinas-traditional" 9 8 "tradicional_3gw_sf9_tx8" "false"
ejecutar_simulacion 5 "Tradicional 3 GW" "salinas-traditional" 9 14 "tradicional_3gw_sf9_tx14" "false"
ejecutar_simulacion 6 "Tradicional 3 GW" "salinas-traditional" 9 16 "tradicional_3gw_sf9_tx16" "false"

# ═══════════════════════════════════════════════════════════════════════════
# GRUPO 3: TRADICIONAL 3 GW - SF12
# ═══════════════════════════════════════════════════════════════════════════
echo ""
echo "╔════════════════════════════════════════════════════════════════╗"
echo "║  GRUPO 3: Tradicional 3 GW - SF12 variación de potencia       ║"
echo "╚════════════════════════════════════════════════════════════════╝"

ejecutar_simulacion 7 "Tradicional 3 GW" "salinas-traditional" 12 8 "tradicional_3gw_sf12_tx8" "false"
ejecutar_simulacion 8 "Tradicional 3 GW" "salinas-traditional" 12 14 "tradicional_3gw_sf12_tx14" "false"
ejecutar_simulacion 9 "Tradicional 3 GW" "salinas-traditional" 12 16 "tradicional_3gw_sf12_tx16" "false"

# ═══════════════════════════════════════════════════════════════════════════
# GRUPO 4: MÓVIL 3 GW + P2P - SF7
# ═══════════════════════════════════════════════════════════════════════════
echo ""
echo "╔════════════════════════════════════════════════════════════════╗"
echo "║  GRUPO 4: Móvil 3 GW + P2P - SF7 variación de potencia        ║"
echo "╚════════════════════════════════════════════════════════════════╝"

log_advertencia "Simulación 10 (SF7, 14dBm) ya ejecutada en Objetivo 1 - OMITIDA"
((COMPLETADAS++))

ejecutar_simulacion 11 "Móvil 3 GW + P2P" "salinas-mobile-3gw" 7 8 "movil_3gw_p2p_sf7_tx8" "true"
ejecutar_simulacion 12 "Móvil 3 GW + P2P" "salinas-mobile-3gw" 7 16 "movil_3gw_p2p_sf7_tx16" "true"

# ═══════════════════════════════════════════════════════════════════════════
# GRUPO 5: MÓVIL 3 GW + P2P - SF9
# ═══════════════════════════════════════════════════════════════════════════
echo ""
echo "╔════════════════════════════════════════════════════════════════╗"
echo "║  GRUPO 5: Móvil 3 GW + P2P - SF9 variación de potencia        ║"
echo "╚════════════════════════════════════════════════════════════════╝"

ejecutar_simulacion 13 "Móvil 3 GW + P2P" "salinas-mobile-3gw" 9 8 "movil_3gw_p2p_sf9_tx8" "true"

log_advertencia "Simulación 14 (SF9, 14dBm) ya ejecutada - OMITIDA"
((COMPLETADAS++))

ejecutar_simulacion 15 "Móvil 3 GW + P2P" "salinas-mobile-3gw" 9 16 "movil_3gw_p2p_sf9_tx16" "true"

# ═══════════════════════════════════════════════════════════════════════════
# GRUPO 6: MÓVIL 3 GW + P2P - SF12
# ═══════════════════════════════════════════════════════════════════════════
echo ""
echo "╔════════════════════════════════════════════════════════════════╗"
echo "║  GRUPO 6: Móvil 3 GW + P2P - SF12 variación de potencia       ║"
echo "╚════════════════════════════════════════════════════════════════╝"

ejecutar_simulacion 16 "Móvil 3 GW + P2P" "salinas-mobile-3gw" 12 8 "movil_3gw_p2p_sf12_tx8" "true"

log_advertencia "Simulación 17 (SF12, 14dBm) ya ejecutada - OMITIDA"
((COMPLETADAS++))

ejecutar_simulacion 18 "Móvil 3 GW + P2P" "salinas-mobile-3gw" 12 16 "movil_3gw_p2p_sf12_tx16" "true"

# ═══════════════════════════════════════════════════════════════════════════
# RESUMEN FINAL
# ═══════════════════════════════════════════════════════════════════════════
echo ""
echo "╔════════════════════════════════════════════════════════════════╗"
echo "║                    RESUMEN DE SIMULACIONES                     ║"
echo "╚════════════════════════════════════════════════════════════════╝"
echo ""

log_mensaje "════════════════════════════════════════════════════════════"
log_exito "Total de simulaciones completadas: $COMPLETADAS/$TOTAL_SIMS"
if [ $FALLIDAS -gt 0 ]; then
    log_error "Simulaciones fallidas: $FALLIDAS"
fi
log_mensaje "════════════════════════════════════════════════════════════"

echo ""
log_mensaje "Archivos de resultados guardados en: $RESULTADOS_DIR"
echo ""
log_mensaje "Listado de archivos generados:"
ls -lh "$RESULTADOS_DIR"/*.csv 2>/dev/null | awk '{print "  " $9 " (" $5 ")"}'

echo ""
if [ $COMPLETADAS -eq $TOTAL_SIMS ]; then
    log_exito "¡TODAS LAS SIMULACIONES COMPLETADAS EXITOSAMENTE!"
    echo ""
    log_mensaje "Siguiente paso: Ejecutar análisis de resultados"
    log_mensaje "Comando: python3 analizar_objetivo2.py"
else
    log_advertencia "Algunas simulaciones no se completaron correctamente"
    log_mensaje "Revisa el log en: $LOG_FILE"
fi

echo ""
log_mensaje "Script finalizado"
echo ""
