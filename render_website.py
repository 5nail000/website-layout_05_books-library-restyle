import json
import os
import io
import math
import argparse

from pathlib import Path
from more_itertools import chunked
from livereload import Server
from jinja2 import Environment, FileSystemLoader, select_autoescape
from contextlib import redirect_stderr


def parse_argparse():
    parser = argparse.ArgumentParser(description="Веб интерфейс для навигации по данным сохранённой библиотеки")
    parser.add_argument(
        'data_folder', type=str, default='media', help='Папка с данными, по умолчанию "media"'
        )

    try:
        data_folder = parser.parse_args().data_folder
    except SystemExit:
        data_folder = 'media'

    return data_folder


def on_reload(data_folder='media'):

    filename_books_descriptions = Path.cwd()/data_folder/'parsed_books_data.json'
    with open(filename_books_descriptions, encoding='utf_8') as file:
        books_descriptions = json.load(file)

    books_cards_per_page = 20
    columns = 2
    pagination = 0
    pages_folder = 'pages'

    os.makedirs(pages_folder, exist_ok=True)
    all_book_cards_chunked = list(chunked(books_descriptions.values(), columns))

    env = Environment(
        loader=FileSystemLoader('.'),
        autoescape=select_autoescape(['html', 'xml']),
    )

    template = env.get_template('template.html')

    current_book = 0
    pagination_continue = True
    while pagination_continue:
        page_books = []
        for num in enumerate(range(int(books_cards_per_page/columns))):
            if current_book >= len(books_descriptions)/columns:
                continue
            page_books.append(all_book_cards_chunked[current_book])
            current_book += 1

        pagination += 1
        pagination_pre = ''
        pagination_next = ''

        if pagination == 1:
            pagination_pre = 'disabled'

        if current_book >= len(books_descriptions)/columns:
            pagination_continue = False
            pagination_next = 'disabled'

        total_pages = math.ceil(len(books_descriptions)/books_cards_per_page)

        # Render Main Page
        prefix = ''
        rendered_page = template.render(
                                        all_book_cards_chunked=page_books,
                                        current_page=pagination,
                                        total_pages=range(total_pages),
                                        previous_btn=pagination_pre,
                                        next_btn=pagination_next,
                                        prefix=prefix
                                        )
        if pagination == 1:
            with open('index.html', 'w', encoding='utf8') as file:
                file.write(rendered_page)

        # Render /pages/
        prefix = '../'
        rendered_page = template.render(
                                        all_book_cards_chunked=page_books,
                                        current_page=pagination,
                                        total_pages=range(total_pages),
                                        previous_btn=pagination_pre,
                                        next_btn=pagination_next,
                                        prefix=prefix
                                        )

        with open(Path.cwd()/pages_folder/f'index{pagination}.html', 'w', encoding='utf8') as file:
            file.write(rendered_page)


if __name__ == '__main__':

    data_folder = parse_argparse()
    print(f'choosing folder: {data_folder}')
    on_reload(data_folder)

    server = Server()
    server.watch('template.html', on_reload)
    server.serve(root='.')
