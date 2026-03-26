from TexSoup import TexSoup
from model import translate_batch
from datetime import datetime
import re

BATCH_SIZE = 8


def get_tex_file(file_path: str) -> TexSoup:
    with open(file_path, 'r') as f:
        soup = TexSoup(f.read())
    return soup


def is_patterned(text):
    patterns = [
        r'\{\{.*?\}\}',
        r'\[\[.*?\]\]',
        r'^\s*%',
        r'\b\w*(?:[a-zA-Zа-яА-ЯёЁ]\w*[0-9_]|[0-9_]\w*[a-zA-Zа-яА-ЯёЁ])\w*\b'
    ]
    for pattern in patterns:
        if re.search(pattern, text):
            return True
    return False


def is_metadata(node):
    metadata_commands = [
        'title', 'author', 'date', 'maketitle',
        'affiliation', 'email', 'thanks', 'address',
        'keywords', 'documentclass', 'usepackage'
    ]
    return hasattr(node, 'name') and node.name in metadata_commands

def is_leaf(node):
    if isinstance(node, str):
        return True
    try:
        children = list(node.children)
        return len(children) == 0
    except Exception:
        return True


def has_inline_math(text):
    return bool(re.search(r'(?<!\\)\$[^$]+\$', text))


def is_special_command(node):
    preserve_commands = [
        'label', 'ref', 'cite', 'citep', 'citet', 'pageref',
        'includegraphics', 'input', 'include',
        'texttt', 'verb', 'lstinline',
        'url', 'href', 'path'
    ]
    return hasattr(node, 'name') and node.name in preserve_commands


def should_translate(node) -> bool:
    if not isinstance(node, str):
        return False
    text = node.strip()
    return (
        len(text) >= 3
        and not is_metadata(node)
        and re.search(r'[a-zA-Z]', text)
        and not has_inline_math(text)
        and not is_special_command(node)
        and not is_patterned(text)
        and '$' not in text
    )


def process_tex_by_positions(file_path: str):
    with open(file_path, 'r') as f:
        source = f.read()

    soup = TexSoup(source)
    pairs = []
    seen_positions = set()  # чтобы не брать одну позицию дважды

    def walk(node):
        try:
            contents = list(node.contents)
        except Exception:
            return
        
        print(f"  [walk] node type={type(node).__name__}, "
              f"name={getattr(node, 'name', '—')}, contents={len(contents)}")
        
        for child in contents:
            print(f"    [child] type={type(child).__name__}, "
                  f"repr={repr(str(child))[:60]}, "
                  f"should_translate={should_translate(child)}")
            
            if should_translate(child):
                text = str(child)
                # Ищем все вхождения, берём первое незанятое
                start = 0
                while True:
                    pos = source.find(text, start)
                    if pos == -1:
                        print(f"    [MISS] не найдено в исходнике: {repr(text)}")
                        break
                    if pos not in seen_positions:
                        seen_positions.add(pos)
                        pairs.append((pos, pos + len(text), text.strip()))
                        print(f"    [HIT] pos={pos} text={repr(text)}")
                        break
                    start = pos + 1
            else:
                walk(child)

    walk(soup)

    # Переводим
    texts = [t for _, _, t in pairs]
    translations = []
    for i in range(0, len(texts), BATCH_SIZE):
        translations.extend(translate_batch(texts[i:i + BATCH_SIZE]))

    # Заменяем с конца (чтобы не сбить позиции)
    pairs_with_translations = sorted(
        zip(pairs, translations),
        key=lambda x: x[0][0],
        reverse=True  # с конца!
    )

    result = list(source)
    for (start, end, _), translated in pairs_with_translations:
        result[start:end] = list(translated)

    return "".join(result)

if __name__ == '__main__':
    start = datetime.now()
    soup = get_tex_file('./data/example.tex')
    result = process_tex_by_positions('./data/example.tex')

    with open('./data/example_translated.tex', 'w') as f:
        f.write(result)

    end = datetime.now()
    print(f"Время выполнения: {end - start}")