// Componente React (no estilo do bundle minificado do GP2040-CE) que substitui a
// seção "ordem dos LEDs" da página /led-config. É injetado por build_ledporpino.py.
// Identificadores do bundle 0.7.12 usados aqui: v = React, u = jsx-runtime, Ve = URL base da API.
const __LTU_ALL=["Up","Down","Left","Right","B1","B2","B3","B4","L1","R1","L2","R2","S1","S2","L3","R3","A1","A2"],
__LTU_SLOT=["Left","Down","Right","Up","B3","B4","R1","L1","B1","B2","R2","L2","A1","L3","R3","A2"],
__LTU_STRIP=[5,3,4,2,10,11,12,13,6,7,8,9,27,18,19,26],
__LTU_PINGEO={18:[185,385,125,185],5:[325,325,120,120],3:[465,320,120,120],4:[590,380,120,120],26:[740,405,135,135],10:[875,335,120,120],11:[995,275,120,120],12:[1150,275,120,120],6:[875,478,120,120],7:[1000,415,120,120],8:[1140,415,120,120],19:[1280,390,125,185],13:[525,600,120,120],2:[645,675,165,170],27:[825,670,165,170],9:[945,600,120,120]},
__LTU_ACT={1:"Up",2:"Down",3:"Left",4:"Right",5:"B1",6:"B2",7:"B3",8:"B4",9:"L1",10:"R1",11:"L2",12:"R2",13:"S1",14:"S2",15:"A1",16:"A2",17:"L3",18:"R3"},
__LTU_OTHER={"-10":"sem função",0:"add-on",19:"Fn",20:"DDI ↑",21:"DDI ↓",22:"DDI ←",23:"DDI →",32:"Turbo",33:"Macro",34:"Macro 1",35:"Macro 2",36:"Macro 3",37:"Macro 4",38:"Macro 5",39:"Macro 6",40:"Combo"},
__LedToggleUI=({ledButtonMap:map,labels:labels,onChange:onChange})=>{
 const[fixed,setFixed]=v.useState(null),[acts,setActs]=v.useState(null),
 ready=!!map&&Object.keys(map).length>0,
 lab={};(labels||[]).forEach(x=>{lab[x.id]=x.label});
 v.useEffect(()=>{if(!ready||fixed!==null)return;
  const canon={};__LTU_ALL.forEach(i=>{canon[i]=null});__LTU_SLOT.forEach((i,k)=>{canon[i]=k});
  const same=__LTU_ALL.every(i=>(map[i]==null||map[i]<0?null:map[i])===canon[i]);
  same||(window.__ltuFix=!0);setFixed(!!window.__ltuFix);same||onChange(canon,16)},[ready]);
 v.useEffect(()=>{fetch(`${Ve}/api/getPinMappings`).then(r=>r.json()).then(d=>{const p={};Object.keys(d||{}).forEach(k=>{/^pin\d+$/.test(k)&&d[k]&&(p[parseInt(k.slice(3))]=d[k].action)});setActs(p)}).catch(()=>{setActs({})})},[]);
 const fn=p=>{if(!acts)return"...";const a=acts[p];if(a==null)return"?";const id=__LTU_ACT[a];return id?(lab[id]||id):(__LTU_OTHER[a]||"ação "+a)};
 if(fixed===null)return u.jsx("p",{className:"card-text",children:"Carregando..."});
 const S=.56,X0=100,Y0=195;
 return u.jsxs("div",{children:[
  u.jsx("p",{className:"card-text",children:"Neste firmware cada LED está ligado ao pino físico do botão, não à função. Você pode trocar a função de qualquer botão no Mapeamento de Pinos (ou trocar de perfil) que o LED continua acendendo no botão certo. Não há nada para ordenar aqui."}),
  fixed?u.jsx("p",{className:"card-text",style:{color:"#ffc107",fontWeight:600},children:"O mapa de LEDs salvo no controle era diferente do que este firmware precisa. Já corrigi aqui na tela: clique em Salvar no fim da página (só precisa fazer isso uma vez; este aviso some quando você recarregar a página depois de salvar)."}):u.jsx("p",{className:"card-text",style:{color:"#4ade80"},children:"Mapa de LEDs correto (16 LEDs)."}),
  u.jsx("div",{style:{position:"relative",width:720,height:330,background:"#2b2f36",border:"1px solid #555",borderRadius:8,margin:"0 0 16px",maxWidth:"100%",overflow:"hidden"},children:__LTU_STRIP.map((p,k)=>{const g=__LTU_PINGEO[p];return u.jsxs("div",{style:{position:"absolute",left:(g[0]-X0)*S-g[2]*S/2,top:(g[1]-Y0)*S-g[3]*S/2,width:g[2]*S,height:g[3]*S,borderRadius:"50%",boxSizing:"border-box",border:"3px solid #3b82f6",background:"rgba(59,130,246,.18)",color:"#fff",display:"flex",flexDirection:"column",alignItems:"center",justifyContent:"center",fontSize:11,lineHeight:1.2,userSelect:"none"},children:[u.jsx("strong",{style:{fontSize:12},children:fn(p)}),u.jsx("span",{children:"GP"+p}),u.jsx("span",{style:{color:"#9ec5ff"},children:"LED "+(k+1)})]},p)})}),
  u.jsx("p",{className:"card-text",children:"No Tema Personalizado as cores continuam sendo escolhidas pelo nome da coluna \"Nome no tema\" abaixo, que é fixo por posição e não muda quando você troca a função do botão."}),
  u.jsxs("div",{className:"d-flex py-1",style:{maxWidth:560,fontWeight:600,borderBottom:"1px solid rgba(255,255,255,.3)"},children:[u.jsx("div",{style:{width:90},children:"LED"}),u.jsx("div",{style:{width:90},children:"Pino"}),u.jsx("div",{style:{width:190},children:"Função atual"}),u.jsx("div",{children:"Nome no tema"})]}),
  __LTU_STRIP.map((p,k)=>u.jsxs("div",{className:"d-flex py-1",style:{maxWidth:560,borderBottom:"1px solid rgba(255,255,255,.12)"},children:[u.jsx("div",{style:{width:90},children:"LED nº "+(k+1)}),u.jsx("div",{style:{width:90},children:"GP"+p}),u.jsx("div",{style:{width:190},children:fn(p)}),u.jsx("div",{children:(lab[__LTU_SLOT[k]]||__LTU_SLOT[k])+" ("+__LTU_SLOT[k]+")"})]},"r"+p))]})};
