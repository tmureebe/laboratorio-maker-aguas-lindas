/*
MAPA TATIL - SISTEMA ELETRONICO NA CAIXA 500 x 380 x 50 mm

VISUALIZACAO ILUSTRATIVA. Pressione F5 no OpenSCAD.
ESP32, protoboard, DFPlayer, microSD, resistor de 1k, falante, USB e 10 botoes.
Modulos e suportes sao genericos, com dimensoes aproximadas, nao medidos.
Fios indicam as funcoes do guia; nao reproduzem a pinagem fisica de uma placa
comercial nem comprimentos definitivos. Nao usar como desenho de ligacao.

Os botoes e seus furos nesta cena sao APENAS VISUAIS. As posicoes abaixo sao
provisorias e editaveis. NENHUM SVG/DXF de fabricacao foi alterado: os dois
paineis de corte continuam lisos, com exatamente 500 x 380 mm.

inspecao: caixa montada, paredes/tampa transparentes, eletronica aparente.
fechada: caixa opaca, botoes sobre o painel.
aberta: painel, nervuras e botoes levantados, com fios ilustrando folga.
sem_tampa: interior visivel; botoes na altura montada, sem desenhar o painel.
eletronica: apenas componentes, botoes e fios, sem MDF.
Use mostrar_pedestal=true para visualizar o conjunto sobre a estrutura.

Dependencia local opcional: pedestal_existente.scad, na mesma pasta.
*/

/* [Visualizacao] */
vista = "sem_tampa"; // [inspecao,fechada,aberta,sem_tampa,eletronica]
mostrar_pedestal = false;
mostrar_paredes = true; // Paredes do pedestal, quando ele estiver visivel.
mostrar_fios = true;
mostrar_fios_botoes = true;
mostrar_rotulos = true;
mostrar_botoes = true;
mostrar_nervuras = true;
abertura_tampa = 105;
furos_apenas_visuais = true;

/* [Botoes - posicoes apenas ilustrativas em mm] */
// Origem: canto dianteiro esquerdo. x para direita; s para a traseira.
// B1..B10: posicoes escolhidas apenas para visualizar o mecanismo.
posicoes_botoes = [
    [65,60], [160,60], [330,60], [435,60],
    [65,175], [160,175], [330,175], [435,175],
    [400,305], [455,305]
];
// Correspondencia funcional do guia, nao ordem fisica dos pinos do modelo.
gpio_botoes = [13,14,27,26,25,33,32,23,19,18];

/* [Detalhe] */
$fn = 24;

/* [Hidden] */
include <pedestal_existente.scad>
largura_caixa = 500;
profundidade_caixa = 380;
altura_caixa = 50;
espessura = 3;
z_painel = 47;
levantar = vista == "aberta" ? abertura_tampa : 0;
com_mdf = vista != "eletronica";
com_painel = vista != "sem_tampa" && com_mdf;
alpha_tampa = vista == "inspecao" ? 0.12 : 1;
alpha_paredes = vista == "inspecao" ? 0.38 : 1;
cores_sinais = [
    [0.95,0.52,0.08], [0.64,0.20,0.85], [0.10,0.65,0.32],
    [0.10,0.52,0.95], [0.93,0.26,0.45], [0.60,0.42,0.08],
    [0.04,0.65,0.65], [0.65,0.20,0.25], [0.45,0.45,0.85], [0.70,0.60,0.03]
];
origem_caixa = [
    [1,0,0,-30],
    [0,0.9874406319167053,-0.15799050110667284,-18.087691567494037],
    [0,0.15799050110667284,0.9874406319167053,865.9441266854824],
    [0,0,0,1]
];

assert(len(posicoes_botoes)==10,"A cena do guia usa dez botoes.");
assert(len(gpio_botoes)==len(posicoes_botoes));
assert(vista=="inspecao" || vista=="fechada" || vista=="aberta" ||
       vista=="sem_tampa" || vista=="eletronica", "Vista invalida.");
for(p=posicoes_botoes)
    assert(p[0]>15 && p[0]<485 && p[1]>30 && p[1]<350,
           "Manter botoes ilustrativos dentro do painel, afastados das bordas.");

module rotulo(s,p,size=4,cor=[.08,.13,.17],alinhamento="left") {
    if(mostrar_rotulos) color(cor) translate(p)
        linear_extrude(.18) text(s,size=size,font="Liberation Sans:style=Bold",
                                halign=alinhamento,valign="center");
}

module fio(pontos,cor=[.1,.1,.1],raio=.6) {
    color(cor) {
        for(i=[0:len(pontos)-2]) {
            d=pontos[i+1]-pontos[i]; l=norm(d);
            if(l>.001) translate(pontos[i])
                rotate([0,acos(d[2]/l),atan2(d[1],d[0])])
                    cylinder(h=l,r=raio,$fn=8);
        }
        for(p=pontos) translate(p) sphere(r=raio,$fn=8);
    }
}

module placa(w,d,h=1.6,cor=[.03,.38,.22]) {
    color(cor) difference() {
        cube([w,d,h]);
        for(x=[2,w-2],y=[2,d-2]) translate([x,y,-.1]) cylinder(h=h+.2,r=.85,$fn=12);
    }
}

module pino(p) {
    color([.78,.65,.24]) translate(p) cylinder(h=2.5,r=.55,$fn=8);
}

module protoboard() {
    translate([45,270,6]) {
        color([.90,.90,.85]) linear_extrude(9)
            translate([2,2]) offset(r=2) square([166,66]);
        color([.73,.74,.71]) translate([4,32,8.9]) cube([162,3,.2]);
        for(i=[0:24],j=[0:4],lado=[0,1])
            color([.21,.23,.24]) translate([8+i*5.6,12+lado*27+j*2.54,9.01])
                cylinder(h=.15,r=.5,$fn=8);
        color([.78,.08,.08]) translate([5,63,9.01]) cube([160,.6,.15]);
        color([.08,.25,.70]) translate([5,67,9.01]) cube([160,.6,.15]);
        rotulo("+",[1,63,9.2],3,[.78,.08,.08]);
        rotulo("-",[1,67,9.2],3,[.08,.25,.70]);
    }
    rotulo("PROTOBOARD",[45,257,3.15],4);
}

module esp32() {
    // Representacao generica; conector USB voltado para a traseira da caixa.
    translate([80,286,22]) {
        placa(28,54,1.6,[.04,.16,.17]);
        for(i=[0:14],x=[1,27]) {
            color([.08,.09,.10]) translate([x-.8,7+i*2.54,-3]) cube([1.6,1.6,3]);
            color([.78,.65,.24]) translate([x,7+i*2.54,-7]) cylinder(h=7,r=.5,$fn=8);
            pino([x,7+i*2.54,1.6]);
        }
        color([.67,.69,.70]) translate([4,18,1.6]) cube([20,25,3]);
        color([.02,.03,.04]) translate([6,3,1.6]) cube([16,12,1]);
        color([.72,.60,.23]) for(i=[0:3]) translate([7,4+i*2.5,2.6]) cube([14,.7,.2]);
        color([.68,.70,.72]) translate([10,51,1.6]) cube([8,8,3]);
        color([.03,.04,.05]) translate([11,58.9,2.2]) cube([6,.2,1.8]);
        color([.13,.13,.14]) for(x=[4,21]) translate([x,46,1.6]) cube([3,3,1.5]);
        rotulo("ESP32",[14,31,4.8],3,[.1,.1,.12],"center");
    }
    // Terminais de distribuicao ilustrativos na protoboard, B1..B10.
    for(i=[0:9]) pino([127+i*3,294,15]);
    rotulo("B1 ... B10",[125,300,15.2],2.8);
}

module dfplayer() {
    translate([291,282,10]) {
        for(p=[[2,2],[23,28]]) color([.82,.82,.80]) translate([p[0],p[1],-7])
            cylinder(h=7,r=2,$fn=12);
        placa(25,30);
        for(i=[0:7],x=[1,24]) pino([x,4+i*3,1.6]);
        color([.12,.13,.14]) translate([7,2,1.6]) cube([11,8,2]);
        color([.65,.68,.70]) translate([3.5,12,1.6]) cube([18,16,3]);
        color([.08,.09,.10]) translate([5.5,23,3.8]) cube([14,11,1]);
        rotulo("SD",[12.5,30,4.9],2.8,[.95,.95,.95],"center");
    }
    rotulo("DFPLAYER + microSD",[279,320,3.15],3.5);
}

module resistor_1k() {
    // Corpo e terminais axialmente em x, sobre a area livre da protoboard.
    color([.64,.65,.66]) translate([136,286,19]) rotate([0,90,0]) cylinder(h=16,r=.35,$fn=8);
    color([.78,.67,.43]) translate([140,286,19]) rotate([0,90,0]) cylinder(h=8,r=1.4,$fn=16);
    for(i=[0:3]) color(i==0?[.35,.15,.04]:i==1?[.02,.02,.02]:i==2?[.75,.03,.02]:[.75,.61,.2])
        translate([141+i*1.6,286,19]) rotate([0,90,0]) cylinder(h=.6,r=1.43,$fn=16);
    rotulo("1k",[143,282,20.5],2.5,[.15,.15,.15],"center");
}

module falante() {
    // Face acustica para a grade frontal; diametro ilustrativo 32, fundo 12.
    translate([330,4,25]) rotate([-90,0,0]) {
        color([.57,.59,.61]) difference() {
            cylinder(h=3,r=16);
            translate([0,0,-.1]) cylinder(h=3.2,r=12.5);
        }
        color([.12,.13,.14]) translate([0,0,.7]) difference() {
            cylinder(h=4,r1=12.5,r2=4);
            translate([0,0,-.1]) cylinder(h=3.7,r1=11.8,r2=3.5);
        }
        color([.1,.1,.11]) translate([0,0,1]) scale([1,1,.35]) sphere(r=4);
        color([.20,.21,.23]) translate([0,0,5]) cylinder(h=7,r=7);
    }
    rotulo("FALANTE 8 ohm",[300,45,3.15],3.5);
}

module botao(i) {
    p=posicoes_botoes[i];
    translate([p[0],p[1],levantar]) {
        color([.08,.36,.20]) translate([-7,-7,40.8]) cube([14,14,1.2]);
        color([.1,.1,.11]) translate([-3,-3,42]) cube([6,6,3.2]);
        color([.73,.75,.77]) translate([-2.8,-2.8,45]) cube([5.6,5.6,.6]);
        color([.17,.17,.18]) translate([0,0,45.3]) cylinder(h=5.4,r=1.9,$fn=16);
        color(cores_sinais[i]) translate([0,0,50.5]) cylinder(h=3,r1=8,r2=7.4);
        for(x=[-4,4]) color([.7,.7,.72]) translate([x,-3,40]) cylinder(h=1.2,r=.45,$fn=8);
        rotulo(str(i+1),[0,0,53.6],4,[1,1,1],"center");
        rotulo(str("B",i+1),[0,14,50.2],3.2,[.12,.14,.16],"center");
    }
}

module ligacoes() {
    // +5V e GND simbolicos: USB/ESP32 -> barramentos -> DFPlayer.
    fio([[104,338,24],[115,340,25],[120,333,15.8]],[.85,.05,.05]);
    fio([[83,338,24],[83,344,25],[115,337,15.8]],[.06,.06,.07]);
    fio([[195,333,15.8],[220,345,18],[235,350,9],[275,350,9],[292,286,13]],[.85,.05,.05]);
    fio([[195,337,15.8],[222,350,18],[235,355,9],[280,355,9],[315,286,13]],[.06,.06,.07]);
    // TX17 -> resistor 1k -> RX do DFPlayer. TX do DFPlayer -> RX16.
    fio([[107,326,24],[125,342,26],[136,286,19]],[.9,.65,.05]);
    fio([[152,286,19],[215,345,19],[235,347,9],[270,347,9],[292,289,13]],[.9,.65,.05]);
    fio([[315,292,13],[320,348,10],[240,348,10],[125,345,26],[107,323,24]],[.15,.62,.78]);
    // Falante somente entre SPK1 e SPK2; nenhum terminal vai a GND.
    fio([[315,301,13],[345,255,9],[350,225,8],[350,65,8],[336,18,19]],[.70,.15,.65],.7);
    fio([[315,304,13],[350,255,9],[355,225,8],[355,65,8],[324,18,19]],[.24,.22,.65],.7);
    // USB conectado ao ESP32, saindo pelo entalhe traseiro existente.
    fio([[94,345,25],[94,351,30],[72,360,39],[72,390,39]],[.13,.14,.16],1.9);
    color([.16,.17,.18]) translate([66,386,35]) cube([12,15,8]);
    rotulo("USB",[72,410,4],5,[.15,.15,.17],"center");
    if(mostrar_botoes && mostrar_fios_botoes) for(i=[0:9]) {
        p=posicoes_botoes[i];
        fio([[127+i*3,294,17.5],[127+i*3,260,18],[127+i*3,255,9],
             [p[0]-4,p[1]-3,9],[p[0]-4,p[1]-3,40.5+levantar]],cores_sinais[i],.48);
        fio([[190,337,15.8],[218,337,18],[230,255,8],
             [p[0]+4,p[1]-3,8],[p[0]+4,p[1]-3,40.5+levantar]],[.09,.09,.10],.43);
    }
}

module perfil_mdf(i) {
    // Geometria de referencia igual a V4; os paineis sao retangulos lisos.
    if(i==0 || i==1) square([500,380]);
    if(i==2) difference() {
        square([494,44]);
        for(k=[0:8]) translate([303+6*k,11]) square([2,22]);
        for(x=[27,147,397,467]) translate([x,32]) circle(r=1.75);
    }
    if(i==3) difference() {
        polygon([[0,0],[494,0],[494,44],[81,44],[81,30],[57,30],[57,44],[0,44]]);
        for(x=[27,147,397,467]) translate([x,32]) circle(r=1.75);
        for(x=[97,109]) translate([x,15]) square([3,8]);
    }
    if(i==4 || i==5) square([380,44]);
    if(i==6 || i==7) polygon([[0,0],[494,0],[494,30],[248.575,30],
        [248.575,14.925],[245.425,14.925],[245.425,30],[0,30]]);
    if(i==8) polygon([[0,0],[105.425,0],[105.425,15.075],[108.575,15.075],
        [108.575,0],[235.425,0],[235.425,15.075],[238.575,15.075],
        [238.575,0],[374,0],[374,30],[0,30]]);
}

module painel_visual() {
    // Furos SOMENTE na cena de visualizacao; nao exportar esta cena para corte.
    difference() {
        linear_extrude(3) perfil_mdf(1);
        if(mostrar_botoes && furos_apenas_visuais) for(p=posicoes_botoes)
            translate([p[0],p[1],-.1]) cylinder(h=3.2,r=2.75,$fn=20);
    }
}

module madeira() {
    color([.50,.68,.72]) linear_extrude(3) perfil_mdf(0);
    color([.50,.68,.72,alpha_paredes]) {
        // As matrizes mantem y e z com o mesmo sentido dos arquivos de corte.
        multmatrix([[1,0,0,3],[0,0,1,0],[0,1,0,3],[0,0,0,1]]) linear_extrude(3) perfil_mdf(2);
        multmatrix([[1,0,0,3],[0,0,1,377],[0,1,0,3],[0,0,0,1]]) linear_extrude(3) perfil_mdf(3);
        multmatrix([[0,0,1,0],[1,0,0,0],[0,1,0,3],[0,0,0,1]]) linear_extrude(3) perfil_mdf(4);
        multmatrix([[0,0,1,497],[1,0,0,0],[0,1,0,3],[0,0,0,1]]) linear_extrude(3) perfil_mdf(5);
    }
    if(com_painel) {
        color([.88,.75,.48,alpha_tampa]) translate([0,0,47+levantar]) painel_visual();
        if(mostrar_nervuras) color([.79,.61,.32,vista=="inspecao"?.55:1]) translate([0,0,levantar]) {
            for(s=[110,240]) multmatrix([[1,0,0,3],[0,0,1,s-1.5],[0,1,0,17],[0,0,0,1]])
                linear_extrude(3) perfil_mdf(6);
            multmatrix([[0,0,1,248.5],[1,0,0,3],[0,1,0,17],[0,0,0,1]]) linear_extrude(3) perfil_mdf(8);
        }
        color([.65,.45,.26,vista=="inspecao"?.6:1]) for(x=[30,150,400,470],s=[13,367])
            translate([x-10,s-10,3+levantar]) cube([20,20,44]);
    }
}

module cena() {
    if(com_mdf) madeira();
    protoboard(); esp32(); dfplayer(); resistor_1k(); falante();
    if(mostrar_botoes) for(i=[0:9]) botao(i);
    if(mostrar_fios) ligacoes();
    rotulo("BOTOES: POSICOES ILUSTRATIVAS - NAO FURAR",[250,-25,4],6,[.65,.13,.09],"center");
}

$vpt = mostrar_pedestal ? [220,170,700] : [250,190,25];
$vpr = [42,0,25];
$vpd = mostrar_pedestal ? 1600 : 880;

if(mostrar_pedestal) {
    pedestal_existente();
    multmatrix(origem_caixa) cena();
} else cena();
