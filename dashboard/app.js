'use strict';
const $ = id => document.getElementById(id);
const form = $('scenario');
let worker, state, playing = false, pending = false, requestId = 0, generation = 0, failed = false, baseline = null;
try { baseline = JSON.parse(localStorage.getItem('qdel-baseline-v1')); } catch {}
const labels = {queued:'Queued', packing:'Packing', ready:'Awaiting rider', en_route:'En route', delivered:'Delivered'};
const fmt = (n, suffix = '', digits = 1) => n == null ? '—' : `${Number(n).toFixed(digits)}${suffix}`;
function configuration() {
  return Object.fromEntries([...new FormData(form)].map(([key,value]) => [key,key === 'dispatch' ? value : Number(value)]));
}
function message(text, error = false) { $('notice').textContent = text; $('notice').classList.toggle('error', error); }
function request(action, extra = {}) {
  pending = true;
  worker.postMessage({id:++requestId,action,...extra});
  controls();
}
function controls() {
  const ready = !!state && !pending && !failed;
  $('play').disabled = !ready || state.finished;
  $('step').disabled = !ready || state.finished || playing;
  $('apply').disabled = pending;
  $('export').disabled = !state || !state.orders.length;
  $('save-baseline').disabled = !state || !state.time;
  $('play').textContent = playing ? 'Ⅱ  Pause' : state?.finished ? '✓  Run complete' : '▶  Run simulation';
}
function boot() {
  const myGeneration = ++generation;
  if (worker) worker.terminate();
  state = null; failed = false; playing = false; pending = true;
  controls();
  worker = new Worker('worker.js');
  worker.onmessage = ({data}) => {
    if (myGeneration !== generation) return;
    if (data.type === 'loading') { message(`${data.message} First load can take a moment.`); return; }
    pending = false;
    if (data.type === 'error') {
      failed = true; playing = false;
      message(`Engine could not run: ${data.message}. Check your connection, then use Apply & restart to retry.`, true);
      controls(); return;
    }
    state = data.state;
    if (state.finished) playing = false;
    render(); controls();
  };
  worker.onerror = event => {
    pending = false; playing = false; failed = true;
    message(`Engine unavailable: ${event.message || 'Worker could not start'}. Apply & restart to retry.`, true); controls();
  };
  request('reset', {config:configuration()});
}
form.addEventListener('submit', event => {event.preventDefault(); if (form.reportValidity()) boot();});
$('preset').onchange = () => {
  const presets = {balanced:{riders:12,processors:4,orders_per_hour:60},rush:{riders:12,processors:4,orders_per_hour:150},lean:{riders:4,processors:4,orders_per_hour:60}};
  for (const [key,value] of Object.entries(presets[$('preset').value])) form.elements[key].value=value;
  if(state) message('Setup changed. Apply & restart to run the new scenario.');
};
form.addEventListener('input',()=>{if(state) message('Setup changed. Apply & restart to run the new scenario.');});
$('play').onclick = () => { playing=!playing; controls(); renderStatus(); };
$('step').onclick = () => request('advance',{minutes:1});
setInterval(()=>{ if(playing && !pending && !failed && state && !state.finished) request('advance',{minutes:Number($('speed').value)/5}); },200);
$('filter').onchange = renderOrders;
for (const id of ['method-button','method-footer']) $(id).onclick = () => $('method').showModal();
$('method').addEventListener('click',event=>{if(event.target === $('method')) $('method').close();});
function renderStatus() {
  if(!state) return;
  $('run-status').textContent = state.finished ? 'COMPLETED' : playing ? '● RUNNING' : state.time ? 'PAUSED' : 'READY TO RUN';
}
function render() {
  const m=state.metrics;
  $('delivered').textContent=m.delivered;
  $('placed').textContent=`${m.placed} total orders placed`;
  $('average').textContent=fmt(m.avg_delivery);
  $('on-time').textContent=fmt(m.on_time,'% ',0);
  $('active').textContent=m.active;
  $('overdue').textContent=`${m.overdue} active orders overdue`;
  $('sla-label').textContent=`${state.config.sla}-minute delivery target`;
  $('clock').textContent=`${String(Math.floor(state.time)).padStart(2,'0')}:${String(Math.floor((state.time%1)*60)).padStart(2,'0')}`;
  $('duration-label').textContent=` / ${state.config.duration} min`;
  $('progress').max=state.config.duration; $('progress').value=state.time;
  for(const key of ['rider','packer']) {$(key+'-pct').textContent=fmt(m[key+'_utilization'],'%',0); $(key+'-util').value=m[key+'_utilization'];}
  $('queued').textContent=`${m.queued} orders`;
  $('order-count').textContent=m.placed;
  message(state.finished ? `Run complete · ${m.delivered} delivered, ${m.active} unfinished, ${m.overdue} overdue. Save a baseline to compare another strategy.` : state.time ? `Seed ${state.config.seed} · ${state.config.dispatch === 'fifo' ? 'FIFO' : 'Shortest-trip-first'} dispatch · ${m.delivered} completed deliveries · ${m.active} in progress` : 'Your lab is ready. Run the simulation or advance one minute at a time.');
  renderStatus(); drawMap(); drawChart(); renderOrders(); renderBaseline();
}
function renderOrders() {
  if(!state) return;
  const filter=$('filter').value;
  const orders=state.orders.filter(o=> filter==='all' || (filter==='active' ? o.status!=='delivered' : o.status===filter)).slice(-100).reverse();
  const tbody=$('order-rows'); tbody.replaceChildren();
  if(!orders.length) {const row=tbody.insertRow(); const cell=row.insertCell();cell.colSpan=7;cell.className='empty-state';cell.textContent=state.orders.length ? 'No orders match this filter.' : 'Your first delivery starts here. Run the simulation to see orders flow.';return;}
  for(const o of orders) {
    const row=tbody.insertRow();
    const duration=o.delivered_at==null?null:o.delivered_at-o.timestamp;
    const values=[o.order_key,o.customer_id,fmt(o.timestamp,' min'),labels[o.status],o.rider_id||'—',fmt(o.distance_km,' km'),duration==null?`Open · ${fmt(state.time-o.timestamp,' min')}`:fmt(duration,' min')];
    values.forEach((value,index)=>{const cell=row.insertCell(); if(index===3){const badge=document.createElement('span');badge.className=`badge ${o.status}`;badge.textContent=value;cell.append(badge);}else cell.textContent=value;});
  }
}
function drawMap() {
  const canvas=$('map'); const rect=canvas.getBoundingClientRect(); if(!rect.width)return;
  const ratio=window.devicePixelRatio||1; canvas.width=rect.width*ratio;canvas.height=rect.height*ratio;
  const ctx=canvas.getContext('2d');ctx.scale(ratio,ratio);
  const w=rect.width,h=rect.height;ctx.fillStyle='#eef2e8';ctx.fillRect(0,0,w,h);
  const scale=Math.min(w-80,h-62)/4.6;const xy=loc=>[w/2+loc[0]*scale,h/2+loc[1]*scale];
  // Street blocks and soft park tiles.
  for(let x=-4;x<4;x++)for(let y=-4;y<4;y++) {
    const [px,py]=xy([x*.5,y*.5]);ctx.fillStyle=(x*7+y*3)%9===0?'#dce7cd':'#e2e8d9';ctx.fillRect(px+4,py+4,scale*.5-8,scale*.5-8);
  }
  ctx.strokeStyle='#fcfdf8';ctx.lineWidth=3;
  for(let i=-4;i<=4;i++){const a=xy([i*.5,-2.2]),b=xy([i*.5,2.2]),c=xy([-2.2,i*.5]),d=xy([2.2,i*.5]);ctx.beginPath();ctx.moveTo(...a);ctx.lineTo(...b);ctx.moveTo(...c);ctx.lineTo(...d);ctx.stroke();}
  ctx.strokeStyle='#d4ddc7';ctx.lineWidth=1;ctx.setLineDash([3,5]);const corner=xy([-2,-2]);ctx.strokeRect(corner[0],corner[1],4*scale,4*scale);ctx.setLineDash([]);
  if(state) {
    const locations=new Map(state.customers.map(c=>[c.loc.join(','),c.loc]));
    for(const loc of locations.values()){const p=xy(loc);ctx.beginPath();ctx.arc(...p,2.4,0,Math.PI*2);ctx.fillStyle='#b3c19e';ctx.fill();}
    for(const o of state.orders.filter(o=>o.status!=='delivered')){const p=xy(o.customer_loc);ctx.beginPath();ctx.arc(...p,4.5,0,Math.PI*2);ctx.fillStyle=o.status==='en_route'?'#769b59':'#d4a44e';ctx.fill();ctx.strokeStyle='#f7faed';ctx.lineWidth=1.5;ctx.stroke();}
    for(const r of state.riders.filter(r=>r.state!=='available')){
      const a=xy(r.start),b=xy(r.destination);ctx.strokeStyle=r.state==='returning'?'#84a88980':'#387f5080';ctx.lineWidth=2;ctx.beginPath();ctx.moveTo(...a);ctx.lineTo(b[0],a[1]);ctx.lineTo(...b);ctx.stroke();
      const p=xy(r.loc);ctx.beginPath();ctx.arc(...p,5,0,Math.PI*2);ctx.fillStyle='#246445';ctx.fill();ctx.lineWidth=2;ctx.strokeStyle='#fff';ctx.stroke();
    }
  }
  const center=xy([0,0]);ctx.shadowColor='#496e3755';ctx.shadowBlur=18;ctx.fillStyle='#244f37';ctx.beginPath();ctx.roundRect(center[0]-15,center[1]-15,30,30,7);ctx.fill();ctx.shadowBlur=0;
  ctx.fillStyle='#dff3b0';ctx.font='bold 17px sans-serif';ctx.textAlign='center';ctx.fillText('q.',center[0],center[1]+5);
  ctx.fillStyle='#38573c';ctx.font='600 8px sans-serif';ctx.fillText('DARK STORE',center[0],center[1]+30);
}
new ResizeObserver(drawMap).observe($('map'));
function drawChart() {
  const history=state.history, svg=$('chart'), max=Math.max(5,...history.map(p=>p.placed)),duration=state.config.duration;
  const x=t=>34+t/duration*550,y=n=>130-n/max*112;
  let markup='';
  for(let i=0;i<4;i++){const value=max*i/3,py=y(value);markup+=`<line x1="34" y1="${py}" x2="584" y2="${py}" stroke="#edf0e6"/><text x="24" y="${py+3}" text-anchor="end" font-size="9" fill="#a0a78f">${Math.round(value)}</text>`;}
  for(let i=0;i<=4;i++)markup+=`<text x="${x(duration*i/4)}" y="153" text-anchor="middle" font-size="9" fill="#a0a78f">${Math.round(duration*i/4)}m</text>`;
  for(const [key,color] of [['placed','#b2bda8'],['delivered','#267357']]){const points=[[0,0],...history.map(p=>[p.time,p[key]])].map(([t,n])=>`${x(t)},${y(n)}`).join(' ');markup+=`<polyline points="${points}" fill="none" stroke="${color}" stroke-width="2.5" stroke-linejoin="round"/>`;}
  svg.innerHTML=markup;
}
$('save-baseline').onclick=()=>{
  baseline=JSON.parse(JSON.stringify({time:state.time,metrics:state.metrics,config:state.config}));
  try{localStorage.setItem('qdel-baseline-v1',JSON.stringify(baseline));}catch{}
  renderBaseline();message('Baseline saved on this device. Change your setup and apply to compare a new run.');
};
function renderBaseline() {
  if(!state || !baseline || !baseline.config || !baseline.metrics || typeof baseline.time!=='number')return;
  const root=$('baseline-content');root.replaceChildren();root.className='';
  const grid=document.createElement('div');grid.className='baseline-grid';root.append(grid);
  for(const [key,label,suffix] of [['delivered','Delivered orders',''],['avg_delivery','Avg. delivery',' min'],['on_time','Within SLA','%'],['overdue','Active overdue','']]){
    const cell=document.createElement('div');cell.className='baseline-cell';
    const title=document.createElement('small');title.textContent=label;
    const current=document.createElement('strong');current.textContent=fmt(state.metrics[key],suffix,key==='delivered'||key==='overdue'?0:1);
    const prior=document.createElement('span');prior.textContent=`Baseline: ${fmt(baseline.metrics[key],suffix,key==='delivered'||key==='overdue'?0:1)}`;
    cell.append(title,current,prior);grid.append(cell);
  }
  const meta=document.createElement('div');meta.className='baseline-meta';
  meta.textContent=`Baseline at ${fmt(baseline.time,' min')} · ${baseline.config.riders} riders · ${baseline.config.processors} packers · ${baseline.config.orders_per_hour} attempts/h · ${baseline.config.dispatch === 'fifo'?'FIFO':'Shortest trip'} · seed ${baseline.config.seed}. Current run at ${fmt(state.time,' min')}.`;
  if(Math.abs(state.time-baseline.time)>.01){const warning=document.createElement('b');warning.textContent=' Compare at the same elapsed time for a fair reading.';meta.append(warning);}
  if(state.config.seed!==baseline.config.seed || state.config.sla!==baseline.config.sla){const warning=document.createElement('b');warning.textContent=' Seed or SLA differs between these scenarios.';meta.append(warning);}
  root.append(meta);
}
$('export').onclick=()=>{
  const keys=['order_key','customer_id','timestamp','status','packing_at','ready_at','dispatched_at','delivered_at','rider_id','processor_id','distance_km'];
  const escape=value=>'"'+String(value??'').replaceAll('"','""')+'"';
  const csv=[keys,...state.orders.map(o=>keys.map(k=>o[k]))].map(row=>row.map(escape).join(',')).join('\r\n');
  const url=URL.createObjectURL(new Blob([csv],{type:'text/csv;charset=utf-8'}));
  const link=document.createElement('a');link.href=url;link.download=`qdel-seed-${state.config.seed}-${Math.floor(state.time)}min.csv`;link.click();setTimeout(()=>URL.revokeObjectURL(url),1000);
};
boot();
