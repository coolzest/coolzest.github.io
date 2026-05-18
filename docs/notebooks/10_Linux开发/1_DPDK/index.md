---
title: DPDK
date: 2026-04-22
description: "DPDK 高性能网络开发专题。"
categories:
  - Linux 开发
  - DPDK
tags:
  - DPDK
  - Linux
  - 高性能网络
comments: true
---

# DPDK

> DPDK 是 Linux 用户态高性能网络开发的重要工具链。这个专题从程序员视角出发，先理解数据面架构，再进入环境准备、网卡绑定、EAL 初始化、mbuf/mempool/ring、ethdev、代码骨架、调试和性能优化。

## 章节目录

- [DPDK 系统开发指南](01_DPDK系统开发指南.md)
- [DPDK 总览与适用场景](02_DPDK总览与适用场景.md)
- [DPDK 开发环境准备](03_开发环境准备.md)
- [Hugepage 与 DPDK 内存模型](04_Hugepage与内存模型.md)
- [网卡绑定与 EAL 启动参数](05_网卡绑定与EAL启动参数.md)
- [EAL 初始化与 lcore 编程模型](06_EAL初始化与lcore模型.md)
- [mempool、mbuf、ring 与 timer](07_mempool_mbuf_ring_timer.md)
- [ethdev 端口初始化与收发包](08_ethdev端口初始化与收发包.md)
- [处理模型、多队列、多核与 NUMA](09_处理模型与多核NUMA.md)
- [Offload 与流表查找](10_Offload与流表查找.md)
- [testpmd 调试与可观测性](11_testpmd调试与可观测性.md)
- [性能优化与生产化](12_性能优化与生产化.md)
- [学习练习与参考资料](13_学习练习与参考资料.md)

## 推荐阅读路线

1. 先读总览和适用场景，确认 DPDK 要解决的问题。
2. 再完成环境、Hugepage、网卡绑定和 EAL 参数。
3. 写最小收包程序，再逐步加入转发、解析、RSS、多队列、统计和控制面。
