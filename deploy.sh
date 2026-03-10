#!/bin/bash
# =============================================================================
# AlphaLens Pro V9.0 部署脚本
# 适用于阿里云 Ubuntu 24.04
# =============================================================================

set -e

# 配置变量
PROJECT_NAME="AlphaLens-Pro"
PROJECT_DIR="/opt/${PROJECT_NAME}"
SERVICE_NAME="alphalens"
PORT=8501

# 颜色定义
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

echo -e "${GREEN}=== AlphaLens Pro V9.0 部署脚本 ===${NC}"

# 检查 root 权限
if [ "$EUID" -ne 0 ]; then 
    echo -e "${YELLOW}请使用 sudo 运行此脚本${NC}"
    exit 1
fi

# 1. 安装系统依赖
echo -e "${GREEN}[1/6] 安装系统依赖...${NC}"
apt update
apt install -y python3 python3-pip python3-venv git curl

# 2. 创建项目目录
echo -e "${GREEN}[2/6] 创建项目目录...${NC}"
mkdir -p ${PROJECT_DIR}
cd ${PROJECT_DIR}

# 3. 复制项目文件（如果不存在）
if [ ! -f "${PROJECT_DIR}/pyproject.toml" ]; then
    echo -e "${YELLOW}请将项目文件复制到 ${PROJECT_DIR}${NC}"
    echo -e "${YELLOW}可以执行: scp -r ./AlphaLens-Pro/* user@your_server:/opt/AlphaLens-Pro/${NC}"
    exit 1
fi

# 4. 创建虚拟环境
echo -e "${GREEN}[3/6] 创建虚拟环境...${NC}"
python3 -m venv venv
source venv/bin/activate

# 5. 安装依赖
echo -e "${GREEN}[4/6] 安装 Python 依赖...${NC}"
pip install --upgrade pip
pip install -e .

# 6. 配置环境变量
echo -e "${GREEN}[5/6] 配置环境变量...${NC}"
if [ ! -f "${PROJECT_DIR}/.env" ]; then
    cp configs/.env.example ${PROJECT_DIR}/.env
    echo -e "${YELLOW}请编辑 ${PROJECT_DIR}/.env 设置 DEEPSEEK_API_KEY${NC}"
fi

# 7. 创建 systemd 服务
echo -e "${GREEN}[6/6] 创建 systemd 服务...${NC}"

cat > /etc/systemd/system/${SERVICE_NAME}.service << EOF
[Unit]
Description=AlphaLens Pro V9.0 - AI Stock Analysis
After=network.target

[Service]
Type=simple
User=root
WorkingDirectory=${PROJECT_DIR}
Environment="PATH=${PROJECT_DIR}/venv/bin"
Environment="PYTHONPATH=${PROJECT_DIR}/src"
ExecStart=${PROJECT_DIR}/venv/bin/streamlit run src/app.py --server.port=${PORT} --server.address=0.0.0.0
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF

# 8. 启动服务
echo -e "${GREEN}启动服务...${NC}"
systemctl daemon-reload
systemctl enable ${SERVICE_NAME}
systemctl restart ${SERVICE_NAME}

# 等待服务启动
sleep 5

# 检查服务状态
if systemctl is-active --quiet ${SERVICE_NAME}; then
    echo -e "${GREEN}✓ AlphaLens Pro 启动成功!${NC}"
    echo -e "${GREEN}访问地址: http://your_server_ip:${PORT}${NC}"
else
    echo -e "${RED}✗ 服务启动失败，请检查日志:${NC}"
    journalctl -u ${SERVICE_NAME} -n 20
fi

# 常用命令
echo -e ""
echo -e "${GREEN}=== 常用命令 ===${NC}"
echo -e "查看状态: systemctl status ${SERVICE_NAME}"
echo -e "查看日志: journalctl -u ${SERVICE_NAME} -f"
echo -e "重启服务: systemctl restart ${SERVICE_NAME}"
echo -e "停止服务: systemctl stop ${SERVICE_NAME}"
