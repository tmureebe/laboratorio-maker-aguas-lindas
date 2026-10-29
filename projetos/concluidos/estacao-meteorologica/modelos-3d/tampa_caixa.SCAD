//
// ======================================================
// TAMPAS AJUSTADAS PARA A CAIXA
// Folga lateral: 0,05 mm por lado
// ======================================================

$fn = 120;

// ------------------------
// PARÂMETROS GERAIS
// ------------------------

folga_lateral = 0.05;

// Dimensões externas da caixa associada
comprimento_caixa = 120;
largura_caixa = 80;
altura_caixa = 50;
parede_caixa = 3;

// Abertura menor da caixa
porta_largura = 30;
porta_altura = 20;

// Distância entre as peças na mesa de impressão
espacamento = 20;

// ======================================================
// PARTE 1 - TAMPA PRINCIPAL
// ======================================================

// ------------------------
// PARÂMETROS DA TAMPA PRINCIPAL
// ------------------------

comprimento_tampa = comprimento_caixa;
largura_tampa = largura_caixa;
espessura_tampa = 3;

// Aba que entra no vão interno da caixa.
// Vão interno: 114 mm x 74 mm.
// Com 0,05 mm de folga por lado: 113,9 mm x 73,9 mm.
comprimento_aba = comprimento_caixa - 2*parede_caixa - 2*folga_lateral;
largura_aba = largura_caixa - 2*parede_caixa - 2*folga_lateral;
profundidade_aba = 8;

diametro_furo = 41.9;
raio_furo = diametro_furo/2;

// Posições
aba_x = (comprimento_tampa - comprimento_aba)/2;
aba_y = (largura_tampa - largura_aba)/2;

centro_x = comprimento_tampa/2;
centro_y = largura_tampa/2;

// ------------------------
// MÓDULO TAMPA PRINCIPAL
// ------------------------

module tampa_principal()
{
    difference()
    {
        union()
        {
            // Tampa externa
            cube([
                comprimento_tampa,
                largura_tampa,
                espessura_tampa
            ]);

            // Aba de encaixe
            translate([
                aba_x,
                aba_y,
                -profundidade_aba
            ])
            cube([
                comprimento_aba,
                largura_aba,
                profundidade_aba
            ]);
        }

        // Furo central
        translate([
            centro_x,
            centro_y,
            -profundidade_aba-1
        ])
        cylinder(
            h=profundidade_aba+espessura_tampa+2,
            r=raio_furo
        );
    }
}

// ======================================================
// PARTE 2 - TAMPA MENOR DA ABERTURA LATERAL
// ======================================================

// ------------------------
// PARÂMETROS DA TAMPA MENOR
// ------------------------

// Aba externa da tampa menor: sobra de 2 mm em cada lado da abertura.
// Abertura: 30 mm x 20 mm.
// Tampa externa: 34 mm x 24 mm.
tampa_menor_aba_externa = 2;
tampa_menor_largura = porta_largura + 2*tampa_menor_aba_externa;
tampa_menor_altura = porta_altura + 2*tampa_menor_aba_externa;
tampa_menor_espessura = 2;

// Aba que entra no buraco menor da caixa.
// Abertura: 30 mm x 20 mm.
// Com 0,05 mm de folga por lado: 29,9 mm x 19,9 mm.
tampa_menor_profundidade_aba = parede_caixa;
tampa_menor_aba_largura = porta_largura - 2*folga_lateral;
tampa_menor_aba_altura = porta_altura - 2*folga_lateral;

// ------------------------
// MÓDULO TAMPA MENOR
// ------------------------

module tampa_menor()
{
    union()
    {
        // Tampa externa
        cube([
            tampa_menor_largura,
            tampa_menor_altura,
            tampa_menor_espessura
        ]);

        // Aba de encaixe
        translate([
            (tampa_menor_largura - tampa_menor_aba_largura)/2,
            (tampa_menor_altura - tampa_menor_aba_altura)/2,
            -tampa_menor_profundidade_aba
        ])
        cube([
            tampa_menor_aba_largura,
            tampa_menor_aba_altura,
            tampa_menor_profundidade_aba
        ]);
    }
}

// ======================================================
// MONTAGEM FINAL
// ======================================================

// Tampa principal
translate([0,0,0])
    tampa_principal();

// Tampa menor ao lado da principal
translate([
    comprimento_tampa + espacamento,
    0,
    0
])
    tampa_menor();
