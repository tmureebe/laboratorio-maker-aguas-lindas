/* Conjunto integrado; a eletrônica e os 18 botões usam a cena compartilhada. */
modo="conjunto"; // [conjunto,caixa,explodido,peca2d,peca3d]
numero_peca=1; // [1:9]
mostrar_paredes=true;
mostrar_tampa=true;
mostrar_eletronica=true;
mostrar_relevo=true;
mostrar_botoes=true;
mostrar_fios=true;
mostrar_fios_botoes=true;
mostrar_rotulos=false;
tacos_impressos=false;
abertura=105;
/* [Hidden] */
use <Caixa_com_sistema_eletronico.scad>
include <pedestal_existente.scad>
include <Geometria_caixa.scad>
module conjunto_caixa(explodido=false) {
 if(mostrar_eletronica) cena_integrada(!mostrar_tampa?"sem_tampa":explodido?"aberta":"fechada",mostrar_relevo,abertura,mostrar_botoes,mostrar_fios,mostrar_fios_botoes,tacos_impressos,mostrar_rotulos);
 else caixa_integrada(tampa=mostrar_tampa,abertura=explodido?abertura:0,impressos=tacos_impressos);
}
if(modo=="conjunto"||modo=="explodido") {
 pedestal_existente();multmatrix(origem_caixa) conjunto_caixa(modo=="explodido");
} else if(modo=="caixa") conjunto_caixa();
else if(modo=="peca2d") perfil_caixa(numero_peca-1);
else if(modo=="peca3d") linear_extrude(3) perfil_caixa(numero_peca-1);
else assert(false,"Modo inválido");
$vpt=[220,170,730];$vpr=[65,0,25];$vpd=1700;
