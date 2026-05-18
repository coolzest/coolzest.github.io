---
title: ethdev 端口初始化与收发包
date: 2026-04-22
description: "使用 ethdev 初始化端口，写出最小收包、转发和包解析程序。"
categories:
  - Linux 开发
  - DPDK
tags:
  - DPDK
  - Linux
  - 高性能网络
comments: true
---

# ethdev 端口初始化与收发包

> 这一章进入真正的网卡编程：端口、队列、descriptor、burst 收发、最小示例和基础包解析。

## 13. ethdev 端口初始化

### 13.1 初始化顺序

一个端口通常按这个顺序启动：

1. `rte_eth_dev_info_get()` 获取设备能力。
2. 设置 `struct rte_eth_conf`。
3. `rte_eth_dev_configure()` 配置 RX/TX queue 数量。
4. `rte_eth_dev_adjust_nb_rx_tx_desc()` 调整 descriptor 数量。
5. `rte_eth_rx_queue_setup()` 配置 RX queue。
6. `rte_eth_tx_queue_setup()` 配置 TX queue。
7. `rte_eth_dev_start()` 启动端口。
8. 可选：`rte_eth_promiscuous_enable()`。
9. 读取 MAC、链路状态、统计信息。

### 13.2 descriptor 数量

RX/TX descriptor 不是越大越好：

- 太小容易丢包或无法吸收突发。
- 太大增加缓存占用和延迟。
- 不同 PMD 有最小值、最大值和对齐要求。

常见入门值：

```c
#define RX_RING_SIZE 1024
#define TX_RING_SIZE 1024
```

正式压测时可比较 512、1024、2048、4096 的吞吐、延迟和丢包。

### 13.3 queue 和 lcore 的关系

常见最佳实践：

- 一个 RX queue 通常只由一个 lcore 轮询。
- 一个 TX queue 通常只由一个 lcore 发送。
- 多个 lcore 共享同一 queue 会引入同步和乱序风险。
- 多队列收包依赖 RSS、flow director 或 rte_flow 把流量分散。
- queue 对应的 mempool 尽量在同 NUMA socket 创建。

### 13.4 RSS

RSS 可以按五元组或其他字段把流量分散到多个 RX queue。基本配置包括：

- `mq_mode = RTE_ETH_MQ_RX_RSS`
- `rss_hf` 指定 hash 字段，例如 IPv4、TCP、UDP。
- RX queue 数量大于 1。
- 网卡支持对应 RSS 类型。

RSS 不是负载均衡万能药：

- 单条大流仍可能只落到一个 queue。
- 非 TCP/UDP 流量可能 hash 不均。
- 隧道流量需要确认硬件是否支持 inner RSS。
- 对称 RSS、reta 表和 hash key 需要按业务调整。

## 14. 第一个完整程序：收包并丢弃

这个程序完成最小闭环：

- 初始化 EAL。
- 创建 mbuf pool。
- 初始化所有可用端口。
- 从每个端口的 RX queue 0 批量收包。
- 释放收到的 mbuf。
- 收到 Ctrl+C 后停止端口并清理 EAL。

它不是高性能转发器，但非常适合作为环境验证和开发骨架。

### 14.1 main.c

```c
#include <inttypes.h>
#include <signal.h>
#include <stdbool.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#include <rte_common.h>
#include <rte_eal.h>
#include <rte_errno.h>
#include <rte_ethdev.h>
#include <rte_ether.h>
#include <rte_lcore.h>
#include <rte_mbuf.h>

#define RX_RING_SIZE 1024
#define TX_RING_SIZE 1024
#define NUM_MBUFS 8191
#define MBUF_CACHE_SIZE 250
#define BURST_SIZE 32

static volatile bool force_quit;

static const struct rte_eth_conf port_conf_default = {
    .rxmode = {
        .mq_mode = RTE_ETH_MQ_RX_NONE,
    },
};

static void
signal_handler(int signum)
{
    if (signum == SIGINT || signum == SIGTERM) {
        force_quit = true;
    }
}

static int
port_init(uint16_t port_id, struct rte_mempool *mbuf_pool)
{
    struct rte_eth_conf port_conf = port_conf_default;
    const uint16_t rx_rings = 1;
    const uint16_t tx_rings = 1;
    uint16_t nb_rxd = RX_RING_SIZE;
    uint16_t nb_txd = TX_RING_SIZE;
    struct rte_eth_dev_info dev_info;
    struct rte_eth_txconf txconf;
    struct rte_ether_addr addr;
    int ret;

    if (!rte_eth_dev_is_valid_port(port_id)) {
        return -1;
    }

    ret = rte_eth_dev_info_get(port_id, &dev_info);
    if (ret != 0) {
        fprintf(stderr, "failed to get dev info for port %u: %s\n",
                port_id, strerror(-ret));
        return ret;
    }

    if (dev_info.tx_offload_capa & RTE_ETH_TX_OFFLOAD_MBUF_FAST_FREE) {
        port_conf.txmode.offloads |= RTE_ETH_TX_OFFLOAD_MBUF_FAST_FREE;
    }

    ret = rte_eth_dev_configure(port_id, rx_rings, tx_rings, &port_conf);
    if (ret < 0) {
        return ret;
    }

    ret = rte_eth_dev_adjust_nb_rx_tx_desc(port_id, &nb_rxd, &nb_txd);
    if (ret < 0) {
        return ret;
    }

    ret = rte_eth_rx_queue_setup(
        port_id,
        0,
        nb_rxd,
        rte_eth_dev_socket_id(port_id),
        NULL,
        mbuf_pool
    );
    if (ret < 0) {
        return ret;
    }

    txconf = dev_info.default_txconf;
    txconf.offloads = port_conf.txmode.offloads;

    ret = rte_eth_tx_queue_setup(
        port_id,
        0,
        nb_txd,
        rte_eth_dev_socket_id(port_id),
        &txconf
    );
    if (ret < 0) {
        return ret;
    }

    ret = rte_eth_dev_start(port_id);
    if (ret < 0) {
        return ret;
    }

    ret = rte_eth_macaddr_get(port_id, &addr);
    if (ret == 0) {
        printf("port %u MAC %02" PRIx8 ":%02" PRIx8 ":%02" PRIx8
               ":%02" PRIx8 ":%02" PRIx8 ":%02" PRIx8 "\n",
               port_id,
               addr.addr_bytes[0], addr.addr_bytes[1], addr.addr_bytes[2],
               addr.addr_bytes[3], addr.addr_bytes[4], addr.addr_bytes[5]);
    }

    ret = rte_eth_promiscuous_enable(port_id);
    if (ret != 0) {
        fprintf(stderr, "promiscuous enable failed for port %u: %s\n",
                port_id, rte_strerror(-ret));
    }

    return 0;
}

static void
drop_loop(void)
{
    uint16_t port_id;

    RTE_ETH_FOREACH_DEV(port_id) {
        int socket_id = rte_eth_dev_socket_id(port_id);
        if (socket_id >= 0 && socket_id != (int)rte_socket_id()) {
            printf("warning: port %u is on remote NUMA node %d, current socket %u\n",
                   port_id, socket_id, rte_socket_id());
        }
    }

    printf("entering drop loop on lcore %u\n", rte_lcore_id());

    while (!force_quit) {
        RTE_ETH_FOREACH_DEV(port_id) {
            struct rte_mbuf *bufs[BURST_SIZE];
            const uint16_t nb_rx = rte_eth_rx_burst(port_id, 0, bufs, BURST_SIZE);

            if (unlikely(nb_rx == 0)) {
                continue;
            }

            for (uint16_t i = 0; i < nb_rx; i++) {
                rte_pktmbuf_free(bufs[i]);
            }
        }
    }
}

int
main(int argc, char **argv)
{
    struct rte_mempool *mbuf_pool;
    uint16_t nb_ports;
    uint16_t port_id;
    int ret;

    signal(SIGINT, signal_handler);
    signal(SIGTERM, signal_handler);

    ret = rte_eal_init(argc, argv);
    if (ret < 0) {
        rte_exit(EXIT_FAILURE, "failed to initialize EAL\n");
    }

    nb_ports = rte_eth_dev_count_avail();
    if (nb_ports == 0) {
        rte_exit(EXIT_FAILURE, "no available Ethernet ports\n");
    }

    mbuf_pool = rte_pktmbuf_pool_create(
        "MBUF_POOL",
        NUM_MBUFS * nb_ports,
        MBUF_CACHE_SIZE,
        0,
        RTE_MBUF_DEFAULT_BUF_SIZE,
        rte_socket_id()
    );
    if (mbuf_pool == NULL) {
        rte_exit(EXIT_FAILURE, "cannot create mbuf pool: %s\n", rte_strerror(rte_errno));
    }

    RTE_ETH_FOREACH_DEV(port_id) {
        ret = port_init(port_id, mbuf_pool);
        if (ret != 0) {
            rte_exit(EXIT_FAILURE, "cannot initialize port %u: %s\n",
                     port_id, rte_strerror(-ret));
        }
    }

    drop_loop();

    RTE_ETH_FOREACH_DEV(port_id) {
        printf("stopping port %u\n", port_id);
        rte_eth_dev_stop(port_id);
        rte_eth_dev_close(port_id);
    }

    rte_eal_cleanup();
    printf("bye\n");
    return 0;
}
```

### 14.2 构建

`meson.build`：

```meson
project('dpdk_drop', 'c', default_options: ['warning_level=2'])

dpdk = dependency('libdpdk')

executable(
  'dpdk-drop',
  'main.c',
  dependencies: dpdk,
  c_args: ['-O3', '-march=native']
)
```

构建：

```bash
meson setup build
ninja -C build
```

### 14.3 运行

假设网卡已经绑定到 `vfio-pci`，并且准备好了 hugepage：

```bash
sudo ./build/dpdk-drop -l 1 -n 4 -a 0000:03:00.0
```

如果想用 pcap 虚拟设备做功能验证：

```bash
sudo ./build/dpdk-drop \
  -l 1 -n 4 \
  --vdev=net_pcap0,rx_pcap=input.pcap,tx_pcap=output.pcap
```

### 14.4 这个程序可以怎么扩展

下一步可以逐个加入：

- 统计每秒收包数和字节数。
- 解析 Ethernet、IPv4、TCP/UDP 头。
- 根据目的 MAC 或 IP 决定转发端口。
- 多 queue 和多 lcore。
- RSS 配置。
- TX burst 和未发送包回收。
- ring 串联 RX、worker、TX。
- flow table、ACL、LPM。

## 15. 从 drop 到 forward

一个最小转发循环大概是：

```c
static inline void
forward_burst(uint16_t rx_port, uint16_t tx_port)
{
    struct rte_mbuf *bufs[BURST_SIZE];
    uint16_t nb_rx;
    uint16_t nb_tx;

    nb_rx = rte_eth_rx_burst(rx_port, 0, bufs, BURST_SIZE);
    if (nb_rx == 0) {
        return;
    }

    nb_tx = rte_eth_tx_burst(tx_port, 0, bufs, nb_rx);

    if (unlikely(nb_tx < nb_rx)) {
        for (uint16_t i = nb_tx; i < nb_rx; i++) {
            rte_pktmbuf_free(bufs[i]);
        }
    }
}
```

关键点：

- `rte_eth_tx_burst()` 可能只发送一部分包，剩下的你必须释放或重试。
- 是否重试要看业务。低延迟系统可能宁可丢包；可靠转发系统可能暂存到 ring。
- 不要在循环内为每个包动态分配内存。
- 尽量批处理解析、查表和发送。

## 16. 包解析基础

### 16.1 获取以太网头

```c
struct rte_ether_hdr *eth;

eth = rte_pktmbuf_mtod(m, struct rte_ether_hdr *);
```

判断协议：

```c
uint16_t ether_type = rte_be_to_cpu_16(eth->ether_type);

if (ether_type == RTE_ETHER_TYPE_IPV4) {
    /* parse IPv4 */
}
```

### 16.2 解析 IPv4

```c
struct rte_ipv4_hdr *ip;

ip = (struct rte_ipv4_hdr *)(eth + 1);

uint8_t ihl = (ip->version_ihl & RTE_IPV4_HDR_IHL_MASK) * RTE_IPV4_IHL_MULTIPLIER;
uint32_t src = rte_be_to_cpu_32(ip->src_addr);
uint32_t dst = rte_be_to_cpu_32(ip->dst_addr);
```

正式代码要先检查长度：

```c
if (rte_pktmbuf_data_len(m) < sizeof(struct rte_ether_hdr) + sizeof(struct rte_ipv4_hdr)) {
    rte_pktmbuf_free(m);
    return;
}
```

如果需要支持多段 mbuf，不能只检查第一个 segment 的 `data_len`，要使用 `pkt_len` 和安全读取函数。

### 16.3 修改 MAC 并转发

```c
struct rte_ether_addr new_dst;
struct rte_ether_addr new_src;

rte_ether_addr_copy(&new_dst, &eth->dst_addr);
rte_ether_addr_copy(&new_src, &eth->src_addr);
```

真实 L2 转发会根据端口和邻居表改写：

- 目的 MAC 改成下一跳 MAC。
- 源 MAC 改成本端出接口 MAC。
- 必要时处理 VLAN。
- IP 转发还要 TTL 减一，并更新 IPv4 header checksum，或使用 checksum offload。
