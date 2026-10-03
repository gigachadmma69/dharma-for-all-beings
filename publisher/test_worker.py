import datetime as dt, tempfile, unittest
from pathlib import Path
from worker import database,tick,validate
NOW=dt.datetime(2026,10,4,12,tzinfo=dt.timezone.utc)
def entry(i='one',h=12):
 return dict(id=i,quote='A verified excerpt.',author=i,work='Work',translator='Translator',source_url='https://example.org/source',locator='p1',context='Context checked',rights_review='Short excerpt reviewed',reviewed_at='2026-10-03',text='A verified excerpt. https://example.org/source',due_at=f'2026-10-04T{h:02}:00:00Z',tradition='Zen',approved=True)
class Checks(unittest.TestCase):
 def setUp(self):self.tmp=tempfile.TemporaryDirectory();self.db=database(Path(self.tmp.name)/'state.sqlite',initialize=True)
 def tearDown(self):self.db.close();self.tmp.cleanup()
 def run_tick(self,q,send,now=NOW):return tick(self.db,q,now,send,True,'2026-10-04T00:00:00Z')
 def test_missing_history_rejected(self):
  with self.assertRaises(Exception):database(Path(self.tmp.name)/'missing.sqlite')
  self.assertFalse((Path(self.tmp.name)/'missing.sqlite').exists())
 def test_existing_history_not_overwritten(self):
  with self.assertRaises(FileExistsError):database(Path(self.tmp.name)/'state.sqlite',initialize=True)
 def test_empty_history_rejected(self):
  p=Path(self.tmp.name)/'empty.sqlite';p.touch()
  with self.assertRaises(ValueError):database(p)
 def test_restart_preserves_dedup(self):
  q=[entry()];self.run_tick(q,lambda _: '123');self.db.close();self.db=database(Path(self.tmp.name)/'state.sqlite')
  self.assertEqual(self.run_tick(q,lambda _:self.fail())['status'],'no_current_slot')
 def test_disabled(self):self.assertEqual(tick(self.db,[entry()],NOW,lambda _:self.fail())['status'],'disabled')
 def test_success_once(self):
  calls=[];s=lambda text:(calls.append(text) or '123');self.assertEqual(self.run_tick([entry()],s)['status'],'published');self.run_tick([entry()],s);self.assertEqual(len(calls),1)
 def test_uncertain_stops_next_slot(self):
  def fail(_):raise TimeoutError()
  self.assertEqual(self.run_tick([entry()],fail)['status'],'reconciliation_required');self.assertEqual(self.run_tick([entry('two',13)],lambda _:self.fail(),NOW+dt.timedelta(hours=1))['status'],'reconciliation_required')
 def test_expired_not_burst(self):self.assertEqual(self.run_tick([entry(h=10)],lambda _:self.fail())['status'],'no_current_slot')
 def test_unapproved(self):
  q=entry();q['approved']=False
  with self.assertRaises(ValueError):validate([q])
 def test_bad_source(self):
  q=entry();q['source_url']='http://example.org'
  with self.assertRaises(ValueError):validate([q])
 def test_consecutive(self):
  a,b=entry(),entry('two',13);b['author']=a['author']
  with self.assertRaises(ValueError):validate([a,b])
 def test_dhammapada_spacing(self):
  a,b=entry(),entry('two',13);a['work']=b['work']='Dhammapada'
  with self.assertRaises(ValueError):validate([a,b])
 def test_diversity(self):
  rows=[entry(str(i),i+12) for i in range(8)]
  for i,q in enumerate(rows):q['quote']=str(i);q['text']=str(i)+' https://example.org/source'
  with self.assertRaises(ValueError):validate(rows)
 def test_cutover(self):self.assertEqual(tick(self.db,[entry()],NOW,lambda _:self.fail(),True,'2026-10-05T00:00:00Z')['status'],'before_cutover')
if __name__=='__main__':unittest.main()
