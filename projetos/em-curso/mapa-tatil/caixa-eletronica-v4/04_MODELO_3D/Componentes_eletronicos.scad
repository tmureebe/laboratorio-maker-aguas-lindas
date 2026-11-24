// Modelos nominais herdados da V4; dimensões físicas a conferir.
module rotulo(s,p,size=4,cor=[.08,.13,.17],alinhamento="left") {
    if($mostrar_rotulos) color(cor) translate(p)
        linear_extrude(.18) text(s,size=size,font="Liberation Sans:style=Bold",
                                halign=alinhamento,valign="center");
}

module fio(pontos,cor=[.1,.1,.1],raio=.6) {
    color(cor) {
        for(i=[0:len(pontos)-2]) {
            d=pontos[i+1]-pontos[i]; l=norm(d);
            if(l>.001) translate(pontos[i])
                rotate([0,acos(d[2]/l),atan2(d[1],d[0])])
                    cylinder(h=l,r=raio,$fn=8);
        }
        for(p=pontos) translate(p) sphere(r=raio,$fn=8);
    }
}

module placa(w,d,h=1.6,cor=[.03,.38,.22]) {
    color(cor) difference() {
        cube([w,d,h]);
        for(x=[2,w-2],y=[2,d-2]) translate([x,y,-.1]) cylinder(h=h+.2,r=.85,$fn=12);
    }
}

module pino(p) {
    color([.78,.65,.24]) translate(p) cylinder(h=2.5,r=.55,$fn=8);
}

module protoboard_original() {
    translate([45,270,6]) {
        color([.90,.90,.85]) linear_extrude(9)
            translate([2,2]) offset(r=2) square([166,66]);
        color([.73,.74,.71]) translate([4,32,8.9]) cube([162,3,.2]);
        for(i=[0:24],j=[0:4],lado=[0,1])
            color([.21,.23,.24]) translate([8+i*5.6,12+lado*27+j*2.54,9.01])
                cylinder(h=.15,r=.5,$fn=8);
        color([.78,.08,.08]) translate([5,63,9.01]) cube([160,.6,.15]);
        color([.08,.25,.70]) translate([5,67,9.01]) cube([160,.6,.15]);
        rotulo("+",[1,63,9.2],3,[.78,.08,.08]);
        rotulo("-",[1,67,9.2],3,[.08,.25,.70]);
    }
    rotulo("PROTOBOARD",[45,257,3.15],4);
}

module esp32_original() {
    // Representacao generica; conector USB voltado para a traseira da caixa.
    translate([80,286,22]) {
        placa(28,54,1.6,[.04,.16,.17]);
        for(i=[0:14],x=[1,27]) {
            color([.08,.09,.10]) translate([x-.8,7+i*2.54,-3]) cube([1.6,1.6,3]);
            color([.78,.65,.24]) translate([x,7+i*2.54,-7]) cylinder(h=7,r=.5,$fn=8);
            pino([x,7+i*2.54,1.6]);
        }
        color([.67,.69,.70]) translate([4,18,1.6]) cube([20,25,3]);
        color([.02,.03,.04]) translate([6,3,1.6]) cube([16,12,1]);
        color([.72,.60,.23]) for(i=[0:3]) translate([7,4+i*2.5,2.6]) cube([14,.7,.2]);
        color([.68,.70,.72]) translate([10,51,1.6]) cube([8,8,3]);
        color([.03,.04,.05]) translate([11,58.9,2.2]) cube([6,.2,1.8]);
        color([.13,.13,.14]) for(x=[4,21]) translate([x,46,1.6]) cube([3,3,1.5]);
        rotulo("ESP32",[14,31,4.8],3,[.1,.1,.12],"center");
    }
    // Terminais de distribuicao ilustrativos na protoboard, B1..B18.
    for(i=[0:17]) pino([127+i*3,294,15]);
    rotulo("B1 ... B18",[125,300,15.2],2.8);
}

module dfplayer_original() {
    translate([291,282,10]) {
        for(p=[[2,2],[23,28]]) color([.82,.82,.80]) translate([p[0],p[1],-7])
            cylinder(h=7,r=2,$fn=12);
        placa(25,30);
        for(i=[0:7],x=[1,24]) pino([x,4+i*3,1.6]);
        color([.12,.13,.14]) translate([7,2,1.6]) cube([11,8,2]);
        color([.65,.68,.70]) translate([3.5,12,1.6]) cube([18,16,3]);
        color([.08,.09,.10]) translate([5.5,23,3.8]) cube([14,11,1]);
        rotulo("SD",[12.5,30,4.9],2.8,[.95,.95,.95],"center");
    }
    rotulo("DFPLAYER + microSD",[279,320,3.15],3.5);
}

module resistor_1k_original() {
    // Corpo e terminais axialmente em x, sobre a area livre da protoboard.
    color([.64,.65,.66]) translate([136,286,19]) rotate([0,90,0]) cylinder(h=16,r=.35,$fn=8);
    color([.78,.67,.43]) translate([140,286,19]) rotate([0,90,0]) cylinder(h=8,r=1.4,$fn=16);
    for(i=[0:3]) color(i==0?[.35,.15,.04]:i==1?[.02,.02,.02]:i==2?[.75,.03,.02]:[.75,.61,.2])
        translate([141+i*1.6,286,19]) rotate([0,90,0]) cylinder(h=.6,r=1.43,$fn=16);
    rotulo("1k",[143,282,20.5],2.5,[.15,.15,.15],"center");
}

module falante() {
    // Face acustica para a grade frontal; diametro ilustrativo 32, fundo 12.
    translate([330,4,25]) rotate([-90,0,0]) {
        color([.57,.59,.61]) difference() {
            cylinder(h=3,r=16);
            translate([0,0,-.1]) cylinder(h=3.2,r=12.5);
        }
        color([.12,.13,.14]) translate([0,0,.7]) difference() {
            cylinder(h=4,r1=12.5,r2=4);
            translate([0,0,-.1]) cylinder(h=3.7,r1=11.8,r2=3.5);
        }
        color([.1,.1,.11]) translate([0,0,1]) scale([1,1,.35]) sphere(r=4);
        color([.20,.21,.23]) translate([0,0,5]) cylinder(h=7,r=7);
    }
    rotulo("FALANTE 8 ohm",[300,45,3.15],3.5);
}


module eletronica() {
 translate([240,0,0]) {protoboard_original();esp32_original();resistor_1k_original();}
 translate([129,-122,0]) dfplayer_original();
 falante();
}
