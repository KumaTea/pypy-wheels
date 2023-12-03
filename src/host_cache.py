import os
import logging
from flask import Flask, send_from_directory


WORKDIR = os.path.expanduser('~')
if os.name == 'nt':
    HTML_DIR = 'E:/Cache/pypy/html'
    CACHE_DIR = 'AppData/Local/pip/cache/wheels'
else:
    HTML_DIR = '/tmp/html'
    CACHE_DIR = '.cache/pip/wheels'

app = Flask(__name__)

logging.basicConfig(
    format='%(asctime)s %(levelname)-8s %(message)s',
    level=logging.INFO,
    datefmt='%Y-%m-%d %H:%M:%S')

logger = logging.getLogger('werkzeug')
logger.setLevel(logging.WARNING)


def get_local_whl_list():
    if not os.path.isdir(f'{WORKDIR}/{CACHE_DIR}'):
        logger.warning('No wheels yet!')
        return []

    whl_list = []
    for root, dirs, files in os.walk(f'{WORKDIR}/{CACHE_DIR}'):
        for file in files:
            if file.endswith('.whl'):
                whl_list.append((file, root.replace(f'{WORKDIR}/', '')))
    logger.warning(f'Found {len(whl_list)} wheels.')
    unique_whl_list = []
    unique_whl_name_list = []
    for whl in whl_list:
        if whl[0] not in unique_whl_name_list:
            unique_whl_name_list.append(whl[0])
            unique_whl_list.append(whl)
    logger.warning(f'Found {len(unique_whl_list)} unique wheels.')
    return unique_whl_list


def gen_html():
    logger.warning('Generating HTML...')
    whl_list = get_local_whl_list()
    whl_list.sort(key=lambda x: x[0])

    html_head = '<!DOCTYPE html><html><head><meta charset="utf-8"><title>Wheels</title></head><body>\n'
    html_tail = '</body></html>\n'
    html_body = ''
    for whl in whl_list:
        path = whl[1].replace('\\', '/')
        name = whl[0]
        html_body += f'<a href="{path}/{name}">{name}</a><br>\n'
    html = html_head + html_body + html_tail

    os.makedirs(HTML_DIR, exist_ok=True)
    with open(f'{HTML_DIR}/index.html', 'w', encoding='utf-8') as f:
        f.write(html)


gen_html()
req_count = 0


@app.route('/')
@app.route('/index.html')
@app.route('/wheels.html')
def index():
    global req_count
    req_count += 1
    if req_count % 100 == 0:
        logger.warning(f'Requested {req_count} times, regenerating HTML...')
        gen_html()
    return send_from_directory(HTML_DIR, 'index.html')


@app.route('/<path:path>')
def send_whl(path):
    if not 'whl' in path:
        logger.error(f'Dismissed: {path}')
        return '', 404
    filename = path.split('/')[-1]
    logger.warning(f'Requested: {filename}')
    return send_from_directory(WORKDIR, path)


if __name__ == '__main__':
    app.run(host='localhost', port=10300, debug=False)
