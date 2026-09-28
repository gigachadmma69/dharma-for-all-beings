"""Prepare the independently hosted, credential-free GitHub Pages mirror."""
import pathlib, shutil, xml.etree.ElementTree as ET
ROOT = pathlib.Path(__file__).resolve().parents[1]
SOURCE_ORIGIN = 'https://dharma-for-all-beings.hogpawg.chatgpt.site'
MIRROR_ORIGIN = 'https://gigachadmma69.github.io/dharma-for-all-beings'
FILES = ('index.html', 'archive.json', 'media.json', 'RIGHTS.md', 'feed.xml')

def prepare():
    target = ROOT / 'docs'
    target.mkdir(exist_ok=True)
    for name in FILES:
        source = ROOT / 'dist' / name
        if name == 'feed.xml':
            tree = ET.parse(source)
            for link in tree.findall('.//link'):
                if link.text and (link.text == SOURCE_ORIGIN or link.text.startswith(SOURCE_ORIGIN + '/')):
                    link.text = MIRROR_ORIGIN + link.text[len(SOURCE_ORIGIN):]
            tree.write(target / name, encoding='utf-8', xml_declaration=True)
        else:
            shutil.copyfile(source, target / name)
    (target / '.nojekyll').write_text('')
    for name in FILES[:-1]:
        assert (target / name).read_bytes() == (ROOT / 'dist' / name).read_bytes()
    original = ET.parse(ROOT / 'dist/feed.xml')
    mirrored = ET.parse(target / 'feed.xml')
    assert [e.text for e in original.findall('.//guid')] == [e.text for e in mirrored.findall('.//guid')]
    assert mirrored.findtext('./channel/link') == MIRROR_ORIGIN
    assert SOURCE_ORIGIN not in (target / 'feed.xml').read_text()
    print('Mirror prepared: identical content, stable feed IDs, mirror-local reading links.')

if __name__ == '__main__':
    prepare()
