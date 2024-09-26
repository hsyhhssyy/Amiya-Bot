#!/bin/bash

BOT_FOLDER=/amiyabot

# step 1: 解压/覆盖bot文件
if [ -f "/amiyabot.tar.gz" ]; then
    tar -zxvf /amiyabot.tar.gz -C /
    mv /temp/* $BOT_FOLDER
    rm -rf /temp
fi

# step 2: 判断是否首次运行
if [ ! -f "$BOT_FOLDER/first_run" ]; then
    cd $BOT_FOLDER
    python entrypoint.py
    touch first_run
fi

# step 3: 启动bot
cd $BOT_FOLDER
python amiya.py