"""Leitores independentes dos arquivos SVG e DXF de fabricação."""
import re
import xml.etree.ElementTree as ET
NS="{http://www.w3.org/2000/svg}"


def dxf_entities(raw):
    lines=raw.splitlines()
    assert len(lines)%2==0
    pairs=list(zip(lines[::2],lines[1::2]))
    assert pairs[pairs.index(('9','$INSUNITS'))+1]==('70','4')
    current=[];entities=[];active=False
    for i,(key,val) in enumerate(pairs):
        if key=='2' and val=='ENTITIES' and pairs[i-1]==('0','SECTION'):
            active=True;continue
        if active and key=='0':
            if current:entities.append(current)
            current=[]
            if val=='ENDSEC':break
            current=[(key,val)]
        elif active and current:current.append((key,val))
    result=[]
    for e in entities:
        if e[0][1]=='LWPOLYLINE':
            assert ('70','1') in e
            pts=[[float(v),float(e[i+1][1])] for i,(k,v) in enumerate(e) if k=='10' and e[i+1][0]=='20']
            assert len(pts)==int(next(v for k,v in e if k=='90'))
            result.append(dict(tipo='poligono',pontos=pts))
        elif e[0][1]=='CIRCLE':
            get=lambda code:float(next(v for k,v in e if k==code))
            result.append(dict(tipo='circulo',centro=[get('10'),get('20')],raio=get('40')))
        else:raise AssertionError(e[0])
    assert result
    return result


def svg_entities(raw):
    root=ET.fromstring(raw)
    assert root.attrib['width'].endswith('mm') and root.attrib['height'].endswith('mm')
    height=float(root.attrib['height'][:-2])
    result=[]
    for elem in root.iter():
        if elem.tag not in (NS+'path',NS+'circle'):continue
        assert elem.attrib['stroke']=='#000000' and elem.attrib['fill']=='none'
        assert float(elem.attrib['stroke-width'])>=.35
        if elem.tag==NS+'path':
            assert elem.attrib['d'].endswith(' Z')
            nums=list(map(float,re.findall(r'-?\d+(?:\.\d+)?',elem.attrib['d'])))
            pts=[[nums[i],round(height-nums[i+1],6)] for i in range(0,len(nums),2)]
            result.append(dict(tipo='poligono',pontos=pts))
        else:
            result.append(dict(tipo='circulo',centro=[float(elem.attrib['cx']),round(height-float(elem.attrib['cy']),6)],raio=float(elem.attrib['r'])))
    assert result
    return result
