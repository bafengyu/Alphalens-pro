#!/bin/bash
# =============================================================================
# AlphaLens Pro V9.0 nohup 启动脚本
# 用于简单部署（不使用 systemd）
# =============================================================================

# 配置
PROJECT_DIR="$(cd "$(dirname "$0")" && pwd)"
VENV_PYTHON="${PROJECT_DIR}/venv/bin/python"
APP_PATH="${PROJECT_DIR}/src/app.py"
LOG_FILE="${PROJECT_DIR}/logs/alphalens.log"
PID_FILE="${PROJECT_DIR}/logs/alphalens.pid"
PORT=8501

# 颜色
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

cd ${PROJECT_DIR}

# 激活虚拟环境
source ${PROJECT_DIR}/venv/bin/activate

start() {
    echo -e "${GREEN}启动 AlphaLens Pro...${NC}"
    
    # 确保日志目录存在
    mkdir -p ${PROJECT_DIR}/logs
    
    # 检查是否已运行
    if [ -f "${PID_FILE}" ]; then
        OLD_PID=$(cat ${PID_FILE})
        if ps -p ${OLD_PID} > /dev/null 2>&1; then
            echo -e "${YELLOW}服务已在运行，PID: ${OLD_PID}${NC}"
            return 1
        fi
    fi
    
    # 启动
    nohup ${VENV_PYTHON} -m streamlit run ${APP_PATH} \
        --server.port=${PORT} \
        --server.address=0.0.0.0 \
        --server.headless=true \
        > ${LOG_FILE} 2>&1 &
    
    echo $! > ${PID_FILE}
    echo -e "${GREEN}✓ 启动成功，PID: $(cat ${PID_FILE})${NC}"
    echo -e "访问地址: http://localhost:${PORT}"
}

stop() {
    echo -e "${YELLOW}停止 AlphaLens Pro...${NC}"
    
    if [ -f "${PID_FILE}" ]; then
        PID=$(cat ${PID_FILE})
        if ps -p ${PID} > /dev/null 2>&1; then
            kill ${PID}
            sleep 2
            echo -e "${GREEN}✓ 已停止${NC}"
        else
            echo -e "${YELLOW}进程已不存在${NC}"
        fi
        rm -f ${PID_FILE}
    else
        echo -e "${YELLOW}未找到 PID 文件${NC}"
    fi
}

restart() {
    stop
    sleep 2
    start
}

status() {
    if [ -f "${PID_FILE}" ]; then
        PID=$(cat ${PID_FILE})
        if ps -p ${PID} > /dev/null 2>&1; then
            echo -e "${GREEN}✓ 服务运行中，PID: ${PID}${NC}"
        else
            echo -e "${RED}✗ 服务未运行（PID 文件过时）${NC}"
        fi
    else
        echo -e "${YELLOW}? 服务状态未知（无 PID 文件）${NC}"
    fi
}

log() {
    tail -f ${LOG_FILE}
}

case "$1" in
    start)
        start
        ;;
    stop)
        stop
        ;;
    restart)
        restart
        ;;
    status)
        status
        ;;
    log)
        log
        ;;
    *)
        echo "用法: $0 {start|stop|restart|status|log}"
        exit 1
        ;;
esac

exit 0
