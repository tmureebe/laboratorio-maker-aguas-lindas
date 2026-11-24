// Asa ampliada para a câmara V7. Unidade: mm.
// Geometria aerodinâmica em X/Z; eixo de articulação Y, origem no eixo.
// perfil curvado baseado nas equações de quatro dígitos, com espessura
// aplicada verticalmente e bordo de fuga engrossado: NÃO é NACA certificado.
corda = 190;
envergadura = 114;
curvatura = 0.02;
pos_curvatura = 0.4;
espessura_relativa = 0.08;
bordo_fuga = 0.8;
altura_corda = 18;
amostras = 240;
modo = "imprimir"; // imprimir, montada, corpo, encaixe
angulo = 0;

function u(i) = (1-cos(180*i/amostras))/2;
function camber(x) = corda*curvatura*(x < pos_curvatura
    ? (2*pos_curvatura*x-x*x)/pow(pos_curvatura,2)
    : (1-2*pos_curvatura+2*pos_curvatura*x-x*x)/pow(1-pos_curvatura,2));
function meia_espessura(x) = 5*espessura_relativa*corda*
    (0.2969*sqrt(x)-0.1260*x-0.3516*x*x+0.2843*x*x*x-0.1036*x*x*x*x)
    + bordo_fuga*x/2;
function ponto(i,sinal) = [corda*(u(i)-0.5),
    altura_corda+camber(u(i))+sinal*meia_espessura(u(i))];
perfil = concat([for(i=[0:amostras]) ponto(i,1)],
                [for(i=[amostras:-1:1]) ponto(i,-1)]);

module corpo() {
    rotate([90,0,0]) linear_extrude(height=envergadura,center=true)
        polygon(perfil);
}

module encaixe_original() {
    // Cópia geométrica sem escala do encaixe B: disco Ø16 × 15,
    // furo Ø3,4. Corte abaixo do início da superfície aerodinâmica antiga.
    intersection() {
        translate([-12,-45,21.168132782]) rotate([-90,0,0])
            import("../../01_IMPRESSAO_3D/02_alternativas_escolher_uma/18_asa_B_curvada.stl");
        translate([-50,-50,-10]) cube([100,100,24]);
    }
}

module asa() {
    union() {
        corpo();
        encaixe_original();
        // Continuação do pescoço, dentro do vão livre entre as orelhas.
        translate([-4,-5,11]) cube([8,10,13]);
    }
}

if (modo == "imprimir") {
    // Ponta plana apoiada na mesa. Altura = envergadura.
    translate([corda/2,8,envergadura/2])
        rotate([-90,0,0]) asa();
} else if (modo == "montada") {
    translate([300,0,104.4]) rotate([0,angulo,0]) asa();
} else if (modo == "corpo") corpo();
else if (modo == "encaixe") encaixe_original();
else assert(false,"Modo desconhecido");
