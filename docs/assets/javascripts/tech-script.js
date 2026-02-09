// 保持头部背景一致：不在滚动时修改样式

// 卡片加载动画
document.addEventListener("DOMContentLoaded", () => {
  const cards = document.querySelectorAll(".md-typeset .card, .md-typeset .grid.cards>li");
  cards.forEach((card, index) => {
    card.style.opacity = "0";
    card.style.transform = "translateY(20px)";
    setTimeout(() => {
      card.style.transition = "opacity 0.6s ease, transform 0.6s ease";
      card.style.opacity = "1";
      card.style.transform = "translateY(0)";
    }, 100 * index);
  });
});
