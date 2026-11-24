/*
MAPA TATIL 500 x 380 mm — revisao 2026-10-29.
Referencia funcional: planta_empirica_campus_posicao_botoes.pdf (sem escala).
Contornos e posicoes relativas dos edificios/passarelas preservados do CAD.
Implantacao reduzida UNIFORMEMENTE a 1:600; nao ha compressao de um eixo.
Rampas, escadas e ambientes internos: representacoes esquematicas da planta.
Unidade de saida: mm. Origem no canto inferior esquerdo; entrada embaixo.
Revisao de soldagem: canais 2,8 x 2,8 mm; pontos 14/15 afastados 0,5 mm cada
para preservar pelo menos 1,2 mm entre canais. Soldar antes de encaixar.
Os 18 alojamentos recebem a chave KFC-A06 de 12 x 12 x 4,3 mm.
Por baixo, cavidades de 15,3 x 12,5 mm liberam o acesso as quatro soldas.
Terminais e soldas ficam nas pecas impressas; apenas os fios atravessam o MDF.
O painel de MDF tem quatro furos de 2,6 mm por botao, alinhados aos terminais.
Os botoes usam o modelo externo, visivel apenas em F5;
nao sao mecanismos impressos e nao integram as exportacoes STL.
A saida (18) foi deslocada 2,5 mm para norte para separar os corpos quadrados.
A copia anterior foi preservada em revisao_500x380/original/.
*/

use <botao_tatil_KFC-A06_12x12x4p3.scad>

/* [Exibicao e exportacao] */
modo = "maquete"; // [maquete,peca,gabarito,furacao]
tipo_peca = "edificio"; // [edificio,passagem,piso,rampa,escada,legenda,painel]
numero_peca = 0;
mostrar_painel = true;
mostrar_botoes = true;
mostrar_numeros = true;
mostrar_escadas = true;
quadra_aberta = false;

/* [Painel e implantacao] */
painel_largura_mm = 500;
painel_profundidade_mm = 380;
espessura_painel_mm = 3;
escala_denominador = 600;
// Posicao deixa os 18 eixos livres das nervuras x=250, y=110 e y=240
// definidas na caixa existente; o contorno CAD continua sem deformacao.
origem_mapa = [17,37];
base_peca_mm = 2;
altura_passagem_mm = 5;
folga_montagem_mm = 0.25;

/* [Botoes KFC-A06 - medidas em mm, sem escala do mapa] */
// Mesmas cotas do modelo botao_tatil_KFC-A06_12x12x4p3.scad.
lado_corpo_botao_mm = 12;
altura_corpo_botao_mm = 3.5;
altura_total_botao_mm = 4.3;
passo_terminais_x_mm = 12.5;
passo_terminais_y_mm = 5;
largura_terminal_mm = 1;
espessura_terminal_mm = 0.3;
avanco_dobra_terminal_mm = 0.42;
// Folga POR LADO, tambem nos rasgos dos terminais.
folga_botao_mm = 0.25;
// Soldar fora da peca e passar a junta pronta pelo canal.
// Envelope de solda de 2 mm com 0,4 mm de folga por lado.
largura_canal_solda_mm = 2.8;
// Altura minima livre por baixo do assento; a cavidade sobe ate ele.
altura_canal_cabos_mm = 2.6;
// Nos pisos baixos, manter terminais e soldas inteiramente acima do MDF.
altura_minima_base_botao_mm = 5;
parede_apoio_botao_mm = 1.2;
espessura_assento_botao_mm = 1.2;
// O assento sob o corpo e fechado no centro; apenas os terminais o atravessam.
// Quatro passagens independentes no MDF, nas coordenadas dos terminais.
diametro_furo_fio_painel_mm = 2.6;
// Altura minima da borda acima do relevo; nos pisos baixos, sobe o necessario
// para manter 1,2 mm de fundo sob o corpo. O atuador fica 0,8 mm acima dela.
altura_aro_botao_mm = 1.2;

/* [Relevos] */
h_blocos_m = 8;
h_restaurante_m = 4;
h_quadra_m = 8;
flecha_restaurante_m = 1.2;
flecha_quadra_m = 2;
altura_numero_mm = 0.7;
tamanho_numero_mm = 3.5;
diametro_braille_mm = 1.6;
altura_braille_mm = 0.7;

/* [Hidden] */
$fn = 48;
eps = 0.02;
fator_mapa = 1000/escala_denominador;
lado_alojamento_botao_mm = lado_corpo_botao_mm+2*folga_botao_mm;
inicio_canal_terminal_x_mm = passo_terminais_x_mm/2-largura_canal_solda_mm/2;
limite_terminal_x_mm = passo_terminais_x_mm/2+largura_canal_solda_mm/2;
// Acesso pela face inferior, com paredes e assento de pelo menos 1,2 mm.
tamanho_acesso_solda_mm = [
    max(lado_alojamento_botao_mm,passo_terminais_x_mm+largura_canal_solda_mm),
    lado_alojamento_botao_mm];
// As paredes envolvem tambem a dobra externa dos terminais.
tamanho_apoio_botao_mm = tamanho_acesso_solda_mm +
    [2*parede_apoio_botao_mm,2*parede_apoio_botao_mm];
// [nome, contorno CAD em m, altura em m, flecha do telhado em m].
// Indices: 0 administrativo (sul); 1 ensino (oeste); 2 restaurante; 3 quadra.
edificios = [
 ["Bloco administrativo",[[217.6272, 100.7502], [217.6948, 120.3727], [176.5253, 120.9273], [176.537, 118.1769], [169.9834, 118.2652], [169.9718, 121.0156], [112.4344, 121.7906], [112.3668, 102.1682], [162.5638, 101.492], [162.5437, 100.0023], [172.2428, 99.8717], [172.2629, 101.3613]],h_blocos_m,0],
 ["Bloco de ensino",[[184.129, 240.6027], [162.9293, 240.4811], [163.1561, 200.9318], [165.7561, 200.9467], [165.9006, 175.7471], [181.9003, 175.8389], [181.6732, 215.4382], [184.2732, 215.4531]],h_blocos_m,0],
 ["Restaurante",[[124.8022, 227.7853], [147.8021, 227.7278], [147.701, 187.253], [124.701, 187.3105]],h_restaurante_m,flecha_restaurante_m],
 ["Quadra poliesportiva",[[269.2322, 180.1107], [238.9713, 180.4327], [238.7024, 132.903], [268.8335, 132.5693]],h_quadra_m,flecha_quadra_m]
];

// Somente as quatro passagens presentes na planta.
passagens = [
 ["Passarela longitudinal",[[176.2922, 175.8067], [169.7392, 175.7691], [169.9718, 121.0156], [176.5253, 120.9273]]],
 ["Passarela junto ao restaurante",[[151.8912, 240.6027], [151.8912, 246.8632], [154.8912, 246.8651], [154.8956, 173.3195], [151.8912, 173.3195]]],
 ["Passarela transversal restaurante - quadra",[[137.1068, 187.2795], [137.1068, 170.3195], [238.7139, 170.3195], [238.7139, 173.3195], [140.1068, 173.3195], [140.1068, 187.272]]],
 ["Acesso da entrada ao bloco administrativo",[[156.1008, 73.1038], [160.0971, 74.6314], [160.0971, 85.2857], [170.5132, 99.895], [165.6474, 99.9605], [156.1008, 86.5709]]]
];

// [nome, canto inferior esquerdo CAD, tamanho CAD].
pisos = [
 ["Entrada principal",[149,51],[16,17]],
 ["Estacionamento",[115,78],[35,18]],
 ["Bicicletario",[177,78],[39,18]]
];

// [numero, nome, Braille, centro CAD, apoio, deslocamento do numero em mm].
// Apoios 0..3: edificios; -1/-2/-3: pisos 0/1/2.
// A planta determina a relacao entre os setores, nao medidas internas.
referencias = [
 [1,"Entrada principal","entrada",[157,60],-1,[0,-10]],
 [2,"Estacionamento","estacionamento",[130,88],-2,[0,-10]],
 [3,"Bicicletário","bicicletário",[195,88],-3,[0,-10]],
 [4,"DAA","daa",[188,114],0,[0,-10]],
 [5,"Biblioteca - 2º andar","biblioteca",[207,106],0,[-12,0]],
 [6,"GEPEX","gepex",[158,116],0,[0,-10]],
 [7,"Centro de seleção audiovisual","seleção audiovisual",[145,116],0,[0,-10]],
 [8,"CORAE","corae",[132,116],0,[0,-10]],
 [9,"UBS","ubs",[119,116],0,[0,-10]],
 [10,"Administração - 2º andar","administração",[135,106],0,[-12,0]],
 [11,"Quadra","quadra",[254,153],3,[0,-10]],
 [12,"Restaurante","restaurante",[136.3,203],2,[0,-10]],
 [13,"Bloco acadêmico / ensino","ensino",[174,188],1,[0,-10]],
 [14,"Laboratórios","laboratórios",[177.9,207],1,[0,-10]],
 [15,"Refeitório","refeitório",[168.0,207],1,[0,-10]],
 [16,"Pátio","pátio",[179,230],1,[0,-10]],
 [17,"Auditório","auditório",[168.5,230],1,[0,-10]],
 [18,"Saída","saída",[173.5,238.3],1,[-12,0]]
];

// [canto inferior esquerdo CAD, tamanho CAD, edificio de apoio, direcao].
escadas = [
 [[163.5,106.5],[8,10],0,0],
 [[175.5,216],[8,7],1,90]
];

function xy_mm(v) = origem_mapa+(v-[75,55])*fator_mapa;
function pontos_mm(p) = [for(v=p) xy_mm(v)];
function limites(p) = [min([for(v=p)v[0]]),min([for(v=p)v[1]]),
                      max([for(v=p)v[0]]),max([for(v=p)v[1]])];
function h_edificio(i) = (i==3 && quadra_aberta) ? base_peca_mm :
                         base_peca_mm+edificios[i][2]*fator_mapa;
function flecha(i) = (i==3 && quadra_aberta) ? 0 : edificios[i][3]*fator_mapa;
function h_topo(i) = h_edificio(i)+flecha(i);
function h_apoio(r) = r[4]>=0 ? h_topo(r[4]) : base_peca_mm;
// Origem do modelo real: centro da face inferior do corpo.
function h_botao(r) = max(altura_minima_base_botao_mm,
                         altura_canal_cabos_mm+espessura_assento_botao_mm,
                         h_apoio(r)+altura_aro_botao_mm-altura_corpo_botao_mm);
function h_borda_botao(r) = h_botao(r)+altura_corpo_botao_mm;
function indice_piso(r) = -r[4]-1;
function lado_rasgo_terminal_mm() = largura_canal_solda_mm;

module planta_edificio(i) { polygon(pontos_mm(edificios[i][1])); }
module planta_piso(i) {
    translate(xy_mm(pisos[i][1])) square(pisos[i][2]*fator_mapa);
}

// Telhado de duas aguas recortado pelo contorno original.
module telhado(p,h) {
    l=limites(p); a=l[0]; b=l[2]; c=l[1]; d=l[3];
    longo_x=(b-a)>=(d-c);
    vertices=longo_x ?
        [[a,c,0],[b,c,0],[b,d,0],[a,d,0],[a,(c+d)/2,h],[b,(c+d)/2,h]] :
        [[a,c,0],[b,c,0],[b,d,0],[a,d,0],[(a+b)/2,c,h],[(a+b)/2,d,h]];
    faces=longo_x ?
        [[3,2,1,0],[0,1,5,4],[1,2,5],[2,3,4,5],[3,0,4]] :
        [[3,2,1,0],[0,1,4],[1,2,5,4],[2,3,5],[3,0,4,5]];
    intersection() {
        polyhedron(points=vertices,faces=faces,convexity=10);
        linear_extrude(h+eps) polygon(p);
    }
}

module rasgos_terminais_2d() {
    x_interno = inicio_canal_terminal_x_mm;
    for(sinal=[-1,1], y=[-passo_terminais_y_mm/2,passo_terminais_y_mm/2])
        scale([sinal,1])
            translate([x_interno,y-largura_canal_solda_mm/2])
                square([limite_terminal_x_mm-x_interno,
                        largura_canal_solda_mm]);
}
// Quatro circulos atravessam o MDF; nenhum furo no centro do botao.
module passagem_cabos_painel_2d() {
    for(x=[-passo_terminais_x_mm/2,passo_terminais_x_mm/2],
        y=[-passo_terminais_y_mm/2,passo_terminais_y_mm/2])
        translate([x,y]) circle(d=diametro_furo_fio_painel_mm);
}

// Abertura ampla por baixo do botao e dos quatro terminais.
// A tampa removida permite soldar pela face inferior antes de colar o relevo.
module acesso_solda_inferior_2d() {
    square(tamanho_acesso_solda_mm,center=true);
}
module furos_cabos_painel() {
    for(r=referencias) translate(concat(xy_mm(r[3]),[-espessura_painel_mm-1]))
        linear_extrude(espessura_painel_mm+2) passagem_cabos_painel_2d();
}
module alojamento_corpo_2d() {
    square([lado_alojamento_botao_mm,lado_alojamento_botao_mm],center=true);
    rasgos_terminais_2d();
}

// O corpo entra por cima e repousa no fundo; os quatro rasgos laterais
// acomodam as laminas e suas dobras sem cortar o assento inteiro.
module furos_botoes(apoio=undef) {
    altura_corte=espessura_painel_mm+max([for(i=[0:3])h_topo(i)])+
                 altura_corpo_botao_mm+altura_aro_botao_mm+20;
    for(r=referencias) if(is_undef(apoio) || r[4]==apoio) {
        q=xy_mm(r[3]);
        translate([q[0],q[1],-espessura_painel_mm-1])
            linear_extrude(altura_corte) rasgos_terminais_2d();
        translate([q[0],q[1],h_botao(r)])
            linear_extrude(altura_corte) alojamento_corpo_2d();
        translate([q[0],q[1],-eps])
            linear_extrude(h_botao(r)-espessura_assento_botao_mm+eps)
                acesso_solda_inferior_2d();
    }
}

module apoios_e_numeros(apoio) {
    for(r=referencias) if(r[4]==apoio) {
        q=xy_mm(r[3]);
        base_apoio=apoio>=0 ? h_edificio(apoio) : base_peca_mm;
        // Apoio desde Z=0: as bordas proximas ao contorno do edificio
        // tambem possuem fundo, sem abas suspensas. Assento horizontal
        // mesmo sobre telhados; apoios vizinhos podem compartilhar parede.
        translate([q[0],q[1],0])
            linear_extrude(h_borda_botao(r))
                square(tamanho_apoio_botao_mm,center=true);
        if(mostrar_numeros)
            translate([q[0]+r[5][0],q[1]+r[5][1],base_apoio-eps])
                linear_extrude((apoio>=0 ? flecha(apoio) : 0)+altura_numero_mm+eps)
                    text(str(r[0]),size=tamanho_numero_mm,
                         font="Liberation Sans:style=Bold",halign="center",valign="center");
    }
}

// Divisorias de ambiente em baixo relevo, respeitando os pares da planta.
// Nao alteram o contorno CAD nem representam paredes medidas.
module linhas_setores(i) {
    if(i==1) {
        for(y=[198,216,224,234])
            translate(xy_mm([160,y])) square([30*fator_mapa,0.6]);
        translate(xy_mm([173,198])) square([0.6,18*fator_mapa]);
        translate(xy_mm([173.8,224])) square([0.6,10*fator_mapa]);
    }
    if(i==0) {
        for(x=[125.5,138.5,151.5,162.2])
            translate(xy_mm([x,111])) square([0.5,12*fator_mapa]);
        translate(xy_mm([112,110])) square([50*fator_mapa,0.5]);
    }
}
module edificio_tatil(i) {
    difference() {
        union() {
            difference() {
                linear_extrude(h_edificio(i)) planta_edificio(i);
                if(i==0 || i==1)
                    translate([0,0,h_edificio(i)-0.5])
                        linear_extrude(0.5+eps) linhas_setores(i);
            }
            if(flecha(i)>0)
                translate([0,0,h_edificio(i)-eps])
                    telhado(pontos_mm(edificios[i][1]),flecha(i)+eps);
            if(i==3 && quadra_aberta) {
                translate([0,0,base_peca_mm-eps])
                    linear_extrude(1.2) difference() {
                        planta_edificio(i); offset(delta=-1.6) planta_edificio(i);
                    }
            }
            apoios_e_numeros(i);
        }
        furos_botoes(i);
    }
}

module rede_passagens_2d() {
    difference() {
        union() for(k=[0:2]) polygon(pontos_mm(passagens[k][1]));
        for(i=[0:3]) offset(delta=folga_montagem_mm) planta_edificio(i);
    }
}
// Tres pecas conectadas: rede central, continuacao norte e acesso da entrada.
module planta_passagem(k) {
    corte=xy_mm([75,188])[1];
    if(k<2) intersection() {
        rede_passagens_2d();
        if(k==0) translate([-1000,-1000]) square([2000,1000+corte-0.15]);
        else translate([-1000,corte+0.15]) square([2000,1000]);
    }
    else difference() {
        union() {
            polygon(pontos_mm(passagens[3][1]));
            // Prolongamento do acesso apos retirar a guarita ausente na planta.
            polygon(pontos_mm([[156.1008,67],[160.0971,67],
                              [160.0971,74.6314],[156.1008,73.1038]]));
        }
        for(i=[0:3]) offset(delta=folga_montagem_mm) planta_edificio(i);
        for(i=[0:2]) offset(delta=folga_montagem_mm) planta_piso(i);
    }
}
module passagem_tatil(k) {
    difference() {
        linear_extrude(altura_passagem_mm) planta_passagem(k);
        furos_botoes();
    }
}
module piso_tatil(k) {
    difference() {
        union() {
            linear_extrude(base_peca_mm) planta_piso(k);
            apoios_e_numeros(-k-1);
            // Textura nas bordas, deixando livres botoes e numeros.
            if(k==1) for(x=[4:8:32])
                translate(concat(xy_mm(pisos[k][1])+[x*fator_mapa,1.5],[base_peca_mm-eps]))
                    cube([1.2,5,0.7+eps]);
            if(k==2) for(y=[3:4:15])
                translate(concat(xy_mm(pisos[k][1])+[36*fator_mapa,y*fator_mapa],[base_peca_mm-eps]))
                    cylinder(d=2.4,h=0.7+eps);
        }
        furos_botoes(-k-1);
    }
}

// Rampa em U a DIREITA do ensino, com duas pernas inclinadas e patamares.
// As alturas exprimem a ligacao do solo ao topo do bloco; nao sao declividades reais.
module trecho_rampa(a,b,largura,h0,h1) {
    p=xy_mm(a); q=xy_mm(b); v=q-p; n=[-v[1],v[0]]/norm(v)*largura*fator_mapa/2;
    t=[p+n,q+n,q-n,p-n];
    polyhedron(points=concat([for(v=t)concat(v,[0])],
                             [concat(t[0],[h0]),concat(t[1],[h1]),
                              concat(t[2],[h1]),concat(t[3],[h0])]),
               faces=[[0,1,2,3],[4,7,6,5],[0,4,5,1],
                      [1,5,6,2],[2,6,7,3],[3,7,4,0]],convexity=10);
}
module rampa_tatil() {
    alto=h_edificio(1); meio=(base_peca_mm+alto)/2;
    difference() {
        union() {
            trecho_rampa([183.5,213],[202,213],4,base_peca_mm,base_peca_mm);
            trecho_rampa([202,213],[202,243],4,base_peca_mm,meio);
            trecho_rampa([202,243],[194,243],4,meio,meio);
            trecho_rampa([194,243],[194,228],4,meio,alto);
            trecho_rampa([194,228],[183.5,228],4,alto,alto);
        }
        linear_extrude(alto+1)
            offset(delta=folga_montagem_mm) planta_edificio(1);
        furos_botoes();
    }
}
module escada_tatil(k) {
    e=escadas[k]; s=e[1]*fator_mapa;
    translate(concat(xy_mm(e[0]),[0])) {
        cube([s[0],s[1],1]);
        for(j=[0:4])
            if(e[3]==0) translate([0,j*s[1]/5,1-eps])
                cube([s[0],s[1]/5,(j+1)*0.6+eps]);
            else translate([j*s[0]/5,0,1-eps])
                cube([s[0]/5,s[1],(j+1)*0.6+eps]);
    }
}
module painel_tatil() {
    difference() {
        translate([0,0,-espessura_painel_mm])
            cube([painel_largura_mm,painel_profundidade_mm,espessura_painel_mm]);
        furos_cabos_painel();
    }
}
module botao_referencia(r) {
    q=xy_mm(r[3]); z=h_botao(r);
    // Apenas F5: inclui o corpo, a chapa, o atuador e os quatro terminais.
    // '%' tambem impede que a referencia entre em uma exportacao acidental.
    %translate([q[0],q[1],z]) botao_kfc_a06(com_terminais=true);
}
// Única montagem de relevos: usada pelo mapa e pela caixa integrada.
module relevos_tateis() {
    for(i=[0:3]) color(i==3?[0.34,0.60,0.79]:[0.96,0.76,0.34]) edificio_tatil(i);
    for(k=[0:2]) color([0.77,0.79,0.77]) passagem_tatil(k);
    for(k=[0:2]) color([0.49,0.69,0.55]) piso_tatil(k);
    color([0.76,0.78,0.79]) rampa_tatil();
    if(mostrar_escadas) for(k=[0:1])
        color([0.91,0.48,0.20]) translate([0,0,h_edificio(escadas[k][2])-eps]) escada_tatil(k);
}
module montagem_tatil() {
    if(mostrar_painel) color([0.70,0.53,0.34]) painel_tatil();
    relevos_tateis();
    if($preview && mostrar_botoes) for(r=referencias) botao_referencia(r);
}

// Gabarito de montagem e de furacao 1:1; mesmos cortes e centros do 3D.
module linha_contorno() {
    difference() { offset(delta=0.15) children(); offset(delta=-0.15) children(); }
}
module centros_e_furos(so_furos=false) {
    for(r=referencias) translate(xy_mm(r[3])) {
        linha_contorno() passagem_cabos_painel_2d();
        if(!so_furos) {
            linha_contorno() alojamento_corpo_2d();
            linha_contorno() square(tamanho_apoio_botao_mm,center=true);
        }
        square([tamanho_apoio_botao_mm[0]+2,0.15],center=true);
        square([0.15,tamanho_apoio_botao_mm[1]+2],center=true);
        translate(r[5]) text(str(r[0]),size=tamanho_numero_mm,
                             font="Liberation Sans:style=Bold",halign="center",valign="center");
    }
}
module gabarito_tatil(so_furos=false) {
    // Linha toda DENTRO do painel: o SVG/DXF mede exatamente 500 x 380.
    difference() {
        square([painel_largura_mm,painel_profundidade_mm]);
        translate([0.3,0.3]) square([painel_largura_mm-0.6,painel_profundidade_mm-0.6]);
    }
    if(!so_furos) {
        for(i=[0:3]) linha_contorno() planta_edificio(i);
        for(k=[0:2]) linha_contorno() planta_passagem(k);
        for(k=[0:2]) linha_contorno() planta_piso(k);
        linha_contorno() projection(cut=false) rampa_tatil();
        for(e=escadas) translate(xy_mm(e[0])) linha_contorno() square(e[1]*fator_mapa);
    }
    centros_e_furos(so_furos);
}

// Legendas externas opcionais: preservam o Braille sem ocupar os pares de botoes.
// Exportar numero_peca 1..18. Nao sao colocadas sobre o painel.
digitos_braille = [[2,4,5],[1],[1,2],[1,4],[1,4,5],[1,5],
                   [1,2,4],[1,2,4,5],[1,2,5],[2,4]];
letras_braille = [
 [1],[1,2],[1,4],[1,4,5],[1,5],[1,2,4],[1,2,4,5],
 [1,2,5],[2,4],[2,4,5],[1,3],[1,2,3],[1,3,4],[1,3,4,5],
 [1,3,5],[1,2,3,4],[1,2,3,4,5],[1,2,3,5],[2,3,4],[2,3,4,5],
 [1,3,6],[1,2,3,6],[2,4,5,6],[1,3,4,6],[1,3,4,5,6],[1,3,5,6]
];
function celas_numero(n) = concat([[3,4,5,6]],
    n>=10 ? [digitos_braille[floor(n/10)],digitos_braille[n%10]] :
            [digitos_braille[n]]);
function cela_letra(c) = c==" " ? [] :
    c=="á" ? [1,2,3,5,6] : c=="é" ? [1,2,3,4,5,6] :
    c=="í" ? [3,4] : c=="ó" ? [3,4,6] : c=="ú" ? [2,3,4,5,6] :
    c=="ã" ? [3,4,5] : c=="õ" ? [2,4,6] : c=="ç" ? [1,2,3,4,6] :
    c=="à" ? [1,2,4,6] : c=="â" ? [1,6] : c=="ê" ? [1,2,6] :
    c=="ô" ? [1,4,5,6] : letras_braille[ord(c)-97];
function celas_palavra(s) = [for(i=[0:len(s)-1]) cela_letra(s[i])];
module ponto_braille() {
    // Calota esferica: diametro da base 1,6 mm e altura 0,7 mm.
    a=diametro_braille_mm/2; h=altura_braille_mm;
    r=(a*a+h*h)/(2*h);
    intersection() {
        translate([0,0,h-r]) sphere(r=r,$fn=24);
        translate([-r,-r,-0.02]) cube([2*r,2*r,h+0.02]);
    }
}
module linha_braille(celas) {
    for(i=[0:len(celas)-1]) for(d=celas[i])
        translate([i*6.6+(d>3?2.7:0),-((d-1)%3)*2.7,0]) ponto_braille();
}
module texto_relevo(s,size=5) {
    linear_extrude(0.8) text(s,size=size,font="Liberation Sans:style=Bold");
}
module legenda_tatil(n) {
    r=referencias[n-1];
    // 250 x 26 mm: texto longo do ponto 7 tambem cabe.
    cube([250,26,2]);
    translate([3,16,2-eps]) texto_relevo(str(n,"  ",r[1]),4.5);
    translate([3,10,2-eps]) linha_braille(concat(celas_numero(n),[[]],celas_palavra(r[2]),
        (n==5 || n==10) ? concat([[]],celas_palavra("andar"),[[]],celas_numero(2)) : []));
}


module peca_exportada() {
    if(tipo_peca=="edificio") {
        assert(numero_peca>=0 && numero_peca<4);
        l=limites(pontos_mm(edificios[numero_peca][1]));
        translate([-l[0],-l[1],0]) edificio_tatil(numero_peca);
    } else if(tipo_peca=="passagem") {
        assert(numero_peca>=0 && numero_peca<3);
        a=numero_peca==0 ? [137.1068,120.9273] :
          numero_peca==1 ? [151.8912,188+0.15/fator_mapa] : [156.1008,68+folga_montagem_mm/fator_mapa];
        translate(concat(-xy_mm(a),[0])) passagem_tatil(numero_peca);
    } else if(tipo_peca=="piso") {
        assert(numero_peca>=0 && numero_peca<3);
        translate(concat(-xy_mm(pisos[numero_peca][1]),[0])) piso_tatil(numero_peca);
    } else if(tipo_peca=="rampa") {
        translate(concat(-xy_mm([183.5,211]),[0])) rampa_tatil();
    } else if(tipo_peca=="escada") {
        assert(numero_peca>=0 && numero_peca<2);
        translate(concat(-xy_mm(escadas[numero_peca][0]),[0])) escada_tatil(numero_peca);
    } else if(tipo_peca=="painel") translate([0,0,espessura_painel_mm]) painel_tatil();
    else if(tipo_peca=="legenda") {
        assert(numero_peca>=1 && numero_peca<=18); legenda_tatil(numero_peca);
    } else assert(false,"Tipo de peca desconhecido");
}

assert(painel_largura_mm==500 && painel_profundidade_mm==380,
       "O painel deste projeto deve medir 500 x 380 mm.");
assert(escala_denominador>0 && espessura_painel_mm>0);
assert(folga_botao_mm>0 && parede_apoio_botao_mm>=1.2 &&
       espessura_assento_botao_mm>=1.2);
assert(diametro_furo_fio_painel_mm>0 &&
       diametro_furo_fio_painel_mm<=largura_canal_solda_mm &&
       diametro_furo_fio_painel_mm<min(passo_terminais_x_mm,passo_terminais_y_mm),
       "As quatro passagens do MDF devem ficar separadas e alinhadas aos canais.");
assert(altura_total_botao_mm>altura_corpo_botao_mm && altura_corpo_botao_mm>0);
assert(altura_minima_base_botao_mm>=5 && altura_canal_cabos_mm>=2.6);
assert(tamanho_acesso_solda_mm[0]>=passo_terminais_x_mm+largura_canal_solda_mm &&
       tamanho_acesso_solda_mm[1]>=passo_terminais_y_mm+largura_canal_solda_mm,
       "A cavidade inferior deve liberar os quatro terminais e suas soldas.");
assert(base_peca_mm>=1.6 && altura_aro_botao_mm>0 && altura_passagem_mm>=2);
for(r=referencias) {
    q=xy_mm(r[3]); meio=tamanho_apoio_botao_mm/2;
    assert(q[0]>meio[0] && q[0]<painel_largura_mm-meio[0] &&
           q[1]>meio[1] && q[1]<painel_profundidade_mm-meio[1],"Botao fora do painel.");
}
for(i=[0:len(referencias)-2],j=[i+1:len(referencias)-1]) {
    delta=xy_mm(referencias[i][3])-xy_mm(referencias[j][3]);
    // Envelopes conservadores incluindo terminais: preservar uma parede
    // entre cavidades. A tolerancia numerica permite a igualdade nominal.
    assert(abs(delta[0])+1e-9>=2*limite_terminal_x_mm+parede_apoio_botao_mm ||
           abs(delta[1])+1e-9>=lado_alojamento_botao_mm+parede_apoio_botao_mm,
           str("Alojamentos de botoes muito proximos: ",referencias[i][0],
               " e ",referencias[j][0]));
}

if(modo=="maquete") montagem_tatil();
else if(modo=="peca") peca_exportada();
else if(modo=="gabarito") gabarito_tatil();
else if(modo=="furacao") gabarito_tatil(so_furos=true);
else assert(false,"Modo desconhecido");
