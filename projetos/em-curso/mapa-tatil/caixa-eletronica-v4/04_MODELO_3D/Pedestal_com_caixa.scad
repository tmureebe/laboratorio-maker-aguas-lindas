/* Caixa adicional 500x380x50. Cortes em 01/02/03; unidades mm.
Tampo liso; sem botões. Volumes coloridos são reservas, não componentes medidos. */
modo="conjunto"; // [conjunto,caixa,explodido,peca2d,peca3d]
numero_peca=1; // [1:9]
mostrar_paredes=true;
mostrar_tampa=true;
mostrar_reservas=false;
abertura=100;
include <pedestal_existente.scad>
nomes_caixa=["C0_BASE", "C1_TAMPO_LISO", "C2_FRENTE", "C3_TRAS_USB", "C4_ESQUERDA", "C5_DIREITA", "C6_NX1", "C7_NX2", "C8_NY"];
origem_caixa=[[1.0, 0.0, 0.0, -30.0], [0.0, 0.9874406319167053, -0.15799050110667284, -18.087691567494037], [0.0, 0.15799050110667284, 0.9874406319167053, 865.9441266854824], [0.0, 0.0, 0.0, 1.0]];
module perfil_caixa(i){
if(i==0) difference() {
polygon([[0, 0], [500.0, 0], [500.0, 380.0], [0, 380.0]]);
}
if(i==1) difference() {
polygon([[0, 0], [500.0, 0], [500.0, 380.0], [0, 380.0]]);
}
if(i==2) difference() {
polygon([[0, 0], [494.0, 0], [494.0, 44.0], [0, 44.0]]);
polygon([[303, 11], [305, 11], [305, 33], [303, 33]]);
polygon([[309, 11], [311, 11], [311, 33], [309, 33]]);
polygon([[315, 11], [317, 11], [317, 33], [315, 33]]);
polygon([[321, 11], [323, 11], [323, 33], [321, 33]]);
polygon([[327, 11], [329, 11], [329, 33], [327, 33]]);
polygon([[333, 11], [335, 11], [335, 33], [333, 33]]);
polygon([[339, 11], [341, 11], [341, 33], [339, 33]]);
polygon([[345, 11], [347, 11], [347, 33], [345, 33]]);
polygon([[351, 11], [353, 11], [353, 33], [351, 33]]);
translate([27.0, 32]) circle(r=1.75,$fn=64);
translate([147.0, 32]) circle(r=1.75,$fn=64);
translate([397.0, 32]) circle(r=1.75,$fn=64);
translate([467.0, 32]) circle(r=1.75,$fn=64);
}
if(i==3) difference() {
polygon([[0, 0], [494, 0], [494, 44], [81, 44], [81, 30], [57, 30], [57, 44], [0, 44]]);
translate([27.0, 32]) circle(r=1.75,$fn=64);
translate([147.0, 32]) circle(r=1.75,$fn=64);
translate([397.0, 32]) circle(r=1.75,$fn=64);
translate([467.0, 32]) circle(r=1.75,$fn=64);
polygon([[97.0, 15], [100.0, 15], [100.0, 23], [97.0, 23]]);
polygon([[109.0, 15], [112.0, 15], [112.0, 23], [109.0, 23]]);
}
if(i==4) difference() {
polygon([[0, 0], [380.0, 0], [380.0, 44.0], [0, 44.0]]);
}
if(i==5) difference() {
polygon([[0, 0], [380.0, 0], [380.0, 44.0], [0, 44.0]]);
}
if(i==6) difference() {
polygon([[0, 0], [494.0, 0], [494.0, 30], [248.575, 30], [248.575, 14.925], [245.425, 14.925], [245.425, 30], [0, 30]]);
}
if(i==7) difference() {
polygon([[0, 0], [494.0, 0], [494.0, 30], [248.575, 30], [248.575, 14.925], [245.425, 14.925], [245.425, 30], [0, 30]]);
}
if(i==8) difference() {
polygon([[0, 0], [105.425, 0], [105.425, 15.075], [108.575, 15.075], [108.575, 0], [235.425, 0], [235.425, 15.075], [238.575, 15.075], [238.575, 0], [374.0, 0], [374.0, 30], [0, 30]]);
}
}
module caixa(explodida=false){
 color([.50,.68,.72]) translate([0,0,explodida?0:0]) multmatrix([[1, 0, 0, 0], [0, 1, 0, 0], [0, 0, 1, 0], [0, 0, 0, 1]]) linear_extrude(3) perfil_caixa(0);
if(mostrar_tampa) color([.88,.75,.48]) translate([0,0,explodida?abertura:0]) multmatrix([[1, 0, 0, 0], [0, 1, 0, 0], [0, 0, 1, 47.0], [0, 0, 0, 1]]) linear_extrude(3) perfil_caixa(1);
 color([.50,.68,.72]) translate([0,0,explodida?0:0]) multmatrix([[1, 0, 0, 3.0], [0, 0, 1, 0], [0, 1, 0, 3.0], [0, 0, 0, 1]]) linear_extrude(3) perfil_caixa(2);
 color([.50,.68,.72]) translate([0,0,explodida?0:0]) multmatrix([[1, 0, 0, 3.0], [0, 0, 1, 377.0], [0, 1, 0, 3.0], [0, 0, 0, 1]]) linear_extrude(3) perfil_caixa(3);
 color([.50,.68,.72]) translate([0,0,explodida?0:0]) multmatrix([[0, 0, 1, 0], [1, 0, 0, 0], [0, 1, 0, 3.0], [0, 0, 0, 1]]) linear_extrude(3) perfil_caixa(4);
 color([.50,.68,.72]) translate([0,0,explodida?0:0]) multmatrix([[0, 0, 1, 497.0], [1, 0, 0, 0], [0, 1, 0, 3.0], [0, 0, 0, 1]]) linear_extrude(3) perfil_caixa(5);
if(mostrar_tampa) color([.88,.75,.48]) translate([0,0,explodida?abertura:0]) multmatrix([[1, 0, 0, 3.0], [0, 0, 1, 108.5], [0, 1, 0, 17.0], [0, 0, 0, 1]]) linear_extrude(3) perfil_caixa(6);
if(mostrar_tampa) color([.88,.75,.48]) translate([0,0,explodida?abertura:0]) multmatrix([[1, 0, 0, 3.0], [0, 0, 1, 238.5], [0, 1, 0, 17.0], [0, 0, 0, 1]]) linear_extrude(3) perfil_caixa(7);
if(mostrar_tampa) color([.88,.75,.48]) translate([0,0,explodida?abertura:0]) multmatrix([[0, 0, 1, 248.5], [1, 0, 0, 3.0], [0, 1, 0, 17.0], [0, 0, 0, 1]]) linear_extrude(3) perfil_caixa(8);
if(mostrar_tampa) color([.65,.45,.26]) translate([20.0,3.0,3+(explodida?abertura:0)]) cube([20,20,44]);
if(mostrar_tampa) color([.65,.45,.26]) translate([140.0,3.0,3+(explodida?abertura:0)]) cube([20,20,44]);
if(mostrar_tampa) color([.65,.45,.26]) translate([390.0,3.0,3+(explodida?abertura:0)]) cube([20,20,44]);
if(mostrar_tampa) color([.65,.45,.26]) translate([460.0,3.0,3+(explodida?abertura:0)]) cube([20,20,44]);
if(mostrar_tampa) color([.65,.45,.26]) translate([20.0,357.0,3+(explodida?abertura:0)]) cube([20,20,44]);
if(mostrar_tampa) color([.65,.45,.26]) translate([140.0,357.0,3+(explodida?abertura:0)]) cube([20,20,44]);
if(mostrar_tampa) color([.65,.45,.26]) translate([390.0,357.0,3+(explodida?abertura:0)]) cube([20,20,44]);
if(mostrar_tampa) color([.65,.45,.26]) translate([460.0,357.0,3+(explodida?abertura:0)]) cube([20,20,44]);
if(mostrar_reservas) color([.2,.65,.3,.45]) translate([30,255,6]) cube([200,95,32]);
if(mostrar_reservas) color([.2,.65,.3,.45]) translate([275,255,6]) cube([100,95,32]);
if(mostrar_reservas) color([.2,.65,.3,.45]) translate([294,3,6]) cube([72,35,38]);
}
if(modo=="conjunto") {pedestal_existente(); multmatrix(origem_caixa) caixa();}
else if(modo=="caixa") caixa();
else if(modo=="explodido") {pedestal_existente(); multmatrix(origem_caixa) caixa(true);}
else if(modo=="peca2d") perfil_caixa(numero_peca-1);
else if(modo=="peca3d") linear_extrude(3) perfil_caixa(numero_peca-1);
else assert(false,"Modo invalido");