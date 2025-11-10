---
title: 关于我
layout: page
hide:
    -footer
comments: true
---

# 关于我

几年前，我曾搭建过一个博客网站，但很快发现对于日常学习和笔记记录来说，传统博客的管理和查阅并不够便捷。这个博客也因此闲置了许久。

直到偶然间，我遇见了 MkDocs 这种文档式网站格式，它简洁高效的特性让我眼前一亮。于是，我决定重新出发，部署了这个以文档为核心的个人网站。

## 初衷与愿景

这个网站的初心很简单：**系统化地记录我的学习历程，构建个人知识体系，方便日后查阅和回顾**。

如果你也偶然来到了这里，无论是技术上的志同道合，还是生活上的共鸣，都欢迎你留下足迹。如果我们的领域有所交集，或者你单纯想交个朋友，非常期待与你相识，一起交流成长。

## 我的学习历程

我目前就读于网络空间安全专业，我的求学之路有些特别：

- 2020年作为广东理科考生入学，最初攻读土木工程
- 2021年选择入伍服役，在部队度过了两年时光  
- 2023年退役后，转专业到网络空间安全，重新开始四年的大学生活

这些经历让我明白，学习从来不是直线前进的过程。在看似曲折的道路上，我其实收获了很多：军旅生涯教会了我纪律和团队协作，跨专业学习锻炼了我的适应能力，不断探索让我保持着对新技术的好奇心。

## 联系我

如果你愿意与我交流，无论是技术探讨、学习心得，还是单纯聊聊天，都非常欢迎：

<div class="contact-section">
  <div class="contact-method">
    <h3>微信</h3>
    <img class="qr-code" id="wechat-qr" src="" alt="微信二维码">
    <p>coolzest</p>
  </div>
  
  <div class="contact-method">
    <h3>GitHub</h3>
    <div class="icon"><i class="fab fa-github"></i></div>
    <p id="github-username">[你的GitHub用户名]</p>
  </div>
  
  <div class="contact-method">
    <h3>邮箱</h3>
    <div class="icon"><i class="fas fa-envelope"></i></div>
    <p id="email-address">[你的邮箱地址]</p>
  </div>
</div>

## 支持我

如果你觉得我的分享对你有帮助，欢迎通过以下方式支持我继续创作：

<div class="support-section">
  <h3>感谢支持</h3>
  <p>你的支持是我持续分享的动力</p>
  
  <div class="donation-codes">
    <div class="donation-method">
      <h4>微信支付</h4>
      <img class="qr-code" id="wechat-pay-qr" src="" alt="微信支付收款码">
    </div>
    
    <div class="donation-method">
      <h4>支付宝</h4>
      <img class="qr-code" id="alipay-qr" src="" alt="支付宝收款码">
    </div>
  </div>
</div>

期待与你相遇，在学习和成长的道路上互相陪伴、共同进步。

<link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">

<style>
:root {
  --card-bg: #f8f9fa;
  --card-text: #333;
  --card-border: #e9ecef;
  --support-bg: #f8f9fa;
  --support-text: #333;
  --primary-color: #4f46e5;
}

[data-md-color-scheme="slate"] {
  --card-bg: #1e293b;
  --card-text: #e2e8f0;
  --card-border: #334155;
  --support-bg: #1e293b;
  --support-text: #e2e8f0;
  --primary-color: #818cf8;
}

.contact-section {
  display: flex;
  flex-wrap: wrap;
  gap: 1.5rem;
  justify-content: space-between;
  margin: 2rem 0;
}

.contact-method {
  flex: 1;
  min-width: 180px;
  text-align: center;
  padding: 1.2rem;
  border-radius: 10px;
  background: var(--card-bg);
  color: var(--card-text);
  box-shadow: 0 2px 4px rgba(0,0,0,0.05);
  border: 1px solid var(--card-border);
}

.contact-method h3 {
  margin-bottom: 0.8rem;
  color: var(--primary-color);
  font-size: 1.1rem;
}

.contact-method .qr-code {
  width: 130px;
  height: 130px;
  margin: 0 auto 0.8rem;
  background: #fff;
  border-radius: 6px;
  display: block;
  object-fit: cover;
  border: 1px solid var(--card-border);
}

.contact-method .icon {
  font-size: 2.2rem;
  margin-bottom: 0.8rem;
  color: var(--primary-color);
}

.contact-method p {
  margin: 0;
  font-weight: 500;
  font-size: 0.9rem;
}

.support-section {
  text-align: center;
  margin: 2rem 0;
  padding: 1.5rem;
  background: var(--support-bg);
  border-radius: 10px;
  color: var(--support-text);
  border: 1px solid var(--card-border);
}

.support-section h3 {
  margin-bottom: 0.5rem;
  color: var(--primary-color);
}

.support-section > p {
  margin-bottom: 1.5rem;
  opacity: 0.8;
  font-size: 0.9rem;
}

.donation-codes {
  display: flex;
  flex-wrap: wrap;
  gap: 1.5rem;
  justify-content: center;
}

.donation-method {
  text-align: center;
}

.donation-method h4 {
  margin-bottom: 0.8rem;
  font-size: 0.95rem;
  color: var(--primary-color);
}

.donation-method .qr-code {
  width: 150px;
  height: 150px;
  margin: 0 auto;
  background: #fff;
  border-radius: 6px;
  display: block;
  object-fit: cover;
  border: 1px solid var(--card-border);
}

.contact-method:hover, .donation-method:hover {
  transform: translateY(-3px);
  transition: transform 0.3s ease;
  box-shadow: 0 4px 8px rgba(0,0,0,0.1);
}

@media (max-width: 768px) {
  .contact-section {
    flex-direction: column;
    align-items: center;
  }
  
  .contact-method {
    width: 100%;
    max-width: 250px;
  }
}
</style>

<script>
// 图片URL配置 - 请在此处替换为您的实际图片URL
const imageUrls = {
  wechatQr: "https://cloudflare-imgbed-84u.pages.dev/file/blog/1762781972949_WeChat.jpg", // 替换为您的微信二维码图片URL
  wechatPay: "https://cloudflare-imgbed-84u.pages.dev/file/blog/1762782010052_微信收款.jpg", // 替换为您的微信支付收款码图片URL
  alipay: "https://cloudflare-imgbed-84u.pages.dev/file/blog/1762782037626_支付宝收款.jpg" // 替换为您的支付宝收款码图片URL
};

// 文本内容配置 - 请在此处替换为您的实际信息
const textContent = {
  githubUsername: "coolzest", // 替换为您的GitHub用户名
  emailAddress: "coolzest@qq.com" // 替换为您的邮箱地址
};

// 设置图片URL
document.addEventListener('DOMContentLoaded', function() {
  // 设置微信二维码
  const wechatQr = document.getElementById('wechat-qr');
  if (wechatQr && imageUrls.wechatQr) {
    wechatQr.src = imageUrls.wechatQr;
  }
  
  // 设置微信支付二维码
  const wechatPayQr = document.getElementById('wechat-pay-qr');
  if (wechatPayQr && imageUrls.wechatPay) {
    wechatPayQr.src = imageUrls.wechatPay;
  }
  
  // 设置支付宝二维码
  const alipayQr = document.getElementById('alipay-qr');
  if (alipayQr && imageUrls.alipay) {
    alipayQr.src = imageUrls.alipay;
  }
  
  // 设置GitHub用户名
  const githubUsername = document.getElementById('github-username');
  if (githubUsername && textContent.githubUsername) {
    githubUsername.textContent = textContent.githubUsername;
  }
  
  // 设置邮箱地址
  const emailAddress = document.getElementById('email-address');
  if (emailAddress && textContent.emailAddress) {
    emailAddress.textContent = textContent.emailAddress;
  }
});
</script>