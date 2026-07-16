from pathlib import Path
from zipfile import ZipFile
import sys
from lxml import etree

W='http://schemas.openxmlformats.org/wordprocessingml/2006/main'
q=lambda n:f'{{{W}}}{n}'
with ZipFile(Path(sys.argv[1])) as z:
    num=etree.fromstring(z.read('word/numbering.xml'))
    doc=etree.fromstring(z.read('word/document.xml'))
abstract={a.get(q('abstractNumId')):(a.find('.//w:numFmt',{'w':W}).get(q('val')),a.find('.//w:lvlText',{'w':W}).get(q('val'))) for a in num.findall(q('abstractNum'))}
mapping={n.get(q('numId')):n.find(q('abstractNumId')).get(q('val')) for n in num.findall(q('num'))}
print('NUMS',[(k,mapping[k],abstract.get(mapping[k])) for k in sorted(mapping,key=int)])
for p in doc.xpath('.//w:p[w:pPr/w:numPr]',namespaces={'w':W}):
    nid=p.xpath('string(w:pPr/w:numPr/w:numId/@w:val)',namespaces={'w':W})
    text=''.join(p.xpath('.//w:t/text()',namespaces={'w':W}))[:90]
    print(nid,mapping.get(nid),abstract.get(mapping.get(nid)),text)
