"""Verify accounting anchors, periods and independent model outputs.
Run after rebuilding the model and exporting the workbook.
"""
from pathlib import Path
import json,re,csv,math,zipfile,xml.etree.ElementTree as ET
from rebuild_research import calculate
from leeno_extensions import normalize
ROOT=Path(__file__).resolve().parents[1]
p=normalize(json.loads((ROOT/'data/research_inputs.json').read_text()))
results=json.loads((ROOT/'model/research_results.json').read_text())
detail=json.loads((ROOT/'model/company_detail.json').read_text())
audit={r['account']:float(r['value_krw'])/1e9 for r in csv.DictReader((ROOT/'data/actuals_audit.csv').open(encoding='utf-8-sig'))}
mapping={'rev':'revenue','op':'operating_profit','ni':'net_income','equity':'equity','cash':'cash','liquid':'liquid_financial_assets','leases':'lease_debt','nonop':'nonop_assets','cfo':'CFO'}
for field,account in mapping.items():assert abs(p['h1'][field]-audit[account])<1e-9,(field,account)
assert abs(p['h1']['da']-audit['depreciation_total']-audit['amortization_total'])<1e-9
assert abs(p['h1']['da']-audit['CFO_depreciation']-audit['CFO_amortization']-audit['RD_depreciation']-audit['RD_amortization'])<1e-9
assert abs(p['h1']['capex']-audit['cash_ppe_acquisition']-audit['cash_intangible_acquisition'])<1e-9
assert abs(p['h1']['nwc']-audit['AR']-audit['inventory']+audit['AP'])<1e-9
assert abs(p['h2_cash_adjustment']+audit['accrued_expense_h1']-audit['accrued_expense_2025'])<1e-9
for cs,r in results.items():
 calc=calculate(p,cs)
 for key in ['dcf_price','rim_price','per_price']:assert abs(calc[key]-r[key])<1e-8
 assert abs(r['rim_identity_error'])<1e-7
 assert abs(detail[cs]['price_hurdle_dcf']-p['reference_price'])<1e-6
 assert abs(r['bridge']['h2_revenue']+p['h1']['rev']-r['forecast'][0]['revenue'])<1e-8
 assert abs(r['forecast'][1]['dividend']-r['forecast'][0]['ni']*p['cases'][cs]['payout'])<1e-8
 assert calculate(p,cs,p['cases'][cs]['wacc']+.01)['dcf_price']<r['dcf_price']
text=(ROOT/'report/FINAL_REPORT.md').read_text();headings=re.findall(r'^## .+',text,re.M)
assert len(headings)==14
for block in re.findall(r'(?:^\|.*\n)+',text,re.M):assert len({len(line.strip('|').split('|')) for line in block.splitlines()})==1
assert (ROOT/'README.md').read_text().endswith(text.replace('](figures/','](report/figures/'))
workbook=ROOT/'model/Equity_Research_Model.xlsx'
with zipfile.ZipFile(workbook) as z:
 ns={'s':'http://schemas.openxmlformats.org/spreadsheetml/2006/main'}
 ws=ET.fromstring(z.read('xl/workbook.xml'));names=[x.attrib['name'] for x in ws.findall('s:sheets/s:sheet',ns)];assert len(names)==12
 for path in z.namelist():
  if path.startswith('xl/worksheets/sheet') and path.endswith('.xml'):
   root=ET.fromstring(z.read(path));errors=[x.attrib.get('r') for x in root.findall('.//s:c',ns) if x.attrib.get('t')=='e'];assert not errors,(path,errors)
checks=json.loads((ROOT/'model/model_validation.json').read_text());assert checks['formula_errors']==0
out=dict(model_version=p['model_version'],accounting_anchors_verified=len(mapping)+5,period_and_dividend_lag_verified=True,rim_ddm_identity_verified=True,reverse_price_reconstruction_tolerance_krw=1e-6,common_section_count=len(headings),workbook_sheets=names,formula_errors=0,excel_python_main_checks=len(checks['scenario_checks']),excel_python_diagnostic_checks=len(checks['diagnostic_checks']),operating_build_checks=len(checks['operating_build_checks']),duration_checks=checks['duration_checks'],observed_peer_checks=checks['peer_checks'],boundary_checks=checks['boundary_checks'],source_limitations=['Customer-specific units and ASP not public','Same-date market CAPM not fully calibrated','Observed TTM peer is one company; normalized forward peer set not estimated','Reference prices not reconciled to exchange-certified close','Operating capital is a book-value proxy, not a full account-level separation'])
(ROOT/'model/review_validation.json').write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n')
print('Verified accounting anchors, three scenarios, dividend lag, reverse DCF, 14 sections and 12 exported worksheets')
