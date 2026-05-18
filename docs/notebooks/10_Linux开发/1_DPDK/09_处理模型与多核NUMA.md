---
title: 处理模型、多队列、多核与 NUMA
date: 2026-04-22
description: "设计 run-to-completion、pipeline、多队列、多核心和 NUMA 亲和策略。"
categories:
  - Linux 开发
  - DPDK
tags:
  - DPDK
  - Linux
  - 高性能网络
comments: true
---

# 处理模型、多队列、多核与 NUMA

> 这一章解决“怎么把程序跑满多核”的问题：处理模型、RSS、queue ownership、CPU 隔离和 NUMA 亲和。

## 17. 处理模型选择

### 17.1 Run-to-completion

一个 lcore 从 RX 到业务处理再到 TX 一次完成。

优点：

- 延迟低。
- cache locality 好。
- 结构简单。
- 少跨核通信。

缺点：

- 某一阶段变重会拖慢整个队列。
- 不适合复杂多阶段处理。
- 核心负载不均时扩展困难。

适合：

- L2/L3 转发。
- 简单 ACL。
- 固定处理流程。
- 极致低延迟场景。

### 17.2 Pipeline

不同 lcore 负责不同阶段，例如 RX、parse、lookup、encrypt、TX，通过 ring 串起来。

优点：

- 阶段清晰，便于扩展。
- 重任务可以分配更多 worker。
- 控制复杂业务更容易。

缺点：

- 跨核传递增加延迟。
- ring 积压会造成抖动。
- 要设计背压和丢包策略。

适合：

- DPI。
- 多阶段安全检测。
- 网关或负载均衡复杂业务。

### 17.3 Event-driven

DPDK 还有 eventdev 模型，适合用事件队列表达调度、顺序和并行关系。它更复杂，但在多阶段包处理和硬件 event device 场景中很有价值。

入门建议先掌握 run-to-completion，再理解 pipeline，最后看 eventdev。

## 18. 多队列、多核与 NUMA

### 18.1 基本原则

性能不够时，不是简单地“多开几个线程”。DPDK 扩展要围绕 NIC queue 和 lcore 映射设计。

推荐原则：

- 每个 RX queue 一个 owner lcore。
- 每个 TX queue 一个 owner lcore。
- 同一 flow 尽量落到同一 lcore，避免乱序。
- NIC、mempool、worker 尽量在同一 NUMA node。
- 控制面和数据面分离。
- 不要让 Linux 调度器随意迁移数据面线程。

### 18.2 CPU 隔离

生产环境常见启动参数：

```text
isolcpus=2-15 nohz_full=2-15 rcu_nocbs=2-15
```

然后 DPDK 使用这些隔离核心：

```bash
sudo ./dpdk-app -l 2-15 -n 4 -- ...
```

同时考虑：

- 关闭或固定 irqbalance。
- 把非 DPDK 中断绑到其他核心。
- CPU governor 设置为 performance。
- 禁止无关服务占用数据面核心。

### 18.3 NUMA 亲和

查看 NIC 所在 NUMA：

```bash
cat /sys/bus/pci/devices/0000:03:00.0/numa_node
```

按 socket 分配 hugepage：

```bash
echo 1024 | sudo tee /sys/devices/system/node/node0/hugepages/hugepages-2048kB/nr_hugepages
```

运行时指定：

```bash
sudo ./dpdk-app -l 2-7 -n 4 --socket-mem=2048,0 -a 0000:03:00.0
```

远端 NUMA 访问会增加延迟，并且会让吞吐上限下降。跨 socket 转发时要通过压测确认成本。
