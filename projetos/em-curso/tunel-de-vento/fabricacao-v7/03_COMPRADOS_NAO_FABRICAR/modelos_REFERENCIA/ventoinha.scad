// REFERENCIA COMERCIAL: NAO IMPRIMIR ESTE MODELO
$fn=96;difference(){cube([30,120,120]);translate([-1,60,60])rotate([0,90,0])cylinder(h=32,r=55);}
 translate([0,60,60])rotate([0,90,0])cylinder(h=30,r=19);
 for(a=[0:60:300])translate([15,60,60])rotate([a,0,0])translate([-2,-3,14])cube([4,6,39]);