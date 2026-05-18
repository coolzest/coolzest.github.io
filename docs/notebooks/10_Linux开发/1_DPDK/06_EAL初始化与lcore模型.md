---
title: EAL 初始化与 lcore 编程模型
date: 2026-04-22
description: "掌握 DPDK 程序初始化顺序、lcore worker 启动和生命周期管理。"
categories:
  - Linux 开发
  - DPDK
tags:
  - DPDK
  - Linux
  - 高性能网络
comments: true
---

# EAL 初始化与 lcore 编程模型

> 这一章从代码结构看 DPDK 程序如何启动：先初始化 EAL，再创建对象、配置端口、启动 worker。

## 8. EAL 初始化和 lcore 编程模型

### 8.1 基本流程

DPDK 程序的主线一般是：

1. 注册信号处理，准备退出标志。
2. 调用 `rte_eal_init(argc, argv)`。
3. 解析应用自己的参数。
4. 创建 mempool、ring、hash/LPM、ACL 等共享对象。
5. 枚举并配置 ethdev 端口和 queue。
6. 启动 worker lcore。
7. main lcore 进入控制面、统计循环，或也参与转发。
8. 收到退出信号后停止端口、释放资源、调用 `rte_eal_cleanup()`。

### 8.2 初始化对象放在 main lcore

经验规则：对象创建和初始化尽量在 main lcore 的初始化阶段完成，例如：

- `rte_pktmbuf_pool_create()`
- `rte_ring_create()`
- `rte_hash_create()`
- `rte_lpm_create()`
- `rte_eth_dev_configure()`
- `rte_eth_rx_queue_setup()`
- `rte_eth_tx_queue_setup()`

很多对象创建函数不是为了并发创建设计的。初始化后，数据结构本身通常可以按文档约束被多个线程使用。

### 8.3 启动 worker

常见形式：

```c
rte_eal_remote_launch(worker_main, worker_arg, worker_lcore_id);
```

等待所有 worker：

```c
uint16_t lcore_id;
RTE_LCORE_FOREACH_WORKER(lcore_id) {
    if (rte_eal_wait_lcore(lcore_id) < 0) {
        return -1;
    }
}
```

最简单的程序也可以只让 main lcore 跑数据面循环，但生产代码通常会把初始化、控制面、统计和数据面核心区分开。
