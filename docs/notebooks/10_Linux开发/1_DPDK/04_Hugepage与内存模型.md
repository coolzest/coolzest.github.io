---
title: Hugepage 与 DPDK 内存模型
date: 2026-04-22
description: "理解 hugepage、NUMA 内存预留和 DPDK 内存启动参数。"
categories:
  - Linux 开发
  - DPDK
tags:
  - DPDK
  - Linux
  - 高性能网络
comments: true
---

# Hugepage 与 DPDK 内存模型

> DPDK 的高速路径离不开内存布局，本章专门讲 hugepage、动态内存、legacy 模式和常见 EAL 内存参数。

## 5. Hugepage 与 DPDK 内存模型

### 5.1 为什么需要 hugepage

网卡 DMA 和高速包处理需要频繁访问大量内存。如果使用普通 4 KB 页：

- 页表项很多，TLB miss 变多。
- 地址转换成本上升。
- 大量小页更难管理 DMA 映射。

Hugepage 使用更大的页，例如 2 MB 或 1 GB，可以显著减少页表和 TLB 压力。DPDK 默认使用 hugetlbfs 中的 hugepage 来支撑内存池、memzone 和部分内部结构。

### 5.2 临时配置 2 MB hugepage

```bash
# 预留 1024 个 2 MB hugepage，也就是 2 GB
echo 1024 | sudo tee /sys/kernel/mm/hugepages/hugepages-2048kB/nr_hugepages

grep Huge /proc/meminfo

sudo mkdir -p /mnt/huge
sudo mount -t hugetlbfs nodev /mnt/huge
mount | grep huge
```

NUMA 机器上最好按 node 预留：

```bash
echo 1024 | sudo tee /sys/devices/system/node/node0/hugepages/hugepages-2048kB/nr_hugepages
echo 1024 | sudo tee /sys/devices/system/node/node1/hugepages/hugepages-2048kB/nr_hugepages
```

### 5.3 持久化 hugepage

`/etc/sysctl.d/80-dpdk-hugepage.conf`：

```conf
vm.nr_hugepages = 2048
```

应用：

```bash
sudo sysctl --system
```

`/etc/fstab`：

```fstab
nodev /mnt/huge hugetlbfs defaults 0 0
```

挂载：

```bash
sudo mkdir -p /mnt/huge
sudo mount /mnt/huge
```

### 5.4 1 GB hugepage

1 GB hugepage 通常需要启动参数预留。示例：

```text
default_hugepagesz=1G hugepagesz=1G hugepages=8
```

然后更新 grub 并重启。不同发行版命令不同，常见形式：

```bash
sudo grub2-mkconfig -o /boot/grub2/grub.cfg
sudo reboot
```

使用 1 GB 页时要更谨慎，因为它更难动态调整，且会一次性占用大块物理内存。优先在生产压测通过后再启用。

### 5.5 DPDK 动态内存模式与 legacy 模式

现代 DPDK 默认倾向动态内存模式。应用运行时可以按需映射和释放 hugepage。好处是启动时不用一次吃掉所有内存，资源利用更灵活。

legacy 模式通过 `--legacy-mem` 开启，更接近早期 DPDK 行为：启动时预留内存，运行期不再动态扩缩。它在某些要求 IOVA 连续大块内存的场景仍有价值。

常用内存相关 EAL 参数：

| 参数 | 作用 | 使用建议 |
| --- | --- | --- |
| `--huge-dir=/mnt/huge` | 指定 hugetlbfs 挂载点 | 多个挂载点或自定义路径时使用 |
| `--socket-mem=1024,1024` | 每个 NUMA socket 预留内存 MB | 多 NUMA 生产环境常用 |
| `--socket-limit=2048,2048` | 限制每个 socket 最大内存 | 防止动态模式吃太多 |
| `--legacy-mem` | 启用 legacy 内存模式 | 兼容或特殊 IOVA 场景 |
| `--single-file-segments` | 每个 memseg list 使用单文件 | 降低文件描述符压力 |
| `--in-memory` | 使用匿名映射，不依赖 hugetlbfs 文件 | 不需要多进程共享时可考虑 |
| `--file-prefix=name` | 修改 hugepage backing file 前缀 | 同机多个 primary 进程必须规划 |
| `--no-huge` | 不用 hugepage | 只适合功能验证，性能通常不可接受 |
