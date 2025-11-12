// 导航栏滚动效果
window.addEventListener('scroll', () => {
  const header = document.querySelector('.md-header');
  if (window.scrollY > 50) {
    header.style.backdropFilter = 'blur(15px)';
    header.style.backgroundColor = 'rgba(255, 255, 255, 0.9)';
  } else {
    header.style.backdropFilter = 'blur(10px)';
    header.style.backgroundColor = 'rgba(255, 255, 255, 0.8)';
  }
});

// 卡片加载动画
document.addEventListener('DOMContentLoaded', () => {
  const cards = document.querySelectorAll('.md-typeset .card, .md-typeset .grid.cards>li');
  cards.forEach((card, index) => {
    card.style.opacity = '0';
    card.style.transform = 'translateY(20px)';
    setTimeout(() => {
      card.style.transition = 'opacity 0.6s ease, transform 0.6s ease';
      card.style.opacity = '1';
      card.style.transform = 'translateY(0)';
    }, 100 * index);
  });
});

