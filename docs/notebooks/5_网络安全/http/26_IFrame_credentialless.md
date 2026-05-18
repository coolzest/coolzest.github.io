---
title: 无凭据 iframe
date: 2026-04-25
description: "MDN HTTP 指南：无凭据 iframe"
categories:
  - 网络安全
  - HTTP
tags:
  - HTTP
  - MDN
comments: true
---
!!! warning "来源声明"
    MDN 暂未提供该页面的官方中文译文；本文基于英文原文翻译整理：[https://mdn.org.cn/zh-CN/docs/Web/HTTP/Guides/IFrame_credentialless](https://mdn.org.cn/zh-CN/docs/Web/HTTP/Guides/IFrame_credentialless)。
    内容版权归 MDN contributors 所有，并受 Creative Commons 许可约束；本站仅用于个人学习归档与排版适配。

# IFrame 无凭据

_实验性_

**IFrame 无凭证** 为开发人员提供了一种机制，可以使用新的临时上下文在 `iframe` 秒内加载第三方资源。它无法访问其常规来源的网络、cookie 和存储数据。它使用顶级文档生命周期本地的新上下文。作为回报，可以取消 `Cross-Origin-Embedder-Policy` (COEP) 嵌入规则，因此设置了 COEP 的文档可以嵌入没有设置 COEP 的第三方文档。

## 问题

各种 Web API 功能只能在选择跨域隔离的网站上使用 - 例如 `SharedArrayBuffer` 和 `high-resolution timers`。这是因为此类功能在[幽灵袭击](https://spectreattack.com/spectre.pdf)中存在被利用的风险，受害者的机密信息可能通过侧通道泄露并被攻击者捕获。

要选择跨源隔离，资源必须使用值为 `same-origin` 的 `Cross-Origin-Opener-Policy`（保护您的源免受攻击）和值为 `credentialless` 或 `require-corp` 的 `Cross-Origin-Embedder-Policy`（保护受害者免受您的源的攻击）。后者阻止文档加载任何未使用 `Cross-Origin-Resource-Policy` 或 [跨域资源共享](https://mdn.org.cn/en-US/docs/Web/HTTP/Guides/CORS) 显式授予文档权限的经过凭据的跨域资源。

限制跨域隔离采用的关键问题是，`Cross-Origin-Embedder-Policy`是递归应用的——任何加载到带有`Cross-Origin-Embedder-Policy`集的文档中`<iframe>`的第三方内容也必须部署`Cross-Origin-Embedder-Policy`才能成功嵌入。对于在应用程序中嵌入第三方内容（例如广告网络内容）的开发人员来说，这是一个问题，因为他们通常无法控制它 - 到目前为止，他们唯一的选择是等待第三方内容提供商实施`Cross-Origin-Embedder-Policy`。

这个问题可以通过IFrame credentialless来解决。

## 解决方案 — Iframe 无凭证

通过将 [`credentialless`](https://mdn.org.cn/en-US/docs/Web/HTML/Reference/Elements/iframe#credentialless) 属性应用于`<iframe>`，或者将等效的 DOM 属性 — `HTMLIFrameElement.credentialless` — 设置为 `true`，即可将 `<iframe>` 设为无凭据。

```html
<iframe
  src="https://en.wikipedia.org/wiki/Spectre_(security_vulnerability)"
  title="Spectre vulnerability Wikipedia page"
  width="960"
  height="600"
  credentialless></iframe>
```

或者：

```html
<iframe width="960" height="600"> </iframe>
```

```js
const iframeElem = document.querySelector("iframe");

iframeElem.credentialless = true;
iframeElem.title = "Spectre vulnerability Wikipedia page";
iframeElem.src =
  "https://en.wikipedia.org/wiki/Spectre_(security_vulnerability)";
```

> [！笔记]
> 可以通过嵌入在 `<iframe>` 中的文档来查询 `window.credentialless` 属性，以测试它是否在无凭据上下文中运行。值 `true` 表示嵌入 `<iframe>` 是无凭据的。

这导致无凭证`<iframe>`内的文档使用新的、短暂的上下文加载——这些上下文无法访问与其来源相关的数据；例如 [曲奇饼](https://mdn.org.cn/en-US/docs/Web/HTTP/Guides/Cookies) 和 [本地存储](https://mdn.org.cn/en-US/docs/Web/API/Window/localStorage)。无凭证存储是单独分区的，存储键由随机数（“使用一次的次数”）值修改，每个顶级文档设置一次。因此，在一个无凭据 `<iframe>` 中设置的 cookie 只能从嵌入同一顶级文档下的其他同源无凭据 `<iframe>` 访问。

随机数对于作为同一顶级文档的后代的每个无凭据 iframe 是共享的，但对于用户导航到的每个不同的顶级文档来说是不同的，并且一旦用户导航离开就不再可以访问。无凭据 IFrame 不跨不同页面共享存储。回到上面提到的cookie，重新加载文档将在不同的上下文中加载无凭据的`<iframe>`，因此之前设置的cookie将不可用。

此外：

- 无凭据 iframe 打开的弹出窗口以 [`rel="noopener"`](https://mdn.org.cn/en-US/docs/Web/HTML/Reference/Attributes/rel/noopener) 设置打开。这可以防止 OAuth 弹出流在无凭据 iframe 中使用。
- 浏览器自动填充或密码管理器功能在无凭据 `<iframe>`s 中不可用。

这样做的结果是，加载到无凭据`<iframe>`中的文档实际上是普通版本或“公共”版本，未使用任何用户的敏感信息进行定制。由于这些文档中没有可泄露的敏感信息，因此它们对于潜在的攻击者来说没有任何用处，因此对于这些 IFrame 的跨源嵌入器策略要求被删除。

## 子 IFrame 内的递归无凭据

如果在 `<iframe>` 上设置 `credentialless`，而该`<iframe>` 嵌入到加载到其中的文档中，则这些子`<iframe>` 将继承无凭据设置。

## 规格

_规范信息请参见 MDN 译文页面。_

## 浏览器兼容性



## 参见

- `Cross-Origin-Opener-Policy`
- `Cross-Origin-Embedder-Policy`
- `Cross-Origin-Resource-Policy`
- [跨域资源共享](https://mdn.org.cn/en-US/docs/Web/HTTP/Guides/CORS)
- `<iframe>` [`credentialless`](https://mdn.org.cn/en-US/docs/Web/HTML/Reference/Elements/iframe#credentialless) 属性
- `HTMLIFrameElement.credentialless`
