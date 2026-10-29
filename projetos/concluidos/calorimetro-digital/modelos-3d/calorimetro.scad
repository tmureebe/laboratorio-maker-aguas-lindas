// ==========================================
// CALORÍMETRO 3D - OPENSCAD
// 4 FUROS EM PARES VERTICAIS
// ==========================================
//
// Configuração:
// - 2 furos alinhados verticalmente
// - outros 2 exatamente opostos
//
// Vista frontal:
//    O
//    O
//
// Vista traseira:
//    O
//    O
//
// ==========================================

$fn = 120;


// ==========================================
// MEDIDAS PRINCIPAIS
// ==========================================

// Parte INTERNA
diametro_interno = 85;      // 8,5 cm
altura_interna   = 145;     // 14,5 cm

// Estrutura
parede = 4;
base   = 6;

// Medidas externas
diametro_externo = diametro_interno + (parede * 2);
altura_total     = altura_interna + base;


// ==========================================
// FUROS LATERAIS
// ==========================================

diametro_furo = 12;

// Alturas dos pares
altura_furo_superior = 95;
altura_furo_inferior = 55;


// ==========================================
// DRENO
// ==========================================

diametro_dreno = 5;


// ==========================================
// CANALETAS DOS FIOS
// ==========================================

largura_canal = 14;
altura_canal  = 10;


// ==========================================
// CORPO PRINCIPAL
// ==========================================

difference() {

    // Corpo externo
    cylinder(
        h = altura_total,
        d = diametro_externo
    );

    // Interior vazio
    translate([0,0,base])
    cylinder(
        h = altura_interna + 1,
        d = diametro_interno
    );


    // ======================================
    // FURO DRENO
    // ======================================

    translate([0,0,-1])
    cylinder(
        h = base + 2,
        d = diametro_dreno
    );


    // ======================================
    // PAR DE FUROS - FRENTE
    // ======================================

    // FURO SUPERIOR
    translate([
        0,
        diametro_externo/2,
        altura_furo_superior
    ])
    rotate([90,0,0])
    cylinder(
        h = parede + 10,
        d = diametro_furo
    );

    // FURO INFERIOR
    translate([
        0,
        diametro_externo/2,
        altura_furo_inferior
    ])
    rotate([90,0,0])
    cylinder(
        h = parede + 10,
        d = diametro_furo
    );


    // ======================================
    // PAR DE FUROS - TRÁS (OPOSITOS)
    // ======================================

    // FURO SUPERIOR
    translate([
        0,
        -diametro_externo/2,
        altura_furo_superior
    ])
    rotate([90,0,0])
    cylinder(
        h = parede + 10,
        d = diametro_furo
    );

    // FURO INFERIOR
    translate([
        0,
        -diametro_externo/2,
        altura_furo_inferior
    ])
    rotate([90,0,0])
    cylinder(
        h = parede + 10,
        d = diametro_furo
    );


    // ======================================
    // CANALETAS PARA FIOS
    // ======================================

    for(i = [0:3]) {

        rotate([0,0,i*90])

        translate([
            -largura_canal/2,
            diametro_externo/2 - 2,
            altura_total - altura_canal
        ])

        cube([
            largura_canal,
            10,
            altura_canal + 1
        ]);
    }
}



// ==========================================
// TAMPA
// ==========================================

translate([130,0,0])

difference() {

    union() {

        // Tampa superior
        cylinder(
            h = 6,
            d = diametro_externo + 4
        );

        // Parte de encaixe
        translate([0,0,-10])
        cylinder(
            h = 10,
            d = diametro_interno - 1
        );
    }


    // ======================================
    // FURO CENTRAL
    // ======================================

    translate([0,0,-12])
    cylinder(
        h = 25,
        d = 14
    );


    // ======================================
    // FUROS DOS CABOS
    // ======================================

    for(i = [0:3]) {

        rotate([0,0,i*90])

        translate([
            diametro_interno/3,
            0,
            -12
        ])

        cylinder(
            h = 25,
            d = 6
        );
    }
}



// ==========================================
// MEDIDAS FINAIS
// ==========================================
//
// INTERNO:
// 85 mm
//
// EXTERNO:
// 93 mm
//
// ALTURA:
// 151 mm
//
// FUROS:
// - 2 na frente
// - 2 atrás
// - alinhados verticalmente
//
// ==========================================