---
title: 压缩字典传输
date: 2026-04-25
description: "MDN HTTP 指南：压缩字典传输"
categories:
  - 网络安全
  - HTTP
tags:
  - HTTP
  - MDN
comments: true
---
!!! warning "来源声明"
    MDN 暂未提供该页面的官方中文译文；本文基于英文原文翻译整理：[https://mdn.org.cn/zh-CN/docs/Web/HTTP/Guides/Compression_dictionary_transport](https://mdn.org.cn/zh-CN/docs/Web/HTTP/Guides/Compression_dictionary_transport)。
    内容版权归 MDN contributors 所有，并受 Creative Commons 许可约束；本站仅用于个人学习归档与排版适配。

# 压缩字典传输

_实验性_

**压缩字典传输** 是一种使用共享压缩字典来显着减少 HTTP 响应的传输大小的方法。

## 概述

HTTP 中使用压缩算法来减少通过网络下载的资源的大小，从而降低带宽成本和加载页面所需的时间。无损 HTTP 压缩算法的工作原理是在源中查找冗余：例如，像字符串 `"function"` 这样的文本重复的地方。然后，它们仅包含冗余字符串的一份副本，并用对该副本的引用替换资源中出现的该字符串。由于引用比字符串短，因此压缩版本更短。

> [！笔记]
> 该技术之前的尝试称为 SDCH（HTTP 共享字典压缩），但从未得到广泛支持，并于 2017 年被删除。压缩字典传输是一种更规范、更强大的实现，得到了更广泛的行业共识。

例如，采用以下 JavaScript：

```js
function a() {
  console.log("Hello World!");
}

function b() {
  console.log("I am here");
}
```

这可以通过用对先前位置和字符数的引用替换重复的字符串来压缩，如下所示：

```plain
function a() {
  console.log("Hello World!");
}

[0:9]b[10:20]I am here[42:46]
```

在本例中，`[0:9]`指的是复制从字符0开始的9个字符。请注意，这是一个演示概念的简化示例，实际算法比这更复杂。

然后，客户端可以在下载后反转压缩以重新创建原始的未压缩资源。

### 压缩字典

Brotli 压缩和 Zstandard 压缩等算法通过允许使用常见字符串的字典来实现更高的效率，因此您不需要在压缩资源中保留它们的任何副本。这些算法附带了压缩 HTTP 响应时使用的预定义默认字典。

压缩字典传输在此基础上构建，使您能够提供自己的字典，该字典特别适用于特定的资源集。然后，压缩算法可以在压缩和解压缩资源时将其作为字节源进行引用。

假设前面示例中的引用包含在该通用字典中，则可以进一步简化为：

```plain
[d0:9]a[d10:20]Hello World![d42:46]
[d0:9]b[d10:20]I am here[d42:46]
```

该字典可以是仅压缩字典传输所需的单独资源，也可以是网站无论如何都需要的资源。

例如，假设您的网站使用 JavaScript 库。您通常会加载库的特定版本，并且可能在库名称中包含版本名称，例如 `<script src="my-library.v1.js">`。当浏览器加载您的页面时，它将获取库的副本作为子资源。

如果您随后更新到该库的 v2，则该库的大部分代码可能会保持不变。因此，网站可以通过告诉浏览器使用`my-library.v1.js`作为`my-library.v2.js`的压缩字典来大大减少`my-library.v2.js`的下载大小。那么 v1 和 v2 之间通用的所有字符串都不需要包含在 v2 的下载中，因为浏览器已经拥有它们。 `my-library.v2.js` 的大部分下载大小只是两个版本之间的增量。

压缩字典传输可以实现比使用默认内置字典压缩高一个数量级的压缩：有关一些实际结果，请参阅 [压缩字典传输示例](https://github.com/WICG/compression-dictionary-transport/blob/main/examples.md)。

## 词典格式

压缩字典不遵循任何特定格式，也没有特定的 MIME 类型。它们是常规文件，可用于压缩具有类似内容的其他文件。

以前版本的文件通常有很多相似的内容，这就是它们成为优秀词典的原因。
使用文件的先前版本作为字典允许压缩算法有效地引用所有未更改的内容，并且仅捕获新版本中相对较小的差异。这种方法称为增量压缩。

另一种方法是将常见字符串（例如 HTML 模板）一起列出在新的 `dictionary.txt` 文件中，以便它可用于压缩网站上的 HTML 页面。您可以通过使用专门的工具（例如 [Brotli 的字典生成器](https://github.com/google/brotli/blob/master/research/dictionary_generator.cc)）进一步优化此功能，该工具可以将字典缩小到最小大小并最小化重叠。

字典还可以用于有效地压缩二进制格式。例如，[WASM](https://mdn.org.cn/en-US/docs/WebAssembly) 二进制文件是大型资源，也可以从增量压缩中受益。

## 现有资源作为字典

要将资源用作字典，服务器应在提供资源的响应中包含 `Use-As-Dictionary` 标头：

```http
Use-As-Dictionary: match="/js/app.*.js"
```

此标头的值指示可以将此资源用作字典的资源：在本例中，包括其 URL 与给定 [图案](https://mdn.org.cn/en-US/docs/Web/API/URL_Pattern_API) 匹配的任何资源。

当稍后请求与给定模式（例如，`app.v2.js`）匹配的资源时，请求将在`Available-Dictionary`标头中包含可用字典的SHA-256哈希值，以及`Accept-Encoding`标头中的`dcb`和/或`dcz`值（用于使用Brotli或ZStandard作为增量压缩）适当）：

```http
Accept-Encoding: gzip, br, zstd, dcb, dcz
Available-Dictionary: :pZGm1Av0IEBKARczz7exkNYsZb8LzaMrV7J32a2fFG4=:
```

然后，服务器可以使用 `Content-Encoding` 标头中给出的所选内容编码，以适当编码的响应进行响应：

```http
Content-Encoding: dcb
```

如果响应是可缓存的，则它必须包含 `Vary` 标头，以防止缓存向不支持字典压缩的资源的客户端提供字典压缩资源或提供使用错误字典压缩的响应：

```http
Vary: accept-encoding, available-dictionary
```

还可以在 `Use-As-Dictionary` 标头中提供可选的 `id` ，以便服务器在不通过哈希存储字典的情况下更轻松地找到字典文件：

```http
Use-As-Dictionary: match="/js/app.*.js", id="dictionary-12345"
```

如果提供了此值，则该值将在未来的请求中发送到 `Dictionary-ID` 标头中：

```http
Accept-Encoding: gzip, br, zstd, dcb, dcz
Available-Dictionary: :pZGm1Av0IEBKARczz7exkNYsZb8LzaMrV7J32a2fFG4=:
Dictionary-ID: "dictionary-12345"
```

服务器仍然必须检查 `Available-Dictionary` 标头中的哈希值 - `Dictionary-ID` 是服务器识别字典的附加信息，但不能取代 `Available-Dictionary` 标头的需要。

## 单独的词典

HTML 文档还可以向浏览器提供压缩字典，该字典不是浏览器通过 `script` 标签等元素下载的资源。有两种方法可以做到这一点：

- 包含一个 [`rel`](https://mdn.org.cn/en-US/docs/Web/HTML/Reference/Attributes/rel) 属性设置为 `compression-dictionary` 的 `link` 元素：

  ```html
  <link rel="compression-dictionary" href="/dictionary.dat" />
  ```

- 使用 `Link` 标头引用字典：

  ```http
  Link: </dictionary.dat>; rel="compression-dictionary"
  ```

然后浏览器在空闲时间下载该字典，并且该响应必须包含 `Use-As-Dictionary` 标头：

```http
Use-As-Dictionary: match="/js/app.*.js"
```

从这里开始，请求匹配资源时的过程与前面的示例类似。

## 创建字典压缩响应

字典压缩响应可以使用 Brotli 或 ZStandard 算法，但有两个额外要求：它们还必须包含魔术头和嵌入的字典哈希。

字典压缩资源可以动态创建，但对于静态资源，最好在构建时提前创建它们。当使用先前版本作为字典时，这将需要决定创建多少个增量压缩版本 - 仅针对最后一个版本，或者针对 X 的某个值针对最后 X 个版本。

给定一个名为 `dictionary.text` 的字典文件和一个名为 `data.text` 的要压缩文件，以下 Bash 命令将使用 Brotli 压缩该文件，生成一个名为 `data.txt.dcb` 的压缩文件：

```bash
echo -en '\xffDCB' > data.txt.dcb && \
openssl dgst -sha256 -binary dictionary.txt >> data.txt.dcb && \
brotli --stdout -D dictionary.txt data.txt >> data.txt.dcb
```

给定相同的输入文件，以下 Bash 命令将使用 ZStandard 压缩文件，生成名为 `data.txt.dcz` 的压缩文件：

```bash
echo -en '\x5e\x2a\x4d\x18\x20\x00\x00\x00' > data.txt.dcz && \
openssl dgst -sha256 -binary dictionary.txt >> data.txt.dcz && \
zstd -D dictionary.txt -f -o tmp.zstd data.txt && \
cat tmp.zstd >> data.txt.dcz
```

请注意，您需要在本地安装 OpenSSL 以及 Brotli 或 ZStandard。

## 限制

压缩算法存在安全攻击的风险，因此压缩字典传输有许多限制，包括：

- 字典必须与使用该字典的资源同源。
- 字典压缩资源必须与文档来源同源，或遵循 [跨域资源共享](https://mdn.org.cn/en-US/docs/Web/HTTP/Guides/CORS) 规则，因此使用 [`crossorigin`](https://mdn.org.cn/en-US/docs/Web/HTML/Reference/Attributes/crossorigin) 属性进行请求，并使用适当的 `Access-Control-Allow-Origin` 标头提供服务。
- 字典受到通常的 HTTP 缓存分区的约束，因此即使源下载相同的资源也无法在源之间共享。需要为每个来源重新下载词典。

此外，字典本身可能成为跟踪向量，因此当禁用 cookie 或启用其他额外的隐私保护时，浏览器可能会限制此功能。

与其他资源一样，如果网站使用 `Content-Security-Policy` 标头，则压缩字典必须是允许的源才能加载。
特别是，当使用 [`<link rel="compression-dictionary">`](https://mdn.org.cn/en-US/docs/Web/HTML/Reference/Attributes/rel/compression-dictionary) 加载 [单独的词典](#separate-dictionary) 时，`connect-src` 指令（或 `default-src`，如果未设置 `connect-src`）必须允许字典位置。

## 规格

_规范信息请参见 MDN 译文页面。_

## 浏览器兼容性



## 参见

- 术语表：
  - Brotli压缩
  - Z标准压缩
- [`<link rel="compression-dictionary">`](https://mdn.org.cn/en-US/docs/Web/HTML/Reference/Attributes/rel/compression-dictionary)
- `Accept-encoding`
- `Content-encoding`
- `Available-Dictionary`
- `Dictionary-ID`
- `Use-As-Dictionary`
- [RFC 9842：压缩字典传输](https://www.rfc-editor.org/rfc/rfc9842)
- [压缩字典传输资源](https://use-as-dictionary.com/)
