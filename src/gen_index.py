import os


whl_path = './whl/wheels.html'
index_dir = './whl/simple'
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

            if pkg_name not in pkgs:
                pkgs[pkg_name] = []
            pkgs[pkg_name].append((pkg_filename, line))

    # fix scipy and SciPy
    lower_pkgs = [pkg for pkg in pkgs if pkg == pkg.lower()]
    diff_pkgs = list(set(pkgs) - set(lower_pkgs))
    dup_pkgs = [pkg for pkg in diff_pkgs if pkg.lower() in pkgs]
    for pkg in dup_pkgs:
        pkgs[pkg].extend(pkgs[pkg.lower()])
        pkgs[pkg.lower()] = pkgs[pkg]  # unix is case sensitive

    for pkg in pkgs:
        pkgs[pkg].sort(key=lambda x: x[0])
        os.makedirs(f'{index_dir}/{pkg}', exist_ok=True)
        with open(f'{index_dir}/{pkg}/index.html', 'w', encoding='utf-8') as f:
            f.write('<!DOCTYPE html>\n<html><body>\n')
            for pkg_filename, line in pkgs[pkg]:
                f.write(line + '\n')
            f.write('</body></html>')

    with open(f'{index_dir}/index.html', 'w', encoding='utf-8') as f:
        f.write('<!DOCTYPE html>\n<html><body>\n')
        for pkg in pkgs:
            f.write(f'<a href="{pkg}">{pkg}</a><br>\n')
        f.write('</body></html>')


if __name__ == '__main__':
    gen_index()
