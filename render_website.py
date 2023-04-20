import json
import os
import math
import argparse

from pathlib import Path
from more_itertools import chunked
from livereload import Server
from jinja2 import Environment, FileSystemLoader, select_autoescape


def get_cli_args():
    parser = argparse.ArgumentParser(description="Веб интерфейс для навигации по данным сохранённой библиотеки")
    parser.add_argument('datafile', type=str, default='parsed_books_data.json', help='Относительный путь к файлу с данными')
    return parser.parse_args().datafile


def on_reload(data_filename):

    full_file_path = data_filename
    with open(full_file_path, encoding='utf_8') as file:
        books_descriptions = json.load(file)

    books_cards_per_page = 20
    total_pages = math.ceil(len(books_descriptions)/books_cards_per_page)
    book_cards_by_pages = list(chunked(books_descriptions.values(), books_cards_per_page))

    folder_path = 'pages'
    os.makedirs(folder_path, exist_ok=True)

    env = Environment(
        loader=FileSystemLoader('.'),
        autoescape=select_autoescape(['html', 'xml']),
    )

    template = env.get_template('template.html')

    for page_num in range(total_pages):

        page_prev_disabled = 'disabled' if page_num == 0 else ''
        page_next_disabled = 'disabled' if page_num == (total_pages-1) else ''

        # Render Main Page
        prefix = ''
        rendered_page = template.render(
                                        books_at_page=book_cards_by_pages[page_num],
                                        current_page=page_num,
                                        total_pages=range(total_pages),
                                        previous_btn=page_prev_disabled,
                                        next_btn=page_next_disabled,
                                        prefix=prefix
                                        )
        if page_num == 0:
            with open('index.html', 'w', encoding='utf8') as file:
                file.write(rendered_page)

        # Render /pages/
        prefix = '../'
        rendered_page = template.render(
                                        books_at_page=book_cards_by_pages[page_num],
                                        current_page=page_num+1,
                                        total_pages=range(total_pages),
                                        previous_btn=page_prev_disabled,
                                        next_btn=page_next_disabled,
                                        prefix=prefix
                                        )

        with open(Path.cwd()/folder_path/f'index{page_num+1}.html', 'w', encoding='utf8') as file:
            file.write(rendered_page)


if __name__ == '__main__':

    data_filename = get_cli_args()
    on_reload(data_filename)

    server = Server()
    server.watch('template.html', lambda: on_reload(data_filename))
    server.serve(root='.')
