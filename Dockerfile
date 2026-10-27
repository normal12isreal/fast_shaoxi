# syntax=docker/dockerfile:1

# 分发镜像：只包含网站、RAG 代码和已有索引，不携带本机数据库或凭据。
FROM python:3.13-slim-trixie

# 与 scripts/toolchain.json 中的 uv 版本保持一致。
COPY --from=ghcr.io/astral-sh/uv:0.13.5 /uv /usr/local/bin/uv

WORKDIR /app

LABEL org.opencontainers.image.source="https://github.com/normal12isreal/fast_shaoxi" \
    org.opencontainers.image.description="绍兴大学学生手册 RAG 网站与 FastAPI 接口" \
    org.opencontainers.image.licenses="MIT"

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    UV_PYTHON_DOWNLOADS=never \
    PATH="/app/.venv/bin:$PATH" \
    RAG_PROJECT_DIR=/app/rag \
    HANDBOOK_DATABASE_PATH=/app/data/site.sqlite3

# 按锁定依赖创建 Linux 虚拟环境，不复制本机 Windows 的 .venv。
# 先安装依赖，让单纯修改应用代码时可以复用这一层。
COPY pyproject.toml uv.lock README.md ./
RUN uv sync --locked --no-dev --no-cache --python /usr/local/bin/python

# .dockerignore 排除所有本机数据；应用首次启动自动创建空数据库并执行迁移。
COPY . .
RUN mkdir -p /app/data /app/rag/.runtime

# 这里只声明容器端口；运行时仍需通过 -p 80:8000 等参数发布端口。
EXPOSE 8000

# 生产式启动：监听容器全部网卡、关闭自动重载，保持当前单进程执行限额。
CMD ["python", "-m", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "1"]
