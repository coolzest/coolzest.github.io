---
title: 朋友
layout: page
hide:
    -footer
    -navigation
    -toc
comments: true
---

<style>
    /* 友链页面专用样式 - 不会影响全局 */
    #links-page {
        font-family: 'Segoe UI', 'PingFang SC', 'Microsoft YaHei', sans-serif;
        max-width: 1200px;
        margin: 0 auto;
        padding: 20px;
    }
    
    /* 跟随MkDocs主题的变量定义 */
    #links-page {
        --card-bg: var(--md-default-bg-color, #ffffff);
        --text-color: var(--md-default-fg-color, #333333);
        --text-secondary: var(--md-default-fg-color--light, #666666);
        --accent-color: var(--md-primary-fg-color, #4a6cf7);
        --accent-hover: var(--md-primary-fg-color--dark, #3a5ce5);
        --border-color: var(--md-default-fg-color--lightest, #eaeaea);
        --shadow: 0 4px 12px rgba(0, 0, 0, 0.08);
        --code-bg: var(--md-code-bg-color, #f5f5f5);
    }
    
    /* 深色主题适配 */
    @media (prefers-color-scheme: dark) {
        #links-page {
            --card-bg: var(--md-default-bg-color, #1a1a1a);
            --text-color: var(--md-default-fg-color, #f0f0f0);
            --text-secondary: var(--md-default-fg-color--light, #b0b0b0);
            --accent-color: var(--md-primary-fg-color, #6c8eff);
            --accent-hover: var(--md-primary-fg-color--dark, #5a7eff);
            --border-color: var(--md-default-fg-color--lightest, #444444);
            --shadow: 0 4px 12px rgba(0, 0, 0, 0.3);
            --code-bg: var(--md-code-bg-color, #2d2d2d);
        }
    }
    
    /* 标题样式 */
    .links-header {
        text-align: center;
        margin-bottom: 40px;
        padding: 20px;
    }
    
    .links-header h1 {
        font-size: 2.5rem;
        margin-bottom: 10px;
        color: var(--text-color);
    }
    
    .links-header p {
        font-size: 1.1rem;
        color: var(--text-secondary);
        max-width: 600px;
        margin: 20px auto 0;
    }
    
    /* 分类导航 */
    .category-nav {
        display: flex;
        gap: 15px;
        margin-bottom: 30px;
        flex-wrap: wrap;
        justify-content: center;
    }
    
    .category-btn {
        padding: 8px 16px;
        background: var(--card-bg);
        border: 1px solid var(--border-color);
        border-radius: 20px;
        color: var(--text-color);
        cursor: pointer;
        transition: all 0.3s;
        font-size: 0.9rem;
    }
    
    .category-btn:hover, .category-btn.active {
        background: var(--accent-color);
        color: white;
        border-color: var(--accent-color);
    }
    
    /* 友链容器样式 */
    .link-navigation {
        display: grid;
        grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
        gap: 20px;
    }
    
    /* 通用卡片样式 */
    .link-card {
        width: 100%;
        height: 100px;
        font-size: 1rem;
        padding: 15px 20px;
        border-radius: 16px;
        transition: all 0.4s cubic-bezier(0.25, 0.46, 0.45, 0.94);
        display: flex;
        align-items: center;
        color: var(--text-color);
        background: var(--card-bg);
        box-shadow: var(--shadow);
        border: 1px solid var(--border-color);
        overflow: hidden;
        position: relative;
        opacity: 1;
        transform: translateY(0) scale(1);
    }
    
    .link-card::before {
        content: '';
        position: absolute;
        top: 0;
        left: -100%;
        width: 100%;
        height: 100%;
        background: linear-gradient(90deg, transparent, rgba(255, 255, 255, 0.2), transparent);
        transition: left 0.5s;
    }
    
    .link-card:hover::before {
        left: 100%;
    }
    
    .link-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 10px 25px rgba(0, 0, 0, 0.15);
        border-color: var(--accent-color);
    }
    
    .link-card a {
        border: none;
        text-decoration: none;
    }
    
    .link-card .ava {
        width: 50px !important;
        height: 50px !important;
        margin: 0 !important;
        margin-right: 15px !important;
        border-radius: 50%;
        transition: transform 0.3s;
        border: 2px solid var(--border-color);
        object-fit: cover;
    }
    
    .link-card:hover .ava {
        transform: scale(1.1);
        border-color: var(--accent-color);
    }
    
    .link-card .card-header {
        overflow: hidden;
        width: auto;
        flex: 1;
    }
    
    .link-card .card-header a {
        color: var(--accent-color);
        font-weight: bold;
        text-decoration: none;
        transition: color 0.3s;
        display: block;
        white-space: nowrap;
        overflow: hidden;
        text-overflow: ellipsis;
    }
    
    .link-card .card-header a:hover {
        color: var(--accent-hover);
        text-decoration: none;
    }
    
    .link-card .card-header .info {
        color: var(--text-secondary);
        font-size: 14px;
        min-width: 0;
        overflow: hidden;
        white-space: nowrap;
        text-overflow: ellipsis;
        margin-top: 5px;
    }
    
    /* 分类标题样式 */
    .category-title {
        grid-column: 1 / -1;
        font-size: 1.5rem;
        color: var(--text-color);
        margin: 30px 0 15px;
        padding-bottom: 10px;
        border-bottom: 2px solid var(--border-color);
        position: relative;
        transition: all 0.4s ease;
    }
    
    .category-title::after {
        content: '';
        position: absolute;
        bottom: -2px;
        left: 0;
        width: 80px;
        height: 2px;
        background: linear-gradient(to right, var(--accent-color), #8a6cf7);
        transition: width 0.4s ease;
    }
    
    /* 卡片隐藏状态 */
    .link-card.hidden {
        opacity: 0;
        transform: translateY(10px) scale(0.95);
        height: 0;
        padding-top: 0;
        padding-bottom: 0;
        margin-top: 0;
        margin-bottom: 0;
        pointer-events: none;
    }
    
    /* 分类标题隐藏状态 */
    .category-title.hidden {
        opacity: 0;
        height: 0;
        margin: 0;
        padding: 0;
        border: none;
        overflow: hidden;
    }
    
    .category-title.hidden::after {
        width: 0;
    }
    
    /* 交换友链区域 - 紧凑版 */
    .exchange-section {
        margin-top: 50px;
        padding: 20px;
        background: var(--card-bg);
        border-radius: 12px;
        box-shadow: var(--shadow);
        border: 1px solid var(--border-color);
    }
    
    .exchange-section h2 {
        font-size: 1.4rem;
        margin-bottom: 15px;
        color: var(--text-color);
        text-align: center;
    }
    
    .exchange-content {
        display: flex;
        gap: 20px;
        align-items: flex-start;
    }
    
    .my-info {
        flex: 1;
        display: flex;
        flex-direction: column;
        gap: 10px;
    }
    
    .my-info h3 {
        margin: 0;
        color: var(--text-color);
        font-size: 1.1rem;
    }
    
    /* 修改：简化我的友链信息展示 */
    .my-info-simple {
        flex: 1;
        padding: 20px;
        background: var(--code-bg);
        border-radius: 8px;
        border: 1px solid var(--border-color);
    }
    
    .my-info-simple h3 {
        margin-top: 0;
        margin-bottom: 15px;
        color: var(--text-color);
        font-size: 1.2rem;
        text-align: center;
    }
    
    .my-info-simple pre {
        background: transparent;
        padding: 0;
        border-radius: 0;
        overflow-x: auto;
        color: var(--text-color);
        border: none;
        text-align: left;
        font-size: 0.9rem;
        margin: 0;
        line-height: 1.5;
        white-space: pre-wrap;
        word-wrap: break-word;
    }
    
    .comment-notice {
        flex: 1;
        padding: 20px;
        border-radius: 8px;
        border: 1px dashed var(--border-color);
        text-align: center;
        display: flex;
        flex-direction: column;
        justify-content: center;
        background: var(--card-bg);
    }
    
    .comment-notice p {
        margin: 0;
        color: var(--text-color);
        font-size: 1rem;
        line-height: 1.5;
    }
    
    .comment-notice p:first-child {
        font-size: 1.1rem;
        font-weight: bold;
        margin-bottom: 10px;
    }
    
    /* 页脚样式 */
    .links-footer {
        text-align: center;
        margin-top: 50px;
        padding: 20px;
        color: var(--text-secondary);
        font-size: 0.9rem;
        border-top: 1px solid var(--border-color);
    }
    
    /* 动画效果 */
    @keyframes fadeInUp {
        from {
            opacity: 0;
            transform: translateY(20px);
        }
        to {
            opacity: 1;
            transform: translateY(0);
        }
    }
    
    .link-card {
        animation: fadeInUp 0.5s ease forwards;
        opacity: 0;
    }
    
    /* 空头像占位符样式 */
    .avatar-placeholder {
        width: 50px;
        height: 50px;
        border-radius: 50%;
        background: var(--accent-color);
        display: flex;
        align-items: center;
        justify-content: center;
        color: white;
        font-weight: bold;
        margin-right: 15px;
    }
    
    /* 小屏优化 */
    @media (max-width: 768px) {
        .link-navigation {
            grid-template-columns: 1fr;
            gap: 15px;
        }
        
        .link-card {
            width: 100%;
            max-width: 100%;
            height: auto;
            min-height: 90px;
        }
        
        .links-header h1 {
            font-size: 2rem;
        }
        
        .exchange-content {
            flex-direction: column;
        }
        
        .exchange-section {
            padding: 15px;
        }
    }
</style>

<!-- 友链页面内容 -->
<div id="links-page">
    <div class="links-header">
        <h1>友情链接</h1>
        <p>这里收集了我喜欢的一些网站和朋友们的主页，欢迎互相交流与学习。</p>
    </div>
    
    <div class="category-nav">
        <button class="category-btn active" data-category="all">全部链接</button>
        <button class="category-btn" data-category="friends">朋友博客</button>
        <button class="category-btn" data-category="tech">技术资源</button>
        <button class="category-btn" data-category="tools">实用工具</button>
        <button class="category-btn" data-category="design">设计灵感</button>
    </div>
    
    <div class="links-content">
        <h2 class="category-title">朋友博客</h2>
        <div class="link-navigation">
            <div class="link-card" data-category="friends">
                <div class="avatar-placeholder">极</div>
                <div class="card-header">
                    <div>
                        <a href="https://jaywhj.netlify.app/" target="_blank">极简主义</a>
                    </div>
                    <div class="info">追求简单与高效的生活方式</div>
                </div>
            </div>
            <div class="link-card" data-category="friends">
                <img class="ava" src="https://i.stardots.io/wcowin/1750089315509.png" alt="Wcowin's blog"/>
                <div class="card-header">
                    <div>
                        <a href="https://wcowin.work/" target="_blank">Wcowin's blog</a>
                    </div>
                    <div class="info">这是一个分享技术的小站</div>
                </div>
            </div>
            <div class="link-card" data-category="friends">
                <div class="avatar-placeholder">T</div>
                <div class="card-header">
                    <div>
                        <a href="https://example.com" target="_blank">技术狂想曲</a>
                    </div>
                    <div class="info">探索前沿技术与编程艺术</div>
                </div>
            </div>
        </div>
        
        <h2 class="category-title">技术资源</h2>
        <div class="link-navigation">
            <div class="link-card" data-category="tech">
                <img class="ava" src="https://i.stardots.io/wcowin/1750220860750.jpg" alt="Macapp"/>
                <div class="card-header">
                    <div>
                        <a href="https://macapp.org.cn" target="_blank">Macapp</a>
                    </div>
                    <div class="info">一个专注于分享Mac资源的频道</div>
                </div>
            </div>
            <div class="link-card" data-category="tech">
                <div class="avatar-placeholder">G</div>
                <div class="card-header">
                    <div>
                        <a href="https://github.com" target="_blank">GitHub</a>
                    </div>
                    <div class="info">全球最大的代码托管平台</div>
                </div>
            </div>
            <div class="link-card" data-category="tech">
                <div class="avatar-placeholder">S</div>
                <div class="card-header">
                    <div>
                        <a href="https://stackoverflow.com" target="_blank">Stack Overflow</a>
                    </div>
                    <div class="info">程序员问答社区</div>
                </div>
            </div>
        </div>
        
        <h2 class="category-title">实用工具</h2>
        <div class="link-navigation">
            <div class="link-card" data-category="tools">
                <div class="avatar-placeholder">N</div>
                <div class="card-header">
                    <div>
                        <a href="https://notion.so" target="_blank">Notion</a>
                    </div>
                    <div class="info">一体化工作空间</div>
                </div>
            </div>
            <div class="link-card" data-category="tools">
                <div class="avatar-placeholder">F</div>
                <div class="card-header">
                    <div>
                        <a href="https://figma.com" target="_blank">Figma</a>
                    </div>
                    <div class="info">协作式UI设计工具</div>
                </div>
            </div>
        </div>
        
        <h2 class="category-title">设计灵感</h2>
        <div class="link-navigation">
            <div class="link-card" data-category="design">
                <div class="avatar-placeholder">D</div>
                <div class="card-header">
                    <div>
                        <a href="https://dribbble.com" target="_blank">Dribbble</a>
                    </div>
                    <div class="info">设计师作品展示平台</div>
                </div>
            </div>
            <div class="link-card" data-category="design">
                <div class="avatar-placeholder">B</div>
                <div class="card-header">
                    <div>
                        <a href="https://behance.net" target="_blank">Behance</a>
                    </div>
                    <div class="info">创意设计作品集</div>
                </div>
            </div>
            <div class="link-card" data-category="design">
                <img class="ava" src="https://i.loli.net/2020/05/14/5VyHPQqR6LWF39a.png" alt="Twitter"/>
                <div class="card-header">
                    <div>
                        <a href="https://twitter.com/" target="_blank">Twitter</a>
                    </div>
                    <div class="info">社交分享平台</div>
                </div>
            </div>
        </div>
    </div>
    
    <!-- 交换友链区域 - 修改版 -->
    <div class="exchange-section">
        <div class="exchange-content">
            <div class="my-info-simple">
                <h3>我的友链信息</h3>
                <pre>名称: Wcowin's Blog
链接: https://coolzest.github.io/
头像: https://cloudflare-imgbed-84u.pages.dev/file/blog/1762782543246_fav.ico
简介: 与自己和解</pre>
            </div>
            
        </div>
    </div>
    
    <div class="links-footer">
        <p>交换友链请在下方评论区留言，提供名称、链接、头像、简介！</p>
    </div>
</div>

<script>
    // 完全稳定的友链页面功能 - 优化动画版本
    (function() {
        // 确保页面完全加载后初始化
        function initLinksPage() {
            console.log('初始化友链页面功能');
            
            // 获取所有必要的元素
            const categoryBtns = document.querySelectorAll('.category-btn');
            const cards = document.querySelectorAll('.link-card');
            const categoryTitles = document.querySelectorAll('.category-title');
            
            // 重置所有状态
            function resetState() {
                // 移除所有隐藏状态
                cards.forEach(card => {
                    card.classList.remove('hidden');
                });
                
                categoryTitles.forEach(title => {
                    title.classList.remove('hidden');
                });
                
                // 重置按钮状态
                categoryBtns.forEach(btn => {
                    btn.classList.remove('active');
                });
                
                // 设置"全部"按钮为活动状态
                const allBtn = document.querySelector('.category-btn[data-category="all"]');
                if (allBtn) allBtn.classList.add('active');
            }
            
            // 处理分类筛选
            function filterByCategory(category) {
                console.log('筛选分类:', category);
                
                // 更新按钮状态
                categoryBtns.forEach(btn => {
                    if (btn.getAttribute('data-category') === category) {
                        btn.classList.add('active');
                    } else {
                        btn.classList.remove('active');
                    }
                });
                
                // 筛选卡片
                cards.forEach(card => {
                    if (category === 'all' || card.getAttribute('data-category') === category) {
                        // 显示卡片 - 使用CSS类控制动画
                        card.classList.remove('hidden');
                    } else {
                        // 隐藏卡片 - 使用CSS类控制动画
                        card.classList.add('hidden');
                    }
                });
                
                // 显示/隐藏分类标题
                categoryTitles.forEach(title => {
                    if (category === 'all') {
                        title.classList.remove('hidden');
                    } else {
                        // 检查该标题下是否有匹配分类的卡片
                        const nextSibling = title.nextElementSibling;
                        if (nextSibling && nextSibling.classList.contains('link-navigation')) {
                            const hasMatchingCard = Array.from(nextSibling.querySelectorAll('.link-card')).some(
                                card => card.getAttribute('data-category') === category && !card.classList.contains('hidden')
                            );
                            if (hasMatchingCard) {
                                title.classList.remove('hidden');
                            } else {
                                title.classList.add('hidden');
                            }
                        }
                    }
                });
            }
            
            // 为所有分类按钮添加点击事件
            categoryBtns.forEach(btn => {
                // 移除可能存在的旧事件监听器
                const newBtn = btn.cloneNode(true);
                btn.parentNode.replaceChild(newBtn, btn);
            });
            
            // 重新获取按钮并添加新的事件监听器
            const newCategoryBtns = document.querySelectorAll('.category-btn');
            newCategoryBtns.forEach(btn => {
                btn.addEventListener('click', function(e) {
                    e.preventDefault();
                    const category = this.getAttribute('data-category');
                    filterByCategory(category);
                });
            });
            
            // 卡片点击效果 - 优化为更平滑的动画
            cards.forEach(card => {
                card.addEventListener('click', function() {
                    // 添加点击反馈
                    this.style.transform = 'scale(0.98)';
                    setTimeout(() => {
                        this.style.transform = '';
                    }, 150);
                });
            });
            
            // 初始化页面状态
            resetState();
            
            // 添加滚动动画
            const observerOptions = {
                threshold: 0.1,
                rootMargin: '0px 0px -50px 0px'
            };
            
            const observer = new IntersectionObserver((entries) => {
                entries.forEach(entry => {
                    if (entry.isIntersecting) {
                        entry.target.style.opacity = '1';
                        entry.target.style.transform = 'translateY(0)';
                    }
                });
            }, observerOptions);
            
            // 观察所有卡片
            cards.forEach(card => {
                observer.observe(card);
            });
            
            console.log('友链页面功能初始化完成');
        }
        
        // 多种初始化方式确保功能正常
        document.addEventListener('DOMContentLoaded', initLinksPage);
        window.addEventListener('load', initLinksPage);
        
        // 如果页面是通过Ajax加载的，也尝试初始化
        if (document.readyState === 'interactive' || document.readyState === 'complete') {
            setTimeout(initLinksPage, 100);
        }
        
        // 监听URL变化（单页应用场景）
        let currentUrl = window.location.href;
        setInterval(() => {
            if (window.location.href !== currentUrl) {
                currentUrl = window.location.href;
                setTimeout(initLinksPage, 500);
            }
        }, 100);
        
        // 监听页面可见性变化
        document.addEventListener('visibilitychange', function() {
            if (!document.hidden) {
                setTimeout(initLinksPage, 100);
            }
        });
        
        // 最后确保无论如何都会尝试初始化
        setTimeout(initLinksPage, 500);
    })();
</script>