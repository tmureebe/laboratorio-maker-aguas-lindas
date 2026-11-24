/*
 BESOURO DIDÁTICO — revisão 2, inspirado na silhueta de um escaravelho.
 Comprimento nominal total de 30 mm, incluindo as antenas.
 Seis pernas curtas; antenas pequenas com ponta engrossada; pronoto largo;
 cabeça baixa e integrada; dois élitros com sutura e estrias longitudinais.

 Peça única, face inferior plana em Z=0. Imprimir nessa orientação.
 Modelo estilizado, sem reprodução exata de uma espécie.
 A versão anterior foi preservada em versao_anterior/.
*/
comprimento_mm = 30;
qualidade = 48;              // 32 para editar; 48 para exportar.
largura_pernas_mm = 1.8;
largura_antenas_mm = 1.3;
mostrar_estrias = true;

$fn = qualidade;
escala = comprimento_mm / 30;
assert(comprimento_mm > 0, "O comprimento deve ser positivo.");
assert(qualidade >= 24, "Use qualidade >= 24.");
assert(largura_pernas_mm >= 1.6 && largura_antenas_mm >= 1.2,
       "Mantenha pernas >= 1,6 e antenas >= 1,2 mm na escala de 30 mm.");

module elipsoide(p, r) {
    translate([p[0], p[1], 0]) scale(r) sphere(r=1);
}

// Extremidades redondas e paredes inclinadas para dentro: o topo
// inteiro se apoia sobre a seção inferior. Sem arcos ou peças suspensas.
module haste(a, b, raio_a, raio_b, altura) {
    hull() {
        translate([a[0], a[1], 0])
            cylinder(h=altura, r1=raio_a, r2=raio_a*0.76, $fn=24);
        translate([b[0], b[1], 0])
            cylinder(h=altura, r1=raio_b, r2=raio_b*0.76, $fn=24);
    }
}
module trilha(pontos, largura) {
    for (i=[0:len(pontos)-2])
        hull() {
            translate(pontos[i]) circle(d=largura, $fn=12);
            translate(pontos[i+1]) circle(d=largura, $fn=12);
        }
}

module volume_elitros() {
    // Carapaça larga, com a maior parte do volume do animal.
    // Extremidade posterior em Y=-16; antenas chegam a Y=+14.
    elipsoide([0,-5.8], [8.8,10.2,6.5]);
}
module linhas_elitros_2d() {
    trilha([[0,-14.8],[0,3.8]], 0.6);
    if (mostrar_estrias)
        for (s=[-1,1]) {
            trilha([[s*1.7,-13.4],[s*2.8,-8],[s*2.8,-3],[s*2.1,1]], 0.45);
            trilha([[s*3.7,-12.3],[s*5.2,-7.6],[s*5.1,-3.2],[s*4.2,0.5]], 0.45);
        }
}
module elitros() {
    difference() {
        volume_elitros();
        // Incisões de 0,35 mm que acompanham a superfície da carapaça.
        // O corte começa em Z=1,8: a base permanece inteiriça.
        difference() {
            translate([0,0,1.8]) linear_extrude(height=10)
                linhas_elitros_2d();
            translate([0,0,-0.35]) volume_elitros();
        }
    }
}

module pronoto() {
    // Placa larga entre cabeça e élitros, sem cintura estreita.
    elipsoide([0,5.0], [7.8,4.4,4.8]);
}
module cabeca() {
    // Perfil baixo: a cabeça não é uma esfera sobre um pescoço.
    hull() {
        elipsoide([0,9.4], [4.3,2.0,2.9]);
        elipsoide([0,10.9], [3.3,1.5,2.3]);
    }
    for (s=[-1,1])
        elipsoide([s*3.4,10.25], [0.85,1.15,2.35]);
}

module seis_pernas() {
    r=largura_pernas_mm/2;
    for (s=[-1,1]) {
        // Anteriores: saem das laterais do tórax, não da cabeça.
        haste([s*5.2,6.4],[s*8.4,7.5],r*1.12,r,1.55);
        haste([s*8.4,7.5],[s*9.9,6.6],r,r*0.82,1.55);
        // Médias: curtas e dobradas junto ao corpo.
        haste([s*6.0,3.8],[s*10.0,3.2],r*1.12,r,1.55);
        haste([s*10.0,3.2],[s*10.7,1.2],r,r*0.82,1.55);
        // Posteriores: raiz torácica, em parte coberta pelos élitros.
        haste([s*4.7,1.3],[s*9.8,-2.5],r*1.12,r,1.55);
        haste([s*9.8,-2.5],[s*9.6,-5.5],r,r*0.82,1.55);
    }
}
module duas_antenas() {
    r=largura_antenas_mm/2;
    for (s=[-1,1]) {
        // Antenas bem menores que as pernas e dirigidas para a frente.
        haste([s*3.2,10.5],[s*4.4,11.8],r,r,1.15);
        haste([s*4.4,11.8],[s*3.9,13.3],r,r,1.15);
        elipsoide([s*3.9,13.3], [1.05,0.7,1.15]);
    }
}
module besouro() {
    intersection() {
        union() {
            color([0.19,0.14,0.07]) seis_pernas();
            color([0.21,0.16,0.08]) duas_antenas();
            color([0.46,0.32,0.12]) elitros();
            color([0.32,0.22,0.08]) pronoto();
            color([0.25,0.17,0.06]) cabeca();
        }
        // Todo o animal, inclusive antenas e pernas, encosta em Z=0.
        translate([-20,-20,0]) cube([40,40,15]);
    }
}
scale([escala,escala,escala]) besouro();
