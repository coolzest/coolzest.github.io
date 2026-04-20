document.addEventListener('DOMContentLoaded', function() {
  // 遍历所有代码块容器（包含代码类型标签的.highlight）
  const codeBlocks = document.querySelectorAll('.highlight');
  codeBlocks.forEach((block) => {
    // 保存原始代码内容（从<pre>标签中提取）
    const pre = block.querySelector('pre');
    if (!pre) return; // 跳过无代码的容器
    const originalCode = pre.textContent.trim();
    
    // 创建按钮容器
    const actionsDiv = document.createElement('div');
    actionsDiv.className = 'code-actions';
    
    // 编辑按钮
    const editBtn = document.createElement('button');
    editBtn.textContent = '编辑代码';
    editBtn.onclick = function() {
      // 创建可编辑文本框
      const textarea = document.createElement('textarea');
      textarea.className = 'code-block-editable';
      textarea.value = originalCode;
      
      // 恢复按钮
      const restoreBtn = document.createElement('button');
      restoreBtn.textContent = '恢复原始';
      restoreBtn.onclick = function() {
        // 还原为原始代码块
        const newPre = document.createElement('pre');
        const code = document.createElement('code');
        code.textContent = originalCode;
        newPre.appendChild(code);
        block.replaceChild(newPre, textarea); // 替换文本框为代码块
        actionsDiv.replaceChild(editBtn, restoreBtn); // 换回编辑按钮
      };
      
      // 替换原始代码块为文本框，按钮换成恢复按钮
      block.replaceChild(textarea, pre);
      actionsDiv.replaceChild(restoreBtn, editBtn);
    };
    
    // 将按钮容器插入到代码块中（在代码类型标签下方，代码内容上方）
    const filename = block.querySelector('span.filename');
    if (filename) {
      block.insertBefore(actionsDiv, filename.nextSibling); // 有标签时放在标签下方
    } else {
      block.insertBefore(actionsDiv, pre); // 无标签时放在代码上方
    }
  });
});