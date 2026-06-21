---
title: 跨源资源策略（CORP）
date: 2026-04-25
description: "MDN HTTP 指南：跨源资源策略（CORP）"
categories:
  - 网络安全
  - HTTP
tags:
  - HTTP
  - MDN
comments: true
---
!!! warning "来源声明"
    MDN 暂未提供该页面的官方中文译文；本文基于英文原文翻译整理：[https://mdn.org.cn/zh-CN/docs/Web/HTTP/Guides/Cross-Origin_Resource_Policy](https://mdn.org.cn/zh-CN/docs/Web/HTTP/Guides/Cross-Origin_Resource_Policy)。
    内容版权归 MDN contributors 所有，并受 Creative Commons 许可约束；本站仅用于个人学习归档与排版适配。

# 跨源资源策略 (CORP)

**跨源资源策略** 是由 [`Cross-Origin-Resource-Policy` HTTP 标头](https://mdn.org.cn/en-US/docs/Web/HTTP/Reference/Headers/Cross-Origin-Resource-Policy) 设置的策略，允许网站和应用程序选择保护来自其他来源的某些请求（例如使用 `<script>` 和 `<img>` 等元素发出的请求），以减轻推测性旁路攻击（如 [幽灵](<https://en.wikipedia.org/wiki/Spectre_(security_vulnerability)>）以及跨站点脚本包含攻击。
CORP 是默认同源策略之外的附加保护层。

> [！笔记]
> 该策略仅对 [`no-cors`](https://fetch.spec.whatwg.org/#concept-request-mode) 请求有效，这些请求默认针对 CORS 安全列表方法/标头发出。

由于此策略是通过 _[响应头](https://mdn.org.cn/en-US/docs/Glossary/Response_header)_ 表达的，因此不会阻止实际请求 - 相反，浏览器通过剥离响应正文来防止 _result_ 泄露。

## 用法

> [！笔记]
> 由于 [Chrome 中的错误](https://crbug.com/1074261)，设置 Cross-Origin-Resource-Policy 可能会破坏 PDF 渲染，从而阻止访问者阅读某些 PDF 的第一页。在生产环境中使用此标头时请务必小心。

Web 应用程序通过 `Cross-Origin-Resource-Policy` HTTP 响应标头设置跨源资源策略，该响应标头接受以下三个值之一：

- `same-site`
  - ：只有来自同一_Site_的请求才能读取资源。

    > [！警告]
    > 这比原点安全性低。 [检查两个来源是否同一站点的算法](https://html.spec.whatwg.org/multipage/origin.html#same-site) 在 HTML 标准中定义，涉及检查_可注册域_。

- `same-origin`
  - ：只有来自同一个源（即方案+主机+端口）的请求才能读取资源。
- `cross-origin`
  - ：来自任何_origin_（同站点和跨站点）的请求都可以读取资源。当使用 COEP 时这很有用（见下文）。

```http
Cross-Origin-Resource-Policy: same-site | same-origin | cross-origin
```

在跨源资源策略检查期间，如果设置了标头，浏览器将拒绝从不同源/站点发出的 `no-cors` 请求。

## 与跨域嵌入策略 (COEP) 的关系

当在文档上使用 `Cross-Origin-Embedder-Policy` HTTP 响应标头时，可用于要求子资源与文档同源，或者附带 `Cross-Origin-Resource-Policy` HTTP 响应标头以指示它们可以嵌入。这就是 `cross-origin` 值存在的原因。

## 历史

该概念最初于 2012 年提出（作为 `From-Origin` 标头），但在 2018 年第二季度提出[复活了](https://github.com/whatwg/fetch/issues/687)，并在 Safari 和 Chromium 中实现。

2018 年初，两个名为 _Meltdown_ 和 _Spectre_ 的侧通道硬件漏洞被披露。这些漏洞由于竞态条件而导致敏感数据泄露，竞态条件是为提高性能而设计的推测执行功能的一部分。

跨源资源策略是作为站点阻止不需要的 `no-cors` 跨源请求的直接方法而开发的。这是针对类似 Spectre 攻击的有效防御，因为浏览器会在攻击者访问响应之前将其正文从给定响应中剥离。

## 规格

_规范信息请参见 MDN 译文页面。_

## 浏览器兼容性



## 参见

- `Cross-Origin-Resource-Policy` HTTP 标头
