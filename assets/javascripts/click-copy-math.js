document.addEventListener('DOMContentLoaded', function() {
  const inlineCodes = document.querySelectorAll(
    'p > code, li > code, td > code, th > code'
  );

  inlineCodes.forEach(code => {
    // 关键优化：使用主题CSS变量，自动适配明暗模式
    code.style.cssText = `
      cursor: copy;
      padding: 2px 4px;
      border-radius: 3px;
      /* 代码背景色：继承主题的代码块背景（明暗主题自动切换） */
      background: var(--md-code-bg-color);
      /* 代码文本色：继承主题的代码文本色（确保黑色主题下清晰） */
      color: var(--md-code-fg-color);
      transition: background 0.2s;
      position: relative;
    `;
    code.title = "点击复制代码";

    // 点击事件：保留原有复制逻辑
    code.addEventListener('click', function(e) {
      e.stopPropagation();
      const codeText = this.textContent;

      navigator.clipboard.writeText(codeText).then(() => {
        showTip(this, '已复制！', '#4CAF50');
      }).catch(err => {
        console.error('复制失败:', err);
        showTip(this, '复制失败', '#f44336');
      });
    });

    // 鼠标悬停样式：使用主题的深色背景变体，适配明暗模式
    code.addEventListener('mouseenter', () => {
      // 深色主题下悬停背景稍深，浅色主题下也同步加深（保持一致性）
      code.style.background = 'var(--md-code-bg-color-dark, rgba(200, 200, 200, 0.8))';
    });
    code.addEventListener('mouseleave', () => {
      code.style.background = 'var(--md-code-bg-color)';
    });
  });

  // 提示框样式保持不变（不影响代码展示）
  function showTip(element, text, color) {
    const existing = element.querySelector('.copy-tip');
    if (existing) {
      existing.remove();
    }
    const tip = document.createElement('span');
    tip.className = 'copy-tip';
    tip.textContent = text;
    tip.style.cssText = `
      position: absolute;
      left: 100%;
      top: 50%;
      transform: translate(8px, -50%);
      padding: 2px 6px;
      background: ${color};
      color: white;
      font-size: 12px;
      border-radius: 3px;
      z-index: 1000;
      opacity: 0;
      transition: opacity 0.2s;
      white-space: nowrap;
      pointer-events: none;
    `;

    element.appendChild(tip);

    setTimeout(() => tip.style.opacity = 1, 10);
    setTimeout(() => {
      tip.style.opacity = 0;
      setTimeout(() => tip.remove(), 200);
    }, 2000);
  }
});
