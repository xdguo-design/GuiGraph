FROM python:3.11-slim

WORKDIR /app

# 安装系统依赖（Oracle 需要 libaio）
RUN apt-get update && apt-get install -y --no-install-recommends \
    git \
    libaio1 \
    && rm -rf /var/lib/apt/lists/*

# 安装 Python 依赖
COPY requirements/base.txt .
RUN pip install --no-cache-dir -r base.txt

# 复制应用代码
COPY . .

# 创建日志目录
RUN mkdir -p logs

# 环境变量：APP_ENV=dev|test|prod（默认 dev）
ENV APP_ENV=dev

# 暴露端口
EXPOSE 10011

# 启动命令（自动加载 .env.{APP_ENV}）
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "10011"]
