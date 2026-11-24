// Chave tátil KFC-A06, 12 × 12 × 4,3 mm, quatro terminais.
// Modelo externo para verificar espaço e encaixe. Todas as medidas em mm.
// Origem no centro da face inferior do corpo (z = 0). Terminais em z negativo.
//
// Produto e fotografia:
// https://www.casadarobotica.com.br/kit-10-chaves-tactil-push-button-botao-12x12x4-3-mm-arduino
// Cotas complementares aproximadas, com base na foto e no desenho da
// chave similar CUI Devices TS14, p. 2:
// https://www.mouser.com/datasheet/2/670/ts14-2943999.pdf
// Para um encaixe justo ou uma PCB, confira essas cotas na peça física.

/* [Dimensões nominais] */
// Lado do corpo quadrado
lado_corpo = 12;
// Altura da base ao topo do atuador
altura_total = 4.3;

/* [Dimensões complementares aproximadas] */
// Altura até a borda superior do corpo
altura_corpo = 3.5;
diametro_atuador = 7.0;
// Distância entre os centros das duas fileiras de terminais
passo_terminais_x = 12.5;
// Distância entre os centros dos terminais de uma mesma fileira
passo_terminais_y = 5.0;
// Comprimento dos terminais abaixo da base do corpo
comprimento_terminais = 3.5;
largura_terminal = 1.0;
espessura_terminal = 0.3;

/* [Exibição] */
mostrar_terminais = true;

botao_kfc_a06(com_terminais = mostrar_terminais);

// Use em outro projeto com use <botao_tatil_KFC-A06_12x12x4p3.scad>.
module botao_kfc_a06(com_terminais = true) {
    $fn = 64;
    sobreposicao = 0.02;
    parede = 0.42;
    lado_chapa = lado_corpo - 2 * parede;
    espessura_chapa = 0.25;
    topo_chapa = altura_corpo - 0.04;
    base_chapa = topo_chapa - espessura_chapa;
    chanfro_atuador = 0.12;

    color("#252629")
        difference() {
            linear_extrude(height = altura_corpo)
                quadrado_chanfrado(lado_corpo, 0.55);
            translate([0, 0, base_chapa])
                linear_extrude(height = espessura_chapa + 0.1)
                    quadrado_chanfrado(lado_chapa, 0.35);
        }

    color("#b9bdc1")
        translate([0, 0, base_chapa - sobreposicao])
            linear_extrude(height = espessura_chapa + sobreposicao)
                quadrado_chanfrado(lado_chapa, 0.35);

    color("#1a1b1c") {
        translate([0, 0, topo_chapa - sobreposicao])
            cylinder(d = diametro_atuador + 0.35, h = 0.14);

        translate([0, 0, topo_chapa + 0.10])
            cylinder(d = diametro_atuador,
                     h = altura_total - topo_chapa - 0.10 - chanfro_atuador
                         + sobreposicao);

        translate([0, 0, altura_total - chanfro_atuador])
            cylinder(d1 = diametro_atuador,
                     d2 = diametro_atuador - 2 * chanfro_atuador,
                     h = chanfro_atuador);

        // Quatro pontos de fixação da chapa visíveis na foto.
        posicao_fixacao = lado_chapa / 2 - 1.15;
        for (x = [-posicao_fixacao, posicao_fixacao],
             y = [-posicao_fixacao, posicao_fixacao])
            translate([x, y, topo_chapa - sobreposicao])
                cylinder(d1 = 1.50, d2 = 1.32, h = 0.31);
    }

    if (com_terminais)
        color("#c3c7cb")
            for (y = [-passo_terminais_y / 2, passo_terminais_y / 2]) {
                translate([0, y, 0]) terminal_kfc_a06();
                mirror([1, 0, 0]) translate([0, y, 0]) terminal_kfc_a06();
            }
}

module quadrado_chanfrado(lado, chanfro) {
    a = lado / 2;
    b = a - chanfro;
    polygon([[-b, -a], [b, -a], [a, -b], [a, b],
             [b, a], [-b, a], [-a, b], [-a, -b]]);
}

module terminal_kfc_a06() {
    x_passo = passo_terminais_x / 2;
    x_raiz = lado_corpo / 2 - 0.55;
    meia_espessura = espessura_terminal / 2;
    z_raiz = 0.68;
    z_dobra = -0.39 * comprimento_terminais;
    z_retorno = -0.78 * comprimento_terminais;

    // Perfil lateral da lâmina em XZ, extrudado ao longo de Y.
    translate([0, largura_terminal / 2, 0])
        rotate([90, 0, 0])
            linear_extrude(height = largura_terminal)
                polygon([
                    [x_raiz, z_raiz + meia_espessura],
                    [x_passo + meia_espessura, z_raiz + meia_espessura],
                    [x_passo + 0.42 + meia_espessura, z_dobra],
                    [x_passo + meia_espessura, z_retorno],
                    [x_passo + meia_espessura, -comprimento_terminais],
                    [x_passo - meia_espessura, -comprimento_terminais],
                    [x_passo - meia_espessura, z_retorno],
                    [x_passo + 0.42 - meia_espessura, z_dobra],
                    [x_passo - meia_espessura, z_raiz - meia_espessura],
                    [x_raiz, z_raiz - meia_espessura]
                ]);
}
