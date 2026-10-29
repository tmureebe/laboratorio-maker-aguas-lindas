$fn = 120;

// ======================
// DIMENSÕES
// ======================

comprimento = 120;
largura = 80;
altura = 50;

parede = 3;

// Abertura menor da caixa.
// A tampa menor correspondente deve ter aba de 29,9 mm x 19,9 mm,
// isto é, 0,05 mm de folga em cada lado.
porta_largura = 30;
porta_altura = 20;

// Altura da abertura
altura_inicio_porta = 6;


// ======================
// CAIXA
// ======================

module caixa() {

    difference() {

        // Corpo externo
        cube([comprimento, largura, altura]);

        // Interior oco
        translate([parede, parede, parede])
            cube([
                comprimento - 2*parede,
                largura - 2*parede,
                altura
            ]);

        // Abertura da portinha
        translate([
            -1,
            (largura - porta_largura)/2,
            altura_inicio_porta
        ])
        cube([
            parede + 2,
            porta_largura,
            porta_altura
        ]);
    }

    // Beiral anti-chuva
    translate([
        0,
        (largura - porta_largura)/2 - 2,
        altura_inicio_porta + porta_altura
    ])
    cube([
        5,
        porta_largura + 4,
        3
    ]);
}


// ======================
// VISUALIZAÇÃO
// ======================

color("white")
caixa();
