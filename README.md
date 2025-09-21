[我的独立博客](http://www.coolzest.github.io/)
=================================

一个简洁的、多设备支持的 Jekyll 博客模板，用于搭建[我的独立博客](http://www.coolzest.github.io/)。  
[我的独立博客](http://www.coolzest.github.io/) 主题基于 [maupassant-jekyll](https://github.com/alafighting/maupassant-jekyll.git) 
重新修改和优化，同时很大程度上参考了 [kuanghy](https://github.com/kuanghy) 的博客主题 [luring](https://github.com/kuanghy/luring)，感谢。  
模板预览：
![template preview](https://camo.githubusercontent.com/74fd2ccea00a682742515ce1d3725283c3385721/687474703a2f2f6f6f6f2e306f302e6f6f6f2f323031352f31302f32342f353632623562653132313737652e6a7067)  
希望你在介绍自己的博客主题时，也能像上面一样，援引一下我的博客主题～～  


## **使用我的博客主题的注意事项：**  
**首先要感谢你使用我的博客主题！**   
我的博客主题里有一些自己定制化的内容，其中涉及到一些信息获取的事宜(比如百度统计的代码，你忘记修改的话，
我可以直接获取到你的网站的各种访问信息呦🙈)，所以我一一都写在了 **[这篇博文](https://www.coolzest.github.io/2018/12/18/notices-for-jekyll-themes-fork/ "对没错，就是是这篇超级暖心的博文")**
 里，敬请访问～～
[![a_glimpse_of_this_blog](https://raw.githubusercontent.com/coolzest/image_gallery/master/blogs/notices_for_fork_theme/a_glimpse_of_this_blog.png)](https://www.coolzest.github.io/2018/12/18/notices-for-jekyll-themes-fork/ "点击图像直达博文～～")  
是不是超级暖心？🐼    


## 主题安装

安装 Jekyll 本地环境，以便于调试：

```bash
gem install jekyll
jekyll new my-awesome-site
cd my-awesome-site
bundle install
bundle exec jekyll serve
# => 打开浏览器 http://localhost:4000
```

下载原作者主题安装调试：

```bash
git clone https://github.com/alafighting/maupassant-jekyll.git maupassant
cd maupassant
# 当然你也可以选择clone我的这个更改后的博客主题，只需改一下地址即可：
# git clone https://github.com/coolzest/coolzest.github.io coolzest
# cd coolzest
gem install jekyll-paginate
jekyll build
jekyll server
```

### 修改说明

#### 复制按钮功能
- **文件位置**：`assets/js/copy-code.js`
- **作用**：为代码框添加复制功能，鼠标悬停时显示复制图标。
- **相关样式**：`assets/css/style.css` 中的 `.copy-button` 和 `pre:hover .copy-button`。

#### 博客整体排版优化
- **文件位置**：`assets/css/style.css`
- **作用**：
  - 调整字体为 `Arial`，提高可读性。
  - 优化标题和段落的间距。
  - 为代码框添加左侧边框和背景色。
  - 设置文章内容区域的最大宽度和居中显示。

#### 测试与验证
- 请在本地运行博客，检查复制按钮和整体排版效果是否符合预期。

**Any star, fork or [donation](https://www.coolzest.github.io/donate/ "赏个铜板") is highly appreciated!!!**  
![yasashii](https://raw.githubusercontent.com/coolzest/image_gallery/master/blogs/anime/%E6%B8%A9%E6%9F%94%E7%9A%84%E7%94%B7%E5%AD%A9%E5%AD%90.jpg "当然，女孩子会更温柔的啦～～")  

------

coolzest(<coolzest@outlook.com>)<br>
2018-09-17
