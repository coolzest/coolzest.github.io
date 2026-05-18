---
title: mempool、mbuf、ring 与 timer
date: 2026-04-22
description: "理解 DPDK 数据面最常用的对象池、包缓冲、跨核队列和定时器。"
categories:
  - Linux 开发
  - DPDK
tags:
  - DPDK
  - Linux
  - 高性能网络
comments: true
---

# mempool、mbuf、ring 与 timer

> 这一章是 DPDK 数据结构核心：包从 mempool 取出，放进 mbuf，经 ring 在核心间传递，再由 timer 处理周期任务。

## 9. mempool：固定对象池

### 9.1 mempool 的作用

DPDK 数据面不能在每个包到来时调用普通 `malloc/free`。原因很简单：

- `malloc/free` 路径复杂，延迟不稳定。
- 多线程竞争会影响吞吐。
- 包对象大小相对固定，非常适合对象池。
- 网卡 RX 队列需要提前挂好可 DMA 的空闲 buffer。

`mempool` 提供固定对象的高速分配回收，常用于 `mbuf` 池，也可用于你自己的会话对象、流表节点、任务对象等。

### 9.2 创建 mbuf pool

```c
struct rte_mempool *mbuf_pool;

mbuf_pool = rte_pktmbuf_pool_create(
    "MBUF_POOL",
    8192,
    250,
    0,
    RTE_MBUF_DEFAULT_BUF_SIZE,
    rte_socket_id()
);

if (mbuf_pool == NULL) {
    rte_exit(EXIT_FAILURE, "cannot create mbuf pool: %s\n", rte_strerror(rte_errno));
}
```

参数含义：

| 参数 | 含义 |
| --- | --- |
| name | mempool 名字，多进程和调试时很重要 |
| n | 对象数量 |
| cache_size | 每个 lcore 的本地 cache 数量 |
| priv_size | 每个 mbuf 的私有区大小 |
| data_room_size | 每个包 buffer 的数据区大小 |
| socket_id | NUMA socket |

### 9.3 mbuf 数量怎么估算

入门可以用：

```text
NUM_MBUFS = nb_ports * nb_queues_per_port * nb_rx_desc * 2 + burst_slack + app_cache
```

实际工程中要考虑：

- RX descriptor 会占住一批 mbuf。
- 应用处理中的包会占住一批 mbuf。
- TX 未完成回收的包会占住一批 mbuf。
- ring 或跨核队列中会暂存一批 mbuf。
- 每个 lcore mempool cache 会缓存一批对象。
- 突发流量和下游拥塞会让 mbuf 短时间堆积。

如果 `rte_eth_rx_burst()` 收不到包，或者驱动日志出现 mbuf 不足，第一反应就是检查 mempool 数量、TX 回收、未发送包释放和 NUMA 分配。

### 9.4 cache_size 不是越大越好

`cache_size` 可以减少访问全局池的竞争，但太大会导致对象分散在各 lcore cache 中，其他核心拿不到空闲对象。经验上：

- 小程序可以先用 128 或 250。
- lcore 很多时要计算总 cache 占用。
- 对象池较小时不要设置过大的 cache。
- 生产压测时同时观察吞吐和 mempool 可用数量。

## 10. mbuf：包的载体

### 10.1 mbuf 保存什么

`rte_mbuf` 保存两类信息：

- 元数据：端口、队列、packet type、offload 标志、RSS hash、VLAN、时间戳、分段信息。
- 数据缓冲：包数据所在地址、数据长度、总长度、headroom、tailroom。

常用字段和函数：

| API/字段 | 用途 |
| --- | --- |
| `rte_pktmbuf_mtod(m, type)` | 获取当前数据指针 |
| `rte_pktmbuf_data_len(m)` | 当前 segment 数据长度 |
| `rte_pktmbuf_pkt_len(m)` | 整个 packet 总长度 |
| `rte_pktmbuf_append(m, len)` | 在尾部追加空间 |
| `rte_pktmbuf_prepend(m, len)` | 在头部预留空间 |
| `rte_pktmbuf_adj(m, len)` | 去掉头部一段数据 |
| `rte_pktmbuf_trim(m, len)` | 去掉尾部一段数据 |
| `rte_pktmbuf_free(m)` | 释放 mbuf 链 |

### 10.2 headroom

默认 mbuf 在数据前面保留 headroom，方便封装新头部，例如加 VLAN、隧道头、以太网头。做封装时优先用 `rte_pktmbuf_prepend()`，不要自己粗暴移动指针。

### 10.3 单段包和多段包

小包通常是单段 mbuf。大包、jumbo frame、TSO 或特殊接收路径可能产生多段 mbuf 链。

处理多段包时要小心：

- `rte_pktmbuf_mtod()` 只拿到第一个 segment 的数据。
- `data_len` 是当前 segment 长度，`pkt_len` 才是整个包长度。
- 如果协议头跨 segment，直接强转结构体会出错。
- 需要使用 `rte_pktmbuf_read()` 或自己处理 segment 遍历。

入门程序可以先禁用 jumbo，确保协议头在第一个 segment，再逐步支持复杂场景。

### 10.4 offload 标志

mbuf 中的 `ol_flags` 和相关字段告诉 PMD 哪些工作由硬件处理，或硬件已经处理了哪些工作。例如：

- RX checksum 校验结果。
- TX checksum offload 请求。
- VLAN strip/insert。
- TCP segmentation offload。
- RSS hash。

使用 offload 的基本步骤：

1. 通过 `rte_eth_dev_info_get()` 查看设备能力。
2. 在 `rte_eth_conf` 或 queue conf 中打开对应 offload。
3. 在 mbuf 中设置对应字段和标志。
4. 用抓包、统计、对端校验确认结果。

不要只设置 mbuf 标志却忘了配置端口能力，也不要在设备不支持时强行假设 offload 生效。

## 11. ring：跨核队列

### 11.1 ring 的典型用途

`rte_ring` 是固定大小循环队列，通常存放指针。典型场景：

- RX lcore 把包交给 worker lcore。
- worker lcore 把处理完的包交给 TX lcore。
- 控制面把配置更新任务发给数据面。
- 对象池之外的自定义消息队列。

### 11.2 单生产者/多生产者，单消费者/多消费者

ring API 有不同并发语义：

| 模式 | 适用场景 | 优点 |
| --- | --- | --- |
| SP/SC | 一个生产者，一个消费者 | 最快，约束最强 |
| MP/SC | 多生产者，一个消费者 | 多输入汇聚 |
| SP/MC | 一个生产者，多消费者 | 少见，需要明确分发语义 |
| MP/MC | 多生产者，多消费者 | 最通用，成本更高 |

能用 SP/SC 就不要无脑用 MP/MC。数据面设计里，明确“谁写、谁读”本身就是性能优化。

### 11.3 burst 与 bulk

ring 支持批量入队/出队。一般优先使用批处理：

```c
unsigned n = rte_ring_enqueue_burst(ring, (void **)pkts, nb_pkts, NULL);
unsigned m = rte_ring_dequeue_burst(ring, (void **)pkts, BURST_SIZE, NULL);
```

批处理的价值：

- 减少原子操作次数。
- 减少函数调用成本。
- 更容易和 `rte_eth_rx_burst()`、`rte_eth_tx_burst()` 对齐。

## 12. timer 与时间

DPDK 提供 timer 库，用于在数据面程序里执行周期性或一次性回调。它通常依赖 EAL 的时间源，例如 TSC。

典型用途：

- 周期性打印统计。
- 定期老化流表。
- 定期刷新控制面状态。
- 触发低频维护任务。

开发建议：

- 高频数据面不要为每个包设置 timer。
- timer 回调不要做阻塞 IO。
- 回调中不要执行复杂内存分配。
- 流表老化可采用分片扫描，避免一次扫完整表造成抖动。

很多生产系统会把定时任务放到独立 service lcore 或控制线程，避免污染收发包核心。
