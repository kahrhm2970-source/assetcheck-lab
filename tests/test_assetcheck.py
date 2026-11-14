import copy,json,tempfile,unittest
from pathlib import Path
import assetcheck as a
BASE=[{'asset_id':'LAB-1','category':'laptop','location':'ZONE-1'}]
class Tests(unittest.TestCase):
 def test_match(self): self.assertEqual(a.reconcile(BASE,BASE)['summary']['matched_assets'],1)
 def test_missing(self): self.assertEqual(a.reconcile(BASE,[])['findings'][0]['code'],'NOT_OBSERVED')
 def test_unknown(self): self.assertEqual(a.reconcile([],BASE)['findings'][0]['code'],'UNREGISTERED')
 def test_change(self):
  x=copy.deepcopy(BASE); x[0]['location']='ZONE-2'
  self.assertEqual(a.reconcile(BASE,x)['findings'][0]['code'],'DETAIL_MISMATCH')
 def test_category(self):
  x=copy.deepcopy(BASE); x[0]['category']='desktop'
  self.assertIn('category:',a.reconcile(BASE,x)['findings'][0]['evidence'])
 def test_duplicate_observed(self):
  r=a.reconcile(BASE,BASE*2)
  self.assertEqual([x['code'] for x in r['findings']],['DUPLICATE_ID']); self.assertEqual(r['summary']['matched_assets'],0)
 def test_duplicate_expected(self): self.assertEqual(a.reconcile(BASE*2,[])['findings'][0]['code'],'DUPLICATE_ID')
 def test_empty(self): self.assertEqual(a.reconcile([],[])['summary']['findings'],0)
 def test_fixture(self):
  r=a.reconcile(a.read_csv(Path('examples/expected.csv')),a.read_csv(Path('examples/observed.csv')))
  self.assertEqual(r['summary'],dict(expected_rows=4,observed_rows=5,ambiguous_ids=1,matched_assets=1,findings=4))
 def test_validation(self):
  for k,v in [('asset_id','x@example.com'),('location','Office'),('category','server')]:
   x=copy.deepcopy(BASE); x[0][k]=v
   with self.subTest(k=k),self.assertRaises(ValueError): a.reconcile(x,[])
 def test_extra(self):
  x=copy.deepcopy(BASE); x[0]['owner']='private'
  with self.assertRaises(ValueError): a.reconcile(x,[])
 def test_limits(self):
  with self.assertRaises(ValueError): a.reconcile(BASE*10001,[])
 def test_escape(self):
  r=a.reconcile(BASE,[]); r['findings'][0]['evidence']='<script>'
  self.assertNotIn('<script>',a.render(r))
 def test_cli(self):
  with tempfile.TemporaryDirectory() as t:
   self.assertEqual(a.main(['examples/expected.csv','examples/observed.csv','--out',t]),1)
   self.assertEqual(json.loads((Path(t)/'report.json').read_text())['summary']['findings'],4)
 def test_bad_header(self):
  with tempfile.TemporaryDirectory() as t:
   p=Path(t)/'bad.csv'; p.write_text('asset_id,asset_id,location\nLAB-1,x,ZONE-1')
   with self.assertRaises(ValueError): a.read_csv(p)
 def test_bom(self):
  with tempfile.TemporaryDirectory() as t:
   p=Path(t)/'bom.csv'; p.write_text('\ufeffasset_id,category,location\nLAB-1,laptop,ZONE-1',encoding='utf-8')
   self.assertEqual(a.read_csv(p),BASE)
