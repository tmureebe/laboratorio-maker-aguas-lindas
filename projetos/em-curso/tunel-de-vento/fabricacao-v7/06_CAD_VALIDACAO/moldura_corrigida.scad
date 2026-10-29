// Corrige o degrau interno de 1,6 mm sem mudar os apoios laterais ou furos.
// Origem da malha: X=0..200, Y=0..154, Z=0..6,5. Canal Y=17..137.
difference() {
 import("referencias/04_moldura_janela_removivel.stl");
 translate([-.1,17,-.1]) cube([200.2,120,1.7]);
}
