#!/bin/bash

BOT_FOLDER=/amiyabot

if [ ! -f "$BOT_FOLDER/first_run" ]; then
    # step 1: 解压bot本体
    tar -zxvf amiyabot.tar.gz -C $BOT_FOLDER
    # step 2: 进入bot目录
    cd $BOT_FOLDER
    # step 3: 初始化配置文件
    python entrypoint.py
    # step 4: 标记已初始化
    touch first_run
fi

# step 5: 运行bot
cd $BOT_FOLDER
python amiya.py