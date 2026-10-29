// V7 MDF. X=fluxo, Y=largura, Z=altura. Milímetros.
// Modelos de fabricação deitados: abertura na direção Z.
parede=3; apoio=6; folga=0.4; E=120+2*parede;
centro=122.4; piso=62.4-parede; externo=E+folga+6;
$fn=64; macho_final=126.2;
module anel(L,fora,dentro) { difference() {
 translate([-fora/2,-fora/2,0]) cube([fora,fora,L]);
 translate([-dentro/2,-dentro/2,-.01]) cube([dentro,dentro,L+.02]);
} }
module uniao_entrada() { // Z=0..12 MDF; Z=12..24 câmara V5
 union() {anel(12,externo,E+folga); translate([0,0,12]) anel(12,externo,124.8+folga);}
}
module uniao_saida() { // Z=0..12 câmara V5; Z=12..24 MDF
 union() {anel(12,externo,124.8+folga); translate([0,0,12]) anel(12,externo,E+folga);}
}
module ligacao(macho=126.2) {
 union() { anel(12,externo,E+folga); translate([0,0,12]) anel(3,131,120);
 translate([0,0,15]) difference() {anel(12,macho,120);
 // Chanfro nominal de 0,4 na borda externa e interna do macho.
 translate([0,0,11.6]) difference() {
 translate([-70,-70,0]) cube([140,140,.41]);
 hull() {translate([-macho/2,-macho/2,0]) cube([macho,macho,.001]);
 translate([-macho/2+.4,-macho/2+.4,.4]) cube([macho-.8,macho-.8,.001]);}
 }
 translate([0,0,11.6]) hull() {translate([-60,-60,0]) cube([120,120,.001]);
 translate([-60.4,-60.4,.4]) cube([120.8,120.8,.001]);}
 } }
}
module cupom_mdf() { anel(12,externo,E+folga); }

peca="entrada";
if(peca=="entrada") uniao_entrada();
if(peca=="saida") uniao_saida();
if(peca=="ligacao") ligacao(macho_final);
if(peca=="cupom") cupom_mdf();
