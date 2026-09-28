"""Read-only source research. Never promotes a candidate or publishes a post."""
import concurrent.futures, datetime, hashlib, html, json, pathlib, re, urllib.parse, urllib.request
from html.parser import HTMLParser
ROOT=pathlib.Path(__file__).resolve().parents[1]
class Passage(HTMLParser):
 def __init__(self): super().__init__();self.text=[];self.links=[];self.skip=0
 def handle_starttag(self,tag,attrs):
  if tag in ('script','style'): self.skip+=1
  if tag=='a':
   href=dict(attrs).get('href')
   if href:self.links.append(href)
 def handle_endtag(self,tag):
  if tag in ('script','style'):self.skip=max(0,self.skip-1)
 def handle_data(self,t):
  if not self.skip:self.text.append(t)
def norm(s):return re.sub(r'\s+',' ',html.unescape(s)).strip()
def inspect(q):
 url=q['url']; parsed=urllib.parse.urlparse(url)
 allowed={'www.lotsawahouse.org','accesstoinsight.org','www.accesstoinsight.org','kwanumzen.org','media.berkeleyzencenter.org','wwzc.org','www.dhammatalks.org'}
 if parsed.scheme!='https' or parsed.hostname not in allowed:return {'id':q['id'],'status':'disallowed_source'}
 try:
  req=urllib.request.Request(url,headers={'User-Agent':'DharmaLibrarySourceCheck/1.0 (read-only archival verification)'})
  with urllib.request.urlopen(req,timeout=25) as response:
   if urllib.parse.urlparse(response.url).hostname not in allowed:raise ValueError('Unexpected redirect host')
   raw=response.read(2_000_001)
   if len(raw)>2_000_000:raise ValueError('Source exceeds size limit')
   if 'pdf' in response.headers.get('Content-Type',''):return {'id':q['id'],'url':url,'status':'manual_pdf_review'}
  p=Passage();p.feed(raw.decode('utf-8',errors='replace'));text=norm(' '.join(p.text));quote=norm(q['quote'])
  links=sorted({urllib.parse.urljoin(url,a).split('#')[0] for a in p.links if urllib.parse.urlparse(urllib.parse.urljoin(url,a)).hostname==parsed.hostname and urllib.parse.urljoin(url,a).startswith('https://')})
  return {'id':q['id'],'url':url,'status':'exact_text_found' if quote in text else 'review_required','source_sha256':hashlib.sha256(raw).hexdigest(),'discovery_links':links[:30]}
 except Exception as exc:return {'id':q['id'],'url':url,'status':'fetch_failed','error_type':type(exc).__name__}
if __name__=='__main__':
 data=json.loads((ROOT/'archive.json').read_text())
 with concurrent.futures.ThreadPoolExecutor(max_workers=3) as pool: results=list(pool.map(inspect,data['teachings']))
 known={q['url'] for q in data['teachings']}
 report={'checked_at':datetime.datetime.now(datetime.timezone.utc).isoformat(),'policy':'Discovery only. Exact-text matching is not contextual or rights verification. Never auto-publish candidates.','sources':results,'candidate_urls':sorted({u for r in results for u in r.get('discovery_links',[]) if u not in known})}
 (ROOT/'research-report.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
 print(json.dumps({'sources_checked':len(results),'candidate_links':len(report['candidate_urls']),'statuses':{s:sum(r['status']==s for r in results) for s in sorted({r['status'] for r in results})}}))
