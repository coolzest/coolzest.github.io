import argparse
import datetime
import html
import importlib
import os
import queue
import re
import shutil
import signal
import socket
import subprocess
import sys
import threading
import time
import webbrowser
from pathlib import Path
from tkinter import (
    BOTH,
    END,
    LEFT,
    RIGHT,
    SINGLE,
    W,
    Y,
    Button,
    Frame,
    Listbox,
    Scrollbar,
    StringVar,
    Text,
    Tk,
    Toplevel,
    messagebox,
    simpledialog,
    ttk,
)
from urllib.parse import quote

from ruamel.yaml import YAML


APP_TITLE = "Coolzest NOTE"
CONDA_ENV = "mkdocs-env"
HOST = "127.0.0.1"
PORT = 8000
CURRENT_PORT = PORT
ROOT_DIR = "docs/notebooks"
MKDOCS_YML = "mkdocs.yml"
NOTEBOOKS_DIR = ROOT_DIR
NAV_DOCUMENT_EXTENSIONS = {".md", ".html"}
BLOG_POSTS_DIR = "docs/notebooks/6_博客/posts"
FRIENDS_FILE = "docs/notebooks/7_朋友.md"
APP_ICON_FILE = "app_assets/coolzest_note.ico"

DISPLAY_NAME_OVERRIDES = {
    "python学习": "Python 学习",
}


def site_url(path=""):
    return f"http://{HOST}:{CURRENT_PORT}/{path}"


def find_available_port(host=HOST, preferred_port=PORT, max_tries=20):
    for port in range(preferred_port, preferred_port + max_tries):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            try:
                sock.bind((host, port))
            except OSError:
                continue
            return port
    return preferred_port

try:
    import pystray
except ImportError:
    pystray = None

Image = None
ImageDraw = None


def load_tray_image_tools():
    global Image, ImageDraw
    if Image is not None and ImageDraw is not None:
        return True
    try:
        Image = importlib.import_module("PIL.Image")
        ImageDraw = importlib.import_module("PIL.ImageDraw")
    except ImportError:
        Image = None
        ImageDraw = None
        return False
    return True


class NativeWindowsTray:
    """Small dependency-free tray icon for Windows.

    It keeps the app usable even when pystray/Pillow are not installed.
    Double-click or right-click the tray icon to show the Tk window again.
    """

    def __init__(self, title, on_show):
        self.title = title
        self.on_show = on_show
        self.thread = None
        self.hwnd = None
        self.nid = None
        self._wndproc_ref = None
        self._ready = threading.Event()

    def run(self):
        self.thread = threading.Thread(target=self._message_loop, daemon=True)
        self.thread.start()
        self._ready.wait(timeout=2)

    def stop(self):
        if os.name != "nt":
            return
        import ctypes
        from ctypes import wintypes

        if self.hwnd and self.nid:
            ctypes.windll.shell32.Shell_NotifyIconW(0x00000002, ctypes.byref(self.nid))
            ctypes.windll.user32.PostMessageW(self.hwnd, wintypes.UINT(0x0010), 0, 0)

    def _message_loop(self):
        if os.name != "nt":
            return

        import ctypes
        from ctypes import wintypes

        user32 = ctypes.windll.user32
        shell32 = ctypes.windll.shell32
        kernel32 = ctypes.windll.kernel32
        WPARAM = ctypes.c_size_t
        LPARAM = ctypes.c_ssize_t
        LRESULT = ctypes.c_ssize_t
        user32.DefWindowProcW.argtypes = [wintypes.HWND, wintypes.UINT, WPARAM, LPARAM]
        user32.DefWindowProcW.restype = LRESULT

        WM_DESTROY = 0x0002
        WM_CLOSE = 0x0010
        WM_USER = 0x0400
        WM_TRAYICON = WM_USER + 20
        WM_LBUTTONDBLCLK = 0x0203
        WM_RBUTTONUP = 0x0205
        NIF_MESSAGE = 0x00000001
        NIF_ICON = 0x00000002
        NIF_TIP = 0x00000004
        NIM_ADD = 0x00000000
        IDI_APPLICATION = 32512

        WNDPROC = ctypes.WINFUNCTYPE(
            LRESULT,
            wintypes.HWND,
            wintypes.UINT,
            WPARAM,
            LPARAM,
        )

        class WNDCLASSW(ctypes.Structure):
            _fields_ = [
                ("style", wintypes.UINT),
                ("lpfnWndProc", WNDPROC),
                ("cbClsExtra", ctypes.c_int),
                ("cbWndExtra", ctypes.c_int),
                ("hInstance", wintypes.HINSTANCE),
                ("hIcon", wintypes.HICON),
                ("hCursor", wintypes.HANDLE),
                ("hbrBackground", wintypes.HANDLE),
                ("lpszMenuName", wintypes.LPCWSTR),
                ("lpszClassName", wintypes.LPCWSTR),
            ]

        class GUID(ctypes.Structure):
            _fields_ = [
                ("Data1", wintypes.DWORD),
                ("Data2", wintypes.WORD),
                ("Data3", wintypes.WORD),
                ("Data4", ctypes.c_ubyte * 8),
            ]

        class NOTIFYICONDATAW(ctypes.Structure):
            _fields_ = [
                ("cbSize", wintypes.DWORD),
                ("hWnd", wintypes.HWND),
                ("uID", wintypes.UINT),
                ("uFlags", wintypes.UINT),
                ("uCallbackMessage", wintypes.UINT),
                ("hIcon", wintypes.HICON),
                ("szTip", wintypes.WCHAR * 128),
                ("dwState", wintypes.DWORD),
                ("dwStateMask", wintypes.DWORD),
                ("szInfo", wintypes.WCHAR * 256),
                ("uTimeoutOrVersion", wintypes.UINT),
                ("szInfoTitle", wintypes.WCHAR * 64),
                ("dwInfoFlags", wintypes.DWORD),
                ("guidItem", GUID),
                ("hBalloonIcon", wintypes.HICON),
            ]

        class POINT(ctypes.Structure):
            _fields_ = [("x", wintypes.LONG), ("y", wintypes.LONG)]

        class MSG(ctypes.Structure):
            _fields_ = [
                ("hwnd", wintypes.HWND),
                ("message", wintypes.UINT),
                ("wParam", WPARAM),
                ("lParam", LPARAM),
                ("time", wintypes.DWORD),
                ("pt", POINT),
            ]

        def wndproc(hwnd, msg, wparam, lparam):
            if msg == WM_TRAYICON and lparam in (WM_LBUTTONDBLCLK, WM_RBUTTONUP):
                self.on_show()
                return 0
            if msg == WM_CLOSE:
                user32.DestroyWindow(hwnd)
                return 0
            if msg == WM_DESTROY:
                user32.PostQuitMessage(0)
                return 0
            return user32.DefWindowProcW(hwnd, msg, wparam, lparam)

        self._wndproc_ref = WNDPROC(wndproc)
        hinstance = kernel32.GetModuleHandleW(None)
        class_name = "CoolzestNoteTrayWindow"

        wc = WNDCLASSW()
        wc.lpfnWndProc = self._wndproc_ref
        wc.hInstance = hinstance
        wc.lpszClassName = class_name
        user32.RegisterClassW(ctypes.byref(wc))

        self.hwnd = user32.CreateWindowExW(
            0,
            class_name,
            self.title,
            0,
            0,
            0,
            0,
            0,
            None,
            None,
            hinstance,
            None,
        )

        icon = user32.LoadIconW(None, IDI_APPLICATION)
        self.nid = NOTIFYICONDATAW()
        self.nid.cbSize = ctypes.sizeof(NOTIFYICONDATAW)
        self.nid.hWnd = self.hwnd
        self.nid.uID = 1
        self.nid.uFlags = NIF_MESSAGE | NIF_ICON | NIF_TIP
        self.nid.uCallbackMessage = WM_TRAYICON
        self.nid.hIcon = icon
        self.nid.szTip = f"{self.title} - 双击显示"
        shell32.Shell_NotifyIconW(NIM_ADD, ctypes.byref(self.nid))
        self._ready.set()

        msg = MSG()
        while user32.GetMessageW(ctypes.byref(msg), None, 0, 0) > 0:
            user32.TranslateMessage(ctypes.byref(msg))
            user32.DispatchMessageW(ctypes.byref(msg))


def project_root():
    candidates = []
    if getattr(sys, "frozen", False):
        candidates.append(Path(sys.executable).resolve().parent)
    candidates.extend([Path(__file__).resolve().parent, Path.cwd()])

    for start in candidates:
        for folder in (start, *start.parents):
            if (folder / MKDOCS_YML).exists() and (folder / NOTEBOOKS_DIR).exists():
                return folder

    if getattr(sys, "frozen", False):
        return Path(sys.executable).resolve().parent
    return Path(__file__).resolve().parent


def notebooks_path():
    return project_root() / NOTEBOOKS_DIR


def blog_posts_path():
    return project_root() / BLOG_POSTS_DIR


def friends_file_path():
    return project_root() / FRIENDS_FILE


def app_icon_path():
    bundled_root = getattr(sys, "_MEIPASS", None)
    if bundled_root:
        bundled_icon = Path(bundled_root) / APP_ICON_FILE
        if bundled_icon.exists():
            return bundled_icon
    return project_root() / APP_ICON_FILE


def open_path(path):
    path = Path(path)
    if os.name == "nt":
        os.startfile(path)
    elif sys.platform == "darwin":
        subprocess.Popen(["open", str(path)])
    else:
        subprocess.Popen(["xdg-open", str(path)])


def parse_prefix(name):
    # 匹配序号前缀，如 "1 ", "1_", "1.1 ", "1.3_"
    match = re.match(r"^(\d+(?:\.\d+)*)(?:[ _]+)", name)
    if match:
        prefix = match.group(1)
        parts = tuple(int(x) for x in prefix.split("."))
        return parts, normalize_display_name(name[match.end() :].strip())

    # 匹配日期前缀，如 "2024-08-17-Linux常用命令"
    match = re.match(r"^(\d{4})-(\d{2})-(\d{2})[-_ ]+", name)
    if match:
        parts = tuple(int(x) for x in match.groups())
        return parts, normalize_display_name(name[match.end() :].strip())

    return (), normalize_display_name(name.strip())


def normalize_display_name(name):
    return DISPLAY_NAME_OVERRIDES.get(name, name)


def sort_key(name):
    prefix, title = parse_prefix(name)
    return 0 if prefix else 1, prefix, title.lower()


def collect_files(root_dir):
    files = []
    for dirpath, dirnames, filenames in os.walk(root_dir):
        dirnames.sort(key=sort_key)
        filenames.sort(key=sort_key)
        for filename in filenames:
            if Path(filename).suffix.lower() not in NAV_DOCUMENT_EXTENSIONS:
                continue

            rel_path = os.path.relpath(os.path.join(dirpath, filename), root_dir)
            rel_path = rel_path.replace(os.sep, "/")
            if rel_path.startswith("6_博客/posts/"):
                continue
            files.append(rel_path)
    return files


def read_front_matter_title(root_dir, rel_path):
    path = os.path.join(root_dir, rel_path)
    try:
        with open(path, "r", encoding="utf-8") as f:
            content = f.read(4096)
    except OSError:
        return None

    match = re.match(r"^---\s*\n(.*?)\n---\s*\n", content, re.DOTALL)
    if not match:
        return None

    title_match = re.search(r"^title:\s*(.+?)\s*$", match.group(1), re.MULTILINE)
    if not title_match:
        return None

    return title_match.group(1).strip().strip("\"'")


def read_html_title(root_dir, rel_path):
    path = os.path.join(root_dir, rel_path)
    try:
        with open(path, "r", encoding="utf-8") as f:
            content = f.read(65536)
    except (OSError, UnicodeError):
        return None

    title_match = re.search(r"<title\b[^>]*>(.*?)</title>", content, re.IGNORECASE | re.DOTALL)
    if not title_match:
        return None

    title = re.sub(r"<[^>]+>", "", title_match.group(1))
    title = html.unescape(title)
    return re.sub(r"\s+", " ", title).strip() or None


def read_document_title(root_dir, rel_path):
    extension = Path(rel_path).suffix.lower()
    if extension == ".md":
        return read_front_matter_title(root_dir, rel_path)
    if extension == ".html":
        return read_html_title(root_dir, rel_path)
    return None


def build_nav(files, root_dir):
    tree = {}
    for rel_path in files:
        parts = rel_path.split("/")
        current = tree
        for part in parts[:-1]:
            prefix, name = parse_prefix(part)
            current = current.setdefault((prefix, name), {})
        prefix, name = parse_prefix(Path(parts[-1]).stem)
        if name.lower() != "index":
            name = read_document_title(root_dir, rel_path) or name
        current[(prefix, name)] = "notebooks/" + rel_path

    def build_tree(node):
        def nav_sort_key(item):
            prefix, name = item[0]
            if name.lower() == "index":
                return -1, (), ""
            return 0 if prefix else 1, prefix, name.lower()

        nav = []
        for key, value in sorted(node.items(), key=nav_sort_key):
            _, name = key
            if isinstance(value, dict):
                nav.append({name: build_tree(value)})
            elif name.lower() == "index":
                nav.append(value)
            else:
                nav.append({name: value})
        return nav

    return build_tree(tree)


def load_mkdocs(path=MKDOCS_YML):
    yaml = YAML()
    yaml.indent(mapping=2, sequence=4, offset=2)
    yaml.width = 4096
    yaml.allow_unicode = True
    yaml.default_flow_style = False

    with open(path, "r", encoding="utf-8") as f:
        config = yaml.load(f)
    return config, yaml


def generate_nav(root_dir=ROOT_DIR, mkdocs_path=MKDOCS_YML):
    files = collect_files(root_dir)
    nav = build_nav(files, root_dir)

    config, yaml = load_mkdocs(mkdocs_path)
    config["nav"] = nav

    with open(mkdocs_path, "w", encoding="utf-8") as f:
        yaml.dump(config, f)

    return len(files)


def find_conda():
    candidates = [
        os.environ.get("CONDA_EXE"),
        shutil.which("conda"),
        Path.home() / "miniconda3" / "Scripts" / "conda.exe",
        Path.home() / "anaconda3" / "Scripts" / "conda.exe",
    ]
    for candidate in candidates:
        if candidate and Path(candidate).exists():
            return str(candidate)
    return "conda"


def find_conda_env_python():
    executable_name = "python.exe" if os.name == "nt" else "python"
    candidates = []

    conda_exe = os.environ.get("CONDA_EXE")
    if conda_exe:
        conda_root = Path(conda_exe).resolve().parent.parent
        candidates.append(conda_root / "envs" / CONDA_ENV / executable_name)

    candidates.extend(
        [
            Path.home() / "miniconda3" / "envs" / CONDA_ENV / executable_name,
            Path.home() / "anaconda3" / "envs" / CONDA_ENV / executable_name,
        ]
    )

    for candidate in candidates:
        if candidate.exists():
            return str(candidate)
    return None


def mkdocs_command(*arguments):
    env_python = find_conda_env_python()
    if env_python:
        return [env_python, "-s", "-m", "mkdocs", *arguments]

    return [
        find_conda(),
        "run",
        "--no-capture-output",
        "-n",
        CONDA_ENV,
        "python",
        "-s",
        "-m",
        "mkdocs",
        *arguments,
    ]


class MkDocsServer:
    def __init__(self, log_callback, status_callback, url_callback=None):
        self.log_callback = log_callback
        self.status_callback = status_callback
        self.url_callback = url_callback
        self.process = None
        self.reader_thread = None
        self.stopping_pids = set()
        self.lock = threading.Lock()

    def is_running(self):
        with self.lock:
            return self.process is not None and self.process.poll() is None

    def start(self):
        with self.lock:
            if self.process is not None and self.process.poll() is None:
                self.log("MkDocs serve 已经在运行。")
                return

            global CURRENT_PORT
            port = find_available_port()
            if port != PORT:
                self.log(f"端口 {PORT} 被占用，改用 {port}。")
            CURRENT_PORT = port
            if self.url_callback is not None:
                self.url_callback(site_url())

            command = mkdocs_command(
                "serve",
                "-a",
                f"{HOST}:{port}",
            )
            self.log("启动命令：" + " ".join(f'"{part}"' if " " in part else part for part in command))

            creationflags = 0
            if os.name == "nt":
                creationflags = subprocess.CREATE_NEW_PROCESS_GROUP

            try:
                self.process = subprocess.Popen(
                    command,
                    cwd=project_root(),
                    stdout=subprocess.PIPE,
                    stderr=subprocess.STDOUT,
                    text=True,
                    encoding="utf-8",
                    errors="replace",
                    bufsize=1,
                    creationflags=creationflags,
                )
            except OSError as exc:
                self.process = None
                self.status_callback("启动失败")
                self.log(f"启动失败：{exc}")
                return

            self.status_callback("运行中")
            self.reader_thread = threading.Thread(target=self._read_output, daemon=True)
            self.reader_thread.start()

    def stop(self):
        with self.lock:
            process = self.process
            self.process = None
            if process is not None:
                self.stopping_pids.add(process.pid)

        if process is None or process.poll() is not None:
            self.status_callback("已停止")
            return

        self.log("正在停止 MkDocs serve...")
        if os.name == "nt":
            subprocess.run(
                ["taskkill", "/PID", str(process.pid), "/T", "/F"],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                check=False,
            )
        else:
            try:
                os.killpg(os.getpgid(process.pid), signal.SIGTERM)
            except OSError:
                process.terminate()

        try:
            process.wait(timeout=5)
        except subprocess.TimeoutExpired:
            process.kill()
        self.status_callback("已停止")
        self.log("MkDocs serve 已停止。")

    def restart(self):
        self.stop()
        self.start()

    def _read_output(self):
        process = self.process
        if process is None or process.stdout is None:
            return

        for line in process.stdout:
            self.log(line.rstrip())

        return_code = process.wait()
        with self.lock:
            stopped_by_us = process.pid in self.stopping_pids
            self.stopping_pids.discard(process.pid)
            if self.process is process:
                self.process = None
        if stopped_by_us:
            return
        if return_code == 0:
            self.status_callback("已停止")
        else:
            self.status_callback(f"已退出：{return_code}")
            self.log(f"MkDocs serve 已退出，返回码：{return_code}")

    def log(self, message):
        self.log_callback(message)


class BlogPostManager:
    def __init__(self, posts_dir=None):
        self.posts_dir = Path(posts_dir) if posts_dir else blog_posts_path()
        self.posts_dir.mkdir(parents=True, exist_ok=True)

    def list_posts(self):
        posts = []
        for file_path in self.posts_dir.glob("*.md"):
            date_value = self._date_from_file(file_path)
            posts.append(
                {
                    "path": file_path,
                    "date": date_value,
                    "stem": file_path.stem,
                    "title": read_front_matter_title(str(file_path.parent), file_path.name) or file_path.stem,
                }
            )
        return sorted(posts, key=lambda item: (item["date"], item["stem"]), reverse=True)

    def create_post(self, title):
        today = datetime.date.today()
        safe_title = (title or "").strip() or today.strftime("%Y年%m月%d日")
        file_path = self._next_post_path(today)
        content = self._post_template(safe_title, today)
        file_path.write_text(content, encoding="utf-8", newline="\n")
        return file_path

    def open_post(self, post):
        open_path(post["path"])

    def open_posts_dir(self):
        open_path(self.posts_dir)

    def _next_post_path(self, date_value):
        base_name = date_value.strftime("%Y-%m-%d")
        file_path = self.posts_dir / f"{base_name}.md"
        counter = 1
        while file_path.exists():
            file_path = self.posts_dir / f"{base_name}-{counter}.md"
            counter += 1
        return file_path

    def _date_from_file(self, file_path):
        match = re.match(r"^(\d{4})-(\d{2})-(\d{2})", file_path.stem)
        if match:
            return datetime.date(*(int(part) for part in match.groups()))

        try:
            content = file_path.read_text(encoding="utf-8", errors="ignore")
            front_matter = re.match(r"^---\s*\n(.*?)\n---\s*\n", content, re.DOTALL)
            if front_matter:
                date_match = re.search(r"^date:\s*(\d{4}-\d{2}-\d{2})", front_matter.group(1), re.MULTILINE)
                if date_match:
                    return datetime.date.fromisoformat(date_match.group(1))
        except OSError:
            pass

        return datetime.date.fromtimestamp(file_path.stat().st_mtime)

    def _post_template(self, title, date_value):
        date_text = date_value.strftime("%Y-%m-%d")
        return (
            "---\n"
            f"title: {title}\n"
            f"date: {date_text}\n"
            'description: ""\n'
            "categories:\n"
            "  - 博客\n"
            "tags: []\n"
            "comments: true\n"
            "---\n\n"
            f"# {title}\n\n"
            "> 先写一句这篇文章想解决什么问题。\n\n"
            "## 背景\n\n"
            "## 正文\n\n"
            "## 小结\n"
        )


class FriendLinksManager:
    SECTION_PATTERN = re.compile(
        r'<div class="link-section" data-category="(?P<id>[^"]+)">\s*'
        r'<h2 class="category-title">(?P<name>.*?)</h2>',
        re.DOTALL,
    )
    LINK_PATTERN = re.compile(
        r'<a href="(?P<link>[^"]+)" target="_blank">(?P<name>.*?)</a>.*?'
        r'<div class="info">(?P<description>.*?)</div>',
        re.DOTALL,
    )

    def __init__(self, file_path=None):
        self.file_path = Path(file_path) if file_path else friends_file_path()

    def read(self):
        return self.file_path.read_text(encoding="utf-8")

    def write(self, content):
        self.file_path.write_text(content, encoding="utf-8", newline="\n")

    def categories(self):
        content = self.read()
        return [
            {
                "id": match.group("id"),
                "name": self._clean_text(match.group("name")),
            }
            for match in self.SECTION_PATTERN.finditer(content)
        ]

    def list_links(self):
        content = self.read()
        sections = self._sections(content)
        links = []
        for section in sections:
            section_text = content[section["start"] : section["end"]]
            for match in self.LINK_PATTERN.finditer(section_text):
                links.append(
                    {
                        "category_id": section["id"],
                        "category_name": section["name"],
                        "name": self._clean_text(match.group("name")),
                        "link": html.unescape(match.group("link").strip()),
                        "description": self._clean_text(match.group("description")),
                    }
                )
        return links

    def add_link(self, category_id, name, link, description, avatar=""):
        name = name.strip()
        link = link.strip()
        description = description.strip()
        avatar = avatar.strip()
        if not name or not link:
            raise ValueError("名称和链接不能为空。")

        content = self.read()
        section = self._find_section(content, category_id)
        insert_at = content.rfind("\n            </div>", section["start"], section["end"])
        if insert_at == -1:
            raise ValueError("没有找到可插入的友链卡片区域。")

        card = self._card_html(name, link, description, avatar)
        self.write(content[:insert_at] + card + content[insert_at:])

    def delete_link(self, item):
        content = self.read()
        section = self._find_section(content, item["category_id"])
        section_text = content[section["start"] : section["end"]]
        link_options = {item["link"], html.escape(item["link"], quote=True)}
        name_options = {item["name"], html.escape(item["name"])}
        anchor_pattern = re.compile(
            r'<a href="(?:' + "|".join(re.escape(value) for value in link_options) + r')" target="_blank">'
            r"(?:"
            + "|".join(re.escape(value) for value in name_options)
            + r")</a>",
            re.DOTALL,
        )
        anchor = anchor_pattern.search(section_text)
        if not anchor:
            raise ValueError("没有在友链文件中找到这条链接。")

        anchor_abs = section["start"] + anchor.start()
        card_start = content.rfind('<div class="link-card">', section["start"], anchor_abs)
        if card_start == -1:
            raise ValueError("没有找到这条链接所属的卡片。")

        line_start = content.rfind("\n", section["start"], card_start)
        if line_start == -1:
            line_start = card_start
        card_end = content.find("\n                </div>", anchor_abs, section["end"])
        if card_end == -1:
            raise ValueError("没有找到这条链接卡片的结束位置。")
        card_end = content.find("\n", card_end + 1, section["end"])
        if card_end == -1:
            card_end = section["end"]

        self.write(content[:line_start] + content[card_end:])

    def _sections(self, content):
        matches = list(self.SECTION_PATTERN.finditer(content))
        footer_pos = content.find('<div class="links-footer">')
        sections = []
        for index, match in enumerate(matches):
            end = matches[index + 1].start() if index + 1 < len(matches) else footer_pos
            if end == -1:
                end = len(content)
            sections.append(
                {
                    "id": match.group("id"),
                    "name": self._clean_text(match.group("name")),
                    "start": match.start(),
                    "end": end,
                }
            )
        return sections

    def _find_section(self, content, category_id):
        for section in self._sections(content):
            if section["id"] == category_id:
                return section
        raise ValueError(f"没有找到分类：{category_id}")

    def _card_html(self, name, link, description, avatar):
        safe_name = html.escape(name)
        safe_link = html.escape(link, quote=True)
        safe_description = html.escape(description)
        safe_avatar = html.escape(avatar, quote=True)
        placeholder = html.escape(name[:1].upper() or "友")
        if avatar:
            avatar_html = f'<img class="ava" src="{safe_avatar}" alt="{safe_name}"/>'
        else:
            avatar_html = f'<div class="avatar-placeholder">{placeholder}</div>'

        return (
            "\n"
            "                <div class=\"link-card\">\n"
            f"                    {avatar_html}\n"
            "                    <div class=\"card-header\">\n"
            "                        <div>\n"
            f"                            <a href=\"{safe_link}\" target=\"_blank\">{safe_name}</a>\n"
            "                        </div>\n"
            f"                        <div class=\"info\">{safe_description}</div>\n"
            "                    </div>\n"
            "                </div>"
        )

    def _clean_text(self, value):
        text = re.sub(r"<.*?>", "", value, flags=re.DOTALL)
        return html.unescape(text).strip()


class MkDocsApp:
    def __init__(self):
        self.root = Tk()
        self.root.title(f"{APP_TITLE} 控制台")
        self._apply_window_icon()
        self.root.geometry("980x680")
        self.root.minsize(820, 560)

        self.log_queue = queue.Queue()
        self.status_var = StringVar(value="准备中")
        self.url_var = StringVar(value=site_url())
        self.nav_count_var = StringVar(value="-")
        self.tray_icon = None
        self.tray_thread = None
        self.exiting = False
        self.blog_posts = []
        self.friend_links = []

        self.server = MkDocsServer(self.enqueue_log, self.set_status, self.set_site_url)
        self.blog_manager = BlogPostManager()
        self.friend_manager = FriendLinksManager()
        self._setup_style()
        self._build_ui()
        self._setup_tray()

        self.root.protocol("WM_DELETE_WINDOW", self.hide_window)
        self.root.after(100, self.drain_log_queue)
        self.root.after(300, self.bootstrap)

    def _apply_window_icon(self):
        icon_path = app_icon_path()
        if not icon_path.exists():
            return
        try:
            self.root.iconbitmap(default=str(icon_path))
        except Exception:
            pass

    def _setup_style(self):
        self.colors = {
            "bg": "#f6f8fb",
            "panel": "#ffffff",
            "ink": "#17202a",
            "muted": "#64748b",
            "accent": "#2563eb",
            "accent_hover": "#1d4ed8",
            "line": "#dbe3ee",
            "soft": "#eaf1ff",
            "danger": "#dc2626",
        }
        self.root.configure(bg=self.colors["bg"])

        style = ttk.Style(self.root)
        try:
            style.theme_use("clam")
        except Exception:
            pass
        style.configure("App.TFrame", background=self.colors["bg"])
        style.configure("Card.TFrame", background=self.colors["panel"], relief="flat")
        style.configure("App.TLabel", background=self.colors["bg"], foreground=self.colors["ink"])
        style.configure("Card.TLabel", background=self.colors["panel"], foreground=self.colors["ink"])
        style.configure("Muted.TLabel", background=self.colors["panel"], foreground=self.colors["muted"])
        style.configure("Title.TLabel", background=self.colors["bg"], foreground=self.colors["ink"], font=("Microsoft YaHei UI", 16, "bold"))
        style.configure("Status.TLabel", background=self.colors["soft"], foreground=self.colors["accent"], padding=(10, 4))

    def _build_ui(self):
        outer = ttk.Frame(self.root, padding=18, style="App.TFrame")
        outer.pack(fill=BOTH, expand=True)

        header = ttk.Frame(outer, style="App.TFrame")
        header.pack(fill="x", pady=(0, 14))

        title_area = ttk.Frame(header, style="App.TFrame")
        title_area.pack(side=LEFT, fill="x", expand=True)
        ttk.Label(title_area, text="知识库本地预览", style="Title.TLabel").pack(anchor=W)
        ttk.Label(
            title_area,
            text="自动生成导航，使用 mkdocs-env 启动本地站点。",
            style="App.TLabel",
            foreground=self.colors["muted"],
        ).pack(anchor=W, pady=(4, 0))
        ttk.Label(header, textvariable=self.status_var, style="Status.TLabel").pack(side=RIGHT)

        info = ttk.Frame(outer, padding=14, style="Card.TFrame")
        info.pack(fill="x", pady=(0, 12))
        self._add_info_row(info, 0, "预览地址", self.url_var)
        self._add_info_row(info, 1, "Conda 环境", CONDA_ENV)
        self._add_info_row(info, 2, "笔记库", str(notebooks_path()))
        self._add_info_row(info, 3, "导航文件数", self.nav_count_var)

        buttons = Frame(outer, bg=self.colors["bg"])
        buttons.pack(fill="x", pady=(2, 12))

        self.start_button = self._make_button(buttons, "启动", self.start_server)
        self.start_button.pack(side=LEFT, padx=(0, 8))
        self.stop_button = self._make_button(buttons, "停止", self.stop_server, variant="light")
        self.stop_button.pack(side=LEFT, padx=(0, 8))
        self.reload_button = self._make_button(buttons, "重载", self.reload_site)
        self.reload_button.pack(side=LEFT, padx=(0, 8))
        self.open_button = self._make_button(buttons, "打开站点", self.open_site)
        self.open_button.pack(side=LEFT, padx=(0, 8))
        self.notebooks_button = self._make_button(buttons, "打开笔记库", self.open_notebooks)
        self.notebooks_button.pack(side=LEFT, padx=(0, 8))
        self.publish_button = self._make_button(buttons, "发布到 GitHub", self.publish_to_github, variant="success")
        self.publish_button.pack(side=LEFT, padx=(0, 8))
        self.hide_button = self._make_button(buttons, "隐藏到托盘", self.hide_window, variant="light")
        self.hide_button.pack(side=LEFT, padx=(0, 8))
        self.exit_button = self._make_button(buttons, "退出", self.quit_app, variant="danger")
        self.exit_button.pack(side=RIGHT)

        self._build_management_card(outer)

        log_wrap = ttk.Frame(outer, padding=1, style="Card.TFrame")
        log_wrap.pack(fill=BOTH, expand=True)
        self.log_text = Text(
            log_wrap,
            height=15,
            wrap="word",
            borderwidth=0,
            highlightthickness=0,
            bg="#0f172a",
            fg="#dbeafe",
            insertbackground="#dbeafe",
            font=("Consolas", 9),
            padx=12,
            pady=10,
        )
        self.log_text.pack(fill=BOTH, expand=True)
        self.log_text.configure(state="disabled")

    def _build_management_card(self, outer):
        manage_card = ttk.Frame(outer, padding=12, style="Card.TFrame")
        manage_card.pack(fill="x", pady=(0, 12))

        manage_head = ttk.Frame(manage_card, style="Card.TFrame")
        manage_head.pack(fill="x", pady=(0, 8))

        title_area = ttk.Frame(manage_head, style="Card.TFrame")
        title_area.pack(side=LEFT, fill="x", expand=True)
        ttk.Label(title_area, text="内容管理", style="Card.TLabel", font=("Microsoft YaHei UI", 11, "bold")).pack(anchor=W)
        self.management_path_var = StringVar(value=str(blog_posts_path()))
        ttk.Label(title_area, textvariable=self.management_path_var, style="Muted.TLabel").pack(anchor=W, pady=(3, 0))

        tab_bar = Frame(manage_head, bg=self.colors["panel"])
        tab_bar.pack(side=RIGHT)
        self.blog_tab_button = self._make_button(tab_bar, "博客管理", lambda: self.show_management_page("blog"), variant="light")
        self.blog_tab_button.pack(side=LEFT, padx=(0, 6))
        self.friend_tab_button = self._make_button(tab_bar, "友链管理", lambda: self.show_management_page("friend"), variant="light")
        self.friend_tab_button.pack(side=LEFT)

        self.manager_pages = ttk.Frame(manage_card, style="Card.TFrame")
        self.manager_pages.pack(fill="x")

        self.blog_panel = ttk.Frame(self.manager_pages, style="Card.TFrame")
        self.friend_panel = ttk.Frame(self.manager_pages, style="Card.TFrame")
        self._build_blog_panel(self.blog_panel)
        self._build_friend_panel(self.friend_panel)
        self.show_management_page("blog")

    def _build_blog_panel(self, parent):
        blog_body = ttk.Frame(parent, style="Card.TFrame")
        blog_body.pack(fill="x")

        list_wrap = Frame(blog_body, bg=self.colors["panel"])
        list_wrap.pack(side=LEFT, fill="both", expand=True, padx=(0, 12))
        self.blog_list = Listbox(
            list_wrap,
            height=6,
            selectmode=SINGLE,
            borderwidth=0,
            highlightthickness=1,
            highlightbackground=self.colors["line"],
            activestyle="none",
            bg="#f8fafc",
            fg=self.colors["ink"],
            font=("Microsoft YaHei UI", 9),
        )
        blog_scroll = Scrollbar(list_wrap, orient="vertical", command=self.blog_list.yview)
        self.blog_list.configure(yscrollcommand=blog_scroll.set)
        self.blog_list.pack(side=LEFT, fill="both", expand=True)
        blog_scroll.pack(side=RIGHT, fill=Y)
        self.blog_list.bind("<Double-Button-1>", lambda _event: self.open_selected_post())

        blog_actions = Frame(blog_body, bg=self.colors["panel"])
        blog_actions.pack(side=RIGHT, fill="y")
        blog_actions.grid_columnconfigure(0, weight=1)
        blog_actions.grid_columnconfigure(1, weight=1)

        self.new_post_button = self._make_button(blog_actions, "新建博客", self.create_blog_post, variant="success")
        self.open_post_button = self._make_button(blog_actions, "打开选中", self.open_selected_post, variant="light")
        self.posts_dir_button = self._make_button(blog_actions, "博客目录", self.open_blog_posts_dir, variant="light")
        self.refresh_posts_button = self._make_button(blog_actions, "刷新列表", self.refresh_blog_posts, variant="light")

        buttons = [
            (self.new_post_button, 0, 0),
            (self.open_post_button, 0, 1),
            (self.posts_dir_button, 1, 0),
            (self.refresh_posts_button, 1, 1),
        ]
        for button, row, column in buttons:
            button.configure(width=10)
            button.grid(row=row, column=column, sticky="ew", padx=(0 if column == 0 else 6, 0), pady=(0, 7))

    def _build_friend_panel(self, parent):
        friend_body = ttk.Frame(parent, style="Card.TFrame")
        friend_body.pack(fill="x")

        friend_list_wrap = Frame(friend_body, bg=self.colors["panel"])
        friend_list_wrap.pack(side=LEFT, fill="both", expand=True, padx=(0, 12))
        self.friend_list = Listbox(
            friend_list_wrap,
            height=6,
            selectmode=SINGLE,
            borderwidth=0,
            highlightthickness=1,
            highlightbackground=self.colors["line"],
            activestyle="none",
            bg="#f8fafc",
            fg=self.colors["ink"],
            font=("Microsoft YaHei UI", 9),
        )
        friend_scroll = Scrollbar(friend_list_wrap, orient="vertical", command=self.friend_list.yview)
        self.friend_list.configure(yscrollcommand=friend_scroll.set)
        self.friend_list.pack(side=LEFT, fill="both", expand=True)
        friend_scroll.pack(side=RIGHT, fill=Y)
        self.friend_list.bind("<Double-Button-1>", lambda _event: self.open_selected_friend())

        friend_actions = Frame(friend_body, bg=self.colors["panel"])
        friend_actions.pack(side=RIGHT, fill="y")
        friend_actions.grid_columnconfigure(0, weight=1)
        friend_actions.grid_columnconfigure(1, weight=1)

        self.add_friend_button = self._make_button(friend_actions, "添加友链", self.add_friend_link, variant="success")
        self.open_friend_button = self._make_button(friend_actions, "打开网址", self.open_selected_friend, variant="light")
        self.delete_friend_button = self._make_button(friend_actions, "删除选中", self.delete_selected_friend, variant="danger")
        self.friend_file_button = self._make_button(friend_actions, "友链文件", self.open_friends_file, variant="light")
        self.friend_page_button = self._make_button(friend_actions, "友链页面", self.open_friends_page, variant="light")
        self.refresh_friend_button = self._make_button(friend_actions, "刷新友链", self.refresh_friend_links, variant="light")

        buttons = [
            (self.add_friend_button, 0, 0),
            (self.open_friend_button, 0, 1),
            (self.delete_friend_button, 1, 0),
            (self.friend_file_button, 1, 1),
            (self.friend_page_button, 2, 0),
            (self.refresh_friend_button, 2, 1),
        ]
        for button, row, column in buttons:
            button.configure(width=10)
            button.grid(row=row, column=column, sticky="ew", padx=(0 if column == 0 else 6, 0), pady=(0, 7))

    def show_management_page(self, kind):
        self.blog_panel.pack_forget()
        self.friend_panel.pack_forget()
        if kind == "friend":
            self.friend_panel.pack(fill="x")
            self.management_path_var.set(str(friends_file_path()))
            self._style_tab_button(self.blog_tab_button, False)
            self._style_tab_button(self.friend_tab_button, True)
        else:
            self.blog_panel.pack(fill="x")
            self.management_path_var.set(str(blog_posts_path()))
            self._style_tab_button(self.blog_tab_button, True)
            self._style_tab_button(self.friend_tab_button, False)

    def _style_tab_button(self, button, active):
        if active:
            button.configure(
                bg=self.colors["accent"],
                fg="#ffffff",
                activebackground=self.colors["accent_hover"],
                activeforeground="#ffffff",
                highlightbackground=self.colors["accent"],
            )
        else:
            button.configure(
                bg="#e8eef8",
                fg=self.colors["ink"],
                activebackground="#dbeafe",
                activeforeground=self.colors["ink"],
                highlightbackground="#b6c7e3",
            )

    def _add_info_row(self, parent, row, label, value):
        ttk.Label(parent, text=f"{label}：", style="Muted.TLabel").grid(row=row, column=0, sticky=W, padx=(0, 8), pady=3)
        textvariable = value if isinstance(value, StringVar) else None
        text = "" if textvariable else value
        ttk.Label(parent, text=text, textvariable=textvariable, style="Card.TLabel").grid(row=row, column=1, sticky=W, pady=3)

    def _make_button(self, parent, text, command, variant="primary"):
        palette = {
            "primary": (self.colors["accent"], "#ffffff", self.colors["accent_hover"]),
            "light": ("#e8eef8", self.colors["ink"], "#dbeafe"),
            "danger": (self.colors["danger"], "#ffffff", "#b91c1c"),
            "success": ("#16a34a", "#ffffff", "#15803d"),
        }
        bg, fg, hover = palette[variant]
        button = Button(
            parent,
            text=text,
            command=command,
            bg=bg,
            fg=fg,
            activebackground=hover,
            activeforeground=fg,
            relief="flat",
            bd=0,
            padx=13,
            pady=7,
            cursor="hand2",
            font=("Microsoft YaHei UI", 9),
            highlightthickness=1,
            highlightbackground=self.colors["line"],
        )
        return button

    def _setup_tray(self):
        if pystray is None or not load_tray_image_tools():
            if os.name == "nt":
                self.tray_icon = NativeWindowsTray(APP_TITLE, lambda: self.root.after(0, self.show_window))
                self.tray_icon.run()
                self.enqueue_log("托盘：使用 Windows 原生托盘图标，双击或右键图标可显示窗口。")
                return
            self.enqueue_log("提示：未安装 pystray/Pillow，托盘隐藏不可用；点击“隐藏”会最小化窗口。")
            return

        image = self._create_tray_image()
        menu = pystray.Menu(
            pystray.MenuItem("显示窗口", lambda: self.root.after(0, self.show_window)),
            pystray.MenuItem("重载", lambda: self.root.after(0, self.reload_site)),
            pystray.MenuItem("打开站点", lambda: self.root.after(0, self.open_site)),
            pystray.MenuItem("退出", lambda: self.root.after(0, self.quit_app)),
        )
        self.tray_icon = pystray.Icon(APP_TITLE, image, APP_TITLE, menu)
        self.tray_thread = threading.Thread(target=self.tray_icon.run, daemon=True)
        self.tray_thread.start()

    def _create_tray_image(self):
        image = Image.new("RGB", (64, 64), "#263238")
        draw = ImageDraw.Draw(image)
        draw.rectangle((10, 10, 54, 54), fill="#4CAF50")
        draw.rectangle((18, 18, 46, 46), fill="#FFFFFF")
        draw.rectangle((24, 24, 40, 40), fill="#263238")
        return image

    def bootstrap(self):
        self.enqueue_log("正在生成导航...")
        try:
            count = generate_nav()
            self.nav_count_var.set(str(count))
            self.enqueue_log(f"导航已更新：{count} 个文档文件。")
            self.refresh_blog_posts()
            self.refresh_friend_links()
        except Exception as exc:
            self.set_status("导航生成失败")
            self.enqueue_log(f"导航生成失败：{exc}")
            messagebox.showerror(APP_TITLE, f"导航生成失败：\n{exc}")
            return

        self.start_server()

    def start_server(self):
        threading.Thread(target=self.server.start, daemon=True).start()

    def stop_server(self):
        threading.Thread(target=self.server.stop, daemon=True).start()

    def reload_site(self):
        def worker():
            self.set_status("重载中")
            try:
                count = generate_nav()
                self.root.after(0, self.nav_count_var.set, str(count))
                self.enqueue_log(f"重载完成：导航已更新，包含 {count} 个文档文件。")
                if not self.server.is_running():
                    self.enqueue_log("服务未运行，正在启动。")
                    self.server.start()
                else:
                    self.set_status("运行中")
                    self.enqueue_log("MkDocs 会检测 mkdocs.yml 变化并自动刷新。")
            except Exception as exc:
                self.set_status("重载失败")
                self.enqueue_log(f"重载失败：{exc}")

        threading.Thread(target=worker, daemon=True).start()

    def refresh_blog_posts(self):
        try:
            self.blog_posts = self.blog_manager.list_posts()
        except Exception as exc:
            self.enqueue_log(f"刷新博客列表失败：{exc}")
            return

        self.blog_list.delete(0, END)
        for post in self.blog_posts[:80]:
            self.blog_list.insert(END, f"{post['date']}  {post['title']}  ({post['path'].name})")
        self.enqueue_log(f"博客列表已刷新：{len(self.blog_posts)} 篇。")

    def create_blog_post(self):
        title = simpledialog.askstring("新建博客", "给这篇博客起个标题：", parent=self.root)
        if title is None:
            return
        try:
            file_path = self.blog_manager.create_post(title)
            self.refresh_blog_posts()
            self.enqueue_log(f"新建博客：{file_path}")
            open_path(file_path)
        except Exception as exc:
            messagebox.showerror(APP_TITLE, f"新建博客失败：\n{exc}")
            self.enqueue_log(f"新建博客失败：{exc}")

    def selected_blog_post(self):
        selection = self.blog_list.curselection()
        if not selection:
            messagebox.showinfo(APP_TITLE, "先在博客列表里选一篇。")
            return None
        index = selection[0]
        if index >= len(self.blog_posts):
            return None
        return self.blog_posts[index]

    def open_selected_post(self):
        post = self.selected_blog_post()
        if not post:
            return
        try:
            self.blog_manager.open_post(post)
            self.enqueue_log(f"打开博客：{post['path']}")
        except Exception as exc:
            messagebox.showerror(APP_TITLE, f"打开博客失败：\n{exc}")

    def open_blog_posts_dir(self):
        try:
            self.blog_manager.open_posts_dir()
        except Exception as exc:
            messagebox.showerror(APP_TITLE, f"打开博客目录失败：\n{exc}")

    def refresh_friend_links(self):
        try:
            self.friend_links = self.friend_manager.list_links()
        except Exception as exc:
            self.enqueue_log(f"刷新友链失败：{exc}")
            return

        self.friend_list.delete(0, END)
        for item in self.friend_links:
            self.friend_list.insert(END, f"[{item['category_name']}] {item['name']}  {item['link']}")
        self.enqueue_log(f"友链列表已刷新：{len(self.friend_links)} 条。")

    def add_friend_link(self):
        data = self.friend_dialog()
        if not data:
            return
        try:
            self.friend_manager.add_link(
                data["category_id"],
                data["name"],
                data["link"],
                data["description"],
                data["avatar"],
            )
            self.refresh_friend_links()
            self.enqueue_log(f"添加友链：{data['name']} -> {data['link']}")
            self.reload_site()
        except Exception as exc:
            messagebox.showerror(APP_TITLE, f"添加友链失败：\n{exc}")
            self.enqueue_log(f"添加友链失败：{exc}")

    def selected_friend_link(self):
        selection = self.friend_list.curselection()
        if not selection:
            messagebox.showinfo(APP_TITLE, "先在友链列表里选一条。")
            return None
        index = selection[0]
        if index >= len(self.friend_links):
            return None
        return self.friend_links[index]

    def open_selected_friend(self):
        item = self.selected_friend_link()
        if not item:
            return
        webbrowser.open(item["link"])

    def delete_selected_friend(self):
        item = self.selected_friend_link()
        if not item:
            return
        confirmed = messagebox.askyesno(APP_TITLE, f"确定删除友链“{item['name']}”吗？")
        if not confirmed:
            return
        try:
            self.friend_manager.delete_link(item)
            self.refresh_friend_links()
            self.enqueue_log(f"删除友链：{item['name']}")
            self.reload_site()
        except Exception as exc:
            messagebox.showerror(APP_TITLE, f"删除友链失败：\n{exc}")
            self.enqueue_log(f"删除友链失败：{exc}")

    def open_friends_file(self):
        path = friends_file_path()
        if not path.exists():
            messagebox.showerror(APP_TITLE, f"找不到友链文件：\n{path}")
            return
        open_path(path)

    def open_friends_page(self):
        webbrowser.open(site_url(quote("notebooks/7_朋友/", safe="/")))

    def friend_dialog(self):
        categories = self.friend_manager.categories()
        if not categories:
            messagebox.showerror(APP_TITLE, "没有解析到友链分类。")
            return None

        dialog = Toplevel(self.root)
        dialog.title("添加友链")
        dialog.resizable(False, False)
        dialog.transient(self.root)
        dialog.grab_set()

        frame = ttk.Frame(dialog, padding=14)
        frame.pack(fill="both", expand=True)

        category_labels = [f"{item['name']} ({item['id']})" for item in categories]
        category_var = StringVar(value=category_labels[0])
        name_var = StringVar()
        link_var = StringVar(value="https://")
        desc_var = StringVar()
        avatar_var = StringVar()
        result = {"value": None}

        fields = [
            ("分类", category_var, "combo"),
            ("名称", name_var, "entry"),
            ("链接", link_var, "entry"),
            ("简介", desc_var, "entry"),
            ("头像 URL", avatar_var, "entry"),
        ]

        for row, (label, var, kind) in enumerate(fields):
            ttk.Label(frame, text=f"{label}：").grid(row=row, column=0, sticky=W, padx=(0, 8), pady=5)
            if kind == "combo":
                widget = ttk.Combobox(frame, textvariable=var, values=category_labels, state="readonly", width=42)
            else:
                widget = ttk.Entry(frame, textvariable=var, width=45)
            widget.grid(row=row, column=1, sticky=W, pady=5)

        buttons = ttk.Frame(frame)
        buttons.grid(row=len(fields), column=0, columnspan=2, sticky="e", pady=(12, 0))

        def submit():
            selected_index = category_labels.index(category_var.get())
            name = name_var.get().strip()
            link = link_var.get().strip()
            if not name or not link or link == "https://":
                messagebox.showinfo(APP_TITLE, "名称和链接不能为空。")
                return
            result["value"] = {
                "category_id": categories[selected_index]["id"],
                "name": name,
                "link": link,
                "description": desc_var.get().strip(),
                "avatar": avatar_var.get().strip(),
            }
            dialog.destroy()

        ttk.Button(buttons, text="取消", command=dialog.destroy).pack(side=LEFT, padx=(0, 8))
        ttk.Button(buttons, text="添加", command=submit).pack(side=LEFT)
        dialog.bind("<Return>", lambda _event: submit())
        dialog.bind("<Escape>", lambda _event: dialog.destroy())

        dialog.update_idletasks()
        x = self.root.winfo_rootx() + (self.root.winfo_width() - dialog.winfo_width()) // 2
        y = self.root.winfo_rooty() + (self.root.winfo_height() - dialog.winfo_height()) // 2
        dialog.geometry(f"+{max(x, 0)}+{max(y, 0)}")
        dialog.wait_window()
        return result["value"]

    def publish_to_github(self):
        message = simpledialog.askstring(
            "发布到 GitHub",
            "提交信息：",
            parent=self.root,
            initialvalue=f"更新博客 {datetime.date.today().isoformat()}",
        )
        if message is None:
            return
        message = message.strip()
        if not message:
            messagebox.showinfo(APP_TITLE, "提交信息不能为空。")
            return

        confirmed = messagebox.askyesno(
            APP_TITLE,
            "将生成导航、构建站点，然后提交并推送 docs、mkdocs.yml、generate_nav.py 和 .github 的变更。\n\n继续发布吗？",
        )
        if not confirmed:
            return

        threading.Thread(target=self._publish_worker, args=(message,), daemon=True).start()

    def _publish_worker(self, message):
        self.set_status("发布中")
        try:
            count = generate_nav()
            self.root.after(0, self.nav_count_var.set, str(count))
            self.enqueue_log(f"发布前已更新导航：{count} 个文档文件。")

            self._run_logged(mkdocs_command("build"))
            self._remove_build_output()

            status = self._capture_command(["git", "status", "--porcelain", "--", "docs", MKDOCS_YML, "generate_nav.py", ".github"])
            if not status.strip():
                self.enqueue_log("没有需要发布的站点变更。")
                self.set_status("无变更")
                return

            self.enqueue_log("将发布以下变更：")
            for line in status.splitlines():
                self.enqueue_log("  " + line)

            self._run_logged(["git", "add", "-A", "--", "docs", MKDOCS_YML, "generate_nav.py", ".github"])
            self._run_logged(["git", "commit", "-m", message])
            self._run_logged(["git", "push"])
            self.set_status("已发布")
            self.enqueue_log("发布完成：GitHub Pages 工作流会继续部署站点。")
        except Exception as exc:
            self.set_status("发布失败")
            self.enqueue_log(f"发布失败：{exc}")
            self.root.after(0, messagebox.showerror, APP_TITLE, f"发布失败：\n{exc}")
        finally:
            self._remove_build_output()

    def _run_logged(self, command):
        self.enqueue_log("执行：" + " ".join(f'"{part}"' if " " in part else part for part in command))
        process = subprocess.Popen(
            command,
            cwd=project_root(),
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            encoding="utf-8",
            errors="replace",
            bufsize=1,
        )
        if process.stdout:
            for line in process.stdout:
                self.enqueue_log(line.rstrip())
        return_code = process.wait()
        if return_code != 0:
            raise RuntimeError(f"命令失败，返回码 {return_code}：{' '.join(command)}")

    def _capture_command(self, command):
        result = subprocess.run(
            command,
            cwd=project_root(),
            text=True,
            encoding="utf-8",
            errors="replace",
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            check=False,
        )
        if result.returncode != 0:
            raise RuntimeError(result.stdout.strip() or f"命令失败：{' '.join(command)}")
        return result.stdout

    def _remove_build_output(self):
        site_dir = project_root() / "site"
        if site_dir.exists() and site_dir.is_dir():
            shutil.rmtree(site_dir)

    def open_site(self):
        webbrowser.open(site_url())

    def open_notebooks(self):
        path = notebooks_path()
        if not path.exists():
            messagebox.showerror(APP_TITLE, f"找不到笔记库目录：\n{path}")
            return
        open_path(path)

    def hide_window(self):
        if self.tray_icon is not None:
            self.root.withdraw()
            self.enqueue_log("窗口已隐藏到托盘。")
        else:
            self.root.iconify()
            self.enqueue_log("托盘不可用，窗口已最小化。")

    def show_window(self):
        self.root.deiconify()
        self.root.lift()
        self.root.focus_force()

    def quit_app(self):
        if self.exiting:
            return
        self.exiting = True
        self.set_status("退出中")
        self.server.stop()
        if self.tray_icon is not None:
            self.tray_icon.stop()
        self.root.destroy()

    def set_status(self, text):
        self.root.after(0, self.status_var.set, text)

    def set_site_url(self, text):
        self.root.after(0, self.url_var.set, text)

    def enqueue_log(self, message):
        timestamp = time.strftime("%H:%M:%S")
        self.log_queue.put(f"[{timestamp}] {message}")

    def drain_log_queue(self):
        while True:
            try:
                line = self.log_queue.get_nowait()
            except queue.Empty:
                break

            self.log_text.configure(state="normal")
            self.log_text.insert(END, line + "\n")
            self.log_text.see(END)
            self.log_text.configure(state="disabled")

        if not self.exiting:
            self.root.after(100, self.drain_log_queue)

    def run(self):
        self.root.mainloop()


def run_nav_only():
    count = generate_nav()
    print(f"导航已更新：{count} 个文档文件。")


def run_serve_only():
    count = generate_nav()
    print(f"导航已更新：{count} 个文档文件。")
    server = MkDocsServer(print, print)
    server.start()
    try:
        while server.is_running():
            time.sleep(1)
    except KeyboardInterrupt:
        server.stop()


def parse_args():
    parser = argparse.ArgumentParser(description="生成 MkDocs 导航，并管理本地预览服务。")
    parser.add_argument("--nav-only", action="store_true", help="只生成 mkdocs.yml 导航，不启动界面和服务。")
    parser.add_argument("--serve-only", action="store_true", help="不打开图形界面，只启动 mkdocs serve。")
    return parser.parse_args()


def main():
    os.chdir(project_root())
    args = parse_args()

    if args.nav_only:
        run_nav_only()
        return

    if args.serve_only:
        run_serve_only()
        return

    app = MkDocsApp()
    app.run()


if __name__ == "__main__":
    main()
