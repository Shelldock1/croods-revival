"""Generate placeholder economy assets for the fake server from schema.json + economy_data.py."""
import json, os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, '..', 'server', 'assets')
schema = json.load(open(os.path.join(HERE, 'schema.json')))
sys.path.insert(0, HERE)
from economy_data import ROWS as rows  # noqa: E402
os.makedirs(OUT, exist_ok=True)
for d in (schema.values() if isinstance(schema, dict) else schema):
    sep = d.get('separator') or ';'
    cols = [d['keyColumn']] if d.get('keyColumn') else []
    for f in d.get('neededFields') or []:
        cols.append(f[:-2] + '1' if f.endswith('[]') else f)
    lines = [sep.join(cols)]
    for row in rows.get(d['filePath'], []):
        # quest rows leave optional columns (camera targets...) empty, which the game reads as nil
        default = '' if d.get('namespace') == 'QUESTS' else '0'
        lines.append(sep.join(str(row.get(c, default)) for c in cols))
    open(os.path.join(OUT, d['filePath']), 'w').write('\n'.join(lines) + '\n')
open(os.path.join(OUT, 'version_check'), 'w').write('0')
open(os.path.join(OUT, 'IAP'), 'w').write('IAP_ITEMS = {}\nIAP_TABS = {}\nIAP_SPEND_CAP = {}\n' + (open(os.path.join(HERE, 'lua_trace.lua')).read() if os.environ.get('TRACE') else ''))
open(os.path.join(OUT, 'alerts'), 'w').write('AlertsDefinitions = {}\n')
for extra in ('inventions.csv', 'map.csv'):
    if not os.path.exists(os.path.join(OUT, extra)):
        open(os.path.join(OUT, extra), 'w').write('name\n')
open(os.path.join(OUT, 'config'), 'w').write('-- no A/B patches\n')
print('wrote', len(os.listdir(OUT)), 'files to', os.path.normpath(OUT))
