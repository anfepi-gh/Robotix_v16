import os, ast, re, json

ADDONS_PATH = r'c:\Desarrollos Locales\Robotix_v16\addons'

BREAKING_PATTERNS = {
    'name_get': r'def\s+name_get\s*\(',
    'old_m2m_tuple': r'\(\s*[0-4]\s*,\s*0\s*,\s*\{',
    'odoo_osv_import': r'from\s+odoo\.osv\s+import',
    'record_cr_direct': r'self\._cr\b|self\._uid\b|self\._context\b',
    'inselect_operator': r'[\'"]\s*inselect\s*[\'"]',
    'group_operator_field': r'group_operator\s*=',
    'check_access_old': r'check_access_rights\s*\(|check_access_rule\s*\(',
    'old_api_decorators': r'@api\.multi|@api\.one|@api\.cr|@api\.v7|@api\.v8',
    'legacy_js_widget': r'Widget\.extend|require\s*\(\s*["\']web\.',
    'xml_attrs_string': r'attrs\s*=\s*["\']\\{',
    'states_xml_attr': r'\bstates\s*=\s*["\']\\{',
}

results = {}

for mod_name in sorted(os.listdir(ADDONS_PATH)):
    mod_path = os.path.join(ADDONS_PATH, mod_name)
    if not os.path.isdir(mod_path):
        continue

    manifest_path = os.path.join(mod_path, '__manifest__.py')
    if not os.path.exists(manifest_path):
        continue

    with open(manifest_path, 'r', encoding='utf-8', errors='ignore') as f:
        manifest_src = f.read()
    try:
        manifest = ast.literal_eval(manifest_src)
    except Exception:
        manifest = {}

    # Walk Python files (skip pycache, static, tests)
    py_files = []
    for root, dirs, files in os.walk(mod_path):
        dirs[:] = [d for d in dirs if d not in ['__pycache__', 'static', 'tests']]
        for fname in files:
            if fname.endswith('.py') and fname != '__manifest__.py':
                py_files.append(os.path.join(root, fname))

    models_found = []
    breaking = {k: [] for k in BREAKING_PATTERNS}

    for py_path in py_files:
        try:
            with open(py_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
        except Exception:
            continue

        rel = os.path.relpath(py_path, mod_path)

        # Find model class definitions
        for m in re.finditer(r'class\s+(\w+)\s*\(.*?models\.(Model|TransientModel|AbstractModel)', content):
            snippet = content[m.start():m.start()+600]
            name_m = re.search(r'_name\s*=\s*["\']([^"\']+)["\']', snippet)
            inh_m = re.search(r'_inherit\s*=\s*["\']([^"\']+)["\']', snippet)
            kind = m.group(2)
            if name_m:
                models_found.append(f'{name_m.group(1)} ({kind})')
            elif inh_m:
                models_found.append(f'inherit: {inh_m.group(1)}')

        # Detect breaking change patterns
        for key, pattern in BREAKING_PATTERNS.items():
            if key in ('legacy_js_widget', 'xml_attrs_string', 'states_xml_attr'):
                continue
            if re.search(pattern, content):
                breaking[key].append(rel)

    # Check JS files for legacy widget patterns
    js_files = []
    static_src = os.path.join(mod_path, 'static', 'src', 'js')
    if os.path.exists(static_src):
        for root, dirs, files in os.walk(static_src):
            # skip lib folders
            dirs[:] = [d for d in dirs if d != 'lib']
            for fname in files:
                if fname.endswith('.js'):
                    fpath = os.path.join(root, fname)
                    js_files.append(os.path.relpath(fpath, mod_path))
                    try:
                        with open(fpath, 'r', encoding='utf-8', errors='ignore') as f:
                            jscontent = f.read()
                        if re.search(BREAKING_PATTERNS['legacy_js_widget'], jscontent):
                            breaking['legacy_js_widget'].append(os.path.relpath(fpath, mod_path))
                    except Exception:
                        pass

    # Check XML for deprecated attrs/states
    for root, dirs, files in os.walk(mod_path):
        dirs[:] = [d for d in dirs if d not in ['__pycache__', 'static']]
        for fname in files:
            if fname.endswith('.xml'):
                fpath = os.path.join(root, fname)
                try:
                    with open(fpath, 'r', encoding='utf-8', errors='ignore') as f:
                        xcontent = f.read()
                    rel = os.path.relpath(fpath, mod_path)
                    if re.search(r'attrs\s*=\s*["\']', xcontent):
                        breaking['xml_attrs_string'].append(rel)
                    if re.search(r'\bstates\s*=\s*["\'][{"]', xcontent):
                        breaking['states_xml_attr'].append(rel)
                except Exception:
                    pass

    results[mod_name] = {
        'name': manifest.get('name', mod_name),
        'summary': (manifest.get('summary', '') or manifest.get('description', '') or '')[:200].strip(),
        'version': manifest.get('version', '?'),
        'depends': manifest.get('depends', []),
        'category': manifest.get('category', ''),
        'models': list(dict.fromkeys(models_found)),
        'breaking': {k: list(dict.fromkeys(v)) for k, v in breaking.items() if v},
        'has_js': bool(js_files),
        'js_files': js_files,
    }

print(json.dumps(results, indent=2, ensure_ascii=False))
