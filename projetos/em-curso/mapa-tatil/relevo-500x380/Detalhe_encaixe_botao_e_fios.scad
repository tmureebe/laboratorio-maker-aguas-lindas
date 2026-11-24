/* DETALHE DE INSPEÇÃO — encaixe KFC-A06, apoio impresso e duas soldas.
Unidades: mm. z=0 é a face superior do MDF, como no mapa.
Geometria impressa: recorte das peças reais de construcoes_vista_aerea.scad.
As cotas dos terminais vêm do modelo nominal; conferir no botão físico.
Fios e gotas de solda são envelopes editáveis para examinar o espaço.
Vermelho indica interseção REAL desses envelopes com plástico ou MDF.
O MDF tem quatro furos de 2,6 mm, um sob cada terminal; sem furo central.
Terminais e soldas ficam no impresso; os fios descem alinhados. Soldar antes de encaixar.
Uma cavidade de 15,3 x 12,5 mm sobe pela face inferior ate 1,2 mm abaixo do corpo.
Para acesso com o botao montado no relevo, usar mostrar_mdf=false e mostrar_ponta_ferro=true.
Este arquivo é para inspeção e não altera as peças de fabricação.

F5: cores e transparências. F6: geometria, sem transparência.
"explodida": botão e fios sobem juntos; verde mostra a face que apoia o corpo.
"soldagem": retira o botão do encaixe e mostra a aproximação do ferro.
Não há trava/adesivo neste encaixe: o assento suporta a pressão, mas não
impede o botão de sair por cima. A ponta do ferro é apenas referência.
Os dois terminais escolhidos são os da fileira y=-2,5, lados x opostos.
Confirmar com multímetro que são contatos distintos antes de soldar.
*/
/* [Inspecao] */
vista="corte"; // [montada,corte,explodida,inferior,soldagem]
numero_botao=4; // [1:18]
mostrar_mdf=true;
mostrar_fios=true;
mostrar_soldas=true;
mostrar_interferencias=true;
mostrar_face_apoio=true;
mostrar_ponta_ferro=false;
transparencia_suporte=0.55; // [0.1:0.05:1]
/* [Envelopes editaveis - conferir na montagem real] */
diametro_fio_isolado=1.4;
diametro_condutor=0.5;
// Diâmetro do envelope de solda; não é cota garantida do processo.
diametro_solda=2;
altura_solda=1.6;
diametro_ponta_ferro=3;
altura_explosao=22;
/* [Hidden] */
$fn=48;
verificacao="nenhuma";
use <construcoes_vista_aerea.scad>
use <botao_tatil_KFC-A06_12x12x4p3.scad>
dados_botoes=[[1, "Entrada principal", 153.667, 45.333, 5.0], [2, "Estacionamento", 108.667, 92.0, 5.0], [3, "Bicicletário", 217.0, 92.0, 5.0], [4, "DAA", 205.333, 135.333, 13.033], [5, "Biblioteca - 2º andar", 237.0, 122.0, 13.033], [6, "GEPEX", 155.333, 138.667, 13.033], [7, "Centro de seleção audiovisual", 133.667, 138.667, 13.033], [8, "CORAE", 112.0, 138.667, 13.033], [9, "UBS", 90.333, 138.667, 13.033], [10, "Administração - 2º andar", 117.0, 122.0, 13.033], [11, "Quadra", 315.333, 200.333, 16.367], [12, "Restaurante", 119.167, 283.667, 8.367], [13, "Bloco acadêmico / ensino", 182.0, 258.667, 13.033], [14, "Laboratórios", 188.5, 290.333, 13.033], [15, "Refeitório", 172.0, 290.333, 13.033], [16, "Pátio", 190.333, 328.667, 13.033], [17, "Auditório", 172.833, 328.667, 13.033], [18, "Saída", 181.167, 342.5, 13.033]];

apoios=[-1,-2,-3,0,0,0,0,0,0,0,3,2,1,1,1,1,1,1];
b=dados_botoes[numero_botao-1];
centro=[b[2],b[3]];
h=b[4];
apoio=apoios[numero_botao-1];
z_terminal=h-3.5;
dz=(vista=="explodida"||vista=="soldagem")?altura_explosao:0;
assert(numero_botao>=1 && numero_botao<=18 && floor(numero_botao)==numero_botao);
assert(diametro_fio_isolado>diametro_condutor && diametro_condutor>0);
assert(diametro_solda>0 && altura_solda>0 && altura_explosao>0);
echo(botao=numero_botao,nome=b[1],base_corpo_z_mm=h,ponta_terminal_z_mm=z_terminal);
lado_rasgo=lado_rasgo_terminal_mm();
echo(rasgo_terminal_mm=[lado_rasgo,lado_rasgo],fio_isolado_mm=diametro_fio_isolado,solda_envelope_mm=[diametro_solda,diametro_solda,altura_solda]);
if(diametro_solda>lado_rasgo) echo("ATENCAO: envelope da solda maior que a largura do rasgo. Verificar vermelho em montada/corte.");

// Trecho real da peça, sem redesenhar um alojamento idealizado.
module suporte_real() {
 intersection() {
  translate([-centro[0],-centro[1],0])
   if(apoio>=0) edificio_tatil(apoio); else piso_tatil(-apoio-1);
  translate([-10,-10,-.01]) cube([20,20,35]);
 }
}
module mdf_real() {
 difference() {
  translate([-11,-11,-3]) cube([22,22,3]);
  translate([0,0,-3.1]) linear_extrude(3.2) passagem_cabos_painel_2d();
 }
}
module cortes_visuais() {
 if(vista=="corte") difference() {
  children();translate([-30,.3,-40]) cube([60,60,100]);
 } else children();
}
module face_apoio() {
 // Seção da peça imediatamente abaixo da base do corpo, limitada à sua planta.
 translate([0,0,h-.015]) linear_extrude(.025)
 intersection() {
  quadrado_chanfrado(12,.55);
  projection(cut=true) translate([0,0,-h+.02]) suporte_real();
 }
}
module segmento(a,b,r) {
 d=b-a;
 translate(a) rotate([0,acos(d[2]/norm(d)),atan2(d[1],d[0])]) cylinder(h=norm(d),r=r,$fn=20);
}
module caminho(p,r) {
 for(i=[0:len(p)-2]) segmento(p[i],p[i+1],r);
 for(q=p) translate(q) sphere(r=r,$fn=20);
}
module soldas() {
 for(s=[-1,1]) translate([s*6.25,-2.5,z_terminal+.2])
  scale([diametro_solda/2,diametro_solda/2,altura_solda/2]) sphere(r=1);
}
module fios(cores=true) {
 // Junta acima do MDF; descida pelo furo individual alinhado ao terminal.
 for(s=[-1,1]) {
  color(cores?"#b77a39":"red")
   caminho([[s*6.25,-2.5,z_terminal+.3],[s*6.25,-2.5,z_terminal-.3]],diametro_condutor/2);
  color(cores?(s<0?"#ef7a23":"#272a30"):"red")
   caminho([[s*6.25,-2.5,z_terminal-.4],
            [s*6.25,-2.5,-7],[s*7,-7,-10]],diametro_fio_isolado/2);
 }
}

module interferencias() {
 // Checagem na posição MONTADA, com suporte inteiro, independente da vista escolhida.
 intersection() {
  union() {suporte_real();if(mostrar_mdf) mdf_real();}
  union() {if(mostrar_soldas) soldas();if(mostrar_fios) fios(false);}
 }
}
module ponta_ferro(s=-1,y=-2.5) {
 // Aproximacao inferior inclinada para o centro da cavidade, com o MDF removido.
 translate([s*6.25,y,z_terminal-altura_solda/2-.2]) rotate([0,s*15,0]) rotate([180,0,0]) {
  color("#9fa5ad") cylinder(h=5,r1=.3,r2=diametro_ponta_ferro/2);
  color("#52565a") translate([0,0,5]) cylinder(h=8,r=diametro_ponta_ferro/2);
 }
}
module detalhe() {
 color([.28,.62,.78,transparencia_suporte]) cortes_visuais() suporte_real();
 if(mostrar_mdf) color([.73,.55,.31,transparencia_suporte]) cortes_visuais() mdf_real();
 if(mostrar_face_apoio) color("#53d25b") cortes_visuais() face_apoio();
 translate([0,0,dz]) {
  translate([0,0,h]) botao_kfc_a06(com_terminais=true);
  if(mostrar_soldas) color("#b6b9bf") soldas();
  if(mostrar_fios) fios();
  if(mostrar_ponta_ferro||vista=="soldagem") ponta_ferro();
 }
 // Na explodida a solda sobe com o botão: a posição de inspeção não é a montagem.
 if(mostrar_interferencias && dz==0) color("red") cortes_visuais() interferencias();
}
if(verificacao=="interferencias") interferencias();
else if(verificacao=="acesso_ferro") intersection() {
 suporte_real();
 union() for(s=[-1,1],y=[-2.5,2.5]) ponta_ferro(s,y);
}
else if(verificacao=="assento") face_apoio();
else detalhe();
$vpt=[0,0,h/2-2];
$vpr=vista=="inferior"?[145,0,25]:[68,0,30];
$vpd=95;
