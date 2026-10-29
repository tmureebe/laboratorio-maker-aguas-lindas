// ========================
// PRISMA TRIANGULAR = T1+T2+T3, COM PINOS/RASGOS
// Thiago — modelo paramétrico para impressão 3D
// Unidades: mm
// ========================

// ----- Parâmetros geométricos do prisma
h  = 60;                      // altura do prisma
A  = [0,   0, 0];
B  = [100, 0, 0];
C  = [30, 70, 0];

A1 = A + [0,0,h];
B1 = B + [0,0,h];
C1 = C + [0,0,h];

// ----- Encaixes (ajuste conforme a impressora/material)
pin_r        = 2.0;           // raio do pino (macho)
pin_h        = 4.0;           // altura do pino além do plano da face
clearance    = 0.30;          // folga total (diferença de raio do furo)
tip_shrink   = 0.30;          // conicidade da ponta do pino (facilita entrada)
edge_margin  = 6.0;           // distância mínima do pino às arestas da face

// ----- Visualização/exportação
// 0 = prisma inteiro (união) | 1 = T1 | 2 = T2 | 3 = T3
which_piece = 0;

// ========================
// Utilitários vetoriais
// ========================
function vadd(a,b)      = [a[0]+b[0], a[1]+b[1], a[2]+b[2]];
function vsub(a,b)      = [a[0]-b[0], a[1]-b[1], a[2]-b[2]];
function smul(s,a)      = [s*a[0], s*a[1], s*a[2]];
function dot(a,b)       = a[0]*b[0] + a[1]*b[1] + a[2]*b[2];
function cross(a,b)     = [ a[1]*b[2]-a[2]*b[1], a[2]*b[0]-a[0]*b[2], a[0]*b[1]-a[1]*b[0] ];
function norm(a)        = sqrt(dot(a,a));
function normalize(a)   = let(n=norm(a)) (n==0 ? [0,0,0] : smul(1/n,a));

function tri_centroid(P,Q,R) = smul(1/3, vadd(P, vadd(Q,R)));

function min3(a,b,c)    = min(a, min(b,c));
function dist(P,Q)      = norm(vsub(P,Q));

// Menor aresta do triângulo
function min_edge_len(P,Q,R) =
    min3(dist(P,Q), dist(Q,R), dist(R,P));

// Moldura ortonormal da face (coloca a face no plano XY, normal em +Z)
function face_frame(P,Q,R) =
    let( ex = normalize(vsub(Q,P)),
         n  = normalize(cross(vsub(Q,P), vsub(R,P))),
         ez = n,
         ey = cross(ez, ex),
         O  = tri_centroid(P,Q,R)
    ) [
        [ex[0], ey[0], ez[0], O[0]],
        [ex[1], ey[1], ez[1], O[1]],
        [ex[2], ey[2], ez[2], O[2]],
        [0,     0,     0,     1   ]
    ];

// Dois pontos para pinos em torno do centróide, ao longo de ex
// Escolhemos deslocamento com base na menor aresta e edge_margin
function pin_offsets(P,Q,R) =
    let( Lmin = min_edge_len(P,Q,R),
         d    = max(edge_margin, 0.20*Lmin)
    )
    [ [ d, 0, 0], [ -d, 0, 0] ];

// ========================
// Primitivas
// ========================
module tetra(p0,p1,p2,p3){
    // orientação consistente
    polyhedron(
        points=[p0,p1,p2,p3],
        faces=[
            [0,2,1],
            [0,1,3],
            [1,2,3],
            [2,0,3]
        ]
    );
}

// Pino “macho” com leve conicidade na ponta
module pin_male(r=pin_r, h=pin_h, tip=tip_shrink){
    // haste cilíndrica + ponta cônica curta
    union(){
        translate([0,0,0])       cylinder(h=h-1.0, r=r, $fn=48);
        translate([0,0,h-1.0])   cylinder(h=1.0, r1=r, r2=max(r-tip, 0.1), $fn=48);
    }
}

// Rasgo “fêmea” (furos) — raio aumentado pela folga
module pin_female(r=pin_r, h=pin_h, clear=clearance){
    cylinder(h=h+1.0, r=r+clear, $fn=48); // um pouco mais fundo para garantir subtração
}

// Coloca dois pinos na face (P,Q,R) saindo no sentido +Z local
module add_pins_on_face(P,Q,R, male=true){
    multmatrix(face_frame(P,Q,R)){
        for (xy = pin_offsets(P,Q,R)){
            translate(xy)
                if (male)
                    pin_male();
                else
                    pin_female();
        }
    }
}

// Subtrai (rasgos) na face — empurra no -Z local para atravessar bem a peça
module subtract_pins_on_face(P,Q,R){
    multmatrix(face_frame(P,Q,R)){
        // dá um mergulho para o lado negativo também
        translate([0,0,-(pin_h+1)])
            for (xy = pin_offsets(P,Q,R)){
                translate(xy)
                    pin_female();
            }
    }
}

// ========================
// Peças com encaixes
// ========================
// T1 e T2 compartilham a face (A1,B,C)
// T2 e T3 compartilham a face (A1,B1,C)

// T1: tetra(A,B,C,A1) com pinos macho na face compartilhada com T2
module T1(){
    difference(){
        // corpo
        tetra(A,B,C,A1);
        // (nenhum rasgo em T1)
    }
    // pinos para acoplar com T2, saindo do plano A1-B-C
    add_pins_on_face(A1,B,C, male=true);
}

// T2: tetra(A1,B,B1,C) com rasgos para T1 e pinos para T3
module T2(){
    difference(){
        tetra(A1,B,B1,C);
        // rasgos para receber T1
        subtract_pins_on_face(A1,B,C);
        // rasgos para receber T3? — aqui T2 é macho para T3, então não
    }
    // pinos macho para acoplar em T3 na face (A1,B1,C)
    add_pins_on_face(A1,B1,C, male=true);
}

// T3: tetra(A1,B1,C1,C) com rasgos para T2
module T3(){
    difference(){
        tetra(A1,B1,C1,C);
        // rasgos para receber T2
        subtract_pins_on_face(A1,B1,C);
    }
    // (nenhum pino em T3)
}

// ========================
// Seletor para visualização/exportação
// ========================
module ALL(){ T1(); T2(); T3(); }

if (which_piece == 0){
    // Para conferir a recomposição do prisma
    // Use F6 e visualize a união no slicer
    ALL();
} else if (which_piece == 1){
    T1();
} else if (which_piece == 2){
    T2();
} else if (which_piece == 3){
    T3();
}
