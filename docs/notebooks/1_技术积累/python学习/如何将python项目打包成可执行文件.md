---
title: 如何将python项目打包成可执行文件？
comments: true
---

# 如何将python项目打包成可执行文件？

## 打包成没有黑框（无控制台窗口）
```bash
pyinstaller -w 脚本名.py  # 隐藏控制台黑框（适合GUI程序）
```
```bash
pyinstaller --windowed 脚本名.py  # 长格式，同-w，无黑框
```

## 基础打包
```bash
pyinstaller 脚本名.py  # 生成dist、build文件夹和spec文件（默认有黑框）
```

## 单文件+无黑框（常用组合）
```bash
pyinstaller -F -w 脚本名.py  # 打包为单个文件且无黑框
```
```bash
pyinstaller --onefile --windowed 脚本名.py  # 长格式，单文件+无黑框
```

## 单文件模式
```bash
pyinstaller -F 脚本名.py  # 打包为单个可执行文件（默认有黑框）
```
```bash
pyinstaller --onefile 脚本名.py  # 长格式，同-F
```

## 自定义输出/缓存目录
```bash
pyinstaller --distpath 目标路径 脚本名.py  # 指定可执行文件输出目录
```
```bash
pyinstaller --workpath 缓存路径 脚本名.py  # 指定临时缓存目录
```

## 自定义图标
```bash
pyinstaller -i 图标.ico 脚本名.py  # 设置图标
```
```bash
pyinstaller --icon 图标.ico 脚本名.py  # 长格式，同-i
```

## 包含额外文件
```bash
pyinstaller --add-data "源路径;目标路径" 脚本名.py  # Windows（分隔符;）
```
```bash
pyinstaller --add-data "源路径:目标路径" 脚本名.py  # Linux/macOS（分隔符:）
```

## 模块相关
```bash
pyinstaller --paths 模块目录 脚本名.py  # 添加模块搜索路径
```
```bash
pyinstaller --exclude-module 模块名 脚本名.py  # 排除不需要的模块
```

## spec文件操作
```bash
pyinstaller --specpath 路径 脚本名.py  # 自定义spec文件生成路径
```
```bash
pyinstaller 脚本名.spec  # 使用spec文件打包
```

## 其他
```bash
pyinstaller -v  # 查看版本
```
```bash
pyinstaller -h  # 查看帮助
```
