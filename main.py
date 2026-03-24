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


def process_tex(file: TexSoup):
    # Шаг 1: собираем все ноды, которые нужно перевести
    nodes_to_translate = [
        node for node in file.descendants
        if should_translate(node)
    ]

    texts = [node.strip() for node in nodes_to_translate]
    print(f"Найдено фрагментов для перевода: {len(texts)}")

    # Шаг 2: переводим батчами
    translations = []
    for i in range(0, len(texts), BATCH_SIZE):
        batch = texts[i: i + BATCH_SIZE]
        print(f"Батч {i // BATCH_SIZE + 1}: переводим {len(batch)} фрагментов...")
        batch_result = translate_batch(batch)
        translations.extend(batch_result)

    # Шаг 3: выводим результат (здесь можно заменить ноды в документе)
    for original, translated in zip(texts, translations):
        print(f"  ОРИ: {original}")
        print(f"  ПЕР: {translated}")
        print()


if __name__ == '__main__':
    start = datetime.now()
    soup = get_tex_file('example.tex')
    process_tex(soup)
    end = datetime.now()
    print(f"Время выполнения: {end - start}")