---
title: " "
hide:
  - toc  # 只隐藏侧边栏，保留导航栏和底栏
  - header
  - footer
  - title
  - navigation
---

<link rel="stylesheet" href="stylesheets/home.css">

<script>
document.addEventListener('DOMContentLoaded', function() {
  document.body.classList.add('home-page');
  
  // 主题切换监听
  const observer = new MutationObserver(function(mutations) {
    mutations.forEach(function(mutation) {
      if (mutation.attributeName === 'data-md-color-scheme') {
        document.body.classList.add('theme-transitioning');
        setTimeout(() => {
          document.body.classList.remove('theme-transitioning');
        }, 400);
      }
    });
  });
  
  observer.observe(document.documentElement, {
    attributes: true,
    attributeFilter: ['data-md-color-scheme']
  });

  
});
</script>

<!-- 头像区域 -->
<div class="avatar-section">
  <div class="avatar-wrapper">
    <div class="flip-container">
      <div class="flip-inner">
        <div class="avatar-front">
          <img src="https://s1.imagehub.cc/images/2025/07/25/27c0e1=a8c303e9d.jpeg" alt="正面头像" loading="eager">
        </div>
        <div class="avatar-back">
          <img src="assets\images\头像.png" alt="背面头像" loading="eager">
        </div>
      </div>
    </div>
    <div class="avatar-glow"></div>
  </div>
</div>

<!-- 重新设计的文字内容区域 -->
<div class="text-content">
  <div class="motto-wrapper">
    <p class="motto">所有的坚持，</p>
    <p class="motto highlight">终会让幸运与你不期而遇</p>
  </div>
  
  <div class="divider"></div>
  
  <p class="subtext">—— 慢慢来，比较快</p>
