#! /bin/sh

# 删除原来版本
if [ -d "shark_transcode" ]; then
  rm -rf shark_transcode
fi

# 删除打包残留文件
if [ -d "build" ]; then
  rm -rf build
fi

rm -rf *.spec

# 打包
pyinstaller -F --clean --additional-hooks-dir hooks --distpath shark_transcode main.py

# 拷贝外部应用
cp -rf bin shark_transcode/

# 拷贝配置文件
mkdir -p shark_transcode/config
cp -rf config/settings.json shark_transcode/config
cp -rf config/sys.json shark_transcode/config
