#!/bin/bash
# Script Completo para Subir LoRaWAN_Tesis a GitHub
# Incluye TODOS los archivos (código + resultados + animaciones)
# Usa Git LFS para archivos grandes

echo "════════════════════════════════════════════════════════════"
echo "  SUBIR PROYECTO COMPLETO LoRaWAN_Tesis A GITHUB"
echo "  (Incluye archivos grandes con Git LFS)"
echo "════════════════════════════════════════════════════════════"
echo ""

# Colores
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m'

function ask() {
    while true; do
        read -p "$1 (s/n): " yn
        case $yn in
            [Ss]* ) return 0;;
            [Nn]* ) return 1;;
            * ) echo "Responde s o n.";;
        esac
    done
}

# Variables
PROJECT_DIR="/home/ingec/ns-3-dev/LoRaWAN_Tesis"

echo -e "${YELLOW}PASO 1: Verificar directorio del proyecto${NC}"
if [ ! -d "$PROJECT_DIR" ]; then
    echo -e "${RED}ERROR: No existe $PROJECT_DIR${NC}"
    exit 1
fi
cd "$PROJECT_DIR" || exit 1
echo -e "${GREEN}✓ Directorio: $PROJECT_DIR${NC}"
echo ""

# Mostrar estadísticas
echo -e "${BLUE}📊 Estadísticas del proyecto:${NC}"
echo "  Archivos: $(find . -type f | wc -l)"
echo "  Carpetas: $(find . -type d | wc -l)"
echo "  Tamaño total: $(du -sh . | cut -f1)"
echo ""

# Mostrar archivos grandes
echo -e "${YELLOW}Archivos grandes detectados (>10MB):${NC}"
find . -type f -size +10M -exec ls -lh {} \; | awk '{print "  " $9 " (" $5 ")"}'
echo ""

echo -e "${YELLOW}PASO 2: Instalar Git y Git LFS${NC}"

# Verificar Git
if ! command -v git &> /dev/null; then
    echo "Instalando Git..."
    sudo apt-get update
    sudo apt-get install -y git
fi
echo -e "${GREEN}✓ Git: $(git --version)${NC}"

# Verificar Git LFS
if ! command -v git-lfs &> /dev/null; then
    echo ""
    echo -e "${YELLOW}Git LFS no está instalado.${NC}"
    echo "Git LFS es necesario para archivos grandes (>50MB)."
    echo ""
    if ask "¿Instalar Git LFS ahora?"; then
        echo "Instalando Git LFS..."
        sudo apt-get install -y git-lfs
        git lfs install
        echo -e "${GREEN}✓ Git LFS instalado${NC}"
    else
        echo -e "${RED}ADVERTENCIA: Sin Git LFS, archivos >100MB fallarán${NC}"
    fi
else
    echo -e "${GREEN}✓ Git LFS: $(git lfs version)${NC}"
    git lfs install
fi
echo ""

echo -e "${YELLOW}PASO 3: Configurar Git${NC}"
CURRENT_NAME=$(git config --global user.name 2>/dev/null)
CURRENT_EMAIL=$(git config --global user.email 2>/dev/null)

if [ -z "$CURRENT_NAME" ]; then
    read -p "Tu nombre completo: " git_name
    git config --global user.name "$git_name"
else
    echo "Nombre: $CURRENT_NAME"
fi

if [ -z "$CURRENT_EMAIL" ]; then
    read -p "Tu email: " git_email
    git config --global user.email "$git_email"
else
    echo "Email: $CURRENT_EMAIL"
fi
echo -e "${GREEN}✓ Git configurado${NC}"
echo ""

echo -e "${YELLOW}PASO 4: Crear archivos de configuración${NC}"

# Crear README.md
cat > README.md << 'EOF'
# Arquitecturas LoRaWAN para Emergencias Marítimas

## 📋 Descripción
Simulación NS-3 de arquitecturas LoRaWAN para comunicaciones de emergencia marítima en Salinas, Ecuador.

**Autora:** Ing. Erika Michelle Chiriguayo Rodríguez  
**Institución:** UPSE - Maestría en Telecomunicaciones

## 📂 Estructura del Proyecto

```
LoRaWAN_Tesis/
├── Resultados Ob1/              # Objetivo 1: Diseño y modelado
│   ├── Animacion_gif/           # Animaciones de red
│   ├── Resultados_Movil_10gw/   # Resultados 10 gateways móviles
│   ├── Resultados_mòvil_3gw/    # Resultados 3 gateways móviles
│   ├── Resultados_tradicional_3gw/  # Arquitectura tradicional
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

## 🚀 Archivos de Simulación

- `salinas-traditional_original.cc` - Arquitectura tradicional (gateways fijos)
- `salinas-mobile-3gw_original.cc` - 3 gateways móviles + P2P
- `salinas-mobile-10gw-p2p.cc` - 10 gateways móviles
- `validacion_simulacion_objetivo2.sh` - Script de validación

## 📊 Resultados Principales

- **PDR Móvil**: 99.20% vs Tradicional: 97.71% (+1.49%)
- **Cobertura**: 100% vs ~95% (+5%)
- **Resiliencia**: Móvil tolera 66% fallos, Tradicional 0%

## 🛠️ Uso

```bash
# Compilar en NS-3
./ns3 run "salinas-mobile-3gw_original --nDevices=50 --simTime=3600"
```

## 📧 Contacto
e.chiriguarodrigue@upse.edu.ec
EOF

echo -e "${GREEN}✓ README.md creado${NC}"

# Crear .gitignore MÍNIMO (para subir TODO)
cat > .gitignore << 'EOF'
# Solo excluir archivos del sistema y temporales
.DS_Store
Thumbs.db
*.swp
*.swo
*~
~$*

# Build de NS-3
.waf-*
.lock-waf*

# Backups
*.bak
*.backup
EOF

echo -e "${GREEN}✓ .gitignore creado (mínimo para subir todo)${NC}"

# Crear .gitattributes para Git LFS
cat > .gitattributes << 'EOF'
# Git LFS - Archivos grandes
*.xml filter=lfs diff=lfs merge=lfs -text
*.csv filter=lfs diff=lfs merge=lfs -text
*.png filter=lfs diff=lfs merge=lfs -text
*.jpg filter=lfs diff=lfs merge=lfs -text
*.pdf filter=lfs diff=lfs merge=lfs -text
EOF

echo -e "${GREEN}✓ .gitattributes creado (LFS para archivos grandes)${NC}"
echo ""

echo -e "${YELLOW}PASO 5: Inicializar Git y Git LFS${NC}"

# Eliminar .git si existe
if [ -d ".git" ]; then
    if ask "¿Repositorio Git existente detectado. Reiniciar?"; then
        rm -rf .git
    fi
fi

git init
echo -e "${GREEN}✓ Repositorio Git inicializado${NC}"

# Configurar Git LFS para archivos grandes
if command -v git-lfs &> /dev/null; then
    echo ""
    echo "Configurando Git LFS para archivos grandes..."
    git lfs track "*.xml"
    git lfs track "*.csv"
    git lfs track "*.png" 
    git lfs track "*.jpg"
    git lfs track "*.pdf"
    echo -e "${GREEN}✓ Git LFS configurado${NC}"
fi
echo ""

echo -e "${YELLOW}PASO 6: Agregar todos los archivos${NC}"
echo "Esto puede tomar varios minutos..."
echo ""

git add .gitattributes
git add .gitignore
git add README.md
git add .

echo ""
echo -e "${BLUE}Resumen de archivos a subir:${NC}"
git status --short | head -20
echo "..."
TOTAL_FILES=$(git status --short | wc -l)
echo "Total: $TOTAL_FILES archivos"
echo ""

if ! ask "¿Continuar con estos archivos?"; then
    echo "Cancelado"
    exit 0
fi

echo -e "${YELLOW}PASO 7: Crear commit inicial${NC}"

git commit -m "Initial commit: Proyecto completo LoRaWAN Tesis

Incluye:
- Código de simulaciones NS-3 (3 arquitecturas)
- Resultados completos Objetivos 1, 2 y 3
- Animaciones NetAnim (XML con Git LFS)
- Scripts de análisis y validación
- Documentación completa

Archivos grandes manejados con Git LFS"

if [ $? -eq 0 ]; then
    echo -e "${GREEN}✓ Commit creado${NC}"
else
    echo -e "${RED}ERROR al crear commit${NC}"
    exit 1
fi
echo ""

echo -e "${YELLOW}PASO 8: Conectar con GitHub${NC}"
echo ""
echo "════════════════════════════════════════════════════════════"
echo "  CREAR REPOSITORIO EN GITHUB"
echo "════════════════════════════════════════════════════════════"
echo ""
echo "1. Abre: https://github.com/new"
echo "2. Repository name: LoRaWAN-Maritime-Emergency-NS3"
echo "3. Description: NS-3 Simulation of LoRaWAN Mobile Gateway"
echo "   Architectures for Maritime Emergency Communications"
echo "4. Selecciona: ○ Public  ○ Private"
echo "5. NO marques: README, .gitignore, License"
echo "6. Clic 'Create repository'"
echo "7. COPIA la URL que aparece"
echo ""

if ask "¿Ya creaste el repositorio en GitHub?"; then
    read -p "Pega la URL del repositorio: " REPO_URL
    REPO_URL=$(echo "$REPO_URL" | xargs)
    
    if git remote | grep -q "origin"; then
        git remote set-url origin "$REPO_URL"
    else
        git remote add origin "$REPO_URL"
    fi
    
    echo -e "${GREEN}✓ Repositorio remoto configurado${NC}"
    echo ""
    
    echo -e "${YELLOW}PASO 9: Obtener Personal Access Token${NC}"
    echo ""
    echo "════════════════════════════════════════════════════════════"
    echo "  CREAR PERSONAL ACCESS TOKEN (PAT)"
    echo "════════════════════════════════════════════════════════════"
    echo ""
    echo "GitHub NO acepta contraseñas desde 2021."
    echo "Necesitas un Personal Access Token:"
    echo ""
    echo "1. Ve a: https://github.com/settings/tokens"
    echo "2. Click 'Generate new token' → 'Classic'"
    echo "3. Note: 'Token para LoRaWAN Tesis'"
    echo "4. Expiration: 90 days"
    echo "5. Select scopes: ☑ repo (marca todo repo)"
    echo "6. Click 'Generate token'"
    echo "7. COPIA el token (ghp_...)"
    echo "   ⚠️  NO LO VERÁS DE NUEVO"
    echo ""
    echo "Al hacer push, GitHub pedirá:"
    echo "  Username: tu-usuario-github"
    echo "  Password: pega-aquí-tu-token"
    echo ""
    
    if ask "¿Ya tienes tu token listo?"; then
        echo ""
        echo -e "${YELLOW}PASO 10: Subir a GitHub${NC}"
        echo ""
        
        git branch -M main
        
        echo "════════════════════════════════════════════════════════════"
        echo "  SUBIENDO ARCHIVOS A GITHUB..."
        echo "  Esto puede tardar varios minutos debido al tamaño"
        echo "════════════════════════════════════════════════════════════"
        echo ""
        
        git push -u origin main
        
        if [ $? -eq 0 ]; then
            echo ""
            echo "════════════════════════════════════════════════════════════"
            echo -e "${GREEN}  ✓✓✓ PROYECTO SUBIDO EXITOSAMENTE ✓✓✓${NC}"
            echo "════════════════════════════════════════════════════════════"
            echo ""
            echo "🌐 Tu repositorio está en:"
            echo "   ${REPO_URL%.git}"
            echo ""
            echo "📊 Archivos subidos: $TOTAL_FILES"
            echo "💾 Tamaño: $(du -sh . | cut -f1)"
            echo ""
            echo "📁 Archivos LFS (grandes):"
            git lfs ls-files 2>/dev/null | head -5
            echo ""
        else
            echo ""
            echo -e "${RED}ERROR al subir${NC}"
            echo ""
            echo "Posibles causas:"
            echo "  • Token inválido"
            echo "  • Sin permisos repo"
            echo "  • Problema de red"
            echo ""
            echo "Intenta:"
            echo "  git push -u origin main"
        fi
    else
        echo ""
        echo "Cuando tengas el token:"
        echo "  cd $PROJECT_DIR"
        echo "  git branch -M main"
        echo "  git push -u origin main"
    fi
else
    echo ""
    echo "Cuando hayas creado el repositorio:"
    echo "  cd $PROJECT_DIR"
    echo "  git remote add origin <URL>"
    echo "  git branch -M main"
    echo "  git push -u origin main"
fi

echo ""
echo "════════════════════════════════════════════════════════════"
echo "  PROCESO COMPLETADO"
echo "════════════════════════════════════════════════════════════"
