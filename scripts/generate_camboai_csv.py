import os
import ast
import csv
from collections import defaultdict

WORKSPACE_ROOT = r"d:\CamboAI"
TARGET_COUNT = 336

def gather_py_files(root):
    files = []
    # skip common vendored/virtualenv directories
    skip_dirs = {'.venv', 'venv', 'node_modules', 'site-packages', 'dist-packages', '__pycache__'}
    for dirpath, dirnames, filenames in os.walk(root):
        # mutate dirnames in-place to avoid walking into skip dirs
        dirnames[:] = [d for d in dirnames if d not in skip_dirs]
        for f in filenames:
            if f.endswith('.py'):
                files.append(os.path.join(dirpath, f))
    return sorted(files)


def normalize_relpath(p, root):
    rel = os.path.relpath(p, root)
    parts = rel.replace('\\', '/').split('/')
    # remove leading repeated 'camboai' segments
    while parts and parts[0].lower() == 'camboai':
        parts = parts[1:]
    return os.path.normpath(os.path.join(*parts)) if parts else os.path.basename(rel)


def is_test_file(p):
    low = p.replace('\\', '/').lower()
    return '/tests/' in low or low.endswith('/tests') or '/test_' in os.path.basename(p).lower()


def extract_doc_and_imports(path):
    try:
        source = open(path, 'r', encoding='utf-8', errors='replace').read()
        mod = ast.parse(source)
        doc = ast.get_docstring(mod)
        imports = set()
        for node in ast.walk(mod):
            if isinstance(node, ast.Import):
                for n in node.names:
                    imports.add(n.name.split('.')[0])
            elif isinstance(node, ast.ImportFrom):
                if node.module:
                    imports.add(node.module.split('.')[0])
        if not doc:
            # fallback: top comments
            lines = source.splitlines()
            comments = []
            for ln in lines:
                s = ln.strip()
                if s.startswith('#'):
                    comments.append(s.lstrip('#').strip())
                elif s == '':
                    break
                else:
                    break
            doc = '\n'.join(comments) if comments else ''
        return doc or '', sorted(imports)
    except Exception as e:
        return f'ERROR_READING:{e}', []


def main():
    all_py = gather_py_files(WORKSPACE_ROOT)
    # exclude obvious test files first
    non_tests = [p for p in all_py if not is_test_file(p)]

    # group by normalized relative path
    groups = defaultdict(list)
    for p in non_tests:
        norm = normalize_relpath(p, WORKSPACE_ROOT)
        groups[norm].append(p)

    canonical = {}
    for norm, candidates in groups.items():
        # prefer candidate with smallest path depth (fewer separators), deterministic tie-breaker: lexicographic
        ranked = sorted(candidates, key=lambda x: (x.count(os.sep), x.lower()))
        canonical[norm] = ranked[0]

    selected = sorted(set(canonical.values()))

    # If we still have more than TARGET_COUNT, remove deepest files deterministically until we hit target
    if len(selected) > TARGET_COUNT:
        # sort by depth desc then path lex
        over = len(selected) - TARGET_COUNT
        selected_sorted = sorted(selected, key=lambda x: (-x.count(os.sep), x.lower()))
        to_remove = set(selected_sorted[:over])
        selected = [p for p in selected if p not in to_remove]
    elif len(selected) < TARGET_COUNT:
        # if fewer, fill from non_tests excluding already selected, preferring shallower paths
        missing = TARGET_COUNT - len(selected)
        remaining = [p for p in non_tests if p not in selected]
        remaining_sorted = sorted(remaining, key=lambda x: (x.count(os.sep), x.lower()))
        selected += remaining_sorted[:missing]

    selected = sorted(selected)

    # write canonical list
    out_list = os.path.join(WORKSPACE_ROOT, 'scripts', 'canonical_336_list.txt')
    with open(out_list, 'w', encoding='utf-8') as f:
        for p in selected:
            f.write(p + '\n')

    # generate CSV with docstrings and imports for selected files
    csv_path = os.path.join(WORKSPACE_ROOT, 'scripts', 'camboai_files_summary.csv')
    with open(csv_path, 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(['absolute_path','relative_path','short_description','primary_purpose','benefits_notes','detected_dependencies','inclusion_reason'])
        for p in selected:
            rel = os.path.relpath(p, WORKSPACE_ROOT)
            doc, imports = extract_doc_and_imports(p)
            short = (doc.splitlines()[0][:200]) if doc else 'No module docstring or top comment'
            primary = (doc.splitlines()[0] if doc else '')
            benefits = ''
            if 'test_' in os.path.basename(p).lower():
                inc = 'excluded_tests'  # shouldn't happen
            else:
                inc = 'canonical-picked'
            # simple auto-benefit heuristics
            bn = []
            if 'database' in os.path.basename(p).lower():
                bn.append('Defines DB models and session helpers')
            if 'service' in os.path.basename(p).lower() or '/services/' in p.replace('\\','/'):
                bn.append('Contains business logic or background tasks')
            if 'api' in p.replace('\\','/') or 'router' in p.lower():
                bn.append('Exposes HTTP endpoints')
            if 'main' in os.path.basename(p).lower():
                bn.append('Application entrypoint / app wiring')
            if not bn:
                bn.append('Implementation detail / helper module')
            writer.writerow([p, rel, short, primary, ' | '.join(bn), ','.join(imports), inc])

    # --- Full detailed CSV ---
    def extract_full_details(path):
        """Return (full_doc, public_symbols, imports, env_vars, external_hints)"""
        try:
            src = open(path, 'r', encoding='utf-8', errors='replace').read()
            mod = ast.parse(src)
            doc = ast.get_docstring(mod) or ''
            symbols = []
            for node in mod.body:
                if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
                    if not node.name.startswith('_'):
                        symbols.append(node.name)
            imports = set()
            for node in ast.walk(mod):
                if isinstance(node, ast.Import):
                    for n in node.names:
                        imports.add(n.name.split('.')[0])
                elif isinstance(node, ast.ImportFrom):
                    if node.module:
                        imports.add(node.module.split('.')[0])

            # env var patterns
            env_vars = set()
            for line in src.splitlines():
                if 'os.getenv' in line or 'os.environ' in line or 'ENV' in line or 'dotenv' in line:
                    env_vars.add(line.strip())

            # external service hints (heuristic)
            hints = set()
            if 'yfinance' in src or 'yf.' in src:
                hints.add('yfinance')
            if 'talib' in src:
                hints.add('TA-Lib')
            if 'redis' in src or 'aioredis' in src:
                hints.add('Redis')
            if 'sqlalchemy' in src or 'Session' in src:
                hints.add('SQLAlchemy/Database')
            if 'openai' in src or 'gpt' in src.lower():
                hints.add('LLM/OpenAI')
            if 'requests' in src or 'httpx' in src:
                hints.add('HTTP Client')

            return doc, sorted(symbols), sorted(imports), sorted(env_vars), sorted(hints)
        except Exception as e:
            return f'ERROR_READING:{e}', [], [], [], []

        def synthesize_description(path, doc, syms, imports2, envs, hints):
            """Create a deterministic human-readable paragraph describing the module.
            Uses docstring, public symbols, imports, env var hints, and service hints.
            """
            parts = []
            rel = os.path.relpath(path, WORKSPACE_ROOT)
            # What it is
            if doc and doc.strip():
                lead = doc.splitlines()[0].strip()
                parts.append(f"Module: {lead}")
            else:
                parts.append(f"Module: {os.path.basename(path)}")

            # What it's used for
            usage = []
            p = path.replace('\\', '/').lower()
            if '/app/api/' in p or '/api/' in p:
                usage.append('exposes HTTP API endpoints for the application')
            if '/services/' in p or 'service' in os.path.basename(p).lower():
                usage.append('contains business logic or background services')
            if 'database' in os.path.basename(p).lower() or '/models/' in p:
                usage.append('defines database models and DB access utilities')
            if 'alembic' in p or 'migrate' in p:
                usage.append('manages database migrations')
            if 'websocket' in p or 'ws' in p:
                usage.append('handles websocket connections and broadcasts')
            if 'dashboard' in p or 'streamlit' in imports2:
                usage.append('renders or supports the dashboard UI')
            if not usage:
                usage.append('implements helper utilities or internal logic')
            parts.append('Purpose: ' + '; '.join(usage) + '.')

            # Benefits
            benefits = []
            if 'Exposes HTTP endpoints' in ' '.join(usage) or '/api/' in p:
                benefits.append('enables remote clients and UIs to interact with the service')
            if 'database' in ' '.join(usage) or 'sqlalchemy' in ','.join(imports2):
                benefits.append('centralizes data model and persistence logic')
            if 'service' in ' '.join(usage) or '/services/' in p:
                benefits.append('encapsulates domain logic for reuse and testing')
            if hints:
                benefits.append('integrates with: ' + ', '.join(hints))
            if not benefits:
                benefits.append('supports internal functionality used by the application')
            parts.append('Benefits: ' + ' '.join(benefits) + '.')

            # Important notes
            notes = []
            if envs:
                notes.append('reads environment values or secrets (see code for exact vars)')
            if 'JWT_SECRET_KEY' in '\n'.join(envs) or 'SECRET_KEY' in '\n'.join(envs):
                notes.append('handles authentication tokens; ensure secret is kept safe')
            if 'TA-Lib' in hints:
                notes.append('depends on TA-Lib (native extension) for technical indicators')
            if 'yfinance' in hints:
                notes.append('uses yfinance for market data; network access required')
            if notes:
                parts.append('Notes: ' + ' '.join(notes) + '.')

            # Short summary join
            descr = ' '.join(parts)
            # keep it concise
            return descr[:1400]

    full_csv = os.path.join(WORKSPACE_ROOT, 'scripts', 'camboai_files_full_detailed.csv')
    with open(full_csv, 'w', newline='', encoding='utf-8') as f:
        w = csv.writer(f)
        w.writerow(['absolute_path','relative_path','full_docstring','public_symbols','imports','env_var_lines','external_service_hints','detailed_description','primary_purpose','benefits_notes','inclusion_reason'])
        for p in selected:
            rel = os.path.relpath(p, WORKSPACE_ROOT)
            doc, syms, imports2, envs, hints = extract_full_details(p)
            primary = (doc.splitlines()[0] if doc else '')
            bn = []
            if 'service' in os.path.basename(p).lower() or '/services/' in p.replace('\\','/'):
                bn.append('Contains business logic or background tasks')
            if 'api' in p.replace('\\','/') or 'router' in p.lower():
                bn.append('Exposes HTTP endpoints')
            if 'database' in os.path.basename(p).lower() or 'models' in p.replace('\\','/'):
                bn.append('Defines DB models and session helpers')
            if not bn:
                bn.append('Implementation detail / helper module')
            descr = synthesize_description(p, doc, syms, imports2, envs, hints)
            w.writerow([p, rel, doc.replace('\n', ' \n ')[:2000], '|'.join(syms), ','.join(imports2), '|'.join(envs), ','.join(hints), descr, primary, ' | '.join(bn), 'canonical-picked'])

    print('FULL_CSV', full_csv)

    print('ALL_PY_COUNT', len(all_py))
    print('NON_TEST_COUNT', len(non_tests))
    print('CANONICAL_SELECTED', len(selected))
    print('CSV_PATH', csv_path)
    print('CANONICAL_LIST', out_list)

if __name__ == '__main__':
    main()
