# 使用python3.9作为基础镜像
FROM mcr.microsoft.com/playwright/python:v1.31.1

# 设置数据卷
VOLUME [ "/amiyabot" ]

# 设置工作目录
WORKDIR /app

# 守护端口
EXPOSE 8088

# 工作目录
COPY requirements.txt /app
COPY entrypoint.sh /app

# 临时目录
COPY . /temp
RUN tar -zcvf amiyabot.tar.gz --exclude=/temp/.git --exclude=/temp/.vscode --exclude=/temp/.idea --exclude=/temp/docker.sh \
    --exclude=/temp/entrypoint.sh --exclude=/temp/install.sh --exclude=/temp/Dockerfile /temp/*
RUN rm -rf /temp

# 安装依赖
RUN pip install -r requirements.txt
RUN playwright install --with-deps chromium

# 启动命令
ENTRYPOINT [ "bash", "entrypoint.sh" ]
