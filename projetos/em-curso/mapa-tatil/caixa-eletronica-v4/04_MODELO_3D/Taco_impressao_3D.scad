/* Taco de fixacao da tampa C1 — caixa V4. Todas as medidas em mm.
   STL: imprimir na orientacao inicial, com a abertura do furo para cima.
   A face de colagem e a extremidade y=altura na orientacao de impressao.
   Os oito tacos sao identicos; girar os traseiros 180 graus na montagem.
   Ver 07_IMPRESSAO_3D/LEIA.md para parametros e montagem. */

/* [Exportacao] */
modo = "impressao"; // [impressao,lote,montagem]
quantidade = 8; // [1:8]
colunas = 4; // [1:4]
intervalo = 6;

/* [Taco] */
largura = 20;
profundidade = 20;
altura_nominal = 44;
// Reduzir pela base se o ensaio a seco exigir folga para tolerancias/cola.
folga_altura = 0;
diametro_guia = 2.8;
profundidade_guia = 18;
// Eixo sempre 12 abaixo da face de colagem: z=47-12=35 na caixa.
distancia_eixo_ao_topo = 12;

/* [Hidden] */
$fn = 64;
altura = altura_nominal - folga_altura;
epsilon = 0.02;

module taco_montagem() {
    assert(largura > diametro_guia + 4);
    assert(profundidade_guia > 0 && profundidade_guia <= profundidade - 2);
    assert(diametro_guia > 0);
    assert(folga_altura >= 0 && folga_altura < altura_nominal);
    assert(distancia_eixo_ao_topo > diametro_guia/2 + 2 &&
           altura - distancia_eixo_ao_topo > diametro_guia/2 + 2);
    // Montagem: x=largura, y=profundidade, z=altura; cola em z=altura.
    // Furo cego entra por y=0; nao atravessa a face de colagem.
    difference() {
        cube([largura, profundidade, altura]);
        translate([largura/2, -epsilon, altura-distancia_eixo_ao_topo])
            rotate([-90,0,0])
                cylinder(d=diametro_guia, h=profundidade_guia+epsilon);
    }
}

module taco_impressao() {
    // Rotacao propria: furo vertical aberto para cima, sem suporte interno.
    // Envelope na mesa: 20 x 44; altura de impressao: 20.
    translate([0,0,profundidade]) rotate([-90,0,0]) taco_montagem();
}

if(modo == "impressao") taco_impressao();
else if(modo == "montagem") taco_montagem();
else if(modo == "lote") {
    assert(quantidade >= 1 && quantidade <= 8 && quantidade == floor(quantidade));
    assert(colunas >= 1 && colunas == floor(colunas));
    assert(intervalo > 0);
    for(i=[0:quantidade-1])
        translate([(i%colunas)*(largura+intervalo),
                   floor(i/colunas)*(altura+intervalo),0]) taco_impressao();
}
else assert(false,"Modo invalido");
