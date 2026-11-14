"""Offline synthetic IT inventory reconciliation. Python 3.10+, stdlib only."""
import argparse
from collections import Counter
import csv
import html
import io
import json
from pathlib import Path
import re

FIELDS = ['asset_id', 'category', 'location']
CATEGORIES = {'laptop', 'desktop', 'printer', 'switch', 'camera'}


def validate(rows):
    if len(rows) > 10000:
        raise ValueError('At most 10000 rows per file')
    for row in rows:
        if set(row) != set(FIELDS) or any(not isinstance(v, str) for v in row.values()):
            raise ValueError('Missing or extra fields')
        if not re.fullmatch(r'LAB-\d{1,8}', row['asset_id']):
            raise ValueError('Use synthetic IDs LAB- followed by 1-8 digits')
        if row['category'] not in CATEGORIES:
            raise ValueError('Unknown category')
        if not re.fullmatch(r'ZONE-\d{1,4}', row['location']):
            raise ValueError('Use synthetic locations ZONE- followed by 1-4 digits')
    return rows


def reconcile(expected, observed):
    validate(expected); validate(observed)
    ec = Counter(r['asset_id'] for r in expected)
    oc = Counter(r['asset_id'] for r in observed)
    ambiguous = {key for key in ec.keys() | oc.keys() if ec[key] > 1 or oc[key] > 1}
    findings = []
    def add(code, asset, evidence, action):
        findings.append(dict(code=code, asset_id=asset, evidence=evidence, next_step=action))
    for key in sorted(ambiguous):
        add('DUPLICATE_ID', key, f'Expected rows={ec[key]}; observed rows={oc[key]}',
            'Verify physical labels and source rows; this ID is excluded from other comparisons.')
    e = {r['asset_id']: r for r in expected if r['asset_id'] not in ambiguous}
    o = {r['asset_id']: r for r in observed if r['asset_id'] not in ambiguous}
    for key in sorted(e.keys() - o.keys()):
        add('NOT_OBSERVED', key, 'Present in register only', 'Recheck inventory scope and authorized movement records; absence is not proof of loss.')
    for key in sorted(o.keys() - e.keys()):
        add('UNREGISTERED', key, 'Present in observation only', 'Verify source register and approved acquisition before updating records.')
    matched = 0
    for key in sorted(e.keys() & o.keys()):
        changes = [f"{f}: {e[key][f]} -> {o[key][f]}" for f in ('category', 'location') if e[key][f] != o[key][f]]
        if changes:
            add('DETAIL_MISMATCH', key, '; '.join(changes), 'Confirm device type and approved movement; do not overwrite the register automatically.')
        else:
            matched += 1
    return {'summary': {'expected_rows':len(expected),'observed_rows':len(observed),
                        'ambiguous_ids':len(ambiguous),'matched_assets':matched,'findings':len(findings)},
            'findings': findings}


def read_csv(path):
    with path.open('rb') as f: raw=f.read(1048577)
    if len(raw)>1048576: raise ValueError('CSV exceeds 1 MiB')
    reader=csv.DictReader(io.StringIO(raw.decode('utf-8-sig'),newline=''),strict=True)
    if reader.fieldnames != FIELDS: raise ValueError('Headers must be asset_id,category,location in that order')
    return validate(list(reader))


def render(report):
    rows=''.join('<tr>'+''.join('<td>'+html.escape(str(r[k]))+'</td>' for k in ('code','asset_id','evidence','next_step'))+'</tr>' for r in report['findings'])
    return '<!doctype html><html lang="en"><meta charset="utf-8"><title>AssetCheck Lab</title><style>body{font:16px system-ui;max-width:1100px;margin:40px auto;padding:20px;background:#f4f7fb;color:#14334b}td,th{padding:12px;border:1px solid #c7d4df;text-align:left}table{border-collapse:collapse;background:white}h1{color:#137568}</style><h1>AssetCheck Lab</h1><p>Synthetic inventory • human review required</p><p>'+html.escape(json.dumps(report['summary']))+'</p><table><tr><th>Finding</th><th>Asset</th><th>Evidence</th><th>Next step</th></tr>'+rows+'</table><p>Duplicate IDs are excluded from other comparisons. Not observed does not establish loss. No records were changed.</p></html>'


def main(argv=None):
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('expected',type=Path); p.add_argument('observed',type=Path)
    p.add_argument('--out',type=Path,default=Path('reports'))
    a=p.parse_args(argv)
    try:
        # Read/validate everything before creating reports.
        report=reconcile(read_csv(a.expected),read_csv(a.observed))
        a.out.mkdir(parents=True,exist_ok=True)
        (a.out/'report.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
        (a.out/'report.html').write_text(render(report),encoding='utf-8')
        print(json.dumps(report['summary'])); return 1 if report['findings'] else 0
    except (ValueError,OSError,csv.Error) as exc:
        print('Unable to complete: '+str(exc)); return 2

if __name__=='__main__': raise SystemExit(main())
