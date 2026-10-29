/*
 COLMEIA INTELIGENTE — montagem eletrônica ilustrativa, sem colmeia
 Rev. B / 14-10-2026. Unidades: mm. Arquivo autossuficiente.
 Versão v2: chicotes por sensor, retornos explícitos e conexões auditáveis.
 A revisão A permanece em montagem_circuito_colmeia.scad.

 Base: relatório final, firmware v2.8 e circuito/esquema_profissional.
 Modelos visuais aproximados: não usar como gabarito mecânico/PCB.
 DevKit de 30 pinos e módulos comerciais representativos; conferir a
 disposição dos pinos e as dimensões nas peças efetivamente instaladas.
 R3/R4 e C1 vêm de desenhos anteriores, ainda sujeitos a confirmação.
 BMS e boost: aparência genérica; o projeto não identifica seus modelos.
 A base clara é um suporte de apresentação, não parte comprovada do protótipo.

 Abrir no OpenSCAD e pressionar F5. Cores fazem parte da visualização.
 F6/STL converte os objetos em geometria e perde as cores do conjunto.
 As coordenadas e os módulos abaixo permitem editar cada componente.
*/

/* [Visualização] */
mostrar_fios = true;
mostrar_base = true;
mostrar_legendas = true;
mostrar_placa_perfurada = true;
mostrar_componentes_a_confirmar = true;
// 0 = montagem; 1 = peças elevadas para inspeção
vista_explodida = 0; // [0:Montagem,1:Explodida]
qualidade = 20; // [12:4:48]
// Exporta terminais e ligações no console para conferência documental.
auditar_conexoes = false;

/* [Hidden] */
$fn = qualidade;
$vpr = [38,0,331];
$vpt = [143,103,12];
$vpd = 420;
preto = [0.045,0.050,0.058];
metal = [0.70,0.73,0.76];
ouro = [0.88,0.65,0.18];
verde = [0.035,0.32,0.19];
azul = [0.025,0.22,0.65];
vermelho = [0.82,0.035,0.04];
laranja = [1.0,0.34,0.035];
amarelo = [0.98,0.77,0.06];
branco = [0.91,0.92,0.90];
roxo = [0.52,0.15,0.72];
ez = vista_explodida * 24;

// Posições dos módulos. O eixo Z corresponde à face inferior da placa.
esp = [158,80,14+ez];
boost = [111,103,12+ez];
bms = [72,91,12+ez];
bat = [8,47,3];
sw = [75,132,9];
dht_ext = [238,55,5+ez];
dht_int = [238,100,5+ez];
mic = [240,146,5+ez];
reed = [220,181,3];
magneto = [220,199,3];

module arredondado(s,r=1) {
    hull() for(x=[r,s[0]-r],y=[r,s[1]-r])
        translate([x,y,0]) cylinder(r=r,h=s[2]);
}
module escrita(t,p,tamanho=2,c=branco,rot=0) {
    color(c) translate(p) rotate([0,0,rot])
        linear_extrude(0.09) text(t,size=tamanho,font="DejaVu Sans",halign="center",valign="center");
}
module haste(a,b,r=0.5,c=metal) {
    d=b-a;
    color(c) translate(a) rotate([0,acos(d[2]/norm(d)),atan2(d[1],d[0])])
        cylinder(h=norm(d),r=r,$fn=12);
}
function bezier(a,b,c,d,t) = pow(1-t,3)*a+3*pow(1-t,2)*t*b+3*(1-t)*t*t*c+t*t*t*d;
module fio(p,c=vermelho,r=0.55) {
    // Bézier cúbica: curva suave, sem dependências externas.
    n=20;
    if(mostrar_fios) for(i=[0:n-1]) {
        a=bezier(p[0],p[1],p[2],p[3],i/n);
        b=bezier(p[0],p[1],p[2],p[3],(i+1)/n);
        haste(a,b,r,c);
        color(c) translate(b) sphere(r=r,$fn=10);
    }
}
module cabo(a,b,c=vermelho,altura=12,r=0.55) {
    fio([a,a+[0,8,altura],b+[0,-8,altura],b],c,r);
}
module solda(p) {
    color(metal) translate(p) scale([1,1,0.48]) sphere(r=1.2,$fn=12);
}
module parafuso(p) {
    translate(p) {
        color(metal) difference() {
            cylinder(r=2.1,h=1.3,$fn=20);
            translate([-1.6,-0.35,0.7]) cube([3.2,0.7,1]);
            translate([-0.35,-1.6,0.7]) cube([0.7,3.2,1]);
        }
    }
}
module pcb(s,c=verde,furos=[]) {
    color(c) difference() {
        arredondado(s,1);
        for(p=furos) translate([p[0],p[1],-0.1]) cylinder(r=1.25,h=s[2]+0.2);
    }
    for(p=furos) color(ouro) translate([p[0],p[1],s[2]])
        difference(){cylinder(r=2,h=0.08);cylinder(r=1.25,h=0.2);}
}
module chip(p,s=[4,5,1.2],n=4) {
    color(preto) translate(p) cube(s);
    for(i=[0:n-1],side=[0,1])
        color(metal) translate(p+[side*(s[0]+0.7)-0.7,(i+0.5)*s[1]/n,0.15]) cube([0.7,0.35,0.45]);
}
module smd(p,s=[1.6,0.8,0.55],c=[0.40,0.28,0.16]) {
    color(c) translate(p) cube(s);
    for(x=[0,s[0]-0.3])color(metal)translate(p+[x,0,0])cube([0.3,s[1],s[2]+0.03]);
}
module header(p,n=3,passo=2.54) {
    translate(p) for(i=[0:n-1]) {
        color(preto) translate([-1.1,i*passo-1.1,0]) cube([2.2,2.2,2.4]);
        color(ouro) translate([-0.32,i*passo-0.32,-2]) cube([0.64,0.64,7.2]);
    }
}
module dupont(p) {
    color(preto) translate(p+[-1.05,-1.05,-3.8]) cube([2.1,2.1,3.8]);
}
module eletrolitico(p,r=2.6,h=6) {
    color([0.12,0.14,0.16])translate(p)cylinder(r=r,h=h);
    color(metal)translate(p+[0,0,h])cylinder(r=r*0.88,h=0.12);
    color([0.68,0.69,0.70]) translate(p+[r-0.3,-0.6,1])cube([0.32,1.2,h-1.5]);
    color([0.3,0.3,0.3])translate(p+[0,0,h+0.13])cube([r*1.3,0.15,0.04],center=true);
}

module placa_perfurada() {
    // Passo nominal de 2,54 mm, ilhas de cobre e furos reais.
    translate([68,39,7]) {
        color([0.49,0.23,0.095]) difference() {
            arredondado([140,123,1.6],2);
            for(x=[5:2.54:136],y=[5:2.54:119])
                translate([x,y,-0.1]) cylinder(r=0.48,h=1.9,$fn=8);
        }
        color([0.76,0.48,0.21]) for(x=[5:2.54:136],y=[5:2.54:119])
            translate([x,y,1.6])difference(){cylinder(r=0.86,h=0.05,$fn=10);cylinder(r=0.48,h=0.1,$fn=8);}
    }
    for(x=[72,204],y=[43,158]) {
        color([0.73,0.12,0.09])translate([x,y,3])cylinder(r=2.5,h=4,$fn=6);
        parafuso([x,y,8.7]);
    }
}

module esp32() {
    translate(esp) {
        pcb([28,52,1.6],preto,[[3,3],[25,3],[3,49],[25,49]]);
        // Módulo RF: blindagem metálica, substrato e antena impressa.
        color([0.08,0.25,0.18])translate([5,25,1.6])cube([18,25.5,0.8]);
        color(metal)translate([5.2,25.2,2.4])arredondado([17.6,18,2.5],0.5);
        escrita("ESP-WROOM-32",[14,36,5],1.65,[0.23,0.25,0.27]);
        escrita("ESP32",[14,31.8,5],2.5,[0.23,0.25,0.27]);
        for(i=[0:4]) {
            color(ouro)translate([6.5+i*3,44,2.45])cube([0.65,5.8,0.1]);
            color(ouro)translate([6.5+i*3, i%2==0?49.2:44,2.45])cube([3.5,0.65,0.1]);
        }
        // Micro-USB com abertura escura e lingueta.
        color(metal)difference(){translate([10,-1,1.6])arredondado([8,6,3.1],0.65);translate([10.7,-1.2,2.1])cube([6.6,5,2]);}
        color(preto)translate([11.3,-0.6,2.2])cube([5.4,4,0.8]);
        chip([11,9,1.7],[6,7,1.1],5);
        chip([4.5,17,1.7],[4.8,6,1.6],3);
        for(x=[5,22]) {
            color(metal)translate([x-1.8,5.5,1.6])cube([3.6,3.6,1.1]);
            color(preto)translate([x,7.3,2.7])cylinder(r=1.1,h=1.1);
        }
        for(i=[0:5])smd([21,11+i*2,1.7]);
        color([0.98,0.06,0.025])translate([7,12,1.8])cube([1.4,1,0.7]);
        for(x=[1.3,26.7]) {
            // Barras fêmeas montadas na placa perfurada e pinos da DevKit.
            color(preto)translate([x-1.1,7.2,-5.3])cube([2.2,38.1,5.2]);
            header([x,8.3,1.6],15);
        }
        escrita("DEVKIT V1",[14,21.5,1.75],1.7);
    }
}

module conversor_boost() {
    translate(boost) {
        pcb([18,38,1.3],azul,[[3,3],[15,35]]);
        color([0.16,0.17,0.18])translate([4.5,14,1.3])arredondado([9,9,4.5],1);
        escrita("220",[9,18.5,5.9],2.4,branco);
        color([0.03,0.29,0.75])translate([4,25,1.3])cube([10,8,6]);
        color(ouro)translate([9,29,7.3])cylinder(r=1.8,h=0.7);
        color(preto)translate([7.6,28.8,8])cube([2.8,0.4,0.06]);
        chip([7,8,1.4],[3,4,1.1],3);
        smd([3,9,1.4],[2.7,1.6,1.1],preto);
        smd([12,10,1.4],[2.7,1.7,1.6]);
        smd([13,22,1.4],[2.7,1.7,1.6]);
        for(p=[[2,5],[16,5],[2,33],[16,33]])solda([p[0],p[1],1.5]);
        escrita("IN+",[4.5,3.5,1.4],1.4);escrita("IN-",[13.5,3.5,1.4],1.4);
        escrita("OUT+",[5,36,1.4],1.2);escrita("OUT-",[13,36,1.4],1.2);
    }
}
module protecao_1s() {
    translate(bms) {
        pcb([18,26,1.1],verde);
        chip([4,6,1.2],[5,6,1],3);
        chip([5,15,1.2],[8,6,1.3],4);
        for(y=[5,8,11])smd([12,y,1.2]);
        for(x=[2,16],y=[2.5,23.5])solda([x,y,1.2]);
        for(i=[0:1]) {
            escrita(i==0?"B+":"B-",[i==0?4:14,4,1.2],1.6);
            escrita(i==0?"P+":"P-",[i==0?4:14,24,1.2],1.6);
        }
    }
}
module celula_18650(p,n) {
    translate(p) {
        // Duas células com a mesma orientação: associação em paralelo.
        color([0.20,0.53,0.38])rotate([-90,0,0])cylinder(r=9.15,h=65);
        color(metal)translate([0,-0.3,0])rotate([-90,0,0])cylinder(r=7.8,h=0.5);
        color([0.12,0.14,0.13])translate([0,64.9,0])rotate([-90,0,0])cylinder(r=8,h=0.3);
        color(metal)translate([0,65.2,0])rotate([-90,0,0])cylinder(r=3.2,h=0.8);
        escrita(str("18650  /  BT",n),[0,32,9.15],2.6,branco,90);
        escrita("+",[0,59,9.15],4,branco);
        escrita("-",[0,6,9.15],4,branco);
    }
}
module suporte_baterias() {
    translate(bat) {
        color(preto)difference(){arredondado([45,75,11],2);translate([2,2,2])cube([41,71,12]);}
        color(preto)translate([21.6,2,2])cube([1.8,71,7]);
        for(x=[11.6,33.4]) {
            celula_18650([x,5,11.3],x<20?1:2);
            // Contatos metálicos traseiros e dianteiros.
            color(metal)translate([x-3,72,3])cube([6,0.6,10]);
            color(metal)translate([x-3,2.2,3])cube([6,0.6,10]);
            for(y=[3:0.7:4.5])color(metal)translate([x,y,11.3])rotate([-90,0,0])
                difference(){cylinder(r=3,h=0.25);cylinder(r=2.6,h=0.3);}
        }
        // Barramentos visíveis do suporte paralelo.
        haste([11.6,72,5],[33.4,72,5],0.7,metal);
        haste([11.6,2.5,5],[33.4,2.5,5],0.7,metal);
    }
}
module chave() {
    translate(sw) {
        color(preto)arredondado([13,20,10],1.5);
        color([0.16,0.17,0.18])translate([-1,-1,9])arredondado([15,22,2],1.5);
        color(vermelho)translate([1,1,10])rotate([8,0,0])arredondado([11,17,2],1.2);
        escrita("I",[6.5,5,13],2.6);escrita("O",[6.5,14,14.1],2.6);
        for(y=[5,15])color(metal)translate([12,y,3])cube([5,1.3,2]);
    }
}
module sensor_dht(p,nome) {
    translate(p) {
        pcb([19,30,1.4],azul,[[9.5,26]]);
        header([4,3,1.4],3);
        // Corpo azul com grelha real, cavidade e divisórias.
        color([0.05,0.40,0.86])difference() {
            translate([3.5,10,1.4])arredondado([12,16,8],0.7);
            for(x=[5,8,11,14],y=[12,16,20,24])
                translate([x-0.65,y-1.1,5])cube([1.3,2.2,5]);
        }
        smd([12,5,1.5],[2.5,1.2,0.8],preto);
        escrita("DHT11",[9.5,28.3,1.5],1.7);
    }
}
module microfone() {
    translate(mic) {
        pcb([16,22,1.2],[0.24,0.12,0.51],[[13,19]]);
        header([2.4,3,1.2],6);
        color(metal)translate([7,9,1.2])arredondado([5,4,1.1],0.4);
        color(preto)translate([9.5,11,2.32])cylinder(r=0.55,h=0.05);
        smd([10,5,1.3]);smd([10,15,1.3]);
        escrita("INMP441",[9.8,18,1.3],1.25,branco,90);
    }
}
module mc38(p,ativo=true) {
    translate(p) {
        color([0.93,0.92,0.86])difference() {
            arredondado([29,10,7],2);
            for(x=[3,26])translate([x,5,-0.1])cylinder(r=1.5,h=8);
        }
        color([0.85,0.84,0.79])translate([7,1.5,7])arredondado([15,7,0.4],1);
        if(ativo)escrita("MC-38",[14.5,5,7.5],1.8,[0.36,0.36,0.33]);
        for(x=[3,26])parafuso([x,5,1]);
    }
}
module resistor_axial(a,b,valor="100k",faixas=[[0.45,0.22,0.08],[0.03,0.03,0.03],[1,0.75,0]]) {
    // Corpo alinhado ao eixo X; terminais nos pontos a e b, de mesmo Y/Z.
    m=(a+b)/2;
    // Terminais separados: não desenhar metal contínuo através do resistor.
    haste(a,m+[-3.2,0,0],0.25,metal);
    haste(m+[3.2,0,0],b,0.25,metal);
    color([0.73,0.62,0.43])translate(m+[-3.2,0,0])rotate([0,90,0])cylinder(r=1.1,h=6.4);
    for(i=[0:2])color(faixas[i])translate(m+[-2+i*1.5,0,0])rotate([0,90,0])cylinder(r=1.13,h=0.6);
    color(ouro)translate(m+[2.3,0,0])rotate([0,90,0])cylinder(r=1.13,h=0.5);
    solda(a);solda(b);
}
// Dois barramentos verticais ao lado direito da DevKit.
function rail3(i)=[193,[58,103,149,88.3][i],10];
function railg(i)=[199,[63.08,108.08,151.54,90.84,46,155,54][i],10];
module barramentos() {
    for(x=[193,199]) haste([x,45,9.5],[x,156,9.5],0.50,metal);
    for(i=[0:3])solda(rail3(i));
    for(i=[0:6])solda(railg(i));
    escrita("3V3",[193,41.7,8.8],1.7);
    escrita("GND",[202,41.7,8.8],1.7);
}

// Pinagem representativa de DevKit 30 pinos: USB voltado para -Y.
function ep(lado,i)=esp+[lado==0?1.3:26.7,8.3+i*2.54,8.2];
E_5V=ep(0,0); E_GND=ep(1,1); E_27=ep(0,5); E_26=ep(0,6);
E_25=ep(0,7); E_33=ep(0,8); E_34=ep(0,11);
E_3V3=ep(1,0); E_4=ep(1,4); E_21=ep(1,10);
function dp(p,i)=p+[4,3+i*2.54,8];
function mp(i)=mic+[2.4,3+i*2.54,7.8];
DIV_A=[132,59,11]; DIV_M=[147,59,11]; DIV_G=[162,59,11];

// Tabela única de terminais usada tanto para a geometria quanto para a auditoria.
terminais = [
 ["BT1.+",bat+[11.6,72,5]], ["BT2.+",bat+[33.4,72,5]],
 ["BT1.-",bat+[11.6,2.5,5]], ["BT2.-",bat+[33.4,2.5,5]],
 ["U2.B+",bms+[2,2.5,1.4]], ["U2.B-",bms+[16,2.5,1.4]],
 ["U2.P+",bms+[2,23.5,1.4]], ["U2.P-",bms+[16,23.5,1.4]],
 ["SW1.1",sw+[17,5,4]], ["SW1.2",sw+[17,15,4]],
 ["U3.IN+",boost+[2,5,1.6]], ["U3.IN-",boost+[16,5,1.6]],
 ["U3.OUT+",boost+[2,33,1.6]], ["U3.OUT-",boost+[16,33,1.6]],
 ["U1.VIN/5V",E_5V], ["U1.GND",E_GND], ["U1.3V3",E_3V3],
 ["U1.GPIO4",E_4], ["U1.GPIO21",E_21], ["U1.GPIO25",E_25],
 ["U1.GPIO26",E_26], ["U1.GPIO33",E_33], ["U1.GPIO27",E_27], ["U1.GPIO34",E_34],
 ["R1.1",DIV_A], ["R1.2",DIV_M], ["R2.1",DIV_M], ["R2.2",DIV_G],
 ["C1.1",DIV_M], ["C1.2",DIV_G],
 ["R3.1",dht_ext+[7,5,3]], ["R3.2",dht_ext+[17,5,3]],
 ["R4.1",dht_int+[7,5,3]], ["R4.2",dht_int+[17,5,3]],
 ["U4.VCC",dp(dht_ext,0)], ["U4.DATA",dp(dht_ext,1)], ["U4.GND",dp(dht_ext,2)],
 ["U5.VCC",dp(dht_int,0)], ["U5.DATA",dp(dht_int,1)], ["U5.GND",dp(dht_int,2)],
 ["U6.VDD",mp(0)], ["U6.GND",mp(1)], ["U6.WS",mp(2)],
 ["U6.SCK",mp(3)], ["U6.SD",mp(4)], ["U6.L/R",mp(5)],
 ["SW2.1",reed+[0,4,3]], ["SW2.2",reed+[0,6,3]],
 ["V3.0",rail3(0)], ["V3.1",rail3(1)], ["V3.2",rail3(2)], ["V3.3",rail3(3)],
 ["G.0",railg(0)], ["G.1",railg(1)], ["G.2",railg(2)], ["G.3",railg(3)],
 ["G.4",railg(4)], ["G.5",[199,155,10]], ["G.6",railg(6)]
];
function terminal(nome)=let(v=[for(t=terminais)if(t[0]==nome)t[1]])
    assert(len(v)==1,str("Terminal inexistente/duplicado: ",nome)) v[0];

// Curvas só nas mudanças de direção: cabos seguem corredores identificáveis.
function entrada(p,i)=let(d=p[i-1]-p[i],r=min(2,norm(d)/3,norm(p[i+1]-p[i])/3))p[i]+d*r/norm(d);
function saida(p,i)=let(d=p[i+1]-p[i],r=min(2,norm(d)/3,norm(p[i-1]-p[i])/3))p[i]+d*r/norm(d);
function arredondar_rota(p)=concat([p[0]],
    [for(i=[1:len(p)-2],j=[0:5])let(t=j/5,a=entrada(p,i),b=saida(p,i))
        (1-t)*(1-t)*a+2*(1-t)*t*p[i]+t*t*b],[p[len(p)-1]]);
module ligar(rede,a,b,via=[],c=preto,r=0.46) {
    pontos=arredondar_rota(concat([terminal(a)],via,[terminal(b)]));
    if(auditar_conexoes)echo(["FIO",rede,a,b,pontos,c,r]);
    if(mostrar_fios) for(i=[0:len(pontos)-2]) {
        if(norm(pontos[i+1]-pontos[i])>0.001)haste(pontos[i],pontos[i+1],r,c);
        color(c)translate(pontos[i])sphere(r=r,$fn=10);
    }
}
module interna(rede,a,b) {
    // Continuidade física pelos barramentos/contatos, sem resistor no caminho.
    if(auditar_conexoes)echo(["INTERNA",rede,a,b]);
}
module ligacoes() {
    if(auditar_conexoes)for(t=terminais)echo(["TERMINAL",t[0],t[1]]);
    interna("BAT+","BT1.+","BT2.+");
    interna("BAT-","BT1.-","BT2.-");
    for(i=[1:3])interna("+3V3","V3.0",str("V3.",i));
    for(i=[1:6])interna("GND","G.0",str("G.",i));
    interna("BAT_SENSE","R1.2","R2.1");

    // Alimentação à esquerda; BAT- permanece exclusivamente no lado B-.
    ligar("BAT+","BT2.+","U2.B+",[[58,119,10],[58,87,10],[74,87,16]],vermelho,0.7);
    ligar("BAT-","BT2.-","U2.B-",[[60,49.5,10],[60,84,10],[88,84,16]],preto,0.7);
    ligar("P+","U2.P+","SW1.1",[[74,124,16],[95,124,16],[95,137,16]],vermelho,0.65);
    ligar("+SYS","SW1.2","U3.IN+",[[103,147,16],[103,98,16],[113,98,16]],laranja,0.65);
    ligar("GND","U2.P-","U3.IN-",[[97,114.5,20],[97,96,20],[127,96,20]],preto,0.65);
    // Retorno explícito entre os dois terminais negativos do boost.
    ligar("GND","U3.IN-","U3.OUT-",[[132,108,16],[132,136,16]],preto,0.6);
    ligar("+5V","U3.OUT+","U1.VIN/5V",[[113,144,16],[136,144,16],[136,88.3,21]],vermelho,0.6);
    ligar("GND","U3.OUT-","G.4",[[134,136,11],[134,43,11],[199,43,11]],preto,0.6);
    ligar("GND","U1.GND","G.3",[[189,90.84,22.2+ez],[199,90.84,22.2+ez]],preto);
    ligar("+3V3","U1.3V3","V3.3",[[189,88.3,22.2+ez],[193,88.3,22.2+ez]],laranja);

    // Medição antes do conversor; divisor próximo à borda anterior da placa.
    ligar("+SYS","U3.IN+","R1.1",[[113,96,16],[113,51,16],[132,51,16]],laranja);
    ligar("BAT_SENSE","R1.2","U1.GPIO34",[[141,59,20],[141,116.24,20],[153,116.24,22.2+ez]],roxo);
    ligar("GND","R2.2","G.6",[[169,59,16],[169,54,16],[195,54,16]],preto);

    // DHT externo: chicote curto de três vias, com dados acima dos barramentos.
    ligar("+3V3","V3.0","U4.VCC",[[207,58,17],[232,58,17]],laranja);
    ligar("DHT_EXT","U1.GPIO4","U4.DATA",[[207,98.46,24+ez],[207,60.54,24+ez],[232,60.54,17]],amarelo);
    ligar("GND","G.0","U4.GND",[[210,63.08,17],[232,63.08,17]],preto);
    // DHT interno: chicote próprio, sem passar por cima do ESP32.
    ligar("+3V3","V3.1","U5.VCC",[[214,103,17],[232,103,17]],laranja);
    ligar("DHT_INT","U1.GPIO21","U5.DATA",[[211,113.7,24+ez],[211,105.54,24+ez],[232,105.54,17]],[0.11,0.72,0.35]);
    ligar("GND","G.1","U5.GND",[[214,108.08,17],[232,108.08,17]],preto);

    // I2S contorna a borda posterior do ESP32: nenhuma via sobre a antena.
    ligar("+3V3","V3.2","U6.VDD",[[216,149,17],[234,149,17]],laranja);
    ligar("GND","G.2","U6.GND",[[216,151.54,17],[234,151.54,17]],preto);
    ligar("I2S_WS","U1.GPIO25","U6.WS",[[150,106.08,24+ez],[150,154.08,20],[218,154.08,20],[234,154.08,17]],[0.05,0.53,0.88]);
    ligar("I2S_BCLK","U1.GPIO26","U6.SCK",[[146,103.54,27+ez],[146,156.62,24],[218,156.62,24],[234,156.62,17]],amarelo);
    ligar("I2S_SD","U1.GPIO33","U6.SD",[[154,108.62,30+ez],[154,159.16,28],[218,159.16,28],[234,159.16,17]],branco);
    ligar("GND","U6.GND","U6.L/R",[[238,151.54,12.8+ez],[238,161.7,12.8+ez]],preto,0.35);

    // Cabo do MC-38 pela periferia; dois fios lado a lado ao chegar ao sensor.
    ligar("LID_SW","U1.GPIO27","SW2.1",[[138,101,24+ez],[138,176,14],[213,176,14],[217,185,10]],roxo);
    // Passagem elevada sobre LID_SW: 4 mm entre centros no cruzamento.
    ligar("GND","G.5","SW2.2",[[204,155,18],[204,178,18],[213,178,18],[217,187,10]],preto);

    // Pull-ups junto aos DHTs: ligações locais, sem quatro fios longos adicionais.
    if(mostrar_componentes_a_confirmar) {
        ligar("+3V3","U4.VCC","R3.1",[[242,58,15+ez],[245,58,15+ez]],laranja,0.28);
        ligar("DHT_EXT","U4.DATA","R3.2",[[242,62,15+ez],[255,62,15+ez]],amarelo,0.28);
        ligar("+3V3","U5.VCC","R4.1",[[242,103,15+ez],[245,103,15+ez]],laranja,0.28);
        ligar("DHT_INT","U5.DATA","R4.2",[[242,107,15+ez],[255,107,15+ez]],[0.11,0.72,0.35],0.28);
        interna("BAT_SENSE","R1.2","C1.1");
        interna("GND","R2.2","C1.2");
    }
    for(p=[E_5V,E_GND,E_3V3,E_4,E_21,E_25,E_26,E_33,E_27,E_34])dupont(p);
    for(p=[dht_ext,dht_int],i=[0:2])dupont(dp(p,i));
    for(i=[0:5])dupont(mp(i));
}

module passivos() {
    resistor_axial(DIV_A,DIV_M);
    resistor_axial(DIV_M,DIV_G);
    if(mostrar_componentes_a_confirmar) {
        resistor_axial(terminal("R3.1"),terminal("R3.2"),"4k7",[[1,0.8,0],[0.6,0.1,0.8],[0.8,0.02,0.02]]);
        resistor_axial(terminal("R4.1"),terminal("R4.2"),"4k7",[[1,0.8,0],[0.6,0.1,0.8],[0.8,0.02,0.02]]);
        haste(DIV_M,[150,66,15],0.25);
        haste(DIV_G,[154,66,15],0.25);
        color([0.69,0.30,0.10])translate([152,66,16])rotate([90,0,0])scale([1,1,0.35])sphere(r=3);
        translate([152,64.9,16])rotate([90,0,0])escrita("104",[0,0,0],1.5,preto);
    }
    escrita("R1 100k",[138,54,8.8],1.8);
    escrita("R2 100k",[156,54,8.8],1.8);
}
module legenda(t,p,tam=3) {
    if(mostrar_legendas)escrita(t,[p[0],p[1],mostrar_base?2.08:0.1],tam,[0.18,0.23,0.29]);
}

module apoios() {
    // Apoios isolantes aproximados; deslocamento vertical na vista explodida.
    for(p=[boost,bms]) for(x=[3,15])
        color([0.80,0.79,0.71])translate([p[0]+x,p[1]+12,8.7])
            cylinder(r=1.5,h=3.3,$fn=12);
    for(p=[dht_ext,dht_int,mic]) for(y=[2,19])
        color([0.80,0.79,0.71])translate([p[0]+13,p[1]+y,2])
            cylinder(r=1.5,h=3,$fn=12);
}

if(mostrar_base)color([0.91,0.92,0.93])arredondado([282,218,2],5);
if(mostrar_placa_perfurada)placa_perfurada();
apoios();
suporte_baterias();chave();esp32();conversor_boost();protecao_1s();
sensor_dht(dht_ext,"externo");sensor_dht(dht_int,"interno");microfone();
mc38(reed);mc38(magneto,false);barramentos();passivos();ligacoes();

legenda("COLMEIA INTELIGENTE | MONTAGEM ELETRONICA",[141,15],4);
legenda("2 x 18650 / PARALELO",[32,37],2.6);
legenda("LIGA / DESLIGA",[82,170],2.5);
legenda("PLACA PERFURADA + ESP32",[145,173],2.8);
legenda("DHT11 EXTERNO",[247,47],2.4);
legenda("DHT11 INTERNO",[247,92],2.4);
legenda("INMP441 / I2S",[248,137],2.4);
legenda("MC-38 + IMA",[239,214],2.3);
legenda("REV. B | Chicotes organizados | firmware v2.8",[113,197],2.6);
legenda("Vermelho: bateria/5V   Laranja: +SYS/3V3   Preto: retorno",[113,205],2.1);

echo("Montagem ilustrativa em mm. Dimensoes comerciais aproximadas.");
echo("Fontes: relatorio final, firmware v2.8 e esquema profissional.");
echo("R3/R4/C1 e alimentacao DHT11: confirmar na montagem original.");
