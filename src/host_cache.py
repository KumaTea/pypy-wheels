import os
from flask import Flask, send_from_directory


WORKDIR = '/home/kuma'
HTML_DIR = '/tmp/html'
CACHE_DIR = '.cache/pip'


def get_local_whl_list():
    whl_list = []
    for root, dirs, files in os.walk(f'{WORKDIR}/{CACHE_DIR}'):
        for file in files:
            if file.endswith('.whl'):
                whl_list.append((file, root.replace(f'{WORKDIR}/', '')))
    return whl_list


def gen_html():
    print('Generating HTML...')
    whl_list = get_local_whl_list()
    print(f'Found {len(whl_list)} wheels.')
    whl_list.sort(key=lambda x: x[0])

    html_head = '<!DOCTYPE html><html><head><meta charset="utf-8"><title>Wheels</title></head><body>\n'
    html_tail = '</body></html>\n'
    html_body = ''
    for whl in whl_list:
        html_body += f'<a href="{whl[1]}/{whl[0]}">{whl[0]}</a><br>\n'
    html = html_head + html_body + html_tail

    os.makedirs(HTML_DIR, exist_ok=True)
    with open(f'{HTML_DIR}/index.html', 'w', encoding='utf-8') as f:
        f.write(html)


app = Flask(__name__)
gen_html()
req_count = 0


@app.route('/')
@app.route('/index.html')
@app.route('/wheels.html')
def index():
    global req_count
    req_count += 1
    if req_count % 100 == 0:
        gen_html()
    return send_from_directory(HTML_DIR, 'index.html')


@app.route('/<path:path>')
def send_whl(path):
    return send_from_directory(WORKDIR, path)


if __name__ == '__main__':
    app.run(host='localhost', port=10300, debug=False)
