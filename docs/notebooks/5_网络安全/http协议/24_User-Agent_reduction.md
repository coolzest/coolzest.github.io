---
title: User-Agent 缩减
date: 2026-04-25
description: "MDN HTTP 指南：User-Agent 缩减"
categories:
  - 网络安全
  - HTTP
tags:
  - HTTP
  - MDN
comments: true
---
!!! warning "来源声明"
    MDN 暂未提供该页面的官方中文译文；本文基于英文原文翻译整理：[https://mdn.org.cn/zh-CN/docs/Web/HTTP/Guides/User-agent_reduction](https://mdn.org.cn/zh-CN/docs/Web/HTTP/Guides/User-agent_reduction)。
    内容版权归 MDN contributors 所有，并受 Creative Commons 许可约束；本站仅用于个人学习归档与排版适配。

# 用户代理减少

**减少用户代理**是一项被广泛接受的浏览器举措，旨在减少用户代理 (UA) 字符串中提供的隐私敏感信息量。

本文展示了由于用户代理减少而导致的 UA 字符串的差异，并解释了如何在需要时访问经过编辑的和附加的 UA 信息。

## 背景

用户代理 (UA) 字符串（在 `User-Agent` HTTP 标头和相关 API 功能（例如 `Navigator.userAgent`、`Navigator.appVersion` 和 `Navigator.platform`）中可用）允许服务器和网络对等方识别请求用户代理的应用程序、操作系统、供应商和/或版本。

### 浏览器检测

理论上，UA 字符串对于检测浏览器和提供代码以解决特定于浏览器的错误或缺乏功能支持非常有用。然而，这是**不可靠**并且**不推荐**：

- 未来的浏览器将修复错误并添加对新功能的支持，因此您的浏览器检测代码需要定期更新，以避免锁定实际上支持您正在测试的功能的浏览器。 [特征检测](https://mdn.org.cn/en-US/docs/Learn_web_development/Extensions/Testing/Feature_detection) 是一个更可靠的策略。
- 您确实无法保证此属性宣传的用户代理确实是您的网站加载的用户代理。浏览器供应商基本上可以对 UA 字符串执行他们喜欢的操作，并且历史上会从此类属性返回虚假值，以免被某些网站锁定。
- 某些浏览器允许用户根据需要更改此字段的值（**UA 欺骗**）。

以下是解决错误和不同浏览器支持的更可靠的策略：

- [特征检测](https://mdn.org.cn/en-US/docs/Learn_web_development/Extensions/Testing/Feature_detection)：检测对某个功能的支持，而不是浏览器版本。
- [渐进增强](https://mdn.org.cn/en-US/docs/Glossary/Progressive_Enhancement)：为尽可能多的用户提供基本内容和功能的基线，同时为可以运行所有必需代码的浏览器提供最佳体验。

另请参阅 [使用用户代理进行浏览器检测](https://mdn.org.cn/en-US/docs/Web/HTTP/Guides/Browser_detection_using_the_user_agent) 了解为什么向不同浏览器提供不同内容通常是一个坏主意的更多信息。

### 隐私问题

此外，UA 字符串中暴露的信息历来引起了[隐私](https://mdn.org.cn/en-US/docs/Web/Privacy) 的关注——它可用于识别特定的用户代理，因此可用于指纹识别。

为了缓解此类问题，[支持浏览器](https://mdn.org.cn/en-US/docs/Web/HTTP/Reference/Headers/User-Agent#browser_compatibility) 实施用户代理缩减，这会更新 `User-agent` 标头和相关 API 功能以提供精简的信息集。

## 减少后UA字符串发生变化

在 [支持浏览器](https://mdn.org.cn/en-US/docs/Web/HTTP/Reference/Headers/User-Agent#browser_compatibility) 中，用户代理缩减从 UA 字符串中删除了三条信息——确切的平台/操作系统版本、设备型号和次要浏览器版本。

让我们看一个示例，以便您了解它的样子。而以前在 Android 上运行的 Chrome 的 UA 字符串可能如下所示：

```plain
Mozilla/5.0 (Linux; Android 16; Pixel 9) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/143.0.12.45 Mobile Safari/537.36
```

用户代理减少更新后，现在看起来像这样：

```plain
Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/143.0.0.0 Mobile Safari/537.36
```

以下部分提供了有关每个美国字符串更改的更多详细信息。

### 平台/操作系统版本和设备型号

平台版本和设备型号始终用固定值表示：

- Android 上的`Android 10; K`。
- macOS 上的`Macintosh; Intel Mac OS X 10_15_7`。
- Windows 上的`Windows NT 10.0; Win64; x64`。
- Chrome 操作系统上的`X11; CrOS x86_64 14541.0.0`。
- Linux 上的`X11; Linux x86_64`。

### 浏览器次要版本

主要浏览器版本号显示正确，但次要版本号始终显示为零 - `0.0.0`。

## 通过客户端提示请求UA信息

您可能仍然拥有依赖于详细 UA 字符串数据的代码，这些数据无法转换为使用特征检测或渐进增强。示例包括细粒度日志记录、欺诈预防措施或根据用户设备类型提供不同内容的软件帮助站点。

如果是这种情况，您仍然可以通过 [`Sec-CH-UA-*`](https://mdn.org.cn/en-US/docs/Web/HTTP/Reference/Headers#user_agent_client_hints) 标头（也称为 **User-Agent 客户端提示**）访问详细的 UA 字符串数据。标头提供了一种更安全、更能保护隐私的方式来发送此类信息，因为服务器必须选择它们想要的信息片段，而不是始终通过 `User-Agent` 字符串发送。它还提供对更广泛的信息选择的访问。

有关更多信息，请参阅[用户代理客户端提示](https://mdn.org.cn/en-US/docs/Web/HTTP/Guides/Client_hints)。

## 通过 JavaScript 访问客户端提示

[用户代理客户端提示 API](https://mdn.org.cn/en-US/docs/Web/API/User-Agent_Client_Hints_API) 允许您通过 JavaScript 访问客户端提示信息。 `Navigator.userAgentData` 属性提供对 `NavigatorUAData` 对象的访问，该对象包含表示低熵客户端提示的属性。

要访问像`Sec-CH-UA-Model`和`Sec-CH-UA-Form-Factors`这样的高熵提示，您需要使用`NavigatorUAData.getHighEntropyValues()`方法。

欲了解更多信息，请参阅[用户代理客户端提示 API](https://mdn.org.cn/en-US/docs/Web/API/User-Agent_Client_Hints_API)。

## 参见

- `User-Agent`
- `Navigator.userAgent`、`Navigator.appVersion`、`Navigator.platform`
- [HTTP 客户端提示](https://mdn.org.cn/en-US/docs/Web/HTTP/Guides/Client_hints)
- [实施特征检测](https://mdn.org.cn/en-US/docs/Learn_web_development/Extensions/Testing/Feature_detection)
- developer.chrome.com 上的[https://developer.chrome.com/docs/privacy-security/user-agent-client-hints](https://developer.chrome.com/docs/privacy-security/user-agent-client-hints) (2020)
