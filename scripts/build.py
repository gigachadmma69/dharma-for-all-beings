import json, html, pathlib
ROOT=pathlib.Path(__file__).resolve().parents[1]
data=json.loads((ROOT/'archive.json').read_text())
def e(s): return html.escape(str(s))
rows=[]
for q in data['teachings']:
 rows.append(f'''<article id="{e(q['id'])}"><div class="number">{q['order']:02d}</div><div><blockquote>{e(q['quote'])}</blockquote><p class="author">{e(q['author'])}</p><p class="credit">{e(q['work'])} · Translation: {e(q['translator'])}</p><details><summary>Source & context</summary><p>{e(q.get('context_note',''))}</p><p>{e(q['locator'])}</p><a href="{e(q['url'])}" rel="noopener noreferrer">Read the original source ↗</a><p class="credit">Verified {e(q['verified_date'])}. Translation rights remain with their respective holders.</p></details><a class="permalink" href="#{e(q['id'])}" aria-label="Link to teaching {q['order']}">§</a></div></article>''')
media=json.loads((ROOT/'media.json').read_text())
media_rows=[]
for m in media['teachings']:
 video=''
 if m.get('youtube_id'):
  import re
  assert re.fullmatch(r'[A-Za-z0-9_-]{11}',m['youtube_id'])
  video=f'<details class="player"><summary>Play teaching here</summary><iframe loading="lazy" title="{e(m["speaker"]+": "+m["title"])}" src="https://www.youtube-nocookie.com/embed/{m["youtube_id"]}?start={m.get("timestamp_seconds") or 0}" allow="fullscreen; picture-in-picture" referrerpolicy="strict-origin-when-cross-origin" allowfullscreen></iframe></details>'
 media_rows.append(f'<article id="{e(m["id"])}"><div class="number">▶</div><div><p class="eyebrow">{e(m["speaker"])}</p><h2>{e(m["title"])}</h2><blockquote>{e(m["quote"])}</blockquote><p class="credit">{e(m["credit"])}</p><p>{e(m["context"])}</p><p><a href="{e(m["watch_url"])}">Watch the teaching ↗</a> · <a href="{e(m["transcript_url"])}">Read the transcript ↗</a></p>{video}<details><summary>About this excerpt</summary><p>{e(m["verification"])}</p><p>{e(m["locator"])}</p></details></div></article>')
related=''.join(f'<p><a href="{e(m["watch_url"])}">{e(m["title"])} ↗</a><br><span class="credit">{e(m["credit"])} {e(m["context"])}</span></p>' for m in media['related_recordings'])
media_section='<section id="watch"><div class="library-title"><strong>WATCH & LISTEN</strong><span>Words in their teaching context</span></div>'+''.join(media_rows)+'<h2>From Tulku Urgyen’s circle</h2>'+related+'</section>'
page='''<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><link rel="alternate" type="application/rss+xml" title="For All Beings" href="feed.xml"><title>For All Beings — A living Dharma library</title><meta name="description" content="Brief Buddhist teachings with exact wording, translator credits, and original sources."><link rel="icon" type="image/svg+xml" href="data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 32 32'%3E%3Crect width='32' height='32' rx='16' fill='%23112738'/%3E%3Ccircle cx='16' cy='16' r='9' fill='none' stroke='%23f4bd54' stroke-width='2'/%3E%3C/svg%3E"><style>
:root{color-scheme:light;--ink:#112738;--muted:#52616b;--accent:#925514}*{box-sizing:border-box}html{scroll-behavior:smooth}body{margin:0;background:#fafbfc;color:var(--ink);font:18px/1.7 system-ui,sans-serif}header,main,footer{max-width:960px;margin:auto;padding:32px}nav{display:flex;justify-content:space-between;gap:24px;border-bottom:1px solid #b8c4cc;padding-bottom:20px;font-size:14px}a{color:inherit;text-underline-offset:4px}h1{font:clamp(3rem,8vw,5.5rem)/1.04 Georgia,serif;letter-spacing:-.045em;margin:48px 0 24px;max-width:650px}header>p{max-width:580px;color:var(--muted)}.eyebrow{text-transform:uppercase;letter-spacing:.16em;font-size:13px}.intro{border-left:3px solid #edb64e;padding-left:20px}.library-title{display:flex;justify-content:space-between;gap:20px;padding:0 0 24px;font-size:14px;border-bottom:1px solid #b8c4cc}article{display:grid;grid-template-columns:48px 1fr;gap:24px;padding:38px 0;border-bottom:1px solid #c9d1d6;scroll-margin-top:24px}blockquote{font:clamp(1.4rem,3.3vw,2rem)/1.5 Georgia,serif;white-space:pre-line;margin:0 0 20px}.number{font:14px/2 monospace;color:var(--accent)}.author{font-weight:600;margin:0}.credit{font-size:14px;color:var(--muted);margin:8px 0 16px}summary{cursor:pointer;font-size:14px;color:var(--accent)}details{font-size:16px}details p{max-width:660px}.permalink{display:inline-block;font-size:14px;margin-top:12px;color:var(--muted)}footer{font-size:14px;color:var(--muted);padding-bottom:70px}footer h2{font-size:18px;color:var(--ink)}:focus-visible{outline:3px solid #bd7619;outline-offset:5px}@media(max-width:600px){header,main,footer{padding:24px}article{grid-template-columns:24px 1fr;gap:12px}nav{flex-wrap:wrap}h1{margin-top:32px}}@media print{details{display:block}nav,.permalink{display:none}article{break-inside:avoid}}
iframe{width:100%;aspect-ratio:16/9;border:0;margin:18px 0}.player{margin:20px 0}#watch{padding:28px 0 50px}#watch h2{font:1.6rem/1.3 Georgia,serif}#watch p{max-width:700px}</style></head><body><header><nav><strong>FOR ALL BEINGS</strong><span><a href="#teachings">Read</a> · <a href="#watch">Watch & listen</a> · <a href="feed.xml">RSS</a> · <a href="archive.json" download>Keep a copy</a> · <a href="https://github.com/gigachadmma69/dharma-for-all-beings">Open source</a></span></nav><h1>A few words.<br>A little less grasping.</h1><p class="intro">Teachings across Buddhist traditions, preserved in their translators’ words. Begin with care; take your time with what follows.</p></header><main id="teachings"><div class="library-title"><strong>THE READING SEQUENCE</strong><span>32 text passages · 2 video-linked excerpts</span></div>'''+media_section+''.join(rows)+'''</main><footer><h2>A library, not a measure of realization.</h2><p>This reading order is an editorial invitation: compassion, accessible practice, then subtler teachings on emptiness and awareness. Traditions differ. A brief passage does not replace its context, practice, or a teacher.</p><p>New selections enter only after source review. This edition was assembled on 28 September 2026. The website does not generate teachings or autonomously post to X; research and publishing are maintained separately.</p><p>Software is MIT-licensed. Quotations and translations are not relicensed: see <a href="RIGHTS.md">rights and attribution</a>. <a href="archive.json" download>Download the archive</a> to preserve it or help it find another home.</p></footer></body></html>'''
(ROOT/'dist').mkdir(exist_ok=True)
(ROOT/'dist/index.html').write_text(page)
(ROOT/'dist/archive.json').write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n')
(ROOT/'dist/media.json').write_text(json.dumps(media,ensure_ascii=False,indent=2)+'\n')
(ROOT/'dist/RIGHTS.md').write_text((ROOT/'RIGHTS.md').read_text())
assert len(rows)==len(data['teachings'])
print(f'Built {len(rows)} sourced teaching entries')

# Portable feed: stable IDs, source links, and no account-specific dependencies.
import xml.etree.ElementTree as ET
rss=ET.Element('rss',version='2.0');channel=ET.SubElement(rss,'channel')
origin='https://dharma-for-all-beings.hogpawg.chatgpt.site'
for name,value in [('title','For All Beings'),('link',origin),('description','Source-verified Buddhist teaching excerpts with full attribution.'),('language','en')]: ET.SubElement(channel,name).text=value
for q in data['teachings']:
 item=ET.SubElement(channel,'item')
 ET.SubElement(item,'title').text=q['author']+' — '+q['work']
 ET.SubElement(item,'link').text=origin+'/#'+q['id']
 ET.SubElement(item,'guid',isPermaLink='false').text=q['id']
 ET.SubElement(item,'description').text=q['quote']+'\n\n'+q['author']+'\nTranslation: '+q['translator']+'\n'+q['url']+'\n'+q.get('context_note','')
for m in media['teachings']:
 item=ET.SubElement(channel,'item')
 ET.SubElement(item,'title').text=m['speaker']+' — '+m['title']
 ET.SubElement(item,'link').text=m['watch_url']
 ET.SubElement(item,'guid',isPermaLink='false').text=m['id']
 ET.SubElement(item,'description').text=m['quote']+'\n\n'+m['credit']+'\n'+m['context']+'\nTranscript: '+m['transcript_url']
ET.indent(rss);ET.ElementTree(rss).write(ROOT/'dist/feed.xml',encoding='utf-8',xml_declaration=True)
assert len(ET.parse(ROOT/'dist/feed.xml').findall('./channel/item'))==len(data['teachings'])+len(media['teachings'])
