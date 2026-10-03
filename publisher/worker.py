"""Portable hourly X publisher. Disabled unless explicitly armed; no AI generation.
Run on an always-on host with persistent SQLite storage. Never use a fresh DB
as automatic failover: ambiguous attempts must be reconciled by a caretaker.
"""
import argparse, datetime as dt, hashlib, json, os, sqlite3, urllib.request
from pathlib import Path
UTC=dt.timezone.utc

def instant(s):
    t=dt.datetime.fromisoformat(s.replace('Z','+00:00'))
    if t.tzinfo is None: raise ValueError('Timezone required')
    return t.astimezone(UTC)

def validate(queue):
    seen=set(); slots=set(); last=None
    ordered=sorted(queue,key=lambda x:instant(x['due_at']))
    for index,q in enumerate(ordered):
        for key in ('id','quote','author','work','translator','source_url','locator','context','rights_review','reviewed_at','text','due_at','tradition'):
            if not isinstance(q.get(key),str) or not q[key].strip(): raise ValueError('Missing approved field: '+key)
        if q.get('approved') is not True: raise ValueError('Unapproved candidate')
        if not q['source_url'].startswith('https://'): raise ValueError('HTTPS source required')
        if q['quote'] not in q['text'] or q['source_url'] not in q['text']: raise ValueError('Quote/source missing from post')
        t=instant(q['due_at'])
        if t.minute or t.second or t.microsecond: raise ValueError('Hourly slots only')
        if t in slots or q['id'] in seen: raise ValueError('Duplicate slot/id')
        if last and last['author']==q['author']: raise ValueError('Consecutive author')
        for previous in ordered[:index]:
            if q['work'].casefold()=='dhammapada' and previous['work'].casefold()=='dhammapada' and t-instant(previous['due_at'])<dt.timedelta(hours=24):raise ValueError('Dhammapada daily limit')
            if previous['quote']==q['quote']:raise ValueError('Duplicate quotation')
        window=ordered[max(0,index-7):index+1]
        if len(window)==8 and (len({x['author'] for x in window})<4 or len({x['tradition'] for x in window})<3):raise ValueError('Insufficient eight-post diversity')
        seen.add(q['id']);slots.add(t);last=q
    return queue

def database(path, initialize=False):
    path=Path(path).resolve()
    if initialize:
        # Exclusive creation prevents overwriting a real publication history.
        fd=os.open(path,os.O_CREAT|os.O_EXCL|os.O_WRONLY,0o600);os.close(fd)
        db=sqlite3.connect(path,timeout=20)
        db.execute('CREATE TABLE events (id TEXT PRIMARY KEY, digest TEXT NOT NULL, state TEXT NOT NULL, attempted_at TEXT NOT NULL, post_id TEXT)')
        db.execute('PRAGMA user_version=1');db.commit()
    else:
        # mode=rw refuses to silently recreate a missing persistent volume.
        db=sqlite3.connect(path.as_uri()+'?mode=rw',uri=True,timeout=20)
        if db.execute('PRAGMA quick_check').fetchone()!=('ok',) or db.execute('PRAGMA user_version').fetchone()!=(1,):
            db.close();raise ValueError('Publication history unavailable; reconcile before recovery')
        db.execute('SELECT id,digest,state,attempted_at,post_id FROM events LIMIT 0')
    db.execute('PRAGMA journal_mode=WAL');db.execute('PRAGMA synchronous=FULL')
    return db

def tick(db,queue,now,send,armed=False,cutover=None):
    validate(queue)
    if not armed:return {'status':'disabled','approved_entries':len(queue)}
    if cutover is None or now<instant(cutover):return {'status':'before_cutover'}
    # A persistent claim precedes the network request. Uncertainty stops the channel.
    db.execute('BEGIN IMMEDIATE')
    if db.execute("SELECT 1 FROM events WHERE state='uncertain'").fetchone():
        db.rollback();return {'status':'reconciliation_required'}
    due=[q for q in queue if instant(cutover)<=instant(q['due_at'])<=now and now-instant(q['due_at'])<dt.timedelta(hours=1) and not db.execute('SELECT 1 FROM events WHERE id=?',(q['id'],)).fetchone()]
    if not due:db.rollback();return {'status':'no_current_slot'}
    previous=db.execute('SELECT attempted_at FROM events ORDER BY attempted_at DESC LIMIT 1').fetchone()
    if previous and now-instant(previous[0])<dt.timedelta(hours=1):db.rollback();return {'status':'hourly_rate_guard'}
    q=min(due,key=lambda q:instant(q['due_at']))
    digest=hashlib.sha256(q['text'].encode()).hexdigest()
    db.execute('INSERT INTO events VALUES (?,?,?,?,NULL)',(q['id'],digest,'uncertain',now.isoformat()));db.commit()
    try:
        pid=send(q['text'])
        if not isinstance(pid,str) or not pid.isdigit():raise ValueError('Missing server post ID')
    except Exception:
        # Do not log credentials, request headers, response bodies, or blindly retry.
        return {'status':'reconciliation_required','id':q['id']}
    db.execute("UPDATE events SET state='published',post_id=? WHERE id=?",(pid,q['id']));db.commit()
    return {'status':'published','id':q['id'],'post_id':pid}

class NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self,*args,**kwargs):return None

def send_x(text):
    token=os.environ.get('X_USER_ACCESS_TOKEN')
    if not token:raise ValueError('Missing user token')
    req=urllib.request.Request('https://api.x.com/2/tweets',data=json.dumps({'text':text}).encode(),headers={'Authorization':'Bearer '+token,'Content-Type':'application/json'},method='POST')
    with urllib.request.build_opener(NoRedirect).open(req,timeout=30) as response:
        payload=json.loads(response.read(1_000_000))
    return payload['data']['id']

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--queue',required=True);p.add_argument('--db',required=True);p.add_argument('--send',action='store_true');p.add_argument('--initialize-state',action='store_true');args=p.parse_args()
    if args.initialize_state and args.send:raise SystemExit('State initialization cannot send posts.')
    q=json.loads(Path(args.queue).read_text());db=database(args.db,initialize=args.initialize_state)
    if args.send and not os.environ.get('X_USER_ACCESS_TOKEN'):raise SystemExit('No user token configured; no attempt made.')
    result=tick(db,q,dt.datetime.now(UTC),send_x,armed=args.send and os.environ.get('PUBLISHER_ENABLED')=='yes',cutover=os.environ.get('PUBLISHER_CUTOVER_UTC'))
    print(json.dumps(result))
    if result['status']=='reconciliation_required':raise SystemExit(2)
