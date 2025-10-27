// 工具函数：节流
const throttle = (fn, delay = 100) => {
  let lastTime = 0;
  return (...args) => {
    const now = Date.now();
    if (now - lastTime >= delay) {
      fn.apply(this, args);
      lastTime = now;
    }
  };
};

// 1. 图片懒加载（保持不变）
document.addEventListener('DOMContentLoaded', () => {
  if (!('IntersectionObserver' in window)) {
    document.querySelectorAll('.md-content img[data-src]').forEach(img => {
      img.src = img.dataset.src;
      img.classList.add('loaded');
    });
    return;
  }

  const imgObserver = new IntersectionObserver((entries) => {
    entries.forEach(entry => {
      if (entry.isIntersecting) {
        const img = entry.target;
        const src = img.dataset.src || img.dataset.srcset;
        if (src) {
          const tempImg = new Image();
          tempImg.src = src;
          tempImg.onload = () => {
            img.src = src;
            img.classList.add('loaded');
            img.removeAttribute('data-src');
          };
          tempImg.onerror = () => {
            img.src = 'assets/images/placeholder.png';
            img.classList.add('loaded', 'error');
          };
        }
        imgObserver.unobserve(img);
      }
    });
  }, { rootMargin: '200px 0px' });

  document.querySelectorAll('.md-content img[data-src]').forEach(img => {
    img.style.opacity = '0';
    imgObserver.observe(img);
  });
});

// 2. 导航栏滚动动效（保持不变）
const handleHeaderShadow = () => {
  const header = document.querySelector('.md-header');
  if (!header) return;

  if (window.scrollY > 50) {
    header.classList.add('md-header--shadow');
    if (document.documentElement.getAttribute('data-md-color-scheme') === 'slate') {
      header.classList.add('md-header--dark-shadow');
    } else {
      header.classList.remove('md-header--dark-shadow');
    }
  } else {
    header.classList.remove('md-header--shadow', 'md-header--dark-shadow');
  }
};

window.addEventListener('scroll', throttle(handleHeaderShadow), { passive: true });
handleHeaderShadow();

// 3. 锚点链接平滑滚动（保持不变）
document.querySelectorAll('a[href^="#"]').forEach(anchor => {
  anchor.addEventListener('click', function(e) {
    const targetId = this.getAttribute('href');
    if (targetId === '#' || targetId.startsWith('#/') || this.host !== window.location.host) return;

    const targetElement = document.querySelector(targetId);
    if (!targetElement) return;

    e.preventDefault();

    const mobileNav = document.querySelector('.md-sidebar--primary');
    if (mobileNav && window.innerWidth < 768) {
      mobileNav.classList.remove('md-sidebar--active');
    }

    const startPos = window.scrollY;
    const targetPos = targetElement.getBoundingClientRect().top + startPos - 80;
    const distance = targetPos - startPos;
    const duration = 800;
    let startTime = null;

    const scrollAnimation = (timestamp) => {
      if (!startTime) startTime = timestamp;
      const progress = timestamp - startTime;
      const ease = progress < duration 
        ? progress / duration * (progress / duration * 3 - 2) * -1 
        : 1;
      window.scrollTo(0, startPos + distance * ease);
      if (progress < duration) {
        requestAnimationFrame(scrollAnimation);
      } else {
        targetElement.classList.add('md-target-highlight');
        setTimeout(() => targetElement.classList.remove('md-target-highlight'), 1200);
      }
    };

    requestAnimationFrame(scrollAnimation);
  });
});

// 4. 主题切换动画（修复：增强触发逻辑）
const themeToggle = document.querySelector('.md-header__button--theme');
if (themeToggle) {
  themeToggle.addEventListener('click', (e) => {
    e.preventDefault(); // 阻止默认行为，确保动画完成后再切换
    const html = document.documentElement;
    
    // 强制添加过渡类，确保动画触发
    html.classList.add('theme-switching');
    
    // 手动触发重排（解决动画不生效的关键）
    void html.offsetWidth;
    
    // 延迟切换主题（给动画留时间）
    setTimeout(() => {
      // 手动切换主题模式（核心修复：确保主题切换与动画同步）
      if (html.getAttribute('data-md-color-scheme') === 'slate') {
        html.setAttribute('data-md-color-scheme', 'default');
      } else {
        html.setAttribute('data-md-color-scheme', 'slate');
      }
      
      // 动画结束后移除类
      setTimeout(() => {
        html.classList.remove('theme-switching');
      }, 500); // 与CSS动画时长一致
    }, 100); // 延迟触发主题切换，确保过渡生效

    // 图标旋转动画
    const icon = themeToggle.querySelector('svg');
    if (icon) {
      icon.style.transition = 'transform 0.6s ease';
      icon.style.transform = 'rotate(180deg)';
      setTimeout(() => {
        icon.style.transform = 'rotate(0)';
      }, 600);
    }
  });
}

// 5. 页面跳转动画（修复：确保无刷新导航生效）
document.addEventListener('DOMContentLoaded', () => {
  // 扩大选择器范围，确保所有内部文章链接被捕获
  const internalLinks = document.querySelectorAll(
    '.md-nav__link[href^="/"],  // 站内绝对路径链接
    '.md-nav__link[href^="./"], // 相对路径链接
    '.md-header__topic[href^="/"],  // 头部标题链接
    '.md-header__button--home[href^="/"]  // 首页按钮链接
  );

  internalLinks.forEach(link => {
    // 过滤外部链接和锚点
    if (link.host !== window.location.host || link.getAttribute('href').startsWith('#')) {
      return;
    }

    link.addEventListener('click', function(e) {
      const currentContent = document.querySelector('.md-content');
      if (!currentContent) return;

      // 关键：强制阻止默认刷新行为（即使instant导航有问题，先确保动画触发）
      e.preventDefault();
      e.stopPropagation();

      // 添加滑出动画
      currentContent.classList.add('md-content--out');
      
      // 强制触发CSS动画（解决浏览器优化导致的动画不执行）
      currentContent.style.animation = 'none';
      currentContent.offsetHeight; // 触发重排
      currentContent.style.animation = null;

      // 动画结束后，使用无刷新导航API跳转（Material主题提供）
      setTimeout(() => {
        if (window.mdNavigationInstant) {
          // 调用Material主题的无刷新导航方法
          window.mdNavigationInstant.navigate(link.href);
        } else {
          // 降级：如果无刷新API不可用，延迟刷新（至少显示动画）
          window.location.href = link.href;
        }
      }, 400); // 与动画时长一致
    });
  });

  // 新页面加载后滑入动画（监听无刷新导航完成事件）
  if (window.mdNavigationInstant) {
    // 监听Material主题的无刷新导航完成事件
    window.mdNavigationInstant.addEventListener('navigate', (event) => {
      if (event.detail.state === 'completed') {
        const newContent = document.querySelector('.md-content');
        if (newContent) {
          newContent.classList.add('md-content--in');
          setTimeout(() => newContent.classList.remove('md-content--in'), 500);
        }
      }
    });
  } else {
    // 降级：普通刷新后触发滑入动画
    const newContent = document.querySelector('.md-content');
    if (newContent) {
      setTimeout(() => {
        newContent.classList.add('md-content--in');
        setTimeout(() => newContent.classList.remove('md-content--in'), 500);
      }, 100);
    }
  }
});

{% extends "base.html" %}

{% block extra_javascript %}
<script>
// 页面加载完成后，触发进入动画
document.addEventListener('DOMContentLoaded', function() {
  const container = document.querySelector('.md-container');
  if (container) {
    // 先添加初始状态类，再触发动画
    container.classList.add('page-transition', 'page-transition-enter');
    setTimeout(() => {
      container.classList.add('page-transition-enter-active');
    }, 10); // 微小延迟确保动画触发
  }

  // 监听所有内部链接的点击事件，触发离开动画
  document.querySelectorAll('a[href^="/"]:not([href^="#"])').forEach(link => {
    link.addEventListener('click', function(e) {
      // 排除外部链接、下载链接和特殊操作链接
      if (this.target === '_blank' || this.hasAttribute('download')) return;

      e.preventDefault(); // 阻止默认跳转
      const targetUrl = this.href;
      const container = document.querySelector('.md-container');

      if (container) {
        // 触发离开动画
        container.classList.add('page-transition-leave-active');
        
        // 动画结束后跳转页面
        setTimeout(() => {
          window.location.href = targetUrl;
        }, 300); // 与 CSS 中 --transition-duration 保持一致
      } else {
        // 若容器不存在，直接跳转
        window.location.href = targetUrl;
      }
    });
  });
});
</script>
{% endblock %}