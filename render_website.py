import json

from pathlib import Path
from more_itertools import chunked
from livereload import Server
from http.server import HTTPServer, SimpleHTTPRequestHandler
from jinja2 import Environment, FileSystemLoader, select_autoescape


def on_reload():

    all_books_filename = Path.cwd()/'downloads'/'parsed_books_data.json'
    with open(all_books_filename, encoding='utf_8') as file:
        all_books = json.load(file)

    all_books_cunked = list(chunked(all_books.values(), 2))

    env = Environment(
        loader=FileSystemLoader('.'),
        autoescape=select_autoescape(['html', 'xml'])
    )

    template = env.get_template('template.html')

    rendered_page = template.render(
        all_books_cunked=all_books_cunked
    )

    with open('index.html', 'w', encoding="utf8") as file:
        file.write(rendered_page)


on_reload()
# server = HTTPServer(('0.0.0.0', 8000), SimpleHTTPRequestHandler)
# server.serve_forever()

server = Server()
server.watch('template.html', on_reload)
server.serve(root='.')
