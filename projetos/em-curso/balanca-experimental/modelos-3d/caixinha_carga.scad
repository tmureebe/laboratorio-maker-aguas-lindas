lado_base = 120;
altura_base = 20;

// rebaixo externo em cada canto
r1_x = 37;          // lado maior, paralelo ao eixo x
r1_y = 34;          // lado menor
r1_h = 2;           // profundidade

dist_borda = 10;    // distância às bordas externas

// rebaixo interno
margem_y = 2;       // 2 mm dos lados de 37 mm
margem_x_interna = 2; // 2 mm do lado de 34 mm mais distante da borda
margem_x_externa = 0; // 0 mm do lado de 34 mm mais próximo da borda
r2_h = 9;           // profundidade adicional abaixo do primeiro rebaixo

// abertura lateral quadrada
abertura_lado = 20;
abertura_h = 11;    // profundidade a partir do topo

eps = 0.01;

// dimensões do segundo rebaixo
r2_x = r1_x - margem_x_interna - margem_x_externa; // 35
r2_y = r1_y - 2*margem_y;                          // 30

module canto_rebaixado(x0, y0, lado_externo_esquerda=true) {

    // 1) rebaixo externo: 37 x 34 x 2
    translate([x0, y0, altura_base - r1_h])
        cube([r1_x, r1_y, r1_h + eps]);

    // 2) rebaixo interno: encostado no lado de 34 mm próximo da borda
    x2 = lado_externo_esquerda ? x0 : x0 + margem_x_interna;
    y2 = y0 + margem_y;

    translate([x2, y2, altura_base - (r1_h + r2_h)])
        cube([r2_x, r2_y, r2_h + eps]);

    // 3) abertura lateral quadrada 20 x 20, centrada no lado de 34 mm externo
    x_centro_abertura = lado_externo_esquerda ? x0 : x0 + r1_x;
    y_centro_abertura = y0 + r1_y/2;

    translate([
        x_centro_abertura - abertura_lado/2,
        y_centro_abertura - abertura_lado/2,
        altura_base - abertura_h
    ])
        cube([abertura_lado, abertura_lado, abertura_h + eps]);
}

difference() {
    // bloco base
    cube([lado_base, lado_base, altura_base]);

    // canto inferior esquerdo
    canto_rebaixado(dist_borda, dist_borda, true);

    // canto inferior direito
    canto_rebaixado(lado_base - dist_borda - r1_x, dist_borda, false);

    // canto superior esquerdo
    canto_rebaixado(dist_borda, lado_base - dist_borda - r1_y, true);

    // canto superior direito
    canto_rebaixado(lado_base - dist_borda - r1_x, lado_base - dist_borda - r1_y, false);
}