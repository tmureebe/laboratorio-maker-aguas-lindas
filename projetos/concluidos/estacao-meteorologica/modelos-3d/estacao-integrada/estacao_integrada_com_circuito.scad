// Montagem ilustrativa, em mm. Abra junto de estacao_integrada.scad.
// Estrutura R2 original reutilizada sem alterar as pecas de fabricacao.
// Eletronica aproximada: conferir dimensoes e pinagem dos componentes reais.
// Referencias: esquema_circuito_estacao_meteorologica.png e firmware v2.
use <estacao_integrada.scad>

/* [Visualizacao] */
vista = "corte"; // [corte,montado,eletronica,caixa_aberta]
mostrar_fios = true;
mostrar_rotulos = true;
qualidade = 32; // [16:16:64]

/* [Componentes aproximados em mm] */
// Breadboard de 400 pontos com AS DUAS reguas de alimentacao removidas.
// O corpo central tem 300 contatos; nao e uma breadboard inteira de 55 mm.
breadboard_dim = [83,35,9];
breadboard_pos = [-53,-34,3.5];
esp32_dim = [49,28,1.6];
esp32_pos = [-53,-32,15];
suporte_dim = [78,22,22];
suporte_pos = [-39,12,3.5];
bateria_d = 18.5;
bateria_l = 65;
cola_espessura = 0.5;

/* [Hidden] */
$fn = qualidade;
z_sensores = 91.4; // Base do abrigo R2: topo em 87.4, espacadores de 4 mm.
vermelho = [0.86,0.10,0.08];
preto = [0.13,0.15,0.18];

module legenda(txt, p, tamanho=2.5, cor="white") {
    if (mostrar_rotulos) color(cor) translate(p)
        linear_extrude(0.12) text(txt,size=tamanho,halign="center",valign="center");
}
module fio(pontos, cor, d=0.85) {
    color(cor) for(i=[0:len(pontos)-2]) hull() {
        translate(pontos[i]) sphere(d=d,$fn=8);
        translate(pontos[i+1]) sphere(d=d,$fn=8);
    }
}
module conector(p) {
    color(preto) translate(p) cube([2,2,3],center=true);
}
module placa(dim, cor) { color(cor) cube(dim); }

module breadboard() {
    translate(breadboard_pos) {
        color([0.94,0.92,0.83]) difference() {
            cube(breadboard_dim);
            translate([1,breadboard_dim[1]/2-1.5,7])
                cube([breadboard_dim[0]-2,3,3]);
            // 30 colunas; 5 contatos independentes de cada lado do canal.
            for(i=[0:29],s=[-1,1],j=[0:4])
                translate([4.67+2.54*i,breadboard_dim[1]/2+s*(3.81+2.54*j),8])
                    cube([0.9,0.9,2],center=true);
        }
        color([0.83,0.76,0.55]) translate([0,0,-cola_espessura])
            cube([breadboard_dim[0],breadboard_dim[1],cola_espessura]);
    }
}
module esp32() {
    translate(esp32_pos) {
        placa(esp32_dim,[0.04,0.15,0.16]);
        // Duas fileiras de headers encaixadas na protoboard.
        for(y=[1.53,26.93]) {
            color(preto) translate([5,y-1,-2.5]) cube([38,2,2.5]);
            color("gold") for(i=[0:14]) translate([4.67+2.54*i,y, -4])
                cylinder(d=0.6,h=6);
        }
        color("silver") translate([19,4,1.6]) cube([18,17,2.5]);
        color(preto) translate([39,2,1.6]) cube([9,21,0.4]);
        color("gold") for(i=[0:3]) translate([40+2*i,3,2.05]) cube([0.6,19,0.1]);
        color("silver") translate([-1,8,1.6]) cube([6,8,3]);
        color(preto) translate([9,9,1.6]) cube([5,5,1.3]);
        legenda("ESP32",[28,12,19.22-15],3,preto);
    }
}
module modulos_alimentacao() {
    // Breakouts sobre adaptadores isolantes/headers na breadboard.
    color(preto) translate([3,-32,12.5]) cube([24,15,2.5]);
    translate([2,-33,15]) {
        placa([26,17,1.6],[0.04,0.23,0.64]);
        color("silver") translate([0,5,1.6]) cube([6,7,3]);
        color(preto) translate([11,5,1.6]) cube([5,5,1.5]);
        legenda("TP4056",[16,13,1.7],2);
    }
    color(preto) translate([-1,-11,12.5]) cube([30,12,2.5]);
    translate([-2,-12,15]) {
        placa([34,17,1.6],[0.03,0.35,0.30]);
        color([0.20,0.22,0.25]) translate([10,4,1.6]) cube([10,10,5]);
        color("RoyalBlue") translate([23,5,1.6]) cube([8,7,6]);
        color("gold") translate([27,8.5,7.6]) cylinder(d=3,h=0.5);
        legenda("5V",[15,9,6.7],2.5);
    }
    // Chave interna acessivel com a caixa aberta; sem novo furo na caixa.
    color(preto) translate([37,-31,3.5]) cube([12,8,7]);
    color("silver") translate([40,-29,10.5]) cube([4,4,4]);
    legenda("S1",[43,-20,3.6],2.5,preto);
}
module suporte_bateria() {
    translate(suporte_pos) {
        // Adesivo sob o suporte: a celula permanece removivel.
        color([0.85,0.65,0.26]) translate([0,0,-cola_espessura])
            cube([suporte_dim[0],suporte_dim[1],cola_espessura]);
        color(preto) difference() {
            cube(suporte_dim);
            translate([2,1.5,2]) cube([suporte_dim[0]-4,suporte_dim[1]-3,suporte_dim[2]+1]);
            translate([8,-1,10]) cube([suporte_dim[0]-16,suporte_dim[1]+2,14]);
        }
        for(x=[2,suporte_dim[0]-2]) color("silver")
            translate([x,suporte_dim[1]/2,11.5]) rotate([0,90,0]) cylinder(d=8,h=0.8);
        color([0.48,0.20,0.65])
            translate([(suporte_dim[0]-bateria_l)/2,suporte_dim[1]/2,11.5])
                rotate([0,90,0]) cylinder(d=bateria_d,h=bateria_l);
        color("silver") translate([(suporte_dim[0]+bateria_l)/2,suporte_dim[1]/2,11.5])
            rotate([0,90,0]) cylinder(d=5,h=1);
        legenda("18650  3.7V",[39,11,21],3);
        legenda("+",[73,11,22.2],3);
    }
}
module sensores() {
    // Rotacao igual a da base com a baioneta travada.
    rotate([0,0,30]) {
        for(x=[-18,18]) {
            for(y=[-8,8]) color("Ivory") translate([x,y,87.4]) cylinder(d=4,h=4);
            // Abracadeira ilustrativa passa pelos rasgos y=+-14 da base.
            color(preto) difference() {
                translate([x-1,-15,83.6]) cube([2,30,x<0 ? 16.8 : 12.3]);
                translate([x-2,-13.5,85]) cube([4,27,x<0 ? 14.05 : 9.55]);
            }
        }
        translate([-25,-12,z_sensores]) {
            placa([14,24,1.6],[0.03,0.28,0.52]);
            color("DodgerBlue") difference() {
                translate([1,5,1.6]) cube([12,15,6]);
                for(x=[3:3:10],y=[7:3:17]) translate([x,y,6.4]) cube([1.2,1.8,2]);
            }
            legenda("DHT11",[7,2.5,1.7],2);
        }
        translate([11,-10,z_sensores]) {
            placa([14,20,1.6],[0.43,0.08,0.52]);
            color("silver") translate([4,8,1.6]) cube([5,4,1.5]);
            color(preto) translate([7,10,3.1]) cylinder(d=0.7,h=0.15);
            legenda("BMP280",[7,16,1.7],2);
        }
        if(mostrar_fios) {
            for(i=[0:2]) fio([[i-1,-2,89],[i-1,-5,96],[-21+3*i,-10,96],[-21+3*i,-10,93]],
                [vermelho,preto,"Orange"][i]);
            for(i=[0:3]) fio([[i-1.5,2,89],[i-1.5,5,97],[14+2.5*i,-8,97],[14+2.5*i,-8,93]],
                [vermelho,preto,"LimeGreen","Gold"][i]);
        }
    }
}
module cabos() {
    // Chicote de 7 vias, dentro do furo livre de 20 mm e do tubo.
    // Cor: vermelho 3V3, preto GND, laranja GPIO4, verde SDA21, amarelo SCL22.
    // Terminais e posicoes ilustrativos; pinagem fisica varia com o modulo.
    cores = [vermelho,preto,"Orange",vermelho,preto,"LimeGreen","Gold"];
    for(i=[0:6]) {
        x = -22+3*i;
        fio([[x,-2,13],[x,-2,25],[i-3,-4,29],[i-3,0,38],[i-3,0,82],
             i<3 ? [(i-1)*cos(30)+1,(i-1)*sin(30)-2*cos(30),89]
                 : [(i-4.5)*cos(30)-1,(i-4.5)*sin(30)+2*cos(30),89]],cores[i]);
        conector([x,-2,14]);
    }
    // Jumpers entre ESP32, contatos livres e placas de alimentacao.
    for(i=[0:4]) fio([[-28+i*4,-7,17],[-28+i*4,-5,22],[-22+i*3,-2,22],[-22+i*3,-2,13]],
        [vermelho,preto,"Orange","LimeGreen","Gold"][i]);
    // Bateria -> TP4056 B+/B-; OUT+ -> S1 -> step-up -> VIN ESP32.
    fio([[38,23,15],[48,23,16],[52,-9,13],[27,-28,18]],vermelho);
    fio([[-38,23,15],[-47,23,15],[-51,8,25],[34,8,26],[29,-24,26],[27,-24,18]],preto);
    fio([[27,-19,18],[34,-19,21],[43,-27,11]],vermelho);
    fio([[43,-25,11],[36,-16,22],[30,-8,18]],vermelho);
    fio([[26,-17,18],[33,-14,22],[30,-3,18]],preto);
    fio([[0,-8,18],[-3,-8,23],[-8,-27,23],[-8,-27,17]],vermelho);
    fio([[0,-3,18],[-4,-3,21],[-12,-27,21],[-12,-27,17]],preto);
}
module eletronica() {
    breadboard(); esp32(); modulos_alimentacao(); suporte_bateria(); sensores();
    if(mostrar_fios) cabos();
}
module estrutura() {
    if(vista=="montado") conjunto();
    if(vista=="corte") difference() {
        conjunto();
        translate([-200,-200,-1]) cube([400,200,220]);
    }
    if(vista=="caixa_aberta") {
        color("LightSteelBlue") difference() {
            caixa(); translate([-200,-200,8]) cube([400,200,50]);
        }
    }
}
assert(suporte_dim[0]<=108 && suporte_dim[1]<=24,"Suporte excede o espaco reservado.");
assert(bateria_d<=19 && bateria_l<=68,"Confira o suporte para esta celula.");
assert(breadboard_dim[0]<=83 && breadboard_dim[1]<=35,"Usar breadboard SEM reguas laterais.");
assert(vista=="corte" || vista=="montado" || vista=="eletronica" || vista=="caixa_aberta","Vista desconhecida.");
estrutura();
eletronica();
