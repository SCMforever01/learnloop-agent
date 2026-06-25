FROM python:3.12-slim

WORKDIR /app

# 安装依赖
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple

# 复制代码
COPY . .

# 暴露端口
EXPOSE 8000

# 启动命令
CMD ["sh", "-c", "python seeds/seed_all.py && uvicorn main:app --host 0.0.0.0 --port 8000"]
