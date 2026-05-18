---
title: testpmd 调试与可观测性
date: 2026-04-22
description: "用 testpmd 验证平台，并为 DPDK 应用设计日志、统计和遥测。"
categories:
  - Linux 开发
  - DPDK
tags:
  - DPDK
  - Linux
  - 高性能网络
comments: true
---

# testpmd 调试与可观测性

> 这一章专门为排障准备：先用 testpmd 验机，再给自己的程序补齐统计、xstats 和 telemetry。

## 21. testpmd：开发前的验机工具

在写代码前，先用 `testpmd` 验证平台，这是最省时间的习惯。

### 21.1 最小启动

```bash
sudo ./build/app/dpdk-testpmd \
  -l 1-3 -n 4 -a 0000:03:00.0 \
  -- \
  --forward-mode=io \
  --auto-start
```

进入交互后常用命令：

```text
show port info all
show port stats all
show port xstats all
show config fwd
show rxq info 0 0
show txq info 0 0
stop
start
quit
```

### 21.2 常见 forward mode

| mode | 含义 | 用途 |
| --- | --- | --- |
| `io` | 收到什么发什么 | 验证收发路径 |
| `mac` | 改写 MAC 后转发 | 验证 L2 转发 |
| `rxonly` | 只收不发 | 验证 RX 和统计 |
| `txonly` | 只发不收 | 压 TX 路径 |
| `csum` | checksum offload 测试 | 验证硬件校验 |
| `flowgen` | 生成多流 | 验证 RSS/多队列 |

### 21.3 用 testpmd 缩小问题

如果你的程序收不到包，先问：

- testpmd 能不能收？
- testpmd 用同样的 EAL 参数能不能启动？
- 同样的 port、queue、hugepage、VFIO 是否正常？
- 链路是否 up？
- 对端是否真的发到了这张网卡？

如果 testpmd 都不行，问题大概率在环境、网卡、驱动、绑定、线缆、交换机或 hugepage。如果 testpmd 可以，你的程序才是重点怀疑对象。

## 22. 日志、统计与遥测

### 22.1 基础统计

端口统计：

```c
struct rte_eth_stats stats;
rte_eth_stats_get(port_id, &stats);

printf("ipackets=%" PRIu64 " ibytes=%" PRIu64 " ierrors=%" PRIu64 "\n",
       stats.ipackets, stats.ibytes, stats.ierrors);
```

扩展统计 xstats 能看到更多 PMD 暴露的计数，例如：

- per queue packets。
- checksum errors。
- missed packets。
- no mbuf。
- MAC 层错误。
- flow hit/miss。

### 22.2 统计设计

数据面统计建议：

- 每个 lcore 用本地计数器，避免每包原子加。
- 周期性汇总到控制面。
- 区分 RX、drop、tx_success、tx_failed、mbuf_alloc_failed。
- 区分原因丢包，例如 ACL drop、no route、tx full、parse error。
- 统计用 cache line 对齐，避免 false sharing。

### 22.3 telemetry

DPDK telemetry 可用于运行期查询内部状态。开发自己的系统时也可以提供类似接口：

- `/stats/ports`
- `/stats/queues`
- `/stats/lcores`
- `/config`
- `/flows`
- `/health`

运维可观测性不是上线以后再补的功能。没有统计的 DPDK 程序，排障会非常痛苦。
