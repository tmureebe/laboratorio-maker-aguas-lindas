// ESTACAO METEOROLOGICA INTEGRADA — unidades: mm.
// Arquivo independente: nao importa STL nem outros arquivos.
// Baseado nos arquivos locais caixa_com_tampas.scad e
// Stevenson_geometrico/stevenson_geometrico.scad.
// Caixa, tampa com duas travas, abrigo com baioneta e aletas encaixaveis.
// A compatibilidade e entre as pecas DESTA versao. Veja LEIA-ME.md.

/* [Visualizacao e exportacao] */
visualizacao = "montado"; // [montado,explodido,pecas,caixa,tampa_caixa,portinha,base_abrigo,aleta,teto,teste_baioneta,teste_tampa,teste_aletas,corte]
numero_aletas = 5; // [1:1:12]
separacao_explodido = 28;

/* [Caixa] */
comprimento_caixa = 120;
largura_caixa = 80;
altura_caixa = 50;
parede_caixa = 3;
espessura_fundo = 3;
espessura_tampa = 3;
beiral_tampa = 2;
folga_tampa = 0.3; // Folga POR LADO, nao diametral.
profundidade_saia = 16;
parede_saia = 2.4;
largura_lingueta = 12;
espessura_lingueta = 1.4;
ressalto_tampa = 0.9; // Alem da face interna da caixa.

/* [Porta de servico] */
porta_largura = 30;
porta_altura = 20;
altura_inicio_porta = 6;
folga_portinha = 0.3;
ressalto_portinha = 0.15; // Interferencia local nos quatro pequenos ressaltos.

/* [Uniao caixa e abrigo] */
folga_tubo = 0.3; // RADIAL. Tubo 42 -> soquete 42.6 mm.
parede_soquete = 4.8;
insercao_tubo = 18;
giro_baioneta = 30;
queda_baioneta = 1.2; // Assento em J: levantar antes de girar para soltar.
angulo_pino_baioneta = 10;
folga_angular_baioneta = 1;
altura_pino_baioneta = 3.6;
projecao_pino_baioneta = 3;
folga_axial_baioneta = 0.3;
diametro_colar = 56;
espessura_colar = 3;

/* [Abrigo e ventilacao] */
diametro_externo = 140;
diametro_plano = 100;
diametro_abertura = 60;
espessura = 2.4;
altura_saia = 20;
passo = 18;
diametro_cabos = 20;
diametro_tubo = 42;
parede_tubo = 2;
comprimento_tubo = 50;

/* [Encaixes das aletas] */
raio_fixacao = 42;
diametro_torre = 12;
diametro_pino = 6.4;
folga_encaixe = 0.3;
ressalto_trava = 0.5;
folga_axial = 0.3;
fenda_pino = 1.6;
altura_cabeca = 0.5;
altura_rampa = 1;
profundidade_receptor = 3.6;

/* [Alca interna para sensores] */
alca_sensores = true;
largura_alca = 32;
altura_alca = 22; // Projecao abaixo da face interna do teto.
profundidade_alca = 6;
espessura_alca = 3.2;

/* [Qualidade] */
resolucao = 96; // [48:24:192]

/* [Hidden] */
$fn = resolucao;
eps = 0.02;
altura_prato = altura_saia + espessura;
z_assento = altura_prato - passo;
altura_torre = passo - espessura;
diametro_interno_tubo = diametro_tubo - 2 * parede_tubo;
diametro_receptor = diametro_pino + 2 * folga_encaixe;
diametro_cabeca = diametro_receptor + 2 * ressalto_trava;
avanco_cabeca = folga_encaixe + ressalto_trava;
diametro_ponta = diametro_pino - 1;
largura_janela = diametro_pino + 2 * folga_encaixe;
z_ponte = altura_saia - profundidade_receptor;
z_raiz_pino = z_ponte - espessura;
z_ombro = z_assento - espessura - folga_axial;
z_cabeca = z_ombro - altura_cabeca;
z_ponta = z_cabeca - altura_rampa;
saia_x = comprimento_caixa - 2 * (parede_caixa + folga_tampa);
saia_y = largura_caixa - 2 * (parede_caixa + folga_tampa);
z_gancho_inferior = -profundidade_saia + 1;
z_gancho_superior = -profundidade_saia + 4.5;
z_janela_tampa = z_gancho_inferior - 0.3;
altura_janela_tampa = z_gancho_superior - z_janela_tampa + 0.4;
raio_soquete = diametro_tubo / 2 + folga_tubo;
raio_externo_soquete = raio_soquete + parede_soquete;
raio_pino_baioneta = diametro_tubo / 2 + projecao_pino_baioneta;
raio_canal_baioneta = raio_pino_baioneta + folga_tubo + 0.1;
z_fim_soquete = espessura_tampa - insercao_tubo;
z_piso_giro = -9;
z_piso_trava = z_piso_giro - queda_baioneta;
altura_canal_giro = altura_pino_baioneta + 2 * folga_axial_baioneta;
z_extremidade_tubo = altura_saia - comprimento_tubo;
z_base_montada = altura_caixa + z_fim_soquete - z_extremidade_tubo;
z_colar_na_base = z_extremidade_tubo + insercao_tubo;
z_pino_na_base = z_extremidade_tubo + z_piso_trava - z_fim_soquete;
altura_total = z_base_montada + (numero_aletas + 1) * passo + altura_prato;

module validar() {
    assert(comprimento_caixa >= 100 && largura_caixa >= 72
           && altura_caixa > insercao_tubo + espessura_fundo + 5,
           "Caixa pequena para o soquete, linguetas ou fundo.");
    assert(parede_caixa >= 2.4 && espessura_fundo >= 2.4
           && espessura_tampa >= 2.4 && parede_saia >= espessura_lingueta,
           "Confira as espessuras da caixa e da tampa.");
    assert(folga_tampa > 0 && folga_tampa <= 0.8 && folga_tubo > 0,
           "As folgas de montagem devem ser positivas.");
    assert(profundidade_saia >= 14 && espessura_lingueta >= 1.2
           && espessura_lingueta <= 1.8 && ressalto_tampa > 0,
           "Confira o comprimento e a espessura das linguetas.");
    assert(raio_externo_soquete + 3 < saia_y / 2 - parede_saia,
           "O soquete deve ficar separado da saia e das linguetas.");
    assert(raio_canal_baioneta + 1.6 < raio_externo_soquete
           && diametro_colar / 2 > raio_externo_soquete + 1,
           "A parede deve conter os pinos e o colar deve cobrir as entradas.");
    assert(giro_baioneta > 15 && giro_baioneta < 60
           && queda_baioneta > 0 && folga_axial_baioneta > 0,
           "Confira giro, queda e folga da baioneta.");
    assert(z_fim_soquete + 2 < z_piso_trava
           && z_piso_giro + altura_canal_giro < -2,
           "Preserve material acima e abaixo das ranhuras da baioneta.");
    assert(comprimento_tubo > insercao_tubo + altura_saia + 2,
           "Tubo curto: a borda do abrigo atingiria a tampa.");
    assert(diametro_cabos > 0 && diametro_cabos < diametro_interno_tubo
           && diametro_tubo < diametro_abertura && parede_tubo >= 2,
           "Confira tubo e passagem de cabos.");
    assert(diametro_externo > diametro_plano
           && diametro_plano > diametro_abertura && espessura >= 2,
           "Confira os diametros e a espessura dos pratos.");
    assert(passo > espessura && passo < altura_prato,
           "As saias dos pratos precisam se sobrepor em altura.");
    assert(raio_fixacao - diametro_torre / 2 > diametro_abertura / 2
           && raio_fixacao + diametro_torre / 2 < diametro_plano / 2,
           "As torres devem caber entre a abertura e a borda plana.");
    assert(diametro_torre - largura_janela >= 3.2
           && fenda_pino > 2 * ressalto_trava + 0.2
           && diametro_ponta - fenda_pino >= 2.4,
           "Confira apoios, fendas e cabecas das travas das aletas.");
    assert(z_raiz_pino - z_ombro >= 10 && z_ponta >= 0
           && passo + z_ponta > z_ponte + folga_axial,
           "Os pinos precisam flexionar e caber no receptor inferior.");
    assert(numero_aletas >= 1 && numero_aletas == floor(numero_aletas)
           && resolucao >= 48 && resolucao == floor(resolucao),
           "Use quantidades e resolucao inteiras.");
    assert(porta_largura >= 20 && porta_altura >= 15
           && altura_inicio_porta > espessura_fundo
           && altura_inicio_porta + porta_altura + 5 < altura_caixa,
           "A porta de servico deve ficar dentro da parede.");
    assert(!alca_sensores || (espessura_alca >= 2.4
           && largura_alca > 4*espessura_alca
           && profundidade_alca >= 3
           && altura_alca >= largura_alca/2 + espessura_alca
           && altura_alca < (numero_aletas+1)*passo - 3
           && sqrt(pow(largura_alca/2,2)+pow(profundidade_alca/2,2))
              < diametro_abertura/2 - 2),
           "Confira a espessura, abertura e folga da alca interna.");
    children();
}

// Cilindro interno compensado para nao reduzir a folga entre facetas.
module furo(diametro, altura) {
    cylinder(h = altura, d = diametro / cos(180 / resolucao));
}

module setor(ri, ro, z, h, inicio, fim) {
    rotate([0, 0, inicio])
        rotate_extrude(angle = fim - inicio, convexity = 8)
            polygon([[ri,z], [ro,z], [ro,z+h], [ri,z+h]]);
}

// Soquete interno, aberto embaixo. As tres ranhuras formam um J.
module soquete_bruto() {
    translate([0,0,z_fim_soquete])
        cylinder(r = raio_externo_soquete, h = insercao_tubo);
}

module cortes_baioneta() {
    translate([0,0,z_fim_soquete-eps])
        furo(2*raio_soquete, insercao_tubo+2*eps);
    a = angulo_pino_baioneta/2 + folga_angular_baioneta;
    for (angulo = [0,120,240]) rotate([0,0,angulo]) {
        // Entrada axial, seguida de giro com o abrigo levantado 1,2 mm.
        setor(raio_soquete-0.5, raio_canal_baioneta,
              z_piso_giro-folga_axial_baioneta,
              espessura_tampa-z_piso_giro+folga_axial_baioneta+eps, -a, a);
        setor(raio_soquete-0.5, raio_canal_baioneta,
              z_piso_giro-folga_axial_baioneta,
              altura_canal_giro, -a, giro_baioneta+a);
        // Ao final do giro, o conjunto desce e fica impedido de retornar.
        setor(raio_soquete-0.5, raio_canal_baioneta,
              z_piso_trava-folga_axial_baioneta,
              altura_canal_giro+queda_baioneta,
              giro_baioneta-a, giro_baioneta+a);
    }
}

module janela_trava_tampa() {
    for (s = [-1,1])
        translate([-largura_lingueta/2-0.5,
                   s*(largura_caixa/2-parede_caixa/2)-parede_caixa,
                   altura_caixa+z_janela_tampa])
            cube([largura_lingueta+1,2*parede_caixa,
                  altura_janela_tampa]);
}

module caixa() {
    difference() {
        translate([-comprimento_caixa/2,-largura_caixa/2,0])
            cube([comprimento_caixa,largura_caixa,altura_caixa]);
        translate([-comprimento_caixa/2+parede_caixa,
                   -largura_caixa/2+parede_caixa,espessura_fundo])
            cube([comprimento_caixa-2*parede_caixa,
                  largura_caixa-2*parede_caixa,altura_caixa]);
        janela_trava_tampa();
        translate([-comprimento_caixa/2-eps,-porta_largura/2,
                   altura_inicio_porta])
            cube([parede_caixa+2*eps,porta_largura,porta_altura]);
    }
    // Pequena cobertura inclinada da porta, projetada PARA FORA da caixa.
    translate([-comprimento_caixa/2,0,altura_inicio_porta+porta_altura+4])
        rotate([90,0,0])
            linear_extrude(height=porta_largura+6, center=true)
                polygon([[eps,0],[eps,3],[-5,0],[-5,-1]]);
}

// Gancho visto na secao YZ; duas linguetas opostas podem ser apertadas
// pelas janelas laterais. A saia tem recortes para deixar a flexao livre.
module lingueta_tampa() {
    y = saia_y/2;
    translate([-largura_lingueta/2,y-espessura_lingueta,-profundidade_saia])
        cube([largura_lingueta,espessura_lingueta,profundidade_saia+eps]);
    translate([-largura_lingueta/2,0,0]) rotate([90,0,90])
        linear_extrude(height=largura_lingueta)
            polygon([[y-eps,z_gancho_inferior],
                     [largura_caixa/2-parede_caixa+ressalto_tampa,
                      z_gancho_superior-0.8],
                     [largura_caixa/2-parede_caixa+ressalto_tampa,
                      z_gancho_superior],
                     [y-eps,z_gancho_superior]]);
}

// Origem da tampa: face inferior do prato em Z=0, topo em Z=3.
module tampa_caixa() {
    difference() {
        union() {
            translate([-comprimento_caixa/2-beiral_tampa,
                       -largura_caixa/2-beiral_tampa,0])
                cube([comprimento_caixa+2*beiral_tampa,
                      largura_caixa+2*beiral_tampa,espessura_tampa]);
            difference() {
                translate([-saia_x/2,-saia_y/2,-profundidade_saia])
                    cube([saia_x,saia_y,profundidade_saia+eps]);
                translate([-saia_x/2+parede_saia,-saia_y/2+parede_saia,
                           -profundidade_saia-eps])
                    cube([saia_x-2*parede_saia,saia_y-2*parede_saia,
                          profundidade_saia+3*eps]);
                for (s=[-1,1])
                    translate([-largura_lingueta/2-1,
                               s*saia_y/2-parede_saia-1,
                               -profundidade_saia-eps])
                        cube([largura_lingueta+2,2*parede_saia+2,
                              profundidade_saia+2*eps]);
            }
            lingueta_tampa();
            mirror([0,1,0]) lingueta_tampa();
            soquete_bruto();
        }
        cortes_baioneta();
    }
}

// Portinha por pressao; quatro ressaltos pequenos comprimem a aba fina.
// E uma tampa de servico removivel, nao um prensa-cabos ou vedacao IP.
module portinha() {
    lx = porta_largura-2*folga_portinha;
    ly = porta_altura-2*folga_portinha;
    cube([porta_largura+4,porta_altura+4,2],center=true);
    difference() {
        translate([0,0,2.5]) cube([lx,ly,3.1],center=true);
        translate([0,0,2.5]) cube([lx-2.4,ly-2.4,3.2],center=true);
    }
    for (s=[-1,1]) {
        hull() {
            translate([s*(lx/2-0.3),0,2]) cube([0.6,6,1],center=true);
            translate([s*(porta_largura/2+ressalto_portinha-0.3),0,2.5])
                cube([0.6,6,0.4],center=true);
        }
        hull() {
            translate([0,s*(ly/2-0.3),2]) cube([6,0.6,1],center=true);
            translate([0,s*(porta_altura/2+ressalto_portinha-0.3),2.5])
                cube([6,0.6,0.4],center=true);
        }
    }
    // Unha externa para puxar, integrada ao prato frontal.
    translate([0,-porta_altura/2-3,0]) cube([10,4,2],center=true);
}

module porta_montada() {
    translate([-comprimento_caixa/2-1,0,
               altura_inicio_porta+porta_altura/2])
        rotate([90,0,90]) portinha();
}

// Abrigo parametrico de revolucao: centro alto e borda inclinada.
module prato(abertura = 0) {
    rotate_extrude(convexity=8)
        polygon([[abertura/2,altura_saia],[diametro_plano/2,altura_saia],
                 [diametro_externo/2,0],[diametro_externo/2,espessura],
                 [diametro_plano/2,altura_prato],[abertura/2,altura_prato]]);
}

module nas_fixacoes() {
    for (angulo=[90,210,330]) rotate([0,0,angulo])
        translate([raio_fixacao,0,0]) children();
}

module suporte_encaixe() {
    difference() {
        translate([0,0,z_assento])
            cylinder(d=diametro_torre,h=altura_torre+eps);
        translate([-diametro_torre/2-eps,-largura_janela/2,z_assento-eps])
            cube([diametro_torre+2*eps,largura_janela,altura_torre+3*eps]);
    }
    translate([0,0,z_raiz_pino]) cylinder(d=diametro_torre,h=espessura);
}

module cabeca(altura) {
    hull() for (lado=[-1,1]) translate([lado*avanco_cabeca,0,0])
        cylinder(d=diametro_pino,h=altura);
}

module pino_bipartido() {
    difference() {
        union() {
            translate([0,0,z_cabeca])
                cylinder(d=diametro_pino,h=z_raiz_pino-z_cabeca+eps);
            translate([0,0,z_cabeca]) cabeca(altura_cabeca);
            hull() {
                translate([0,0,z_ponta]) cylinder(d=diametro_ponta,h=eps);
                translate([0,0,z_cabeca]) cabeca(eps);
            }
        }
        translate([-fenda_pino/2,-diametro_cabeca/2-eps,z_ponta-eps])
            cube([fenda_pino,diametro_cabeca+2*eps,z_raiz_pino-z_ponta+3*eps]);
    }
}

module torre_encaixe() { suporte_encaixe(); pino_bipartido(); }
module receptores() {
    nas_fixacoes() translate([0,0,altura_saia-eps])
        furo(diametro_receptor,espessura+2*eps);
}

module macho_baioneta(rampa=true) {
    translate([0,0,z_colar_na_base]) difference() {
        cylinder(d=diametro_colar,h=espessura_colar);
        translate([0,0,-eps]) furo(diametro_interno_tubo,espessura_colar+2*eps);
    }
    // Concordancia a 45 graus: sustenta o colar na orientacao de impressao.
    if (rampa) translate([0,0,z_colar_na_base+espessura_colar]) difference() {
        cylinder(d1=diametro_colar,d2=diametro_tubo,
                 h=(diametro_colar-diametro_tubo)/2);
        translate([0,0,-eps]) furo(diametro_interno_tubo,
                                 (diametro_colar-diametro_tubo)/2+2*eps);
    }
    for (angulo=[0,120,240]) hull() {
        setor(diametro_tubo/2-0.5,raio_pino_baioneta,
              z_pino_na_base,0.6,
              angulo-angulo_pino_baioneta/2,angulo+angulo_pino_baioneta/2);
        setor(diametro_tubo/2-0.5,diametro_tubo/2+0.1,
              z_pino_na_base+altura_pino_baioneta-eps,eps,
              angulo-angulo_pino_baioneta/2,angulo+angulo_pino_baioneta/2);
    }
}

module base_abrigo() {
    difference() {
        union() {
            prato(diametro_cabos/cos(180/resolucao));
            translate([0,0,z_extremidade_tubo]) difference() {
                cylinder(d=diametro_tubo,h=comprimento_tubo+eps);
                translate([0,0,-eps])
                    cylinder(d=diametro_interno_tubo,h=comprimento_tubo+3*eps);
            }
            macho_baioneta();
        }
        receptores();
        // Ranuras universais para pequenas abracadeiras: sem presumir
        // dimensoes ou furos de uma placa DHT11/BMP280 especifica.
        for (x=[-18,18],y=[-14,14])
            translate([x-1.5,y-4.5,altura_saia-eps])
                cube([3,9,espessura+2*eps]);
    }
}

module aleta() {
    difference() {
        union() { prato(diametro_abertura); nas_fixacoes() torre_encaixe(); }
        receptores();
    }
}
// Alca solidaria ao teto, voltada para DENTRO do abrigo.
// Permite suspender os sensores com abracadeiras, sem perfurar a cobertura.
// Na impressao com o teto invertido, as diagonais fecham o vao a 45 graus.
module alca_interna_sensores() {
    meia = largura_alca/2;
    fundo = altura_saia-altura_alca;
    ponta = fundo-1+espessura_alca*sqrt(2);
    rotate([90,0,0]) linear_extrude(height=profundidade_alca,center=true)
        difference() {
            polygon([[-meia,altura_saia+eps],[-meia,fundo+meia-1],
                     [-1,fundo],[1,fundo],[meia,fundo+meia-1],
                     [meia,altura_saia+eps]]);
            polygon([[-meia+espessura_alca,altura_saia+2*eps],
                     [-meia+espessura_alca,ponta+meia-espessura_alca],
                     [0,ponta],
                     [meia-espessura_alca,ponta+meia-espessura_alca],
                     [meia-espessura_alca,altura_saia+2*eps]]);
        }
}
module teto() {
    prato();
    nas_fixacoes() torre_encaixe();
    if (alca_sensores) alca_interna_sensores();
}

module imprimir_prato() {
    translate([0,0,altura_prato]) rotate([180,0,0]) children();
}
module imprimir_tampa() {
    translate([0,0,espessura_tampa]) rotate([180,0,0]) tampa_caixa();
}
module imprimir_portinha() { translate([0,0,1]) portinha(); }

module conjunto(explodir=0) {
    color("LightSteelBlue") caixa();
    color("LightSteelBlue") porta_montada();
    color("SteelBlue") translate([0,0,altura_caixa+explodir]) tampa_caixa();
    translate([0,0,z_base_montada+2*explodir]) rotate([0,0,giro_baioneta]) {
        color("Ivory") base_abrigo();
        for (i=[1:numero_aletas])
            color(i%2==0 ? "WhiteSmoke" : "Ivory")
                translate([0,0,i*(passo+explodir)]) aleta();
        color("White") translate([0,0,(numero_aletas+1)*(passo+explodir)]) teto();
    }
}

// Uma unidade de cada tipo; para imprimir o conjunto sao necessarias
// numero_aletas copias da aleta. Exporte cada tipo separadamente.
module pecas() {
    caixa();
    translate([155,0,0]) imprimir_tampa();
    translate([255,0,0]) imprimir_portinha();
    translate([0,165,0]) imprimir_prato() base_abrigo();
    translate([160,165,0]) imprimir_prato() aleta();
    translate([320,165,0]) imprimir_prato() teto();
}

module teste_baioneta() {
    // Soquete real num anel curto: imprimir com a face da tampa na mesa.
    translate([-40,0,espessura_tampa]) rotate([180,0,0]) difference() {
        union() {
            cylinder(d=diametro_colar+4,h=espessura_tampa);
            soquete_bruto();
        }
        cortes_baioneta();
    }
    // Tubo curto real, colar apoiado na mesa e pinos para cima.
    translate([40,0,insercao_tubo+espessura_colar]) rotate([180,0,0])
        translate([0,0,-z_extremidade_tubo]) union() {
            translate([0,0,z_extremidade_tubo]) difference() {
                cylinder(d=diametro_tubo,h=insercao_tubo+espessura_colar);
                translate([0,0,-eps])
                    cylinder(d=diametro_interno_tubo,
                             h=insercao_tubo+espessura_colar+2*eps);
            }
            macho_baioneta(false);
        }
}

module teste_tampa() {
    // Janela e lingueta na orientacao real de impressao.
    translate([-20,0,0]) difference() {
        translate([-10,0,0]) cube([20,parede_caixa,profundidade_saia]);
        translate([-largura_lingueta/2-0.5,-eps,
                   profundidade_saia+z_janela_tampa])
            cube([largura_lingueta+1,parede_caixa+2*eps,
                  altura_janela_tampa]);
    }
    translate([20,0,espessura_tampa]) rotate([180,0,0])
        translate([0,-saia_y/2,0]) union() {
            translate([-10,saia_y/2-5,0]) cube([20,10,espessura_tampa]);
            lingueta_tampa();
            // Guia externa da amostra: encosta na face externa da plaqueta
            // e reproduz automaticamente a folga interna de 0,3 mm.
            translate([-10,saia_y/2+parede_caixa+folga_tampa,-4])
                cube([20,1.2,4+eps]);
        }
}

module teste_aletas() {
    for (i=[0,1]) translate([i*28,0,0]) imprimir_prato() {
        difference() {
            union() {
                translate([-10,-10,altura_saia]) cube([20,20,espessura]);
                if (i==0) suporte_encaixe(); else torre_encaixe();
            }
            if (i==0) translate([0,0,altura_saia-eps])
                furo(diametro_receptor,espessura+2*eps);
        }
    }
}

validar() {
    if (visualizacao=="montado") conjunto();
    else if (visualizacao=="explodido") conjunto(separacao_explodido);
    else if (visualizacao=="pecas") pecas();
    else if (visualizacao=="caixa") caixa();
    else if (visualizacao=="tampa_caixa") imprimir_tampa();
    else if (visualizacao=="portinha") imprimir_portinha();
    else if (visualizacao=="base_abrigo") imprimir_prato() base_abrigo();
    else if (visualizacao=="aleta") imprimir_prato() aleta();
    else if (visualizacao=="teto") imprimir_prato() teto();
    else if (visualizacao=="teste_baioneta") teste_baioneta();
    else if (visualizacao=="teste_tampa") teste_tampa();
    else if (visualizacao=="teste_aletas") teste_aletas();
    else if (visualizacao=="corte") difference() {
        conjunto();
        translate([-200,-200,-eps]) cube([400,200,altura_total+2]);
    }
    else assert(false,"Visualizacao desconhecida.");
}
