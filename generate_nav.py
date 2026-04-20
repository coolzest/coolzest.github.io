import os
import re
from ruamel.yaml import YAML

def parse_prefix(name):
    # 匹配序号前缀，如 "1 ", "1_", "1.1 ", "1.3_"
    match = re.match(r'^(\d+(?:\.\d+)*)(?:[ _]+)', name)
    if match:
        prefix = match.group(1)
        parts = tuple(int(x) for x in prefix.split('.'))
        return parts, name[match.end():].strip()
    return (), name.strip()

def sort_key(name):
    prefix, title = parse_prefix(name)
    return prefix, title.lower()

def collect_files(root_dir):
    files = []
    for dirpath, dirnames, filenames in os.walk(root_dir):
        dirnames.sort(key=sort_key)
        filenames.sort(key=sort_key)
        for filename in filenames:
            if filename.lower().endswith('.md'):
                rel_path = os.path.relpath(os.path.join(dirpath, filename), root_dir)
                rel_path = rel_path.replace(os.sep, '/')
                if rel_path.startswith('6_博客/posts/'):
                    continue
                files.append(rel_path)
    return files

def build_nav(files):
    tree = {}
    for rel_path in files:
        parts = rel_path.split('/')
        current = tree
        for part in parts[:-1]:
            prefix, name = parse_prefix(part)
            current = current.setdefault((prefix, name), {})
        prefix, name = parse_prefix(parts[-1])
        name = name[:-3] if name.endswith('.md') else name
        current[(prefix, name)] = 'notebooks/' + rel_path

    def build_tree(node):
        nav = []
        for key, value in sorted(node.items(), key=lambda item: (item[0][0], item[0][1].lower())):
            _, name = key
            if isinstance(value, dict):
                nav.append({name: build_tree(value)})
            elif name.lower() == 'index':
                nav.append(value)
            else:
                nav.append({name: value})
        return nav

    return build_tree(tree)

def load_mkdocs(path='mkdocs.yml'):
    yaml = YAML()
    yaml.indent(mapping=2, sequence=4, offset=2)
    yaml.width = 4096
    yaml.allow_unicode = True
    yaml.default_flow_style = False

    with open(path, 'r', encoding='utf-8') as f:
        config = yaml.load(f)
    return config, yaml

def main():
    root_dir = 'docs/notebooks'
    files = collect_files(root_dir)
    nav = build_nav(files)

    config, yaml = load_mkdocs()
    config['nav'] = nav

    with open('mkdocs.yml', 'w', encoding='utf-8') as f:
        yaml.dump(config, f)

if __name__ == '__main__':
    main()
