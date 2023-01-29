import json
import os

from pathlib import Path
from more_itertools import chunked
from livereload import Server
from jinja2 import Environment, FileSystemLoader, select_autoescape

# from http.server import HTTPServer, SimpleHTTPRequestHandler


def on_reload():

    all_books_filename = Path.cwd()/'downloads'/'parsed_books_data.json'
    with open(all_books_filename, encoding='utf_8') as file:
        all_books = json.load(file)

    per_page = 20
    columns = 2
    pagination = 0
    pages_folder = 'pages'

    os.makedirs(pages_folder, exist_ok=True)
    all_books_cunked = list(chunked(all_books.values(), columns))

    env = Environment(
        loader=FileSystemLoader('.'),
        autoescape=select_autoescape(['html', 'xml'])
    )

    template = env.get_template('template.html')

    current_book = 0
    pagination_continue = True
    while pagination_continue:
        page_books = []
        for num in enumerate(range(int(per_page/columns))):
            if current_book >= len(all_books)/columns:
                continue
            page_books.append(all_books_cunked[current_book])
            current_book += 1

        pagination += 1
        rendered_page = template.render(all_books_cunked=page_books)

        with open(Path.cwd()/pages_folder/f'index{pagination}.html', 'w', encoding="utf8") as file:
            file.write(rendered_page)

        if current_book >= len(all_books)/columns:
            pagination_continue = False


on_reload()
# server = HTTPServer(('0.0.0.0', 8000), SimpleHTTPRequestHandler)
# server.serve_forever()

server = Server()
server.watch('template.html', on_reload)
server.serve(root='.')
