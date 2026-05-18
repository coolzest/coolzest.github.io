---
title: 网卡绑定与 EAL 启动参数
date: 2026-04-22
description: "掌握 VFIO、网卡绑定、设备选择、核心绑定和多进程启动参数。"
categories:
  - Linux 开发
  - DPDK
tags:
  - DPDK
  - Linux
  - 高性能网络
comments: true
---

# 网卡绑定与 EAL 启动参数

> 这一章把网卡从 Linux 内核路径切到 DPDK 路径，并解释 DPDK 应用启动命令里最常见的 EAL 参数。

## 6. 网卡绑定、VFIO 与驱动选择

### 6.1 为什么要绑定驱动

DPDK 应用要直接操作网卡队列，就需要让 DPDK PMD 能访问设备。常见方式是把网卡从 Linux 内核网络驱动解绑，再绑定到 `vfio-pci` 或某些 UIO 驱动。

这意味着：

- 被绑定的物理端口通常不会再显示为普通 `ethX` 可配置 IP 的网卡。
- 该端口不能继续被 NetworkManager、systemd-networkd、ifconfig、iproute2 正常管理。
- 如果是远程机器，千万不要把管理网口绑定走，否则可能直接断连。

### 6.2 查设备状态

DPDK 源码或安装目录中一般有 `dpdk-devbind.py`：

```bash
sudo dpdk-devbind.py --status
lspci -nn | grep -i ether
```

输出中需要关注：

- PCI 地址，例如 `0000:03:00.0`。
- 当前驱动，例如 `ixgbe`、`i40e`、`ice`、`mlx5_core`、`vfio-pci`。
- 是否有 `Active` 标记。有活动 IP 的端口不要随手解绑。

### 6.3 使用 vfio-pci

推荐优先使用 VFIO。它借助 IOMMU 做 DMA 隔离，安全性和通用性更好。

```bash
sudo modprobe vfio-pci

# 如果系统启用了 IOMMU，直接绑定
sudo dpdk-devbind.py -b vfio-pci 0000:03:00.0

# 查看结果
sudo dpdk-devbind.py --status
```

如果提示 IOMMU 相关问题，需要检查启动参数：

Intel 平台常见：

```text
intel_iommu=on iommu=pt
```

AMD 平台常见：

```text
amd_iommu=on iommu=pt
```

`vfio-pci` 的 no-IOMMU 模式只建议实验室使用。它会降低 DMA 隔离安全性，不应作为生产默认方案。

### 6.4 恢复内核驱动

先确认原驱动：

```bash
ethtool -i eth0
lspci -k -s 0000:03:00.0
```

恢复示例：

```bash
sudo dpdk-devbind.py -b ixgbe 0000:03:00.0
sudo ip link set eth0 up
```

具体驱动名取决于网卡，例如 `ixgbe`、`i40e`、`ice`、`mlx5_core`、`bnxt_en`。

### 6.5 bifurcated driver

有些 PMD 支持 bifurcated driver 模式，即内核驱动仍参与设备管理，DPDK 通过特定机制访问数据路径。典型好处是：

- 网卡仍可能保留 Linux 网络接口。
- 运维和控制面更容易融入现有系统。
- 安全模型可能更容易接受。

但不同网卡支持差异很大，开发前要查对应 NIC driver 文档。不要假设所有网卡都能这样工作。

## 7. EAL 参数与启动方式

DPDK 应用的命令行通常分两段：

```bash
sudo ./dpdk-app [EAL 参数] -- [应用自己的参数]
```

`--` 前面由 EAL 解析，后面由你的程序解析。

### 7.1 核心绑定

最常见：

```bash
sudo ./dpdk-app -l 1-4 -n 4 -- ...
```

`-l 1-4` 表示使用逻辑核 1 到 4。

更精细的 `--lcores`：

```bash
sudo ./dpdk-app --lcores='(1-2)@1,(3-4)@2' -n 4 -- ...
```

实际工程中建议用清晰、可复现的 lcore 规划：

| 核心角色 | 示例 | 说明 |
| --- | --- | --- |
| main lcore | 1 | 初始化、控制面、低频任务 |
| RX/TX worker | 2-9 | 每个核心处理一个或多个 queue |
| stats/service | 10 | 统计、遥测、慢路径 |
| spare | 11 | 预留给调试或热切换 |

查看 lcore：

```bash
lscpu -e=CPU,CORE,SOCKET,NODE,ONLINE
```

### 7.2 内存通道 `-n`

`-n` 是内存通道数量，常见示例中会写 `-n 4`。现代平台不总是靠这个参数决定真实性能，但很多示例仍保留。不了解硬件时可以先用 `-n 4` 跑通。

### 7.3 设备选择

允许某个 PCI 设备：

```bash
sudo ./dpdk-app -l 1-4 -n 4 -a 0000:03:00.0 -- ...
```

屏蔽某个设备：

```bash
sudo ./dpdk-app -l 1-4 -n 4 -b 0000:03:00.1 -- ...
```

使用虚拟设备：

```bash
sudo ./dpdk-app -l 1-2 -n 4 --vdev=net_pcap0,rx_pcap=input.pcap,tx_pcap=output.pcap -- ...
```

### 7.4 多进程

DPDK 支持 primary/secondary 进程。常见用途：

- 主进程负责设备初始化和数据面。
- 次进程读取统计、遥测或执行辅助操作。
- 多个进程共享 hugepage-backed 内存和 memzone。

常用参数：

```bash
--proc-type=primary
--proc-type=secondary
--file-prefix=myapp
```

多进程要特别小心：

- `--file-prefix` 必须规划，避免不同应用误共享或冲突。
- primary 先启动，secondary 再附加。
- 共享结构要自己设计同步机制。
- 不是所有对象创建 API 都适合多个进程同时调用。

### 7.5 日志和诊断参数

```bash
--log-level=lib.eal:debug
--log-level=pmd.net.ixgbe:debug
--trace=eal
--no-pci
--no-huge
```

建议开发期保留足够日志，上线后控制输出量。数据面循环里不要频繁打印日志，尤其不要每个包打印。
