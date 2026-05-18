---
title: DPDK 系统开发指南
date: 2026-04-22
description: "DPDK 系统开发指南的分章入口。"
categories:
  - Linux 开发
  - DPDK
tags:
  - DPDK
  - Linux
  - 高性能网络
  - 数据平面
comments: true
---

# DPDK 系统开发指南

> 原来的长文已经拆成多个专题页。细节仍然保留，只是按开发路线拆开，读起来不用一次滚到底。

## 阅读顺序

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

## 使用建议

- 第一次学习：按顺序读，从总览、环境、内存、网卡绑定开始。
- 准备写代码：重点看 EAL、mempool/mbuf/ring、ethdev、收发包示例。
- 准备压测上线：重点看 testpmd、可观测性、性能优化与生产化。

## 官方资料

本文参考 DPDK 官方 Programmer's Guide 与 Linux Getting Started Guide，并在最后一章集中列出链接。
