#!/usr/bin/env python3
"""Relê SVG/DXF, importa DXF no Inkscape e renderiza todos os pares.

Requer Inkscape com suas extensões Python, Python, Pillow e Matplotlib.
O leitor externo DXF é chamado com o Python do sistema. Nenhum arquivo de
corte é modificado. Previews têm área ajustada ao desenho, não são gabaritos.
"""
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor
import argparse
import hashlib
import json
import re
import shutil
import subprocess
import tempfile
import xml.etree.ElementTree as ET
import zipfile
from PIL import Image, ImageOps, ImageDraw, ImageFont, ImageFilter

ROOT=Path(__file__).resolve().parents[1]
NS='{http://www.w3.org/2000/svg}'


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


def bounds(e):
    if e['tipo']=='circulo':
        x,y=e['centro'];r=e['raio'];return [x-r,y-r,x+r,y+r]
    xs,ys=zip(*e['pontos']);return [min(xs),min(ys),max(xs),max(ys)]


def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--referencia-zip',type=Path)
    args=ap.parse_args()
    importer=Path('/usr/share/inkscape/extensions/dxf_input.py')
    assert shutil.which('inkscape') and importer.exists(),'Inkscape e importador DXF não encontrados.'
    out=ROOT/'05_GUIA/Conferencia_cortes';out.mkdir(exist_ok=True)
    files=sorted(p for folder in ['01_CORTE_PAINEIS','02_CHAPA_600x400','03_PECAS'] for p in (ROOT/folder).glob('*.svg'))
    assert len(files)==12
    reference=zipfile.ZipFile(args.referencia_zip) if args.referencia_zip else None
    reader=r'''
import sys,json
sys.path.insert(0,'/usr/share/inkscape/extensions')
import inkex
r=inkex.load_svg(sys.argv[1]).getroot()
paths=[p for g in r.xpath('//svg:g[@inkscape:groupmode="layer"]') for p in g.xpath('.//svg:path')]
sizes=[]
for p in paths:
 b=p.bounding_box();sizes.append([b.width*25.4/96,b.height*25.4/96])
print(json.dumps(sizes))
'''
    def run(svg):
        dxf=svg.with_suffix('.dxf')
        a=svg_entities(svg.read_text());b=dxf_entities(dxf.read_text())
        assert a==b,svg
        if reference:
            old=reference.read(str(dxf.relative_to(ROOT.parent))).decode('ascii')
            assert dxf_entities(old)==b,'Geometria alterada: '+str(dxf)
        prefix=svg.parent.name[:2]+'_'+svg.stem
        with tempfile.TemporaryDirectory(prefix='caixa_dxf_') as temp:
            imported=Path(temp)/'importado.svg'
            cmd=['/usr/bin/python3',str(importer),str(dxf),'--scalemethod=file','--gcodetoolspoints=false','--output='+str(imported)]
            proc=subprocess.run(cmd,capture_output=True,text=True)
            assert proc.returncode==0,(dxf,proc.stderr)
            read=subprocess.run(['/usr/bin/python3','-c',reader,str(imported)],capture_output=True,text=True)
            assert read.returncode==0,read.stderr
            sizes=json.loads(read.stdout)
            assert len(sizes)==len(b),(dxf,len(sizes),len(b))
            for size,entity in zip(sizes,b):
                x0,y0,x1,y1=bounds(entity)
                assert abs(size[0]-(x1-x0))<.00002 and abs(size[1]-(y1-y0))<.00002,(dxf,size,entity)
            previews={}
            for fmt,path in [('SVG',svg),('DXF',imported)]:
                png=out/f'{prefix}_{fmt}.png'
                proc=subprocess.run(['inkscape',str(path),'--export-type=png','--export-area-drawing',
                                     '--export-width=1200','--export-background=white','--export-background-opacity=1',
                                     '--export-filename='+str(png)],capture_output=True,text=True)
                assert proc.returncode==0 and png.exists(),proc.stderr
                img=Image.open(png).convert('RGB')
                gray=img.convert('L')
                ink=sum(n for value,n in enumerate(gray.histogram()) if value<220)
                assert ink>1000,(svg,fmt,ink)
                previews[fmt]=dict(arquivo=png.name,pixels_visiveis=ink)
        xs=[];ys=[]
        for e in b:
            x0,y0,x1,y1=bounds(e);xs.extend([x0,x1]);ys.extend([y0,y1])
        return dict(arquivo=str(svg.relative_to(ROOT)),contornos=len(b),
                    dimensoes_geometria_mm=[max(xs)-min(xs),max(ys)-min(ys)],
                    SVG_DXF_equivalentes=True,DXF_importado_no_Inkscape=True,
                    geometria_anterior_preservada=True if reference else None,
                    sha256_svg=hashlib.sha256(svg.read_bytes()).hexdigest(),
                    sha256_dxf=hashlib.sha256(dxf.read_bytes()).hexdigest(),previas=previews)
    with ThreadPoolExecutor(max_workers=3) as pool:report=list(pool.map(run,files))
    if reference:reference.close()
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    from matplotlib.backends.backend_pdf import PdfPages
    with PdfPages(ROOT/'05_GUIA/Conferencia_SVG_DXF.pdf') as pdf:
        for start in range(0,len(report),2):
            fig,axes=plt.subplots(2,2,figsize=(11.69,8.27))
            for row,item in enumerate(report[start:start+2]):
                for col,fmt in enumerate(['SVG','DXF']):
                    ax=axes[row,col];im=Image.open(out/item['previas'][fmt]['arquivo'])
                    # Margem de exibição: só na prévia, sem alterar o arquivo de corte.
                    im=im.convert('L').point(lambda v:0 if v<248 else 255)
                    im=im.filter(ImageFilter.MinFilter(3))
                    im=ImageOps.expand(im,border=30,fill='white')
                    ax.imshow(im,cmap='gray',vmin=0,vmax=255,interpolation='antialiased');ax.axis('off')
                    name=Path(item['arquivo']).stem
                    ax.set_title(f'{fmt} • {name}\n{item["contornos"]} contorno(s) • importação e renderização conferidas',fontsize=9)
            fig.suptitle('Conferência visual dos arquivos reais — SVG e DXF',fontsize=17,y=.96)
            fig.text(.05,.025,'Prévias com contraste reforçado, sem escala de impressão. Painéis: 500 × 380 mm. Cortar pelos eixos vetoriais.',fontsize=8)
            fig.subplots_adjust(left=.03,right=.97,bottom=.07,top=.87,hspace=.35,wspace=.08)
            pdf.savefig(fig);plt.close(fig)
    # Contato das nove peças, renderizadas diretamente dos SVG finais.
    items=[r for r in report if r['arquivo'].startswith('03_PECAS/')]
    canvas=Image.new('RGB',(1200,900),'#edf0f2')
    font=ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',17)
    for i,item in enumerate(items):
        tile=Image.new('RGB',(390,285),'white')
        img=Image.open(out/item['previas']['SVG']['arquivo']).convert('RGB')
        img=ImageOps.contain(img,(350,210))
        # A redução da prévia não pode apagar os traços subpixel. Contraste
        # reforçado somente na imagem de apresentação, nunca no vetor de corte.
        img=img.convert('L').point(lambda v:0 if v<248 else 255).convert('RGB')
        tile.paste(img,((390-img.width)//2,20+(210-img.height)//2))
        draw=ImageDraw.Draw(tile)
        draw.text((15,238),Path(item['arquivo']).stem,fill='#203340',font=font)
        w,h=item['dimensoes_geometria_mm']
        draw.text((15,262),f'{w:g} × {h:g} mm',fill='#203340',font=font)
        canvas.paste(tile,((i%3)*400+5,(i//3)*300+5))
    canvas.save(ROOT/'05_GUIA/Previa_dos_cortes.png')
    final=dict(pares_conferidos=len(report),leitor_independente='Importador DXF do Inkscape 1.1.2, unidades do arquivo (mm)',
               correcao='SVG: traço preto explícito 0,35 mm. DXF: seções HEADER/TABLES/BLOCKS/ENTITIES e camada CORTE visível.',
               limites='Prévias sem escala física. Todos os contornos de corte permanecem nas coordenadas originais.',arquivos=report)
    (ROOT/'05_GUIA/CONFERENCIA_SVG_DXF.json').write_text(json.dumps(final,indent=2,ensure_ascii=False))
    print(f'{len(report)} pares equivalentes; {sum(x["contornos"] for x in report)} contornos importados; 24 renderizações visíveis.')


if __name__=='__main__':main()
