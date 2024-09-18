echo -n "请输入版本号: "
read version

# 压缩文件
tar -zcvf amiyabot.tar.gz --exclude=.git --exclude=.vscode --exclude=.idea --exclude=docker.sh \
    --exclude=entrypoint.sh --exclude=install.sh --exclude=Dockerfile --exclude=amiyabot.tar.gz \
    *

docker build -t amiyabot/amiyabot:$version .