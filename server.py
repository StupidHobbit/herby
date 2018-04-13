import pathlib
from cryptography.fernet import Fernet

from aiohttp import web
import jinja2
import aiohttp_jinja2
from yaml import load, Loader

from bd_routines import *
from get_routes import get_routes
from post_routes import post_routes


def load_config(file="polls.yaml"):
    stream = open(str(pathlib.Path('.') / 'config' / file))
    conf = load(stream, Loader)
    return conf


def init_func(argv):
    app = web.Application()

    app['config'] = load_config()

    app.router.add_routes(get_routes)
    app.router.add_routes(post_routes)
    app.router.add_static('/static', 'static', append_version=True)
    aiohttp_jinja2.setup(app,
                         loader=jinja2.FileSystemLoader('templates'))

    cipher_key = Fernet.generate_key()
    cipher = Fernet(cipher_key)
    app['cipher'] = cipher

    app.on_startup.append(init_db)
    app.on_startup.append(init_alphabet)
    app.on_cleanup.append(close_db)

    return app


async def init_alphabet(app):
    ans = await send_request(app, "SELECT DISTINCT substr(name, 1, 1) FROM Herb;")
    #herbs_alphabet = list(set(item[0][0].upper() for item in ans))
    herbs_alphabet = [item[0].upper() for item in ans]
    herbs_alphabet.sort()
    app['herbs_alphabet'] = herbs_alphabet

    ans = await send_request(app, "SELECT DISTINCT substr(name, 1, 1) FROM Collection;")
    collections_alphabet = [item[0].upper() for item in ans]
    collections_alphabet.sort()
    app['collection_alphabet'] = collections_alphabet
