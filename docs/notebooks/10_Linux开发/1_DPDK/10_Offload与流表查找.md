---
title: Offload 与流表查找
date: 2026-04-22
description: "理解 checksum、RSS、TSO、rte_flow、hash、LPM 和 ACL 的工程用法。"
categories:
  - Linux 开发
  - DPDK
tags:
  - DPDK
  - Linux
  - 高性能网络
comments: true
---

# Offload 与流表查找

> 这一章把硬件 offload 和查表能力串起来：哪些工作交给网卡，哪些工作放在 DPDK 库中完成。

## 19. offload 设计

### 19.1 常见 offload

| offload | 作用 | 注意 |
| --- | --- | --- |
| RX checksum | 硬件验证 L3/L4 checksum | 要检查 mbuf 标志 |
| TX checksum | 硬件生成 checksum | mbuf 字段必须设置正确 |
| VLAN strip/insert | 硬件剥离或插入 VLAN | 会影响包头解析位置 |
| TSO | TCP 大包分段 | 需要正确设置 TCP/IP header |
| RSS | 多队列分发 | hash 字段和 reta 表要配置 |
| timestamp | 硬件时间戳 | 与 PTP/驱动能力相关 |
| scatter/gather | 多段包收发 | 解析代码必须支持多段 |

### 19.2 使用 offload 的安全流程

1. 查询能力：`rte_eth_dev_info_get()`。
2. 检查能力位：`rx_offload_capa`、`tx_offload_capa`。
3. 在端口或 queue 配置中启用。
4. 设置 mbuf 的 `ol_flags` 和相关 header 长度。
5. 用真实流量验证。
6. 暴露统计和错误计数，避免“以为硬件做了，实际没做”。

### 19.3 不要过早打开所有 offload

很多问题来自“为了性能把能开的都开了”。建议：

- 先跑无 offload 的正确版本。
- 一次只打开一种 offload。
- 每次打开后用 pcap、对端协议栈和统计验证。
- 记录每种 offload 对吞吐、延迟和 CPU 的影响。

## 20. rte_flow、ACL、Hash、LPM

### 20.1 hash

Hash 库适合精确匹配：

- 五元组 flow table。
- MAC 表。
- 会话表。
- NAT 映射。
- 用户自定义 key。

设计 key 时要注意：

- 字节序统一。
- 结构体 padding 清零。
- key 长度固定且明确。
- 更新路径和查询路径的并发语义清晰。

### 20.2 LPM

LPM 是最长前缀匹配，适合 IP 路由查找：

- IPv4 路由表。
- IPv6 路由表。
- 网段级策略。

典型流程：

1. 初始化 LPM 表。
2. 控制面加载路由。
3. 数据面用目的 IP 查下一跳。
4. 根据下一跳决定端口和 MAC 重写。

### 20.3 ACL

ACL 适合多字段规则匹配，例如：

- 源/目的 IP 前缀。
- 源/目的端口范围。
- 协议号。
- 优先级和动作。

ACL 的性能依赖规则数量、字段组织、batch 大小和 CPU SIMD 能力。规则更新通常放控制面，数据面使用构建好的上下文。

### 20.4 rte_flow

`rte_flow` 用于把匹配和动作下发给硬件或驱动，例如：

- 按五元组导入某个 queue。
- 丢弃某类包。
- 修改 header。
- meter、mark、count。
- 隧道匹配和 steering。

不同网卡支持差异很大。使用前要查 NIC PMD 文档，并在初始化时检测失败路径。不要把某张网卡的 `rte_flow` 能力当成所有环境都有。
