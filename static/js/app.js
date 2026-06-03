/**
 * app.js — Animal Classification Expert System v2 (Portfolio SPA)
 * Features: Wizard, Image AI, Voice, Taxonomy Tree, Encyclopedia, History, Particles, Theme
 */

// ═══════════════════════════════════════════════════════════════════
//  STATE
// ═══════════════════════════════════════════════════════════════════
const STATE = {
  step: 1,
  totalSteps: 7,
  facts: {},
  theme: localStorage.getItem('aes-theme') || 'dark',
  history: [],
  taxonomy: null,
  section: 'wizard',
  speech: null
};

const TOTAL = 7;
const FIELDS = [null,'has_backbone','warm_blooded','body_covering','reproduction','diet','has_wings','aquatic'];
const SIDEBAR_MAP = [null,'t-backbone','t-warmblood','t-covering','t-repro','t-diet','t-wings','t-aquatic'];

const LABELS = {
  has_backbone:  {1:'Vertebrate', 0:'Invertebrate'},
  warm_blooded:  {1:'Warm-blooded', 0:'Cold-blooded'},
  body_covering: {fur:'Fur/Hair', feathers:'Feathers', scales:'Scales', moist_skin:'Moist Skin', shell:'Shell/Exoskeleton', none:'Bare/Chitin'},
  reproduction:  {live_birth:'Live Birth', eggs_land:'Eggs (Land)', eggs_water:'Eggs (Water)', metamorphosis:'Metamorphosis'},
  diet:          {carnivore:'Carnivore', herbivore:'Herbivore', omnivore:'Omnivore', insectivore:'Insectivore', any:'Unknown'},
  has_wings:     {1:'Yes',0:'No'},
  aquatic:       {1:'Aquatic',0:'Terrestrial'},
};

// ═══════════════════════════════════════════════════════════════════
//  INIT
// ═══════════════════════════════════════════════════════════════════
document.addEventListener('DOMContentLoaded', () => {
  initTheme();
  initParticles();
  showSection('wizard');
  showPanel(1);
  updateSidebar();
  updateProgress();
  loadStats();
  bindEvents();
  initSpeech();
});

function bindEvents(){
  // Theme toggle
  document.getElementById('themeToggle').addEventListener('click', toggleTheme);

  // Nav
  document.querySelectorAll('.nav-btn[data-section]').forEach(btn => {
    btn.addEventListener('click', () => showSection(btn.dataset.section));
  });

  // Image dropzone
  const dz = document.getElementById('dropzone');
  dz.addEventListener('click', () => document.getElementById('fileInput').click());
  dz.addEventListener('dragover', e => { e.preventDefault(); dz.classList.add('dragover'); });
  dz.addEventListener('dragleave', () => dz.classList.remove('dragover'));
  dz.addEventListener('drop', e => {
    e.preventDefault(); dz.classList.remove('dragover');
    if(e.dataTransfer.files.length) handleImageFile(e.dataTransfer.files[0]);
  });
  document.getElementById('fileInput').addEventListener('change', e => {
    if(e.target.files.length) handleImageFile(e.target.files[0]);
  });

  // Voice
  document.getElementById('voiceBtn').addEventListener('click', toggleVoice);

  // Search
  const searchInput = document.getElementById('searchInput');
  let debounce;
  searchInput.addEventListener('input', () => {
    clearTimeout(debounce);
    debounce = setTimeout(() => doSearch(searchInput.value), 350);
  });

  // Modal close
  document.getElementById('modalBackdrop').addEventListener('click', e => {
    if(e.target === e.currentTarget) closeModal();
  });
}

// ═══════════════════════════════════════════════════════════════════
//  THEME
// ═══════════════════════════════════════════════════════════════════
function initTheme(){
  document.documentElement.setAttribute('data-theme', STATE.theme);
  updateThemeIcon();
}
function toggleTheme(){
  STATE.theme = STATE.theme === 'dark' ? 'light' : 'dark';
  document.documentElement.setAttribute('data-theme', STATE.theme);
  localStorage.setItem('aes-theme', STATE.theme);
  updateThemeIcon();
}
function updateThemeIcon(){
  const btn = document.getElementById('themeToggle');
  btn.textContent = STATE.theme === 'dark' ? '☀️' : '🌙';
}

// ═══════════════════════════════════════════════════════════════════
//  SECTION NAV
// ═══════════════════════════════════════════════════════════════════
function showSection(id){
  STATE.section = id;
  document.querySelectorAll('.section').forEach(s => s.classList.remove('active'));
  document.getElementById('sec-'+id)?.classList.add('active');
  document.querySelectorAll('.nav-btn').forEach(b => b.classList.remove('active'));
  document.querySelector(`.nav-btn[data-section="${id}"]`)?.classList.add('active');

  if(id === 'taxonomy') renderTaxonomy();
  if(id === 'encyclopedia') doSearch('');
  if(id === 'history') loadHistory();
}

// ═══════════════════════════════════════════════════════════════════
//  WIZARD LOGIC
// ═══════════════════════════════════════════════════════════════════
function selectYN(btn){
  const parent = btn.closest('.panel');
  parent.querySelectorAll('.yn-btn').forEach(b => b.classList.remove('selected'));
  btn.classList.add('selected');
  STATE.facts[btn.dataset.field] = parseInt(btn.dataset.val);
  updateSidebar();
  document.getElementById('btnNext').disabled = false;
  if(STATE.step < TOTAL) setTimeout(goNext, 400);
  else showClassifyBtn();
}

function selectOpt(btn){
  const parent = btn.closest('.panel');
  parent.querySelectorAll('.opt-btn').forEach(b => b.classList.remove('selected'));
  btn.classList.add('selected');
  STATE.facts[btn.dataset.field] = btn.dataset.val;
  updateSidebar();
  document.getElementById('btnNext').disabled = false;
  if(STATE.step < TOTAL) setTimeout(goNext, 400);
  else showClassifyBtn();
}

function goNext(){
  if(STATE.step >= TOTAL) return;
  STATE.step++;
  showPanel(STATE.step);
}
function goBack(){
  if(STATE.step <= 1) return;
  STATE.step--;
  showPanel(STATE.step);
}
function showPanel(n){
  document.querySelectorAll('.panel').forEach(p => p.classList.remove('active'));
  document.getElementById('panel-'+n)?.classList.add('active');
  document.getElementById('btnBack').style.display = n>1 ? '' : 'none';

  const field = FIELDS[n];
  const hasAns = field && STATE.facts[field] !== undefined;
  const btnNext = document.getElementById('btnNext');
  btnNext.disabled = !hasAns;

  if(n === TOTAL && STATE.facts[field] !== undefined){
    showClassifyBtn();
  } else {
    btnNext.style.display = '';
    document.getElementById('btnClassify').style.display = 'none';
  }
  updateProgress();
}
function showClassifyBtn(){
  document.getElementById('btnNext').style.display = 'none';
  document.getElementById('btnClassify').style.display = '';
}
function updateProgress(){
  const pct = ((STATE.step - 1) / TOTAL) * 100;
  document.getElementById('progressFill').style.width = pct + '%';
  for(let i=1;i<=TOTAL;i++){
    const el = document.getElementById('s'+i);
    if(!el) continue;
    el.className = 'step' + (i < STATE.step ? ' done' : i === STATE.step ? ' active' : '');
  }
}
function updateSidebar(){
  const entries = [
    ['t-backbone', STATE.facts.has_backbone, LABELS.has_backbone],
    ['t-warmblood', STATE.facts.warm_blooded, LABELS.warm_blooded],
    ['t-covering',  STATE.facts.body_covering, LABELS.body_covering],
    ['t-repro',     STATE.facts.reproduction,  LABELS.reproduction],
    ['t-diet',      STATE.facts.diet,          LABELS.diet],
    ['t-wings',     STATE.facts.has_wings,     LABELS.has_wings],
    ['t-aquatic',   STATE.facts.aquatic,       LABELS.aquatic],
  ];
  entries.forEach(([id, val, map]) => {
    const el = document.getElementById(id);
    if(!el) return;
    const label = (val !== undefined && val !== null) ? (map[val] || val) : null;
    if(label){
      el.textContent = label;
      el.className = 'trait-val';
    } else {
      el.textContent = '—';
      el.className = 'trait-val empty';
    }
  });
}

async function runClassify(){
  hideError();
  hideResult();
  showSpinner(true);
  try{
    const resp = await fetch('/api/classify', {
      method:'POST',
      headers:{'Content-Type':'application/json'},
      body: JSON.stringify(STATE.facts),
    });
    const data = await resp.json();
    showSpinner(false);
    if(!data.success) return showError(data.message || 'Classification failed.');
    renderResult(data, 'wizard');
  } catch(e){
    showSpinner(false);
    showError('Server error. Make sure Flask is running on port 5000.');
  }
}

function resetAll(){
  STATE.facts = {};
  STATE.step = 1;
  document.querySelectorAll('.opt-btn,.yn-btn').forEach(b => b.classList.remove('selected'));
  hideResult();
  hideError();
  showPanel(1);
  updateSidebar();
  updateProgress();
  window.scrollTo({top:0, behavior:'smooth'});
}

// ═══════════════════════════════════════════════════════════════════
//  IMAGE CLASSIFICATION
// ═══════════════════════════════════════════════════════════════════
function handleImageFile(file){
  if(!file.type.startsWith('image/')){
    showErrorImage('Please upload an image file (JPG, PNG, WEBP).');
    return;
  }
  const url = URL.createObjectURL(file);
  const preview = document.getElementById('imgPreview');
  preview.src = url;
  preview.style.display = '';
  document.getElementById('imgPreviewWrap').style.display = 'block';
  document.getElementById('imgResult').style.display = 'none';
  hideErrorImage();
  uploadImage(file);
}

async function uploadImage(file){
  document.getElementById('imgSpinner').classList.add('show');
  const form = new FormData();
  form.append('image', file);
  try{
    const resp = await fetch('/api/classify_image', {method:'POST', body:form});
    const data = await resp.json();
    document.getElementById('imgSpinner').classList.remove('show');
    if(!data.success) return showErrorImage(data.message || 'Image classification failed.');
    renderImageResult(data);
  } catch(e){
    document.getElementById('imgSpinner').classList.remove('show');
    showErrorImage('Server error. Is Flask running? Does it have torch installed?');
  }
}

function renderImageResult(d){
  const wrap = document.getElementById('imgResult');
  wrap.style.display = 'block';
  wrap.innerHTML = '';

  if(d.species){
    const s = d.species;
    wrap.innerHTML = `
      <div class="glass result-hero">
        <span class="res-emoji">${s.emoji || '🐾'}</span>
        <div class="res-class">${s.common_name}</div>
        <div class="res-sci">${s.scientific_name}</div>
        <div class="res-desc">${s.description || ''}</div>
        <div class="conf-badge">🤖 AI Confidence: <strong>${d.confidence}%</strong></div>
        ${d.top5 ? `<div style="margin-top:0.8rem;font-size:0.78rem;color:var(--muted)">Top-5: ${d.top5.slice(0,3).map(t=>t.label).join(', ')}</div>` : ''}
      </div>
      <div class="result-grid">
        <div class="glass info-card"><h4>📦 Taxonomy</h4>
          <p><strong>Class:</strong> ${s.class_name || '—'}<br><strong>Order:</strong> ${s.order_name || '—'}</p>
        </div>
        <div class="glass info-card"><h4>🌍 Info</h4>
          <p><strong>Habitat:</strong> ${s.habitat || '—'}<br><strong>Diet:</strong> ${s.diet || '—'}</p>
        </div>
      </div>
      <div class="glass info-card"><h4>🧠 Fun Fact</h4><p>${s.facts || '—'}</p></div>
      <div class="text-center mt-1"><button class="btn btn-outline" onclick="document.getElementById('fileInput').click()">📤 Classify Another Image</button></div>
    `;
    wrap.classList.add('active');
  } else {
    // No exact species match
    wrap.innerHTML = `
      <div class="glass result-hero">
        <span class="res-emoji">🔍</span>
        <div class="res-class">${d.label || 'Unknown'}</div>
        <div class="res-desc">Image AI detected this animal but it is not yet mapped in our taxonomy database.</div>
        <div class="conf-badge">🤖 Confidence: <strong>${d.confidence}%</strong></div>
      </div>
      <div class="text-center mt-1"><button class="btn btn-outline" onclick="document.getElementById('fileInput').click()">📤 Try Another</button></div>
    `;
    wrap.classList.add('active');
  }
}

function showErrorImage(msg){
  const box = document.getElementById('imgError');
  box.textContent = '⚠️ ' + msg;
  box.classList.add('show');
}
function hideErrorImage(){ document.getElementById('imgError').classList.remove('show'); }

// ═══════════════════════════════════════════════════════════════════
//  VOICE (Web Speech API)
// ═══════════════════════════════════════════════════════════════════
function initSpeech(){
  const SR = window.SpeechRecognition || window.webkitSpeechRecognition;
  if(!SR){
    document.getElementById('voiceStatus').textContent = '⚠️ Speech Recognition not supported in this browser. Try Chrome/Edge.';
    document.getElementById('voiceBtn').style.opacity = '0.4';
    return;
  }
  STATE.speech = new SR();
  STATE.speech.continuous = false;
  STATE.speech.interimResults = true;
  STATE.speech.lang = 'en-US';

  STATE.speech.onstart = () => {
    document.getElementById('voiceBtn').classList.add('recording');
    document.getElementById('voiceStatus').textContent = '🎙️ Listening... describe the animal!';
    document.getElementById('voiceTranscript').textContent = '';
  };
  STATE.speech.onend = () => {
    document.getElementById('voiceBtn').classList.remove('recording');
    document.getElementById('voiceStatus').textContent = 'Tap microphone to speak again';
  };
  STATE.speech.onresult = (e) => {
    let text = '';
    for(let i=e.resultIndex;i<e.results.length;i++){
      text += e.results[i][0].transcript;
    }
    document.getElementById('voiceTranscript').textContent = text;
    if(e.results[e.results.length-1].isFinal){
      runVoiceClassify(text);
    }
  };
  STATE.speech.onerror = (e) => {
    document.getElementById('voiceBtn').classList.remove('recording');
    document.getElementById('voiceStatus').textContent = 'Error: ' + e.error;
  };
}
function toggleVoice(){
  if(!STATE.speech) return;
  if(document.getElementById('voiceBtn').classList.contains('recording')){
    STATE.speech.stop();
  } else {
    STATE.speech.start();
  }
}
async function runVoiceClassify(text){
  document.getElementById('voiceSpinner').classList.add('show');
  hideErrorVoice();
  try{
    const resp = await fetch('/api/voice_classify', {
      method:'POST', headers:{'Content-Type':'application/json'},
      body: JSON.stringify({text}),
    });
    const data = await resp.json();
    document.getElementById('voiceSpinner').classList.remove('show');
    if(!data.success) return showErrorVoice(data.message || 'Could not classify from voice.');
    renderResult(data, 'voice', 'voiceResult');
  } catch(e){
    document.getElementById('voiceSpinner').classList.remove('show');
    showErrorVoice('Server error.');
  }
}
function showErrorVoice(msg){
  const box = document.getElementById('voiceError');
  box.textContent = '⚠️ ' + msg;
  box.classList.add('show');
}
function hideErrorVoice(){ document.getElementById('voiceError').classList.remove('show'); }

// ═══════════════════════════════════════════════════════════════════
//  RESULT RENDERING (shared)
// ═══════════════════════════════════════════════════════════════════
function hideResult(){
  const r = document.getElementById('resultPanel');
  r.style.display = 'none'; r.classList.remove('active');
}
function showResult(containerId='resultPanel'){ 
  const r = document.getElementById(containerId);
  r.style.display = 'block'; 
  requestAnimationFrame(()=>r.classList.add('active'));
  setTimeout(()=>r.scrollIntoView({behavior:'smooth', block:'start'}), 50);
}
function showSpinner(show){
  document.getElementById('spinner').style.display = show ? 'block' : 'none';
}
function showError(msg){
  const box = document.getElementById('errorBox');
  box.textContent = '⚠️ ' + msg;
  box.style.display = 'flex';
}
function hideError(){ document.getElementById('errorBox').style.display = 'none'; }

function renderResult(d, mode='wizard', containerId=null){
  const panel = document.getElementById(containerId || 'resultPanel');
  panel.innerHTML = '';

  const tc = d.taxon_class || {};
  const to = d.taxon_order || {};
  const best = d.best_species || (d.species && d.species[0]) || null;

  // Hero
  const emoji = best ? best.emoji : (tc.emoji || '🐾');
  const title = best ? best.common_name : (to.common_name || tc.common_name || 'Unknown');
  const sci = best ? best.scientific_name : (to.name || tc.name || '');
  const desc = best ? (best.description || '') : (tc.description || '');

  const hero = document.createElement('div');
  hero.className = 'glass result-hero';
  hero.innerHTML = `
    <span class="res-emoji">${emoji}</span>
    <div class="res-class">${title}</div>
    <div class="res-sci">${sci}</div>
    <div class="res-desc">${desc}</div>
    ${d.hybrid_confidence !== undefined ? `<div class="conf-badge">🧠 Hybrid Confidence: <strong>${d.hybrid_confidence}%</strong></div>` : ''}
    ${d.ml_confidence ? `<div class="conf-badge" style="margin-left:0.5rem;background:rgba(0,168,255,0.08);border-color:rgba(0,168,255,0.2);color:var(--accent-2)">🤖 ML: <strong>${d.ml_confidence}%</strong></div>` : ''}
    ${d.confidence && !d.hybrid_confidence ? `<div class="conf-badge">📊 Confidence: <strong>${d.confidence}%</strong></div>` : ''}
  `;
  panel.appendChild(hero);

  // Detail cards
  if(best){
    const grid = document.createElement('div');
    grid.className = 'result-grid';
    grid.innerHTML = `
      <div class="glass info-card"><h4>🌍 Habitat & Distribution</h4><p>${best.habitat || '—'}<br><br><strong>Range:</strong> ${best.distribution || '—'}</p></div>
      <div class="glass info-card"><h4>📊 Life Data</h4>
        <ul>
          <li><strong>Diet:</strong> ${best.diet || '—'}</li>
          <li><strong>Lifespan:</strong> ${best.lifespan || '—'}</li>
          <li><strong>Status:</strong> ${best.conservation_status || '—'}</li>
          <li><strong>Class:</strong> ${best.class_name || tc.common_name || '—'}</li>
          <li><strong>Order:</strong> ${best.order_name || to.common_name || '—'}</li>
        </ul>
      </div>
    `;
    panel.appendChild(grid);
    if(best.facts){
      const facts = document.createElement('div');
      facts.className = 'glass info-card';
      facts.innerHTML = `<h4>✨ Did You Know?</h4><p>${best.facts}</p>`;
      panel.appendChild(facts);
    }
  } else {
    // Class/Order generic info
    const grid = document.createElement('div');
    grid.className = 'result-grid';
    grid.innerHTML = `
      <div class="glass info-card"><h4>📦 Taxonomy</h4>
        <p><strong>Class:</strong> ${tc.name || '—'} (${tc.common_name || ''})<br>
           <strong>Order:</strong> ${to.name || '—'} (${to.common_name || '—'})</p>
      </div>
      <div class="glass info-card"><h4>🧬 Characteristics</h4><p>${tc.characteristics || '—'}</p></div>
    `;
    panel.appendChild(grid);
  }

  // Examples
  if(d.examples && d.examples.length){
    const exWrap = document.createElement('div');
    exWrap.className = 'glass info-card';
    exWrap.innerHTML = `<h4>🐾 Known Examples</h4><div class="chips">${d.examples.map(e => `<span class="chip">${e}</span>`).join('')}</div>`;
    panel.appendChild(exWrap);
  }

  // Alternatives
  if(d.alternatives && d.alternatives.length){
    const altWrap = document.createElement('div');
    altWrap.className = 'glass info-card';
    altWrap.innerHTML = `<h4>🔀 Close Alternatives</h4><div class="chips">${d.alternatives.map(a => `<span class="chip">${a.emoji} ${a.class_name}${a.order_name ? ' — '+a.order_name : ''} (${a.confidence}%)</span>`).join('')}</div>`;
    panel.appendChild(altWrap);
  }

  // Reasoning
  if(d.reasoning && d.reasoning.length){
    const rBox = document.createElement('div');
    rBox.className = 'glass reasoning-box';
    rBox.innerHTML = `<h4>🧠 Inference Reasoning Chain</h4>` +
      d.reasoning.map(s => `<div class="reason-step">${escapeHtml(s)}</div>`).join('');
    panel.appendChild(rBox);
  }

  // Action button
  const act = document.createElement('div');
  act.className = 'text-center mt-1';
  act.innerHTML = `<button class="btn btn-outline" onclick="resetAll()">← Classify Another Animal</button>`;
  panel.appendChild(act);

  showResult(containerId || 'resultPanel');
}

function escapeHtml(t){
  const d = document.createElement('div'); d.textContent = t; return d.innerHTML;
}

// ═══════════════════════════════════════════════════════════════════
//  TAXONOMY TREE
// ═══════════════════════════════════════════════════════════════════
async function renderTaxonomy(){
  const wrap = document.getElementById('taxonomyWrap');
  if(STATE.taxonomy) return drawTaxonomy(STATE.taxonomy);
  wrap.innerHTML = '<div class="spinner-wrap show"><div class="spinner"></div>Loading taxonomy tree...</div>';
  try{
    const resp = await fetch('/api/taxonomy');
    const data = await resp.json();
    if(data.success){
      STATE.taxonomy = data.tree;
      drawTaxonomy(data.tree);
    }
  } catch(e){ wrap.innerHTML = '<p class="text-center" style="color:var(--muted)">Failed to load taxonomy.</p>'; }
}

function drawTaxonomy(tree){
  const wrap = document.getElementById('taxonomyWrap');
  wrap.innerHTML = '';
  tree.forEach((cls, idx) => {
    const node = document.createElement('div');
    node.className = 'glass tree-wrap' + (idx===0?' open':'');
    node.innerHTML = `
      <div class="tree-class-header" onclick="this.parentElement.classList.toggle('open')">
        <span class="tree-toggle">▶</span>
        <span>${cls.emoji || '◆'} ${cls.name}</span>
        <span style="color:var(--muted);font-size:0.8rem;margin-left:0.4rem">— ${cls.common_name}</span>
      </div>
      <div class="tree-orders" style="display:${idx===0?'block':'none'}">
        ${(cls.orders || []).map(o => `
          <div class="tree-order">
            <div class="tree-order-name">${o.emoji || '•'} ${o.name} <span style="color:var(--muted);font-size:0.82rem">(${o.common_name || ''})</span></div>
            <div class="tree-species">
              ${(o.species || []).map(sp => `
                <span class="species-tag" onclick="openSpeciesModal(${sp.id})">${sp.emoji || '🐾'} ${sp.common_name}</span>
              `).join('')}
              ${(!o.species || !o.species.length) ? '<span style="color:var(--muted);font-size:0.75rem">No species data yet</span>' : ''}
            </div>
          </div>
        `).join('')}
      </div>
    `;
    // Manual toggle logic override for animation
    const header = node.querySelector('.tree-class-header');
    const ordersDiv = node.querySelector('.tree-orders');
    header.onclick = () => {
      const isOpen = node.classList.toggle('open');
      ordersDiv.style.display = isOpen ? 'block' : 'none';
    };
    wrap.appendChild(node);
  });
}

// ═══════════════════════════════════════════════════════════════════
//  ENCYCLOPEDIA / SEARCH
// ═══════════════════════════════════════════════════════════════════
async function doSearch(q){
  const wrap = document.getElementById('encycloGrid');
  wrap.innerHTML = '<div class="spinner-wrap show" style="grid-column:1/-1"><div class="spinner"></div></div>';
  try{
    const url = q ? `/api/search?q=${encodeURIComponent(q)}` : '/api/search?q=';
    const resp = await fetch(url);
    const data = await resp.json();
    wrap.innerHTML = '';
    if(!data.results || !data.results.length){
      wrap.innerHTML = '<p class="text-center" style="color:var(--muted);grid-column:1/-1">No results found.</p>';
      return;
    }
    data.results.forEach(sp => {
      const card = document.createElement('div');
      card.className = 'glass encyco-card';
      card.innerHTML = `
        <div class="ec-emoji">${sp.emoji || '🐾'}</div>
        <div class="ec-title">${sp.common_name}</div>
        <div class="ec-sub">${sp.scientific_name}</div>
        <div class="ec-meta">
          <span>${sp.class_name || ''}</span>
          <span style="color:${statusColor(sp.conservation_status)}">${sp.conservation_status || ''}</span>
        </div>
      `;
      card.onclick = () => openSpeciesModal(sp.id);
      wrap.appendChild(card);
    });
  } catch(e){
    wrap.innerHTML = '<p class="text-center" style="color:var(--danger);grid-column:1/-1">Search failed.</p>';
  }
}
function statusColor(s){
  if(!s) return 'var(--muted)';
  const low = s.toLowerCase();
  if(low.includes('endangered')) return 'var(--danger)';
  if(low.includes('vulnerable') || low.includes('threatened')) return 'var(--warn)';
  if(low.includes('near')) return '#f0a000';
  return 'var(--success)';
}

// ═══════════════════════════════════════════════════════════════════
//  SPECIES MODAL
// ═══════════════════════════════════════════════════════════════════
async function openSpeciesModal(id){
  const backdrop = document.getElementById('modalBackdrop');
  const body = document.getElementById('modalBody');
  body.innerHTML = '<div class="spinner-wrap show"><div class="spinner"></div>Loading...</div>';
  backdrop.classList.add('show');
  try{
    const resp = await fetch(`/api/species/${id}`);
    const data = await resp.json();
    if(!data.success) throw new Error(data.message);
    const s = data.data;
    body.innerHTML = `
      <div class="md-hero">
        <div class="md-emoji">${s.emoji || '🐾'}</div>
        <div class="md-info">
          <h4>${s.common_name}</h4>
          <div class="sci">${s.scientific_name}</div>
          <div style="color:var(--muted);font-size:0.85rem">${s.class_name} · ${s.order_name}</div>
        </div>
      </div>
      <div class="md-grid">
        <div class="md-item"><h5>🌍 Habitat</h5><p>${s.habitat || '—'}</p></div>
        <div class="md-item"><h5>🍽️ Diet</h5><p>${s.diet || '—'}</p></div>
        <div class="md-item"><h5>⏳ Lifespan</h5><p>${s.lifespan || '—'}</p></div>
        <div class="md-item"><h5>📍 Distribution</h5><p>${s.distribution || '—'}</p></div>
        <div class="md-item"><h5>🛡️ Conservation</h5><p style="color:${statusColor(s.conservation_status)}">${s.conservation_status || '—'}</p></div>
        <div class="md-item"><h5>ℹ️ Class Description</h5><p>${s.description || '—'}</p></div>
      </div>
      <div class="md-facts"><strong>✨ Fun Fact:</strong> ${s.facts || 'No fact available.'}</div>
    `;
  } catch(e){
    body.innerHTML = '<p style="color:var(--danger)">Failed to load species details.</p>';
  }
}
function closeModal(){ document.getElementById('modalBackdrop').classList.remove('show'); }

// ═══════════════════════════════════════════════════════════════════
//  HISTORY
// ═══════════════════════════════════════════════════════════════════
async function loadHistory(){
  const wrap = document.getElementById('historyTable');
  wrap.innerHTML = '<tr><td colspan="6" style="text-align:center"><div class="spinner" style="margin:1rem auto"></div></td></tr>';
  try{
    const resp = await fetch('/api/history');
    const data = await resp.json();
    if(!data.success) throw new Error();
    wrap.innerHTML = '';
    if(!data.history || !data.history.length){
      wrap.innerHTML = '<tr><td colspan="6" style="text-align:center;color:var(--muted)">No classifications yet. Start exploring!</td></tr>';
      return;
    }
    data.history.slice(0,50).forEach(h => {
      const tr = document.createElement('tr');
      tr.innerHTML = `
        <td>${h.timestamp || '—'}</td>
        <td><span class="badge badge-${h.input_type || 'wizard'}">${h.input_type || 'wizard'}</span></td>
        <td>${h.class_name || '—'} ${h.order_name ? '· '+h.order_name : ''}</td>
        <td>${h.species_emoji || ''} ${h.species_name || '—'}</td>
        <td><strong style="color:var(--accent)">${h.confidence || '—'}%</strong></td>
        <td>${h.ml_confidence ? `<span style="color:var(--accent-2)">${h.ml_confidence}%</span>` : '—'}</td>
      `;
      wrap.appendChild(tr);
    });
  } catch(e){
    wrap.innerHTML = '<tr><td colspan="6" style="text-align:center;color:var(--danger)">Failed to load history.</td></tr>';
  }
}

// ═══════════════════════════════════════════════════════════════════
//  STATS
// ═══════════════════════════════════════════════════════════════════
async function loadStats(){
  try{
    const resp = await fetch('/api/stats');
    const data = await resp.json();
    if(data.success){
      document.getElementById('statClasses').textContent = data.stats.classes || 0;
      document.getElementById('statOrders').textContent = data.stats.orders || 0;
      document.getElementById('statSpecies').textContent = data.stats.species || 0;
      document.getElementById('statClassifications').textContent = data.stats.classifications || 0;
    }
  } catch(e){ /* silent */ }
}

// ═══════════════════════════════════════════════════════════════════
//  PARTICLE CANVAS BACKGROUND
// ═══════════════════════════════════════════════════════════════════
function initParticles(){
  const canvas = document.getElementById('particles');
  if(!canvas) return;
  const ctx = canvas.getContext('2d');
  let particles = [];
  const count = window.innerWidth < 768 ? 30 : 70;

  function resize(){
    canvas.width = window.innerWidth;
    canvas.height = window.innerHeight;
  }
  resize();
  window.addEventListener('resize', resize);

  for(let i=0;i<count;i++){
    particles.push({
      x:Math.random()*canvas.width, y:Math.random()*canvas.height,
      vx:(Math.random()-0.5)*0.4, vy:(Math.random()-0.5)*0.4,
      size:Math.random()*2+1,
      alpha:Math.random()*0.5+0.2,
    });
  }

  function draw(){
    ctx.clearRect(0,0,canvas.width,canvas.height);
    particles.forEach((p,i) => {
      p.x += p.vx; p.y += p.vy;
      if(p.x<0) p.x = canvas.width;
      if(p.x>canvas.width) p.x = 0;
      if(p.y<0) p.y = canvas.height;
      if(p.y>canvas.height) p.y = 0;
      ctx.beginPath();
      ctx.arc(p.x, p.y, p.size, 0, Math.PI*2);
      ctx.fillStyle = `rgba(0,255,180,${p.alpha})`;
      ctx.fill();
      // connect nearby
      for(let j=i+1;j<particles.length;j++){
        const q = particles[j];
        const dx = p.x-q.x, dy = p.y-q.y;
        const dist = Math.sqrt(dx*dx+dy*dy);
        if(dist < 120){
          ctx.beginPath();
          ctx.moveTo(p.x,p.y); ctx.lineTo(q.x,q.y);
          ctx.strokeStyle = `rgba(0,255,180,${0.12*(1-dist/120)})`;
          ctx.lineWidth = 0.5;
          ctx.stroke();
        }
      }
    });
    requestAnimationFrame(draw);
  }
  draw();
}
