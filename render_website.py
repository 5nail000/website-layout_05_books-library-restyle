import json
import os
import math

from pathlib import Path
from more_itertools import chunked
from livereload import Server
from jinja2 import Environment, FileSystemLoader, select_autoescape


def on_reload():

    filename_books_description = Path.cwd()/'media'/'parsed_books_data.json'
    with open(filename_books_description, encoding='utf_8') as file:
        books_description = json.load(file)

    per_page = 20
    columns = 2
    pagination = 0
    pages_folder = 'pages'

    os.makedirs(pages_folder, exist_ok=True)
    all_books_chunked = list(chunked(books_description.values(), columns))

    env = Environment(
        loader=FileSystemLoader('.'),
        autoescape=select_autoescape(['html', 'xml']),
    )

    env.globals['static'] = 'static/'
    template = env.get_template('template.html')

    current_book = 0
    pagination_continue = True
    while pagination_continue:
        page_books = []
        for num in enumerate(range(int(per_page/columns))):
            if current_book >= len(books_description)/columns:
                continue
            page_books.append(all_books_chunked[current_book])
            current_book += 1

        pagination += 1
        pagination_pre = ''
        pagination_next = ''

        if pagination == 1:
            pagination_pre = 'disabled'

        if current_book >= len(books_description)/columns:
            pagination_continue = False
            pagination_next = 'disabled'

        total_pages = math.ceil(len(books_description)/per_page)

        rendered_page = template.render(
                                        all_books_chunked=page_books,
                                        current_page=pagination,
                                        total_pages=range(total_pages),
                                        previous_btn=pagination_pre,
                                        next_btn=pagination_next
                                        )

        if pagination == 1:  # Main Page
            with open('index.html', 'w', encoding='utf8') as file:
                file.write(rendered_page)

        with open(Path.cwd()/pages_folder/f'index{pagination}.html', 'w', encoding='utf8') as file:
            file.write(rendered_page)


if __name__ == '__main__':

    on_reload()

    server = Server()
    server.watch('template.html', on_reload)
    server.serve(root='.')
