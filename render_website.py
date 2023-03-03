import json
import os
import math
import argparse

from pathlib import Path
from more_itertools import chunked
from livereload import Server
from jinja2 import Environment, FileSystemLoader, select_autoescape


def parse_argparse():
    parser = argparse.ArgumentParser(description="Веб интерфейс для навигации по данным сохранённой библиотеки")
    parser.add_argument(
        'data_folder', type=str, default='media', help='Папка с данными, по умолчанию "media"'
        )

    try:
        data_folder = parser.parse_args().data_folder
        if os.path.isfile(data_folder):
            filename = os.path.basename(data_folder)
            dir_name = os.path.dirname(data_folder)
        else:
            filename = 'parsed_books_data.json'
            dir_name = data_folder
    except SystemExit:
        filename = 'parsed_books_data.json'
        dir_name = Path.cwd()/'media'

    return dir_name, filename


def on_reload(data_path, data_filename):

    full_file_path = f'{data_path}{os.sep}{data_filename}'
    with open(full_file_path, encoding='utf_8') as file:
        books_descriptions = json.load(file)

    columns = 2
    books_cards_per_page = 20
    total_pages = math.ceil(len(books_descriptions)/books_cards_per_page)

    doubled_cards = list(chunked(books_descriptions.values(), columns))
    book_cards_by_pages = list(chunked(doubled_cards, int(books_cards_per_page/columns)))

    pages_folder = 'pages'
    os.makedirs(pages_folder, exist_ok=True)

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
                                        prefix=prefix,
                                        mediafolder=data_path
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
                                        prefix=prefix,
                                        mediafolder=data_path
                                        )

        with open(Path.cwd()/pages_folder/f'index{page_num+1}.html', 'w', encoding='utf8') as file:
            file.write(rendered_page)


if __name__ == '__main__':

    data_path, data_filename = parse_argparse()
    print(f'loaded data from: {data_path}{os.sep}{data_filename}')
    on_reload(data_path, data_filename)

    server = Server()
    server.watch('template.html', on_reload(data_path, data_filename))
    server.serve(root='.')
