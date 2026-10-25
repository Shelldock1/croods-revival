"""Stand-in for Rovio's cloud.rovio.com so The Croods 1.3.1 can start offline.

Routes come from routes.json (reloaded on every request). Economy files the
game downloads as "assets" are served from ./assets/, encrypted the way the
game expects (AES-256-CBC, zero IV, PKCS7, key embedded in libCroods.so).
"""
import hashlib
import json
import os
import threading
import time
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import urlparse, parse_qs, unquote

from cryptography.hazmat.primitives import padding
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes

HERE = os.path.dirname(os.path.abspath(__file__))
ROUTES = os.path.join(HERE, 'routes.json')
SAVES = os.path.join(HERE, 'saves.json')  # cloud saves: {key: {"hash": ..., "value": ...}}
saves_lock = threading.Lock()
ASSETS = os.path.join(HERE, 'assets')
BASE = 'http://10.0.2.2:8000'
# key used by GameLua::loadTextFileToString for downloaded files (libCroods.so @ 0x6a91a0)
ASSET_KEY = bytes.fromhex('38a89ab39f107ae8a05e943442840399439631f86cf8c2a8874900178e2fdba5')


def encrypt(data):
    padder = padding.PKCS7(128).padder()
    data = padder.update(data) + padder.finalize()
    enc = Cipher(algorithms.AES(ASSET_KEY), modes.CBC(b'\0' * 16)).encryptor()
    return enc.update(data) + enc.finalize()


def load_saves():
    try:
        with open(SAVES, encoding='utf-8') as f:
            return json.load(f)
    except Exception:
        return {}


def store_saves(saves):
    tmp = SAVES + '.tmp'
    with open(tmp, 'w', encoding='utf-8') as f:
        json.dump(saves, f)
    os.replace(tmp, SAVES)


def parse_form(body):
    # value is url-safe base64, so decode by hand ('+' must not turn into a space)
    out = {}
    for part in body.decode('latin-1').split('&'):
        if part:
            k, _, v = part.partition('=')
            out.setdefault(unquote(k), []).append(unquote(v))
    return out


def asset_bytes(name):
    path = os.path.join(ASSETS, os.path.basename(name))
    if not os.path.isfile(path):
        return None
    return encrypt(open(path, 'rb').read())


class Handler(BaseHTTPRequestHandler):
    # keep-alive: the game's curl client reuses one connection for all CDN downloads
    protocol_version = 'HTTP/1.1'

    def reply(self, code, data, ctype='application/json'):
        print(f'<-- {code} {data[:300]!r}', flush=True)
        self.send_response(code)
        self.send_header('Content-Type', ctype)
        self.send_header('Content-Length', str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    def handle_any(self):
        n = int(self.headers.get('Content-Length') or 0)
        body = self.rfile.read(n) if n else b''
        url = urlparse(self.path)
        print(f'--> {self.command} {self.path}\n    body={body[:500]!r}', flush=True)

        if url.path == '/assets/2.0/asset':
            names = parse_qs(url.query).get('assetNames', [])
            out = []
            for name in names:
                data = asset_bytes(name)
                if data is None:
                    print(f'    missing asset {name}', flush=True)
                    continue
                out.append({'name': name, 'hash': hashlib.md5(data).hexdigest(),
                            'cdnURL': f'{BASE}/cdn/{name}', 'os': 'android',
                            'distributionChannel': 'google', 'clientVersion': '1.3.1'})
            return self.reply(200, json.dumps({'assets': out}).encode())
        if url.path.startswith('/cdn/'):
            data = asset_bytes(url.path[len('/cdn/'):])
            if data is None:
                return self.reply(404, b'')
            return self.reply(200, data, 'application/octet-stream')

        if url.path == '/storage/state':
            return self.storage(url, body)

        try:
            routes = json.load(open(ROUTES))
        except Exception:
            routes = {}
        r = routes.get(url.path)
        if r is None:
            return self.reply(404, b'{"error": "unknown"}')
        out = r.get('body', {})
        data = out if isinstance(out, str) else json.dumps(out)
        data = data.replace('"__NOW__"', str(int(time.time())))
        self.reply(r.get('code', 200), data.encode() if r.get('code') != 204 else b'')

    def storage(self, url, body):
        """Cloud save. GET ?key=K -> [{key, hash, value}] or 204 if nothing saved;
        POST key=K&value=V&hash=H&force=F -> stores V and answers with the same list."""
        with saves_lock:
            saves = load_saves()
            if self.command == 'POST':
                form = parse_form(body)
                keys = form.get('key', [])
                values = form.get('value', [])
                for k, v in zip(keys, values):
                    saves[k] = {'hash': hashlib.md5(v.encode()).hexdigest(), 'value': v}
                store_saves(saves)
            else:
                keys = parse_qs(url.query).get('key', [])
            out = [{'key': k, 'hash': saves[k]['hash'], 'value': saves[k]['value']}
                   for k in keys if k in saves]
        if not out:
            return self.reply(204, b'')
        return self.reply(200, json.dumps(out).encode())

    do_GET = do_POST = do_PUT = do_DELETE = handle_any

    def log_message(self, *a):
        pass


if __name__ == '__main__':
    print('Fake Rovio server on http://127.0.0.1:8000 (emulator sees it as 10.0.2.2:8000)', flush=True)
    ThreadingHTTPServer(('127.0.0.1', 8000), Handler).serve_forever()
