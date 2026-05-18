---
title: Fetch 元数据
date: 2026-04-25
description: "MDN HTTP 指南：Fetch 元数据"
categories:
  - 网络安全
  - HTTP
tags:
  - HTTP
  - MDN
comments: true
---
!!! warning "来源声明"
    MDN 暂未提供该页面的官方中文译文；本文基于英文原文翻译整理：[https://mdn.org.cn/zh-CN/docs/Web/HTTP/Guides/Fetch_metadata](https://mdn.org.cn/zh-CN/docs/Web/HTTP/Guides/Fetch_metadata)。
    内容版权归 MDN contributors 所有，并受 Creative Commons 许可约束；本站仅用于个人学习归档与排版适配。

# 获取元数据

**获取元数据** 是一组 HTTP 请求标头的术语，这些标头向服务器提供有关发出请求的上下文的信息。

除此之外，获取元数据可以让服务器知道：

- 该请求是否表示文档之间的导航，或者对子资源的请求，或者是由 JavaScript 显式发出的，例如使用 `fetch()` API。

- 资源的请求者和被请求的资源之间的关系：是否是同源、同站、还是来自完全不同的站点。

通过使用这些标头中的信息来允许或拒绝特定请求，服务器可以实现针对[_跨域攻击_](#cross-origin-attacks)（例如[跨站点请求伪造 (CSRF)](https://mdn.org.cn/en-US/docs/Web/Security/Attacks/CSRF)和各种[跨站点泄漏](https://mdn.org.cn/en-US/docs/Web/Security/Attacks/XS-Leaks)）的防御。

## 获取元数据标头

[获取元数据规范](https://w3c.github.io/webappsec-fetch-metadata/)定义了四个获取元数据标头：

- `Sec-Fetch-Site`
- `Sec-Fetch-Mode`
- `Sec-Fetch-User`
- `Sec-Fetch-Dest`

与所有 `Sec-` 前缀标头一样，这些是禁止的请求标头，这意味着它们不能由网站的前端代码设置或修改。

### 秒取目标

该标头指示请求的_目的地_。该属性在 Fetch API 中定义，并作为 `Request.destination` 属性公开。

我们可以粗略地将其视为返回资源的使用方式。

对于大多数替换元素，标头的值会命名该资源将用于的元素，例如 `iframe`、`object`、`audio` 或 `video`。值 `image` 表示该资源将用作由替换元素引用的图像，例如 HTML `img` 元素、CSS `background-image` 属性、SVG `image` 或 Web 平台中使用从子资源加载的图像的任何其他位置。

其他一些有趣的目的地值包括：

- `document`
  - ：请求是针对作为顶级导航目标的新文档（例如，用户单击页面中的链接或提交表单）。

- `script`
  - ：资源将用作从 HTML `script` 元素加载的脚本或在 Web Worker 中调用`importScripts()`。

更具体的值用于指示资源用作脚本的其他位置，例如工作集（`audioworklet`和`paintworklet`）和工作人员（`sharedworker`、`serviceworker`和`worker`）。

- `empty`
  - ：请求没有定义的目的地：除了其他可能的原因之外，如果请求是 `fetch()` 调用的结果，则这是给出的值。

有关可能值的完整集合，请参阅此标头的 `reference page`。

### 秒取模式

该标头指示请求的_模式_。与_目的地_一样，模式在 [Fetch API](https://mdn.org.cn/en-US/docs/Web/API/Fetch_API) 中定义，并作为 `Request.mode` 属性公开。

其最常用的值是：

- `navigate`
  - ：请求表示文档之间的导航（例如，用户单击链接）。

- `no-cors`
  - ：请求是在`no-cors`模式下发出的。

这意味着允许跨域，而无需服务器发送适当的 [跨域资源共享](https://mdn.org.cn/en-US/docs/Web/HTTP/Guides/CORS) 标头，但限制是客户端中运行的 JavaScript 无法访问响应（它是_opaque_）。

这是加载图像、字体、脚本和样式表等子资源的页面的默认模式，并解释了为什么默认情况下允许其他站点使用您站点的子资源，即使您尚未配置 CORS 来允许它。

- `cors`
  - ：如果请求是跨源的，那么服务器必须使用适当的[跨域资源共享](https://mdn.org.cn/en-US/docs/Web/HTTP/Guides/CORS)标头进行响应，否则请求将失败。如果服务器确实使用适当的 CORS 标头进行响应，则响应正文和某些标头将可供调用者使用。

当请求者需要访问返回的资源（例如，从服务器检索一些 JSON 的 fetch 调用）时，最常见的是使用 [获取API](https://mdn.org.cn/en-US/docs/Web/API/Fetch_API) 从 JavaScript 发出的跨源请求。

- `same-origin`
  - ：仅当请求者与所请求的资源同源时才允许该请求。

### Sec-Fetch-Site

该标头指示所请求资源的来源与资源请求者的来源之间的关系。

它表明请求者是否来自：

- 与请求的资源相同的来源。
- 来源不同，但地点相同。
- 另一个网站。

例如，如果用户单击`https://books.example.org/authors`页面中的链接，浏览器会发出请求以获取链接目标中指定的文档。下表显示了不同链接目标值的关联 `Sec-Fetch-Site` 标头的值：

| 链接目标 | `Sec-Fetch-Site`值 |
| ---------------------------------- | ---------------------- |
| `https://books.example.org/titles` | `same-origin` |
| `https://login.example.org/` | `same-site` |
| `https://books.example.com/titles` | `cross-site` |

类似的映射适用于其他 HTTP 请求，例如：

- 通过 `form` 元素的 [`action`](https://mdn.org.cn/en-US/docs/Web/HTML/Reference/Elements/form#action) 属性提交表单。
- 对图像、字体或脚本等子资源的请求。
- 使用 `fetch()` API 发出的请求。

对于没有站点作为请求者的请求，`Sec-Fetch-Site` 标头也可能具有值 `none`，包括例如用户在浏览器地址栏中键入 URL 或单击书签时发出的请求。规范将其称为 [用户直接发起的请求](https://w3c.github.io/webappsec-fetch-metadata/#directly-user-initiated)。

### Sec-获取-用户

仅当请求是由用户操作（例如单击链接）发起时才包含此标头，并且如果包含，则始终具有值 `?1`。

## 跨域攻击

获取元数据对于防御“跨源攻击”特别有用。这些攻击通常针对拥有合法网站帐户并登录该网站的用户。攻击者创建一个网站，向合法网站发出_跨域请求_，然后诱骗用户执行该请求。

> [！笔记]
> 我们在本指南中使用术语“跨源攻击”，尽管许多攻击通常称为“跨站点攻击”。
>
> 起源是一个比站点更具限制性的概念。特别是，站点包含域的子域，而源不包含：因此 `https://example.org` 和 `https://login.example.org` 是同一站点，但源不同。
>
> 这意味着虽然所有跨站点攻击都是跨源攻击，但某些跨源攻击并不是跨站点攻击。例如，如果攻击者获得了站点子域的控制权，则他们可以使用_跨域_、_同站点_请求来攻击该站点。为了包含这些攻击，我们使用限制性更强的术语。

例如，攻击者的站点可能包含提交到合法站点的 `form` 元素。对于某些跨域攻击，根本不需要用户交互：攻击者的页面只需在页面加载时向合法站点执行`fetch()`请求，然后用户只需打开攻击者的页面即可执行跨域请求。

由于请求来自用户的浏览器，因此它将包含合法站点为用户设置的任何 cookie，包括合法站点用于识别用户身份的 cookie。因此，该请求将被授予该用户的权限。

我们可以区分两种跨域攻击：

- [跨站请求伪造（CSRF）](https://mdn.org.cn/en-US/docs/Web/Security/Attacks/CSRF) 攻击：在这类攻击中，跨源请求会使用攻击者提供的参数，在合法服务器上执行某些有实际影响的操作。例如，该请求可能要求服务器将资金从目标用户的账户转入攻击者的账户。

- [跨站点泄漏](https://mdn.org.cn/en-US/docs/Web/Security/Attacks/XS-Leaks)：在这些攻击中，攻击者通常通过诸如[错误事件](https://mdn.org.cn/en-US/docs/Web/Security/Attacks/XS-Leaks#leaking_page_existence_using_error_events)之类的旁路渠道，使用请求来获取有关用户与目标站点的关系的信息。

大多数网站都会希望拒绝某些跨域请求，同时允许其他请求：例如，如果您拒绝所有跨域请求，则没有人能够从其他站点导航到您的站点！

使用获取元数据，服务器可以根据上下文的详细信息构建允许或拒绝跨源请求的策略。

## 资源隔离策略

一种常见的策略称为_资源隔离策略_。当服务器收到请求时，它会检查请求的获取元数据标头以仅允许：

- 同源请求（有时是同站点请求，如果您信任您的子域）。
- 来自其他来源的顶级导航请求，以便用户可以通过单击其他网站中的链接来访问您的网站。
- 对旨在跨域访问的特定端点的请求，包括任何使用 [跨域资源共享](https://mdn.org.cn/en-US/docs/Web/HTTP/Guides/CORS) 的请求。

例如，以下[表达](https://mdn.org.cn/en-US/docs/Learn_web_development/Extensions/Server-side/Express_Nodejs)代码仅允许同源请求、用户直接发起的请求和导航。

```js
function isAllowed(req) {
  // Allow same-origin requests
  // Allow directly user-initiated requests (from bookmarks, address bar etc.)
  const secFetchSite = req.headers["sec-fetch-site"];
  if (secFetchSite === "same-origin" || secFetchSite === "none") {
    return true;
  }

  // Allow cross-site navigations, such as clicking links
  const secFetchMode = req.headers["sec-fetch-mode"];
  if (secFetchMode === "navigate" && req.method === "GET") {
    return true;
  }

  // Deny everything else
  return false;
}

app.get("/admin", (req, res) => {
  res.setHeader("Vary", "sec-fetch-site, sec-fetch-mode");
  if (isAllowed(req)) {
    // Respond with the admin page if the user is admin
    getAdminPage(req, res);
  } else {
    res.status(403).send("Forbidden");
  }
});
```

请注意，它还发送 `Vary` 响应标头。这确保了如果响应被缓存，则缓存的响应将仅提供给与我们正在使用的 Fetch 元数据标头具有相同值的请求。

[资源隔离策略](https://xsleaks.dev/docs/defenses/isolation-policies/resource-isolation/)页面提供了更多资源隔离策略的示例代码。

## 参见

- [CSRF](https://mdn.org.cn/en-US/docs/Web/Security/Attacks/CSRF)
- [跨站点泄漏](https://mdn.org.cn/en-US/docs/Web/Security/Attacks/XS-Leaks)
- [使用获取元数据保护您的资源免受网络攻击](https://web.dev/articles/fetch-metadata) (web.dev)
- [获取元数据](https://xsleaks.dev/docs/defenses/opt-in/fetch-metadata/)（XS-Leaks 维基）
