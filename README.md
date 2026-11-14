# AssetCheck Lab | مطابقة جرد أجهزة تقنية المعلومات

**الحسين علي أبو طالب — Alhussin Ali Abutalib**

Educational IT Support / IT Technician portfolio built with AI assistance. All example assets and locations are fictional. No production use or commercial work experience is claimed.

## Problem and approach

قبل تحديث سجل الأجهزة، نحتاج مقارنة القائمة المسجلة بما رُصد في الجرد. يقارن المشروع ملفي CSV محليًا ويصدر تقرير HTML وJSON بالأدلة وخطوة المراجعة المقترحة: جهاز لم يُرصد، جهاز غير مسجل، اختلاف نوع أو موقع، أو تكرار رقم أصل.

## Run: Python 3.10+, no dependencies

```sh
python assetcheck.py examples/expected.csv examples/observed.csv --out reports/demo
python -m unittest discover -s tests -v
```

Open `reports/demo/report.html`. Use `python3` or Windows `py -3` if needed. Codespaces can run the same commands; download the report to view on mobile. No server, API key, network call or admin rights needed.

Exit codes: **0** no findings, **1** review needed (report generated), **2** invalid input/I/O failure. A failed run may leave old reports: check the exit code before opening them. Outputs overwrite files of the same name in --out; source CSV files are not changed.

## Synthetic demo

| Metric | Expected |
|---|---:|
| Register rows | 4 |
| Observation rows | 5 |
| Duplicate/ambiguous IDs | 1 |
| Fully matching assets | 1 |
| Findings | 4 |

The four findings are: LAB-4 duplicate, LAB-3 not observed, LAB-5 unregistered, LAB-2 location mismatch. Duplicate IDs in either source are excluded from all other comparisons; no arbitrary first/last row wins. Counts are input rows, not necessarily physical-device totals. No percentage is claimed.

## Input contract

Both UTF-8 CSV files require exact ordered headers `asset_id,category,location`. IDs must be synthetic `LAB-` followed by 1–8 digits, location `ZONE-` followed by 1–4 digits. Category: laptop, desktop, printer, switch or camera. Values are case-sensitive with no whitespace normalization. Empty files with headers are valid. Missing/extra columns, duplicate headers, invalid values, files over 1 MiB and more than 10000 data rows fail validation. Repeated asset IDs are valid input and produce a review finding.

## Interpretation and limits

`NOT_OBSERVED` means absent from the supplied observation file, not proven lost or stolen. The observation must cover the same scope and period as the register. A label may be wrong, a device moved, or a register outdated. `UNREGISTERED` is not proof of unauthorized hardware. A category/location mismatch is one finding per asset even if both fields differ.

No barcode reader, network discovery, serial-number matching, procurement, depreciation, custody, audit certification or automatic register updates. Zero findings means only consistency of these supplied fields. A human must verify evidence and approved movement records. See [Arabic workflow](docs/WORKFLOW_AR.md).

## Privacy

No employee names, emails, serials or descriptions are needed. This tool is intentionally restricted to synthetic lab identifiers; it is not an anonymizer. Keep actual organizational inventory and exports private. Reports include the supplied synthetic IDs and locations. Only fictional samples belong in public GitHub. `.gitignore` excludes reports/ and private/; it does not protect arbitrary files elsewhere.

## Interview demo

Explain why accurate inventory helps device handover and troubleshooting. Run the demo, show why the duplicate is treated as ambiguous, investigate LAB-3 through scope and movement records, then explain why updating the register needs human approval.

## Official implementation references

- [Python csv](https://docs.python.org/3/library/csv.html)
- [Python collections.Counter](https://docs.python.org/3/library/collections.html#collections.Counter)
- [Python html.escape](https://docs.python.org/3/library/html.html#html.escape)
- [Python unittest](https://docs.python.org/3/library/unittest.html)

AI assistance was used for implementation, tests and documentation. These are educational comparison rules, not an industry compliance standard.
