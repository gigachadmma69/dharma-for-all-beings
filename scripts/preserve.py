"""Validate, package and restore-test the public library. Python standard library only."""
import argparse, hashlib, json, pathlib, re, subprocess, sys, tempfile, zipfile
import xml.etree.ElementTree as ET
from urllib.parse import urlparse
ROOT = pathlib.Path(__file__).resolve().parents[1]
FILES = ['archive.json','media.json','reserve.json','LICENSE','RIGHTS.md','README.md','CONTINUITY.md',
         'scripts/build.py','scripts/research.py','scripts/preserve.py',
         'automation-templates/research.yml','dist/index.html','dist/archive.json',
         'dist/media.json','dist/RIGHTS.md','dist/feed.xml']

def require(condition, message):
    if not condition: raise ValueError(message)

def safe_url(value):
    p=urlparse(value)
    require(p.scheme=='https' and p.hostname and not p.username and not p.password, 'Invalid public source URL')

def check(root):
    data=json.loads((root/'archive.json').read_text())
    media=json.loads((root/'media.json').read_text())
    ids=set(); quotes=set()
    for q in data['teachings']:
        for k in ['id','quote','author','translator','work','locator','verified_date','url']:
            require(isinstance(q.get(k),str) and q[k].strip(), 'Missing quotation provenance: '+k)
        require(re.fullmatch(r'[a-zA-Z0-9_-]+',q['id']), 'Unsafe entry ID')
        require(q['id'] not in ids,'Duplicate entry ID');ids.add(q['id'])
        normalized=' '.join(q['quote'].casefold().split())
        require(normalized not in quotes,'Duplicate quotation');quotes.add(normalized)
        safe_url(q['url'])
    for q in media['teachings']:
        for k in ['id','quote','speaker','credit','source_url','transcript_url','watch_url','verification','locator']:
            require(isinstance(q.get(k),str) and q[k].strip(), 'Missing media provenance: '+k)
        require(q['id'] not in ids,'Duplicate media ID');ids.add(q['id'])
        normalized=' '.join(q['quote'].casefold().split())
        require(normalized not in quotes,'Duplicate media quotation');quotes.add(normalized)
        for k in ['source_url','transcript_url','watch_url']:safe_url(q[k])
        require(q.get('timestamp_seconds') is None or (type(q['timestamp_seconds']) is int and q['timestamp_seconds']>=0),'Invalid timestamp')
    reserve=json.loads((root/'reserve.json').read_text())['entries']
    reserve_ids=set(ids)
    for q in reserve:
        for k in ['id','quote','author','translator','work','locator','verified_date','url']:
            require(isinstance(q.get(k),str) and q[k].strip(), 'Missing reserve provenance: '+k)
        require(q['id'] not in reserve_ids,'Duplicate reserve ID');reserve_ids.add(q['id'])
        normalized=' '.join(q['quote'].casefold().split())
        require(normalized not in quotes,'Duplicate reserve quotation');quotes.add(normalized)
        safe_url(q['url'])
    require(json.loads((root/'dist/archive.json').read_text())==data,'Published archive is stale')
    require(json.loads((root/'dist/media.json').read_text())==media,'Published media is stale')
    items=ET.parse(root/'dist/feed.xml').findall('./channel/item')
    require({i.findtext('guid') for i in items}==ids and len(items)==len(ids),'Feed IDs missing or duplicated')
    for f in FILES:
        content=(root/f).read_text()
        require(not re.search(r'(?:gh[pousr]_[A-Za-z0-9]{30,}|sk-[A-Za-z0-9_-]{32,}|-----BEGIN (?:RSA |OPENSSH )?PRIVATE KEY-----)',content),'Possible secret in export: '+f)
    return {'text_entries':len(data['teachings']),'media_entries':len(media['teachings']),'feed_entries':len(items),'reserve_entries':len(reserve)}

def package(destination):
    result=check(ROOT)
    destination=destination.resolve(); destination.parent.mkdir(parents=True,exist_ok=True)
    require(not destination.exists(),'Refusing to overwrite an existing release')
    with zipfile.ZipFile(destination,'w',compression=zipfile.ZIP_DEFLATED) as z:
        for name in FILES:z.write(ROOT/name,name)
    digest=hashlib.sha256(destination.read_bytes()).hexdigest()
    destination.with_suffix('.zip.sha256').write_text(digest+'  '+destination.name+'\n')
    return {**result,'archive':str(destination),'sha256':digest}

def restore_test(archive,checksum):
    expected=checksum.read_text().split()[0]
    require(hashlib.sha256(archive.read_bytes()).hexdigest()==expected,'Archive checksum mismatch')
    with tempfile.TemporaryDirectory(prefix='dharma-restore-') as tmp:
        target=pathlib.Path(tmp)
        with zipfile.ZipFile(archive) as z:
            require(set(z.namelist())==set(FILES) and len(z.namelist())==len(FILES),'Unexpected archive members')
            require(sum(i.file_size for i in z.infolist())<20_000_000,'Archive exceeds restore budget')
            for name in FILES:
                # Exact allowlist; no extraction of arbitrary paths or executable metadata.
                out=target/name;out.parent.mkdir(parents=True,exist_ok=True);out.write_bytes(z.read(name))
        before={p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in (target/'dist').iterdir() if p.is_file()}
        check(target)
        require((target/'scripts/build.py').read_bytes()==(ROOT/'scripts/build.py').read_bytes(),'Packaged build script differs from trusted local builder; inspect before executing')
        subprocess.run([sys.executable,'scripts/build.py'],cwd=target,check=True,capture_output=True)
        after={p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in (target/'dist').iterdir() if p.is_file()}
        require(before==after,'Restored build differs from packaged public output')
        return {'restoration':'passed','rebuild':'identical','network_required':False}

def fault_test():
    import shutil
    with tempfile.TemporaryDirectory(prefix='dharma-fault-test-') as tmp:
        root=pathlib.Path(tmp)
        for f in FILES:
            (root/f).parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(ROOT/f,root/f)
        original=(root/'archive.json').read_text()
        cases={}
        for label,mutate in [
          ('duplicate',lambda d:d['teachings'].append(dict(d['teachings'][0]))),
          ('missing_credit',lambda d:d['teachings'][0].pop('translator')),
          ('unsafe_source',lambda d:d['teachings'][0].update(url='javascript:alert(1)'))]:
            d=json.loads(original);mutate(d);(root/'archive.json').write_text(json.dumps(d))
            try:check(root)
            except ValueError:cases[label]='caught'
            else:raise AssertionError('Fault not caught: '+label)
        (root/'archive.json').write_text(original)
        (root/'dist/feed.xml').write_text('<rss><channel/></rss>')
        try:check(root)
        except ValueError:cases['missing_feed_items']='caught'
        else:raise AssertionError('Missing feed entries not caught')
        return cases

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('action',choices=['check','package','restore-test','fault-test']);p.add_argument('archive',nargs='?',type=pathlib.Path);p.add_argument('--checksum',type=pathlib.Path);a=p.parse_args()
    try:
        if a.action=='check':result=check(ROOT)
        elif a.action=='fault-test':result=fault_test()
        elif a.action=='package':
            require(a.archive is not None,'Supply archive output path');result=package(a.archive)
        else:
            require(a.archive is not None and a.checksum is not None,'Supply archive and checksum');result=restore_test(a.archive,a.checksum)
        print(json.dumps(result))
    except (ValueError,AssertionError) as exc:
        print('Preservation check failed: '+str(exc),file=sys.stderr);sys.exit(1)
