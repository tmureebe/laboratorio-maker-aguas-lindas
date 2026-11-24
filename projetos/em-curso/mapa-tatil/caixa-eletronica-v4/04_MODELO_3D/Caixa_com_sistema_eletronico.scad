/* Caixa integrada 500 x 380 x 50 mm; 18 KFC-A06 nas posições e alturas do mapa.
Componentes eletrônicos são representações nominais da V4, a conferir na peça real.
Fios ilustram rotas mecânicas; não constituem esquema elétrico nem atribuição de GPIO.
A tampa de CNC está em 01_CORTE_PAINEIS/C1_TAMPO_FURADO_500x380.dxf.
*/
/* [Visualizacao] */
vista="inspecao"; // [inspecao,fechada,aberta,sem_tampa,eletronica]
mostrar_pedestal=false;
mostrar_paredes=true;
mostrar_fios=true;
mostrar_fios_botoes=true;
mostrar_rotulos=true;
mostrar_botoes=true;
mostrar_relevo=true;
tacos_impressos=false;
abertura_tampa=105;
/* [Hidden] */
$fn=24;
use <../../relevo-500x380/botao_tatil_KFC-A06_12x12x4p3.scad>
use <../../relevo-500x380/construcoes_vista_aerea.scad>
include <pedestal_existente.scad>
include <Geometria_caixa.scad>
include <Componentes_eletronicos.scad>
module botao_mapa(b,abertura=0) {
 translate([b[1],b[2],50+b[3]+abertura]) botao_kfc_a06(com_terminais=true);
}
module cabos(abertura=0,botoes=true,fios_botoes=true) {
 // Rotas baixas sob as nervuras; folga de serviço ao abrir a tampa.
 fio([[334,345,25],[334,362,39],[334,394,39]],[.12,.13,.15],1.9);
 fio([[435,333,16],[465,333,9],[465,210,9],[421,164,13]],[.85,.05,.05]);
 fio([[435,337,16],[470,337,8],[470,205,8],[444,164,13]],[.06,.06,.07]);
 fio([[347,326,24],[376,286,19]],[.9,.65,.05]);
 fio([[392,286,19],[460,250,8],[421,167,13]],[.9,.65,.05]);
 fio([[444,170,13],[460,250,9],[347,323,24]],[.15,.62,.78]);
 fio([[444,179,13],[460,150,8],[350,65,8],[336,18,19]],[.70,.15,.65],.7);
 fio([[444,182,13],[465,150,8],[355,65,8],[324,18,19]],[.24,.22,.65],.7);
 if(botoes && fios_botoes) for(i=[0:len(botoes_mapa)-1]) {
  b=botoes_mapa[i]; z=50+b[3]-3.5+abertura;
  // Cada fio sobe pelo furo de MDF alinhado ao seu terminal.
  fio([[367+i*3,294,17.5],[367+i*3,250,8],[b[1]-6.25,250,8],
       [b[1]-6.25,b[2]-2.5,8],[b[1]-6.25,b[2]-2.5,z]],[.95,.52,.08],.7);
  fio([[430,337,16],[475,250,7],[b[1]+6.25,250,7],
       [b[1]+6.25,b[2]-2.5,7],[b[1]+6.25,b[2]-2.5,z]],[.09,.09,.10],.7);
 }
}
module cena_integrada(v="inspecao",relevo=true,abertura=105,botoes=true,fios=true,fios_botoes=true,impressos=false,rotulos=true) {
 $mostrar_rotulos=rotulos;
 dz=v=="aberta"?abertura:0;
 assert(v=="inspecao"||v=="fechada"||v=="aberta"||v=="sem_tampa"||v=="eletronica");
 if(v!="eletronica") caixa_integrada(tampa=v!="sem_tampa",abertura=dz,alpha=v=="inspecao"?.25:1,impressos=impressos);
 eletronica();
 if(relevo && v!="sem_tampa" && v!="eletronica") translate([0,0,50+dz]) {
  // Peças de relevo; o painel real é exclusivamente C1, evitando duplicação.
  relevos_tateis();
 }
 if(botoes) for(b=botoes_mapa) botao_mapa(b,dz);
 if(fios) cabos(dz,botoes,fios_botoes);
}
$vpt=mostrar_pedestal?[220,170,740]:[250,190,40];
$vpr=[42,0,25];$vpd=mostrar_pedestal?1600:880;
if(mostrar_pedestal) {pedestal_existente();multmatrix(origem_caixa) cena_integrada(vista,mostrar_relevo,abertura_tampa,mostrar_botoes,mostrar_fios,mostrar_fios_botoes,tacos_impressos,mostrar_rotulos);}
else cena_integrada(vista,mostrar_relevo,abertura_tampa,mostrar_botoes,mostrar_fios,mostrar_fios_botoes,tacos_impressos,mostrar_rotulos);
