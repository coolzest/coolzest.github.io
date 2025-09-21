// JavaScript for adding copy functionality to code blocks

document.addEventListener("DOMContentLoaded", function () {
    const codeBlocks = document.querySelectorAll("pre code");

    codeBlocks.forEach((block) => {
        // Create a copy button
        const button = document.createElement("button");
        button.innerText = "复制";
        button.className = "copy-button";

        // Append the button to the code block
        const pre = block.parentNode;
        pre.style.position = "relative";
        pre.appendChild(button);

        // Add click event to copy the code
        button.addEventListener("click", () => {
            navigator.clipboard.writeText(block.innerText).then(() => {
                button.innerText = "已复制!";
                setTimeout(() => (button.innerText = "复制"), 2000);
            });
        });
    });
});