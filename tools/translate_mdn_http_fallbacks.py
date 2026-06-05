import re
import time
from pathlib import Path

from deep_translator import GoogleTranslator


ROOT = Path(__file__).resolve().parents[1]
HTTP_DIR = ROOT / "docs" / "notebooks" / "5_网络安全" / "http"

FILES = {
    "09_Compression_Dictionary_Transport.md": "压缩字典传输",
    "16_Cross-Origin_Resource_Policy_(CORP).md": "跨源资源策略（CORP）",
    "24_User-Agent_reduction.md": "User-Agent 缩减",
    "25_Fetch_metadata.md": "Fetch 元数据",
    "26_IFrame_credentialless.md": "无凭据 iframe",
    "27_Network_Error_Logging_(NEL).md": "网络错误日志（NEL）",
}

translator = GoogleTranslator(source="en", target="zh-CN")
cache: dict[str, str] = {}


def translate_plain(text: str) -> str:
    if not re.search(r"[A-Za-z]", text):
        return text
    if text in cache:
        return cache[text]
    for attempt in range(4):
        try:
            result = translator.translate(text)
            cache[text] = result
            time.sleep(0.08)
            return result
        except Exception:
            if attempt == 3:
                return text
            time.sleep(1.5 * (attempt + 1))
    return text


def translate_inline(text: str) -> str:
    links: list[tuple[str, str]] = []

    def hold_link(match: re.Match[str]) -> str:
        label = translate_inline(match.group(1))
        url = match.group(2)
        token = f"⟦{1000 + len(links)}⟧"
        links.append((token, f"[{label}]({url})"))
        return token

    text = re.sub(r"\[([^\]]+)\]\(([^)]+)\)", hold_link, text)

    codes: list[tuple[str, str]] = []

    def hold_code(match: re.Match[str]) -> str:
        token = f"⟦{2000 + len(codes)}⟧"
        codes.append((token, match.group(0)))
        return token

    text = re.sub(r"`[^`]+`", hold_code, text)
    translated = translate_plain(text)
    for token, value in links + codes:
        translated = translated.replace(token, value)
    return translated


def translate_table_row(line: str) -> str:
    if not line.startswith("|") or re.fullmatch(r"\|?\s*:?-{3,}:?\s*(\|\s*:?-{3,}:?\s*)+\|?", line):
        return line
    parts = line.split("|")
    translated = []
    for index, part in enumerate(parts):
        if index in (0, len(parts) - 1) and part == "":
            translated.append(part)
        else:
            translated.append(translate_inline(part.strip()))
    return "| " + " | ".join(translated[1:-1]) + " |" if line.startswith("|") and line.endswith("|") else "|".join(translated)


def translate_line(line: str) -> str:
    if not line.strip():
        return line
    if line.lstrip().startswith(("```", "<", "</")):
        return line
    if line.startswith("|"):
        return translate_table_row(line)
    if line.startswith("!!!"):
        return line

    match = re.match(r"^(\s*(?:#{1,6}\s+|[-*]\s+|\d+\.\s+|>\s+|- :\s*|:\s*))(.*)$", line)
    if match:
        return match.group(1) + translate_inline(match.group(2))

    return translate_inline(line)


def replace_front_matter(content: str, title: str) -> str:
    match = re.match(r"^---\s*\n(.*?)\n---\s*\n", content, re.S)
    if not match:
        return content
    front = match.group(1)
    front = re.sub(r"^title:.*$", f"title: {title}", front, flags=re.M)
    front = re.sub(r'^description:.*$', f'description: "MDN HTTP 指南：{title}"', front, flags=re.M)
    return "---\n" + front + "\n---\n" + content[match.end():]


def translate_content(content: str) -> str:
    front_match = re.match(r"^---\s*\n.*?\n---\s*\n", content, re.S)
    front = front_match.group(0) if front_match else ""
    body = content[len(front):]

    output: list[str] = []
    in_code = False
    for line in body.splitlines():
        if line.lstrip().startswith("```"):
            in_code = not in_code
            output.append(line)
            continue
        if in_code:
            output.append(line)
            continue
        output.append(translate_line(line))
    return front + "\n".join(output) + "\n"


def main() -> None:
    for filename, title in FILES.items():
        path = HTTP_DIR / filename
        content = path.read_text(encoding="utf-8")
        content = replace_front_matter(content, title)
        content = translate_content(content)
        content = content.replace(f"# {FILES[filename] if filename in FILES else title}", f"# {title}", 1)
        path.write_text(content, encoding="utf-8", newline="\n")
        print(f"translated {filename} -> {title}")


if __name__ == "__main__":
    main()
