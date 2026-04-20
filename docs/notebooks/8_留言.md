---
title: 留言板
layout: page
hide:
    -footer
    -navigation
    -toc
comments: true
---

<div class="guestbook-container">
  <div class="guestbook-header">
    <h1>留言板</h1>
    <p>欢迎留下您的想法和足迹</p>
  </div>

  <div class="guestbook-content">
    <p>在这里，您可以分享阅读感悟、提出建议，或只是简单打个招呼。</p>
    <p>期待与您的交流，每一条留言我都会认真阅读。</p>
  </div>
</div>

<style>
.guestbook-container {
  max-width: 800px;
  margin: 0 auto;
  padding: 2rem;
}

.guestbook-header {
  text-align: center;
  margin-bottom: 3rem;
  padding-bottom: 2rem;
  border-bottom: 1px solid #eaeaea;
}

.guestbook-header h1 {
  font-size: 2.5rem;
  color: #2c3e50;
  margin-bottom: 1rem;
  font-weight: 300;
}

.guestbook-header p {
  color: #7f8c8d;
  font-size: 1.1rem;
  margin: 0;
}

.guestbook-content {
  text-align: center;
  line-height: 1.8;
  color: #555;
  margin-bottom: 3rem;
}

.guestbook-content p {
  margin-bottom: 1rem;
}

/* 评论区域样式 */
#comments {
  margin-top: 3rem;
  padding-top: 2rem;
  border-top: 1px solid #eaeaea;
}

/* 响应式调整 */
@media (max-width: 768px) {
  .guestbook-container {
    padding: 1rem;
  }
  
  .guestbook-header h1 {
    font-size: 2rem;
  }
}
</style>