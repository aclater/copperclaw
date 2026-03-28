#!/usr/bin/env bash
# OPERATION COPPERCLAW — Platform-aware start script
# COSMIC INDIGO // REL KESTREL COALITION // EXERCISE
#
# Detects OS and GPU, runs pre-flight checks, writes a compose override,
# then starts the stack.
#
# Supported platforms:
#   macOS Apple Silicon  — RamaLama via Metal/MLX
#   macOS Intel          — CPU only (recommend LLM_BACKEND=anthropic)
#   Linux NVIDIA         — CUDA (default compose, no override needed)
#   Linux AMD            — ROCm via /dev/kfd + /dev/dri
#   Linux CPU only       — No GPU (recommend LLM_BACKEND=anthropic)

set -euo pipefail

OVERRIDE_FILE=".compose.platform-override.yml"
PREFLIGHT_ERRORS=0
PREFLIGHT_WARNINGS=0

# ---------------------------------------------------------------------------
# Output helpers
# ---------------------------------------------------------------------------
red='\033[0;31m'
yellow='\033[0;33m'
green='\033[0;32m'
bold='\033[1m'
nc='\033[0m'

info()  { echo -e "  ${bold}[CHECK]${nc}  $*"; }
ok()    { echo -e "  ${green}[OK]${nc}     $*"; }
warn()  { echo -e "  ${yellow}[WARN]${nc}   $*"; ((PREFLIGHT_WARNINGS++)); }
err()   { echo -e "  ${red}[ERROR]${nc}  $*"; ((PREFLIGHT_ERRORS++)); }
fatal() { echo -e "\n  ${red}${bold}FATAL:${nc} $*\n"; exit 1; }

# ---------------------------------------------------------------------------
# Pre-flight checks
# ---------------------------------------------------------------------------
preflight() {
    echo ""
    echo -e "${bold}Pre-flight checks${nc}"
    echo "  ----------------------------------------"

    # --- Container runtime ---
    info "Container runtime"
    if command -v podman-compose &>/dev/null; then
        COMPOSE_CMD="podman-compose"
        ok "podman-compose found: $(podman-compose --version 2>&1 | head -1)"
    elif command -v docker &>/dev/null && docker compose version &>/dev/null 2>&1; then
        COMPOSE_CMD="docker compose"
        ok "docker compose found: $(docker compose version --short 2>/dev/null || echo 'ok')"
    elif command -v docker-compose &>/dev/null; then
        COMPOSE_CMD="docker-compose"
        ok "docker-compose found: $(docker-compose --version 2>&1 | head -1)"
    else
        err "No container runtime found."
        echo "       Install one of:"
        echo "         Linux : sudo dnf install podman podman-compose"
        echo "         macOS : brew install podman podman-compose  (or Docker Desktop)"
        echo "         Win   : Install Docker Desktop"
        COMPOSE_CMD=""
    fi

    # --- Podman daemon / machine (macOS) ---
    if [ "$OS" = "Darwin" ] && [ -n "${COMPOSE_CMD:-}" ]; then
        info "Podman machine / Docker Desktop"
        if echo "$COMPOSE_CMD" | grep -q podman; then
            if ! podman info &>/dev/null 2>&1; then
                err "Podman machine is not running."
                echo "       Start it with:  podman machine start"
                echo "       Or switch to Docker Desktop."
            else
                ok "Podman machine is running"
            fi
        else
            if ! docker info &>/dev/null 2>&1; then
                err "Docker Desktop does not appear to be running. Start Docker Desktop."
            else
                ok "Docker Desktop is running"
            fi
        fi
    fi

    # --- Podman daemon (Linux) ---
    if [ "$OS" = "Linux" ] && echo "${COMPOSE_CMD:-}" | grep -q podman; then
        info "Podman socket"
        if ! podman info &>/dev/null 2>&1; then
            warn "Podman socket not responding. If using rootless Podman, run:"
            echo "         systemctl --user start podman.socket"
        else
            ok "Podman responding"
        fi
    fi

    # --- Java ---
    info "Java 21"
    if command -v java &>/dev/null; then
        JAVA_VER=$(java -version 2>&1 | awk -F '"' '/version/ {print $2}' | cut -d. -f1)
        if [ "${JAVA_VER:-0}" -ge 21 ] 2>/dev/null; then
            ok "Java $JAVA_VER"
        else
            warn "Java ${JAVA_VER:-unknown} found — Java 21+ required."
            echo "         Install: sdk install java 21  (via SDKMAN)"
            echo "                  brew install openjdk@21  (macOS)"
            echo "                  sudo dnf install java-21-openjdk-devel  (Fedora/RHEL)"
        fi
    else
        err "Java not found."
        echo "       Install: sdk install java 21  (via SDKMAN)"
        echo "                brew install openjdk@21  (macOS)"
        echo "                sudo dnf install java-21-openjdk-devel  (Fedora/RHEL)"
    fi

    # --- Maven ---
    info "Maven 3.9+"
    if command -v mvn &>/dev/null; then
        MVN_VER=$(mvn --version 2>&1 | awk '/Apache Maven/ {print $3}')
        ok "Maven $MVN_VER"
    else
        err "Maven not found."
        echo "       Install: sdk install maven  (via SDKMAN)"
        echo "                brew install maven  (macOS)"
        echo "                sudo dnf install maven  (Fedora/RHEL)"
    fi

    # --- Python ---
    info "Python 3.11+"
    PYTHON_CMD=""
    for cmd in python3.11 python3.12 python3.13 python3; do
        if command -v "$cmd" &>/dev/null; then
            PY_VER=$($cmd --version 2>&1 | awk '{print $2}')
            PY_MINOR=$(echo "$PY_VER" | cut -d. -f2)
            if [ "${PY_MINOR:-0}" -ge 11 ] 2>/dev/null; then
                PYTHON_CMD="$cmd"
                ok "Python $PY_VER ($cmd)"
                break
            fi
        fi
    done
    if [ -z "$PYTHON_CMD" ]; then
        warn "Python 3.11+ not found (needed for operator-service)."
        echo "         Install: brew install python@3.11  (macOS)"
        echo "                  sudo dnf install python3.11  (Fedora/RHEL)"
    fi

    # --- curl (used by smoke-test and health checks) ---
    info "curl"
    if command -v curl &>/dev/null; then
        ok "curl found"
    else
        warn "curl not found — smoke-test.sh will not work."
        echo "         Install: brew install curl  (macOS)"
        echo "                  sudo dnf install curl  (Fedora/RHEL)"
    fi

    # --- Built JARs ---
    info "Compiled services (Maven build)"
    MISSING_JARS=0
    for svc in isr-tasking collection allsource-analyst target-nomination \
               legal-review commander execution bda develop cot-gateway; do
        JAR_DIR="agents/${svc}-service/target"
        if ! ls "${JAR_DIR}"/*.jar &>/dev/null 2>&1; then
            MISSING_JARS=$((MISSING_JARS + 1))
        fi
    done
    for svc in state-service sse-bridge-service; do
        if ! ls "${svc}/target"/*.jar &>/dev/null 2>&1; then
            MISSING_JARS=$((MISSING_JARS + 1))
        fi
    done
    if [ "$MISSING_JARS" -gt 0 ]; then
        warn "$MISSING_JARS service(s) have not been compiled. Build them first:"
        echo "         mvn install -f shared-java/pom.xml"
        echo "         mvn package -f parent-pom.xml -DskipTests"
    else
        ok "All service JARs present"
    fi

    # --- Python deps for operator-service ---
    info "operator-service Python dependencies"
    if [ -f operator-service/requirements.txt ]; then
        DEPS_OK=false
        if [ -d operator-service/.venv ] && operator-service/.venv/bin/python -c "import fastapi, anthropic, aiokafka" &>/dev/null 2>&1; then
            DEPS_OK=true
        elif [ -n "$PYTHON_CMD" ] && $PYTHON_CMD -c "import fastapi, anthropic, aiokafka" &>/dev/null 2>&1; then
            DEPS_OK=true
        fi
        if [ "$DEPS_OK" = "true" ]; then
            ok "Python deps installed"
        else
            warn "operator-service Python dependencies may not be installed."
            echo "         $PYTHON_CMD -m pip install -r operator-service/requirements.txt"
        fi
    fi

    # --- Platform-specific GPU checks ---
    if [ "$OS" = "Linux" ] && [ "${GPU:-cpu}" = "nvidia" ]; then

        info "NVIDIA driver"
        if nvidia-smi &>/dev/null 2>&1; then
            GPU_NAME=$(nvidia-smi --query-gpu=name --format=csv,noheader 2>/dev/null | head -1)
            ok "nvidia-smi: $GPU_NAME"
        else
            err "NVIDIA driver not responding (nvidia-smi failed)."
            echo "       Install drivers: https://rpmfusion.org/Howto/NVIDIA"
        fi

        info "NVIDIA Container Toolkit (nvidia-ctk)"
        if command -v nvidia-ctk &>/dev/null; then
            ok "nvidia-ctk found"
        else
            err "nvidia-ctk not found — GPU passthrough into containers will fail."
            echo "       Install: https://docs.nvidia.com/datacenter/cloud-native/container-toolkit/install-guide.html"
            echo "                sudo dnf install nvidia-container-toolkit  (Fedora/RHEL)"
        fi

        info "NVIDIA CDI configuration"
        if [ -f /etc/cdi/nvidia.yaml ] || ls /etc/cdi/nvidia*.yaml &>/dev/null 2>&1; then
            ok "CDI config present at /etc/cdi/"
        else
            err "NVIDIA CDI config not found — containers cannot access the GPU."
            echo "       Generate it with:"
            echo "         sudo nvidia-ctk cdi generate --output=/etc/cdi/nvidia.yaml"
            echo "       Then re-run this script."
        fi

        info "SELinux container_use_devices boolean"
        if command -v getsebool &>/dev/null; then
            if getsebool container_use_devices 2>/dev/null | grep -q "on$"; then
                ok "container_use_devices is on"
            else
                err "SELinux is blocking container access to NVIDIA devices."
                echo "       Enable with:"
                echo "         sudo setsebool -P container_use_devices 1"
            fi
        else
            ok "SELinux not present — skipping"
        fi

    fi

    if [ "$OS" = "Linux" ] && [ "${GPU:-cpu}" = "amd" ]; then

        info "ROCm — /dev/kfd and /dev/dri"
        if [ -e /dev/kfd ]; then
            ok "/dev/kfd present"
        else
            err "/dev/kfd not found — ROCm device is not available."
            echo "       Install ROCm: https://rocm.docs.amd.com/en/latest/deploy/linux/quick_start.html"
        fi

        info "ROCm user groups (video, render)"
        MISSING_GROUPS=""
        id | grep -q "video"  || MISSING_GROUPS="$MISSING_GROUPS video"
        id | grep -q "render" || MISSING_GROUPS="$MISSING_GROUPS render"
        if [ -z "$MISSING_GROUPS" ]; then
            ok "User is in video and render groups"
        else
            warn "User is not in group(s):$MISSING_GROUPS — ROCm device access may be denied."
            echo "         sudo usermod -aG video,render \$USER"
            echo "         Then log out and back in."
        fi

    fi

    # --- .env ---
    info ".env file"
    if [ -f .env ]; then
        ok ".env exists"
        # Check for anthropic key if backend is set to anthropic
        LLM_BACKEND_VAL=$(grep -E '^LLM_BACKEND=' .env 2>/dev/null | cut -d= -f2 | tr -d '"' || true)
        if [ "${LLM_BACKEND_VAL:-ramalama}" = "anthropic" ]; then
            ANTHROPIC_KEY=$(grep -E '^ANTHROPIC_API_KEY=' .env 2>/dev/null | cut -d= -f2 | tr -d '"' || true)
            if [ -z "$ANTHROPIC_KEY" ]; then
                err "LLM_BACKEND=anthropic but ANTHROPIC_API_KEY is not set in .env."
            else
                ok "ANTHROPIC_API_KEY is set"
            fi
        fi
    else
        cp .env.example .env
        warn ".env was missing — created from .env.example."
        echo "         Review .env and set LLM_BACKEND / ANTHROPIC_API_KEY before continuing."
    fi

    echo "  ----------------------------------------"

    if [ "$PREFLIGHT_ERRORS" -gt 0 ]; then
        echo -e "\n  ${red}${bold}$PREFLIGHT_ERRORS error(s) must be resolved before starting.${nc}"
        echo -e "  ${yellow}$PREFLIGHT_WARNINGS warning(s) noted.${nc}\n"
        exit 1
    elif [ "$PREFLIGHT_WARNINGS" -gt 0 ]; then
        echo -e "\n  ${yellow}$PREFLIGHT_WARNINGS warning(s). Continuing — check output above.${nc}\n"
    else
        echo -e "\n  ${green}All checks passed.${nc}\n"
    fi
}

# ---------------------------------------------------------------------------
# Override generators
# ---------------------------------------------------------------------------

override_mac_apple_silicon() {
    cat > "$OVERRIDE_FILE" <<'EOF'
# Auto-generated by start.sh — macOS Apple Silicon
# Removes NVIDIA CDI device; RamaLama detects Metal/MLX automatically.
version: "3.8"
services:
  ramalama:
    devices: []
EOF
}

override_mac_intel() {
    cat > "$OVERRIDE_FILE" <<'EOF'
# Auto-generated by start.sh — macOS Intel
# Removes NVIDIA CDI device; RamaLama will run CPU-only (very slow).
version: "3.8"
services:
  ramalama:
    devices: []
EOF
}

override_linux_amd() {
    cat > "$OVERRIDE_FILE" <<'EOF'
# Auto-generated by start.sh — Linux AMD GPU (ROCm)
# Replaces NVIDIA CDI device with ROCm device mounts.
version: "3.8"
services:
  ramalama:
    devices:
      - /dev/kfd:/dev/kfd
      - /dev/dri:/dev/dri
    group_add:
      - video
      - render
EOF
}

override_linux_cpu() {
    cat > "$OVERRIDE_FILE" <<'EOF'
# Auto-generated by start.sh — Linux CPU only
# Removes NVIDIA CDI device; RamaLama will run CPU-only (very slow).
version: "3.8"
services:
  ramalama:
    devices: []
EOF
}

# ---------------------------------------------------------------------------
# GPU detection (Linux)
# ---------------------------------------------------------------------------
detect_gpu_linux() {
    if command -v nvidia-smi &>/dev/null && nvidia-smi &>/dev/null 2>&1; then
        echo "nvidia"
    elif command -v rocm-smi &>/dev/null && rocm-smi &>/dev/null 2>&1; then
        echo "amd"
    elif [ -e /dev/kfd ]; then
        echo "amd"
    else
        echo "cpu"
    fi
}

# ---------------------------------------------------------------------------
# Platform detection
# ---------------------------------------------------------------------------
OS=$(uname -s)
ARCH=$(uname -m)
PLATFORM_LABEL=""
USE_OVERRIDE=true
GPU=""
COMPOSE_CMD=""

if [ "$OS" = "Darwin" ]; then
    if [ "$ARCH" = "arm64" ]; then
        PLATFORM_LABEL="macOS Apple Silicon (Metal/MLX)"
        override_mac_apple_silicon
    else
        PLATFORM_LABEL="macOS Intel (CPU only)"
        override_mac_intel
    fi
elif [ "$OS" = "Linux" ]; then
    GPU=$(detect_gpu_linux)
    case "$GPU" in
        nvidia)
            PLATFORM_LABEL="Linux NVIDIA CUDA"
            USE_OVERRIDE=false
            rm -f "$OVERRIDE_FILE"
            ;;
        amd)
            PLATFORM_LABEL="Linux AMD GPU (ROCm)"
            override_linux_amd
            ;;
        cpu)
            PLATFORM_LABEL="Linux CPU only"
            override_linux_cpu
            ;;
    esac
else
    fatal "Unsupported OS: $OS"
fi

echo ""
echo -e "${bold}OPERATION COPPERCLAW${nc}"
echo "  Platform : $PLATFORM_LABEL"

# ---------------------------------------------------------------------------
# Pre-flight
# ---------------------------------------------------------------------------
preflight

# ---------------------------------------------------------------------------
# Launch
# ---------------------------------------------------------------------------
COMPOSE_ARGS="-f podman-compose.yml"
if [ "$USE_OVERRIDE" = "true" ] && [ -f "$OVERRIDE_FILE" ]; then
    COMPOSE_ARGS="$COMPOSE_ARGS -f $OVERRIDE_FILE"
fi

LOG_DIR="logs"
LOG_FILE="$LOG_DIR/copperclaw.log"
mkdir -p "$LOG_DIR"

# Rotate logs: keep last 5, each capped at 50 MB
if [ -f "$LOG_FILE" ]; then
    for i in 4 3 2 1; do
        [ -f "$LOG_FILE.$i" ] && mv "$LOG_FILE.$i" "$LOG_FILE.$((i+1))"
    done
    mv "$LOG_FILE" "$LOG_FILE.1"
fi

echo "  Runtime  : $COMPOSE_CMD"
echo "  Override : $USE_OVERRIDE"
echo "  Log file : $LOG_FILE"
echo ""
echo "Starting COPPERCLAW... (tailing log — Ctrl+C stops the tail, not the stack)"
echo "  To stop the stack: ./scripts/stop.sh  or  podman-compose down"
echo ""

# shellcheck disable=SC2086
$COMPOSE_CMD $COMPOSE_ARGS up "$@" >> "$LOG_FILE" 2>&1 &
COMPOSE_PID=$!

# Give compose a moment to fail fast if something is immediately wrong
sleep 2
if ! kill -0 "$COMPOSE_PID" 2>/dev/null; then
    echo -e "  ${red}Compose exited immediately — check $LOG_FILE for errors.${nc}"
    exit 1
fi

echo "$COMPOSE_PID" > "$LOG_DIR/compose.pid"
tail -f "$LOG_FILE"
