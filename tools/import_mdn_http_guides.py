import base64
import json
import re
import shutil
import urllib.parse
import urllib.request
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
OUT_DIR = ROOT / "docs" / "notebooks" / "5_网络安全" / "http"
ASSET_DIR = ROOT / "docs" / "assets" / "images" / "mdn" / "http"
RAW_BASE_EN = "https://raw.githubusercontent.com/mdn/content/main"
RAW_BASE_ZH = "https://raw.githubusercontent.com/mdn/translated-content/main"
DATE = "2026-04-25"

ORDER = [
    "index.md",
    "overview",
    "evolution_of_http",
    "messages",
    "session",
    "connection_management_in_http_1.x",
    "cookies",
    "caching",
    "compression",
    "compression_dictionary_transport",
    "conditional_requests",
    "range_requests",
    "content_negotiation",
    "authentication",
    "cors",
    "csp",
    "cross-origin_resource_policy",
    "permissions_policy",
    "redirections",
    "proxy_servers_and_tunneling",
    "protocol_upgrade_mechanism",
    "mime_types",
    "browser_detection_using_the_user_agent",
    "client_hints",
    "user-agent_reduction",
    "fetch_metadata",
    "iframe_credentialless",
    "network_error_logging",
]

TITLE_OVERRIDES = {
    "index.md": "HTTP 指南",
}


def fetch_text(url: str) -> str:
    req = urllib.request.Request(url, headers={"User-Agent": "coolzest-mdn-importer"})
    with urllib.request.urlopen(req, timeout=60) as response:
        return response.read().decode("utf-8")


def fetch_bytes(url: str) -> bytes:
    req = urllib.request.Request(url, headers={"User-Agent": "coolzest-mdn-importer"})
    with urllib.request.urlopen(req, timeout=60) as response:
        return response.read()


def url_exists(url: str) -> bool:
    req = urllib.request.Request(url, headers={"User-Agent": "coolzest-mdn-importer"})
    try:
        with urllib.request.urlopen(req, timeout=30) as response:
            response.read(1)
            return True
    except Exception:
        return False


def parse_front_matter(markdown: str) -> tuple[dict[str, str], str]:
    match = re.match(r"^---\s*\n(.*?)\n---\s*\n?", markdown, re.DOTALL)
    if not match:
        return {}, markdown

    meta: dict[str, str] = {}
    for line in match.group(1).splitlines():
        if ":" not in line:
            continue
        key, value = line.split(":", 1)
        meta[key.strip()] = value.strip().strip("\"'")
    return meta, markdown[match.end() :]


def macro_text(args: str) -> str:
    quoted = re.findall(r"""['"]([^'"]+)['"]""", args)
    if len(quoted) >= 2:
        return quoted[1]
    if quoted:
        return quoted[0]
    return args.strip()


def convert_macros(markdown: str) -> str:
    inline_labels = {
        "Deprecated_Inline": "已弃用",
        "Experimental_Inline": "实验性",
        "Non-standard_Inline": "非标准",
        "SecureContext_Inline": "安全上下文",
        "optional_inline": "可选",
    }

    for macro, label in inline_labels.items():
        markdown = re.sub(r"\{\{\s*" + re.escape(macro) + r"\s*(?:\([^}]*\))?\s*\}\}", f"_{label}_", markdown, flags=re.I)

    code_macros = [
        "CSP",
        "HTTPHeader",
        "HTTPMethod",
        "HTTPStatus",
        "HTTPVersion",
        "DOMxRef",
        "domxref",
        "CSSxRef",
        "cssxref",
        "HTMLElement",
        "htmlelement",
        "SVGElement",
        "svgelement",
        "JSxRef",
        "jsxref",
        "MathMLElement",
        "RFC",
        "Glossary",
        "glossary",
    ]

    def replace_macro(match: re.Match[str]) -> str:
        name = match.group(1)
        text = macro_text(match.group(2))
        if name.lower() in {"glossary", "rfc"}:
            return text
        return f"`{text}`"

    pattern = r"\{\{\s*(" + "|".join(code_macros) + r")\s*\((.*?)\)\s*\}\}"
    markdown = re.sub(pattern, replace_macro, markdown, flags=re.I | re.S)
    markdown = re.sub(r"\{\{\s*Compat\s*\}\}", "", markdown, flags=re.I)
    markdown = re.sub(r"\{\{\s*SeeCompatTable\s*\}\}", "_实验性_", markdown, flags=re.I)
    markdown = re.sub(r"\{\{\s*Specifications\s*\}\}", "_规范信息请参见 MDN 原文页面。_", markdown, flags=re.I)
    markdown = re.sub(r"\{\{\s*SubPagesWithSummaries\s*\}\}", "", markdown, flags=re.I)
    markdown = re.sub(r"\{\{\s*[A-Za-z0-9_-]+\s*\((.*?)\)\s*\}\}", lambda match: macro_text(match.group(1)), markdown, flags=re.S)
    return markdown


def make_anchor(text: str) -> str:
    text = re.sub(r"<[^>]+>", "", text)
    text = re.sub(r"`([^`]+)`", r"\1", text)
    text = text.replace("_", " ")
    text = text.lower()
    text = re.sub(r"[^\w\s-]", "", text)
    text = re.sub(r"\s+", "-", text.strip())
    return text


def convert_mdn_links(markdown: str) -> str:
    def replace_link(match: re.Match[str]) -> str:
        label, url = match.group(1), match.group(2)
        if url.startswith(("/en-US/docs/", "/zh-CN/docs/")):
            return f"[{label}](https://mdn.org.cn{url})"
        if url.startswith("#"):
            return f"[{label}](#{make_anchor(url[1:])})"
        return match.group(0)

    return re.sub(r"\[([^\]]+)\]\(([^)]+)\)", replace_link, markdown)


def localize_images(markdown: str, page_key: str, source_base_url: str) -> str:
    page_asset_dir = ASSET_DIR / page_key.replace(".", "_")
    page_asset_rel = f"../../../assets/images/mdn/http/{page_key.replace('.', '_')}"

    def replace_image(match: re.Match[str]) -> str:
        alt, url = match.group(1), match.group(2)
        if url.startswith("/shared-assets/"):
            source_url = "https://mdn.github.io" + url
        elif url.startswith("/"):
            source_url = "https://mdn.org.cn" + url
        elif url.startswith(("http://", "https://")):
            source_url = url
        else:
            source_url = urllib.parse.urljoin(source_base_url + "/", url)

        if not source_url.startswith(("http://", "https://")):
            return match.group(0)

        parsed = urllib.parse.urlparse(source_url)
        name = Path(parsed.path).name or "image"
        if not name:
            return match.group(0)
        page_asset_dir.mkdir(parents=True, exist_ok=True)
        target = page_asset_dir / name
        try:
            target.write_bytes(fetch_bytes(source_url))
        except Exception:
            return match.group(0)
        return f"![{alt}]({page_asset_rel}/{name})"

    return re.sub(r"!\[([^\]]*)\]\(([^)]+)\)", replace_image, markdown)


def raw_url(item: dict) -> str:
    return raw_url_for(item, "en")


def raw_url_for(item: dict, lang: str) -> str:
    base = RAW_BASE_ZH if lang == "zh" else RAW_BASE_EN
    path = item["path"]
    if lang == "zh":
        path = path.replace("files/en-us/", "files/zh-cn/", 1)
    if item["type"] == "dir":
        return f"{base}/{path}/index.md"
    return f"{base}/{path}"


def raw_base_url(item: dict) -> str:
    return raw_base_url_for(item, "en")


def raw_base_url_for(item: dict, lang: str) -> str:
    base = RAW_BASE_ZH if lang == "zh" else RAW_BASE_EN
    path = item["path"]
    if lang == "zh":
        path = path.replace("files/en-us/", "files/zh-cn/", 1)
    if item["type"] == "dir":
        return f"{base}/{path}"
    return f"{base}/{str(path).rsplit('/', 1)[0]}"


def output_name(index: int, key: str, title: str) -> str:
    if key == "index.md":
        return "index.md"
    safe_title = re.sub(r"[\\/:*?\"<>|]+", "", title).strip()
    safe_title = safe_title.replace(" ", "_")
    return f"{index:02d}_{safe_title}.md"


def mdn_url(meta: dict[str, str], key: str) -> str:
    slug = meta.get("slug")
    if slug:
        return f"https://mdn.org.cn/zh-CN/docs/{slug}"
    if key == "index.md":
        return "https://mdn.org.cn/zh-CN/docs/Web/HTTP/Guides"
    return f"https://mdn.org.cn/zh-CN/docs/Web/HTTP/Guides/{key}"


def front_matter(title: str) -> str:
    return (
        "---\n"
        f"title: {title}\n"
        f"date: {DATE}\n"
        f'description: "MDN HTTP 指南：{title}"\n'
        "categories:\n"
        "  - 网络安全\n"
        "  - HTTP\n"
        "tags:\n"
        "  - HTTP\n"
        "  - MDN\n"
        "comments: true\n"
        "---\n\n"
    )


def notice(source_url: str) -> str:
    return (
        '!!! info "来源声明"\n'
        f"    本文照搬整理自 MDN Web Docs 中文文档：[{source_url}]({source_url})。\n"
        "    内容版权归 MDN contributors 所有，并受 Creative Commons 许可约束；本站仅用于个人学习归档与排版适配。\n\n"
    )


def fallback_notice(source_url: str) -> str:
    return (
        '!!! warning "来源声明"\n'
        f"    MDN 暂未提供该页面的官方中文译文；本文基于英文原文归档：[{source_url}]({source_url})。\n"
        "    内容版权归 MDN contributors 所有，并受 Creative Commons 许可约束；本站仅用于个人学习归档与排版适配。\n\n"
    )


def main() -> None:
    if OUT_DIR.exists():
        shutil.rmtree(OUT_DIR)
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    ASSET_DIR.mkdir(parents=True, exist_ok=True)

    by_name = {
        name: {
            "name": name,
            "path": f"files/en-us/web/http/guides/{name}" if name == "index.md" else f"files/en-us/web/http/guides/{name}",
            "type": "file" if name == "index.md" else "dir",
        }
        for name in ORDER
    }
    ordered = list(ORDER)

    old_theory_page = ROOT / "docs" / "notebooks" / "2_理论学习" / "计算机网络" / "07_HTTP概述.md"
    if old_theory_page.exists():
        old_theory_page.unlink()
    old_assets = ROOT / "docs" / "assets" / "images" / "mdn" / "http-overview"
    if old_assets.exists():
        shutil.rmtree(old_assets)

    written = []
    index_entries = []
    fallback_pages = []
    for number, name in enumerate(ordered):
        zh_raw_url = raw_url_for(by_name[name], "zh")
        has_zh = url_exists(zh_raw_url)
        lang = "zh" if has_zh else "en"
        raw = fetch_text(raw_url_for(by_name[name], lang))
        meta, body = parse_front_matter(raw)
        title = TITLE_OVERRIDES.get(name) or meta.get("title") or name.replace("_", " ").title()
        body = convert_macros(body)
        body = convert_mdn_links(body)
        body = localize_images(body, name.removesuffix(".md"), raw_base_url_for(by_name[name], lang))

        if not body.lstrip().startswith("# "):
            body = f"# {title}\n\n{body.lstrip()}"

        path = OUT_DIR / output_name(number, name, title)
        if name != "index.md":
            index_entries.append((title, path.name, mdn_url(meta, name)))
        if not has_zh:
            fallback_pages.append(title)

        source_url = mdn_url(meta, name)
        content = front_matter(title) + (notice(source_url) if has_zh else fallback_notice(source_url)) + body.rstrip() + "\n"
        path.write_text(content, encoding="utf-8", newline="\n")
        written.append(path)

    index_path = OUT_DIR / "index.md"
    if index_path.exists():
        index_content = index_path.read_text(encoding="utf-8")
        index_content = re.sub(r"\n## 本地归档列表\n\n.*\Z", "", index_content, flags=re.S)
        index_content = index_content.rstrip() + "\n\n## 本地归档列表\n\n"
        for item_title, item_name, item_url in index_entries:
            index_content += f"- [{item_title}]({item_name}) - [MDN 原文]({item_url})\n"
        index_path.write_text(index_content, encoding="utf-8", newline="\n")

    print(f"Imported {len(written)} MDN HTTP guide files into {OUT_DIR}")
    if fallback_pages:
        print("Fallback to English for:")
        for title in fallback_pages:
            print(f"  - {title}")
    for path in written:
        print(path.relative_to(ROOT))


if __name__ == "__main__":
    main()
