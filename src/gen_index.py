import os
import shutil


whl_path = './whl/wheels.html'
index_dir = './whl/simple'
cdn_index_dir = './whl/cdn'
if os.name == 'nt':
    whl_path = '.' + whl_path
    index_dir = '.' + index_dir


def gen_index():
    pkgs = {}
    with open(whl_path, 'r', encoding='utf-8') as f:
        whl_html = f.read()

    for line in whl_html.split('\n'):
        if '<a' in line:
            # a_tag_open_start = line.find('<a href="')
            a_tag_open_end = line.find('">')
            a_tag_close = line.find('</a>')
            pkg_filename = line[a_tag_open_end + len('">'):a_tag_close]
            # pkg_url = line[a_tag_open_start + len('<a href="'):a_tag_open_end]
            pkg_name = pkg_filename.split('-')[0]

            if pkg_name.lower() not in pkgs:
                pkgs[pkg_name.lower()] = []
            pkgs[pkg_name.lower()].append((pkg_filename, line))

    for pkg in pkgs:
        pkgs[pkg].sort(key=lambda x: x[0])
        os.makedirs(f'{index_dir}/{pkg}', exist_ok=True)
        with open(f'{index_dir}/{pkg}/index.html', 'w', encoding='utf-8') as f:
            f.write(
                f'<!DOCTYPE html>\n'
                f'<html>\n'
                f'<head>\n'
                f'<meta name="pypi:repository-version" content="1.0">\n'
                f'<title>Links for {pkg}</title>\n'
                f'</head>\n'
                f'<body>\n'
                f'<h1>Links for {pkg}</h1>\n'
            )
            for pkg_filename, line in pkgs[pkg]:
                f.write(line + '\n')
            f.write('</body></html>')

    with open(f'{index_dir}/index.html', 'w', encoding='utf-8') as f:
        f.write(
            '<!DOCTYPE html>\n'
            '<html>\n'
            '<head>\n'
            '<meta name="pypi:repository-version" content="1.0">\n'
            '<title>Package Index</title>\n'
            '<body>\n'
            '<h1>Package Index</h1>\n'
        )
        for pkg in pkgs:
            f.write(f'<a href="{pkg}">{pkg}</a><br>\n')
        f.write('</body></html>')


def gen_cdn_index():
    shutil.copytree(index_dir, cdn_index_dir)
    files = os.walk(cdn_index_dir)
    for root, dirs, files in files:
        for file in files:
            if file.endswith('.html'):
                with open(f'{root}/{file}', 'r', encoding='utf-8') as f:
                    html = f.read()
                html = html.replace('https://github.com/', 'https://gh.kmtea.eu/https://github.com/')
                with open(f'{root}/{file}', 'w', encoding='utf-8') as f:
                    f.write(html)


if __name__ == '__main__':
    gen_index()
    gen_cdn_index()
