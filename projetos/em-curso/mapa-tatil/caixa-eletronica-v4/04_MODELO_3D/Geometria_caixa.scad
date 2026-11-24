// Geometria compartilhada: corte, inspeção e conjunto usam os mesmos perfis.
use <Taco_impressao_3D.scad>
nomes_caixa=["C0_BASE", "C1_TAMPO_FURADO", "C2_FRENTE", "C3_TRAS_USB", "C4_ESQUERDA", "C5_DIREITA", "C6_NX1", "C7_NX2", "C8_NY"];
origem_caixa=[[1, 0, 0, -30], [0, 0.9874406319167053, -0.15799050110667284, -18.087691567494037], [0, 0.15799050110667284, 0.9874406319167053, 865.9441266854824], [0, 0, 0, 1]];
botoes_mapa=[[1, 153.667, 45.333, 5.0], [2, 108.667, 92.0, 5.0], [3, 217.0, 92.0, 5.0], [4, 205.333, 135.333, 13.033], [5, 237.0, 122.0, 13.033], [6, 155.333, 138.667, 13.033], [7, 133.667, 138.667, 13.033], [8, 112.0, 138.667, 13.033], [9, 90.333, 138.667, 13.033], [10, 117.0, 122.0, 13.033], [11, 315.333, 200.333, 16.367], [12, 119.167, 283.667, 8.367], [13, 182.0, 258.667, 13.033], [14, 188.5, 290.333, 13.033], [15, 172.0, 290.333, 13.033], [16, 190.333, 328.667, 13.033], [17, 172.833, 328.667, 13.033], [18, 181.167, 342.5, 13.033]];
tacos_caixa=[[30, 13], [150, 13], [400, 13], [470, 13], [30, 367], [150, 367], [270, 367], [470, 367]];
module perfil_caixa(i) {
if(i==0) difference() {
polygon([[0, 0], [500, 0], [500, 380], [0, 380]]);
}
if(i==1) difference() {
polygon([[0, 0], [500, 0], [500, 380], [0, 380]]);
translate([147.417, 42.833]) circle(r=1.3,$fn=64);
translate([147.417, 47.833]) circle(r=1.3,$fn=64);
translate([159.917, 42.833]) circle(r=1.3,$fn=64);
translate([159.917, 47.833]) circle(r=1.3,$fn=64);
translate([102.417, 89.5]) circle(r=1.3,$fn=64);
translate([102.417, 94.5]) circle(r=1.3,$fn=64);
translate([114.917, 89.5]) circle(r=1.3,$fn=64);
translate([114.917, 94.5]) circle(r=1.3,$fn=64);
translate([210.75, 89.5]) circle(r=1.3,$fn=64);
translate([210.75, 94.5]) circle(r=1.3,$fn=64);
translate([223.25, 89.5]) circle(r=1.3,$fn=64);
translate([223.25, 94.5]) circle(r=1.3,$fn=64);
translate([199.083, 132.833]) circle(r=1.3,$fn=64);
translate([199.083, 137.833]) circle(r=1.3,$fn=64);
translate([211.583, 132.833]) circle(r=1.3,$fn=64);
translate([211.583, 137.833]) circle(r=1.3,$fn=64);
translate([230.75, 119.5]) circle(r=1.3,$fn=64);
translate([230.75, 124.5]) circle(r=1.3,$fn=64);
translate([243.25, 119.5]) circle(r=1.3,$fn=64);
translate([243.25, 124.5]) circle(r=1.3,$fn=64);
translate([149.083, 136.167]) circle(r=1.3,$fn=64);
translate([149.083, 141.167]) circle(r=1.3,$fn=64);
translate([161.583, 136.167]) circle(r=1.3,$fn=64);
translate([161.583, 141.167]) circle(r=1.3,$fn=64);
translate([127.417, 136.167]) circle(r=1.3,$fn=64);
translate([127.417, 141.167]) circle(r=1.3,$fn=64);
translate([139.917, 136.167]) circle(r=1.3,$fn=64);
translate([139.917, 141.167]) circle(r=1.3,$fn=64);
translate([105.75, 136.167]) circle(r=1.3,$fn=64);
translate([105.75, 141.167]) circle(r=1.3,$fn=64);
translate([118.25, 136.167]) circle(r=1.3,$fn=64);
translate([118.25, 141.167]) circle(r=1.3,$fn=64);
translate([84.083, 136.167]) circle(r=1.3,$fn=64);
translate([84.083, 141.167]) circle(r=1.3,$fn=64);
translate([96.583, 136.167]) circle(r=1.3,$fn=64);
translate([96.583, 141.167]) circle(r=1.3,$fn=64);
translate([110.75, 119.5]) circle(r=1.3,$fn=64);
translate([110.75, 124.5]) circle(r=1.3,$fn=64);
translate([123.25, 119.5]) circle(r=1.3,$fn=64);
translate([123.25, 124.5]) circle(r=1.3,$fn=64);
translate([309.083, 197.833]) circle(r=1.3,$fn=64);
translate([309.083, 202.833]) circle(r=1.3,$fn=64);
translate([321.583, 197.833]) circle(r=1.3,$fn=64);
translate([321.583, 202.833]) circle(r=1.3,$fn=64);
translate([112.917, 281.167]) circle(r=1.3,$fn=64);
translate([112.917, 286.167]) circle(r=1.3,$fn=64);
translate([125.417, 281.167]) circle(r=1.3,$fn=64);
translate([125.417, 286.167]) circle(r=1.3,$fn=64);
translate([175.75, 256.167]) circle(r=1.3,$fn=64);
translate([175.75, 261.167]) circle(r=1.3,$fn=64);
translate([188.25, 256.167]) circle(r=1.3,$fn=64);
translate([188.25, 261.167]) circle(r=1.3,$fn=64);
translate([182.25, 287.833]) circle(r=1.3,$fn=64);
translate([182.25, 292.833]) circle(r=1.3,$fn=64);
translate([194.75, 287.833]) circle(r=1.3,$fn=64);
translate([194.75, 292.833]) circle(r=1.3,$fn=64);
translate([165.75, 287.833]) circle(r=1.3,$fn=64);
translate([165.75, 292.833]) circle(r=1.3,$fn=64);
translate([178.25, 287.833]) circle(r=1.3,$fn=64);
translate([178.25, 292.833]) circle(r=1.3,$fn=64);
translate([184.083, 326.167]) circle(r=1.3,$fn=64);
translate([184.083, 331.167]) circle(r=1.3,$fn=64);
translate([196.583, 326.167]) circle(r=1.3,$fn=64);
translate([196.583, 331.167]) circle(r=1.3,$fn=64);
translate([166.583, 326.167]) circle(r=1.3,$fn=64);
translate([166.583, 331.167]) circle(r=1.3,$fn=64);
translate([179.083, 326.167]) circle(r=1.3,$fn=64);
translate([179.083, 331.167]) circle(r=1.3,$fn=64);
translate([174.917, 340.0]) circle(r=1.3,$fn=64);
translate([174.917, 345.0]) circle(r=1.3,$fn=64);
translate([187.417, 340.0]) circle(r=1.3,$fn=64);
translate([187.417, 345.0]) circle(r=1.3,$fn=64);
}
if(i==2) difference() {
polygon([[0, 0], [494, 0], [494, 44], [0, 44]]);
polygon([[303, 11], [305, 11], [305, 33], [303, 33]]);
polygon([[309, 11], [311, 11], [311, 33], [309, 33]]);
polygon([[315, 11], [317, 11], [317, 33], [315, 33]]);
polygon([[321, 11], [323, 11], [323, 33], [321, 33]]);
polygon([[327, 11], [329, 11], [329, 33], [327, 33]]);
polygon([[333, 11], [335, 11], [335, 33], [333, 33]]);
polygon([[339, 11], [341, 11], [341, 33], [339, 33]]);
polygon([[345, 11], [347, 11], [347, 33], [345, 33]]);
polygon([[351, 11], [353, 11], [353, 33], [351, 33]]);
translate([27, 32]) circle(r=1.75,$fn=64);
translate([147, 32]) circle(r=1.75,$fn=64);
translate([397, 32]) circle(r=1.75,$fn=64);
translate([467, 32]) circle(r=1.75,$fn=64);
}
if(i==3) difference() {
polygon([[0, 0], [494, 0], [494, 44], [343, 44], [343, 30], [319, 30], [319, 44], [0, 44]]);
translate([27, 32]) circle(r=1.75,$fn=64);
translate([147, 32]) circle(r=1.75,$fn=64);
translate([267, 32]) circle(r=1.75,$fn=64);
translate([467, 32]) circle(r=1.75,$fn=64);
polygon([[359, 15], [362, 15], [362, 23], [359, 23]]);
polygon([[371, 15], [374, 15], [374, 23], [371, 23]]);
}
if(i==4) difference() {
polygon([[0, 0], [380, 0], [380, 44], [0, 44]]);
}
if(i==5) difference() {
polygon([[0, 0], [380, 0], [380, 44], [0, 44]]);
}
if(i==6) difference() {
polygon([[0, 0], [77, 0], [77, 12], [237, 12], [237, 0], [307, 0], [307, 12], [367, 12], [367, 0], [494, 0], [494, 30], [248.575, 30], [248.575, 14.925], [245.425, 14.925], [245.425, 30], [0, 30]]);
}
if(i==7) difference() {
polygon([[0, 0], [87, 0], [87, 12], [222, 12], [222, 0], [277, 0], [277, 12], [447, 12], [447, 0], [494, 0], [494, 30], [248.575, 30], [248.575, 14.925], [245.425, 14.925], [245.425, 30], [0, 30]]);
}
if(i==8) difference() {
polygon([[0, 0], [27, 0], [27, 12], [92, 12], [92, 0], [105.425, 0], [105.425, 15.075], [108.575, 15.075], [108.575, 0], [122, 0], [122, 12], [217, 12], [217, 0], [235.425, 0], [235.425, 15.075], [238.575, 15.075], [238.575, 0], [262, 0], [262, 12], [352, 12], [352, 0], [374, 0], [374, 30], [0, 30]]);
}
}
module caixa_integrada(tampa=true,abertura=0,alpha=1,impressos=false) {
 color([0.5,.68,.48,alpha]) translate([0,0,0]) multmatrix([[1, 0, 0, 0], [0, 1, 0, 0], [0, 0, 1, 0], [0, 0, 0, 1]]) linear_extrude(3) perfil_caixa(0);
if(tampa) color([0.88,.68,.48,alpha]) translate([0,0,abertura]) multmatrix([[1, 0, 0, 0], [0, 1, 0, 0], [0, 0, 1, 47], [0, 0, 0, 1]]) linear_extrude(3) perfil_caixa(1);
 color([0.5,.68,.48,alpha]) translate([0,0,0]) multmatrix([[1, 0, 0, 3], [0, 0, 1, 0], [0, 1, 0, 3], [0, 0, 0, 1]]) linear_extrude(3) perfil_caixa(2);
 color([0.5,.68,.48,alpha]) translate([0,0,0]) multmatrix([[1, 0, 0, 3], [0, 0, 1, 377], [0, 1, 0, 3], [0, 0, 0, 1]]) linear_extrude(3) perfil_caixa(3);
 color([0.5,.68,.48,alpha]) translate([0,0,0]) multmatrix([[0, 0, 1, 0], [1, 0, 0, 3], [0, 1, 0, 3], [0, 0, 0, 1]]) linear_extrude(3) perfil_caixa(4);
 color([0.5,.68,.48,alpha]) translate([0,0,0]) multmatrix([[0, 0, 1, 497], [1, 0, 0, 3], [0, 1, 0, 3], [0, 0, 0, 1]]) linear_extrude(3) perfil_caixa(5);
if(tampa) color([0.88,.68,.48,alpha]) translate([0,0,abertura]) multmatrix([[1, 0, 0, 3], [0, 0, 1, 108.5], [0, 1, 0, 17], [0, 0, 0, 1]]) linear_extrude(3) perfil_caixa(6);
if(tampa) color([0.88,.68,.48,alpha]) translate([0,0,abertura]) multmatrix([[1, 0, 0, 3], [0, 0, 1, 238.5], [0, 1, 0, 17], [0, 0, 0, 1]]) linear_extrude(3) perfil_caixa(7);
if(tampa) color([0.88,.68,.48,alpha]) translate([0,0,abertura]) multmatrix([[0, 0, 1, 248.5], [1, 0, 0, 3], [0, 1, 0, 17], [0, 0, 0, 1]]) linear_extrude(3) perfil_caixa(8);
if(tampa) for(p=tacos_caixa) color([.65,.45,.26,alpha]) translate([p[0]-10,p[1]-10,3+abertura])
if(impressos) {if(p[1]>190) translate([20,20,0]) rotate([0,0,180]) taco_montagem(); else taco_montagem();} else cube([20,20,44]);
}
