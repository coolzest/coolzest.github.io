---
title: 网络错误日志（NEL）
date: 2026-04-25
description: "MDN HTTP 指南：网络错误日志（NEL）"
categories:
  - 网络安全
  - HTTP
tags:
  - HTTP
  - MDN
comments: true
---
!!! warning "来源声明"
    MDN 暂未提供该页面的官方中文译文；本文基于英文原文翻译整理：[https://mdn.org.cn/zh-CN/docs/Web/HTTP/Guides/Network_Error_Logging](https://mdn.org.cn/zh-CN/docs/Web/HTTP/Guides/Network_Error_Logging)。
    内容版权归 MDN contributors 所有，并受 Creative Commons 许可约束；本站仅用于个人学习归档与排版适配。

# 网络错误记录 (NEL)

_实验性_

网络错误日志记录是一种可以通过 `NEL` HTTP _[响应头](https://mdn.org.cn/en-US/docs/Glossary/Response_header)_ 配置的机制。此实验性标头允许网站和应用程序选择接收有关来自支持浏览器的失败（如果需要，成功）网络获取的报告。

报告被发送到 `Report-To` 标头中定义的报告组。

## 用法

Web 应用程序通过 NEL 标头选择此行为，该标头是一个 _[JSON 编码](https://mdn.org.cn/en-US/docs/Glossary/Response_header)_ 对象：

```http
NEL: { "report_to": "nel",
       "max_age": 31556952 }
```

需要浏览器认为安全的来源。

可以在 NEL 标头中指定以下对象键：

- 报告对象
  - ：向 [报告API](https://mdn.org.cn/en-US/docs/Web/API/Reporting_API) 组发送网络错误报告（见下文）。
- 最大年龄
  - ：指定策略的生命周期，以秒为单位（类似于 HSTS 策略受时间限制）。引用的报告组的生命周期应至少与 NEL 策略一样长。
- 包含子域
  - ：如果`true`，则该NEL策略也对源站的所有子域启用，但仅针对DNS解析过程中出现的网络错误。如果 `include_subdomains` 不存在、为 `false` 或其他（非 DNS 相关）网络错误，则不会为子域启用 NEL 策略。报告组还必须设置为包含子域，此选项才能生效。
- 成功分数
  - ：0 到 1 之间的浮点值，指定要报告的**成功**网络请求的比例。默认为 0，因此如果 JSON 负载中不存在密钥，则不会报告成功的网络请求。
- 失败分数
  - ：0 到 1 之间的浮点值，指定要报告的 **失败** 网络请求的比例。默认为 1，因此如果 JSON 负载中不存在密钥，则将报告所有失败的网络请求。

上面引用的报告组在 `Report-To` 标头中以通常的方式定义，例如：

```http
Report-To: { "group": "nel",
             "max_age": 31556952,
             "endpoints": [
              { "url": "https://example.com/csp-reports" }
             ]
           }
```

## 错误报告

在这些示例中，显示了报告 API 响应内容。顶级 **`"body"`** 键包含网络错误报告。

### HTTP 400（错误请求）响应

```json
{
  "age": 20,
  "type": "network-error",
  "url": "https://example.com/previous-page",
  "body": {
    "elapsed_time": 338,
    "method": "POST",
    "phase": "application",
    "protocol": "http/1.1",
    "referrer": "https://example.com/previous-page",
    "sampling_fraction": 1,
    "server_ip": "192.0.2.172",
    "status_code": 400,
    "type": "http.error",
    "url": "https://example.com/bad-request"
  }
}
```

### DNS 名称未解析

请注意，本报告中的阶段设置为`dns`，并且没有`server_ip`可包含。

```json
{
  "age": 20,
  "type": "network-error",
  "url": "https://example.com/previous-page",
  "body": {
    "elapsed_time": 18,
    "method": "POST",
    "phase": "dns",
    "protocol": "http/1.1",
    "referrer": "https://example.com/previous-page",
    "sampling_fraction": 1,
    "server_ip": "",
    "status_code": 0,
    "type": "dns.name_not_resolved",
    "url": "https://example-host.com/"
  }
}
```

网络错误的类型可能是规范中的以下预定义值之一，但浏览器可以添加并发送自己的错误类型：

- `dns.unreachable`
  - : 用户的DNS服务器无法访问
- `dns.name_not_resolved`
  - ：用户的 DNS 服务器已响应，但无法解析所请求的 URI 的 IP 地址。
- `dns.failed`
  - ：由于之前的错误未涵盖的原因（例如 SERVFAIL），对 DNS 服务器的请求失败
- `dns.address_changed`
  - ：出于安全原因，如果发送原始报告的服务器 IP 地址与错误生成时的当前服务器 IP 地址不同，则报告数据将降级为仅包含有关此问题的信息，并将类型设置为`dns.address_changed`。
- `tcp.timed_out`
  - ：与服务器的 TCP 连接超时
- `tcp.closed`
  - ：TCP连接被服务器关闭
- `tcp.reset`
  - ：TCP连接被重置
- `tcp.refused`
  - : TCP 连接被服务器拒绝
- `tcp.aborted`
  - : TCP 连接被中止
- `tcp.address_invalid`
  - : IP 地址无效
- `tcp.address_unreachable`
  - : IP地址不可达
- `tcp.failed`
  - ：由于之前的错误未涵盖的原因，TCP 连接失败
- `http.error`
  - ：用户代理成功收到响应，但状态代码为[4xx](https://httpwg.org/specs/rfc9110.html#status.4xx)或[5xx](https://httpwg.org/specs/rfc9110.html#status.5xx)
- `http.protocol.error`
  - ：由于 HTTP 协议错误，连接被中止
- `http.response.invalid`
  - ：响应为空、内容长度不匹配、编码不正确和/或其他阻止用户代理处理响应的条件
- `http.response.redirect_loop`
  - ：由于检测到重定向循环，请求被中止
- `http.failed`
  - ：由于之前的错误未涵盖的 HTTP 协议错误，导致连接失败

## 规格

_规范信息请参见 MDN 译文页面。_

## 浏览器兼容性



## 参见

- [报告API](https://mdn.org.cn/en-US/docs/Web/API/Reporting_API)
