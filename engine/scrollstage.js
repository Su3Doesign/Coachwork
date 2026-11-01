// Scroll stage: one 3D model on a fixed, transparent canvas behind the whole page.
// Every element with data-pose='{...}' is a stop; as the page scrolls the camera glides from stop to stop
// (orbit yaw/pitch/distance round an anchor, lens, and a screen shift that moves the model left/right/up/down),
// holding while a stop's content is centred and easing between stops. Damped, with a slow idle drift and pointer parallax.
import * as THREE from 'three';
import { GLTFLoader } from 'three/addons/loaders/GLTFLoader.js';
import { DRACOLoader } from 'three/addons/loaders/DRACOLoader.js';
import { RoomEnvironment } from 'three/addons/environments/RoomEnvironment.js';
import { EffectComposer } from 'three/addons/postprocessing/EffectComposer.js';
import { RenderPass } from 'three/addons/postprocessing/RenderPass.js';
import { UnrealBloomPass } from 'three/addons/postprocessing/UnrealBloomPass.js';
import { OutputPass } from 'three/addons/postprocessing/OutputPass.js';
import { ShaderPass } from 'three/addons/postprocessing/ShaderPass.js';

// Bloom that keeps a transparent canvas transparent: the stock blur writes alpha 1 everywhere, which would turn
// the page behind the model black, so its alpha follows the glow's own brightness instead.
function makeBloom(renderer, scene, camera, o = {}) {
  const composer = new EffectComposer(renderer);
  composer.setPixelRatio(renderer.getPixelRatio());
  composer.addPass(new RenderPass(scene, camera));
  // a mirror-sharp highlight can overflow the half-float buffer; one bad pixel then spreads through the blur as a
  // black block, so overflow and NaN are cleaned before the bloom
  composer.addPass(new ShaderPass({ uniforms: { tDiffuse: { value: null } },
    vertexShader: 'varying vec2 vUv; void main() { vUv = uv; gl_Position = projectionMatrix * modelViewMatrix * vec4(position, 1.0); }',
    fragmentShader: 'uniform sampler2D tDiffuse; varying vec2 vUv; void main() { vec4 c = texture2D(tDiffuse, vUv); if (any(isnan(c)) || any(isinf(c))) c = vec4(0.0); c.rgb = min(c.rgb, vec3(40.0)); c.a = clamp(c.a, 0.0, 1.0); gl_FragColor = c; }' }));
  const bloom = new UnrealBloomPass(new THREE.Vector2(512, 512), o.strength ?? 0.55, o.radius ?? 0.55, o.threshold ?? 1.0);
  for (const m of bloom.separableBlurMaterials) {
    m.fragmentShader = m.fragmentShader.replace('gl_FragColor = vec4(diffuseSum/weightSum, 1.0);',
      'vec3 cc = diffuseSum / weightSum; gl_FragColor = vec4(cc, clamp(max(cc.r, max(cc.g, cc.b)), 0.0, 1.0));');
    m.needsUpdate = true;
  }
  composer.addPass(bloom);
  composer.addPass(new OutputPass());
  return { composer, bloom };
}

const DEG = Math.PI / 180;
const POSE_KEYS = ['yaw', 'pitch', 'dist', 'fov', 'tx', 'ty', 'tz', 'sx', 'sy', 'roll', 'lights', 'spin', 'env', 'drift', 'shadow'];
const BASE_POSE = { at: 'center', yaw: 30, pitch: 8, dist: 2.4, fov: 30, tx: 0, ty: 0, tz: 0, sx: 0, sy: 0, roll: 0, lights: 0, spin: 0, env: 1, drift: 1, shadow: 1 };

// A car-photography studio for reflections: a dim cyclorama, one long overhead softbox, two side strips, a rim light
// behind and a pale floor, so dark paint shows crisp highlight lines instead of a washed-out room.
function studioRoom(o = {}) {
  const k = Object.assign({ walls: 0.16, floor: 0.32, top: 7, strips: 4.5, rim: 3 }, typeof o === 'object' ? o : {});
  const room = new THREE.Scene();
  const box = new THREE.Mesh(new THREE.BoxGeometry(14, 8, 14), new THREE.MeshBasicMaterial({ side: THREE.BackSide }));
  box.material.color.setScalar(k.walls); box.position.y = 3.6; room.add(box);
  const glow = (w, h, v, pos, look) => {
    const m = new THREE.Mesh(new THREE.PlaneGeometry(w, h), new THREE.MeshBasicMaterial({ side: THREE.DoubleSide }));
    m.material.color.setScalar(v); m.position.set(...pos); m.lookAt(...look); room.add(m); return m;
  };
  glow(14, 14, k.floor, [0, -0.39, 0], [0, 10, 0]);
  glow(7, 2.4, k.top, [0, 5.2, 0], [0, 0, 0]);
  glow(0.35, 5, k.strips, [-4.2, 2.2, 0], [0, 1.4, 0]).rotation.z += 0;
  glow(0.35, 5, k.strips, [4.2, 2.2, 0], [0, 1.4, 0]);
  glow(4, 1.2, k.rim, [0, 2.4, -6.5], [0, 1, 0]);
  glow(2.5, 0.8, k.rim * 0.6, [0, 1.6, 6.5], [0, 1, 0]);
  return room;
}

function scrollStage(o) {
  const opt = Object.assign({ front: -1, ground: true, exposure: 1, envIntensity: 1, hold: 0.18, damp: 4.2, mobile: 700,
    key: { pos: [-4, 7, -3], intensity: 1.4, color: 0xffffff }, rim: { pos: [5, 3, 4], intensity: 0.8, color: 0xffffff } }, o);
  const reduce = matchMedia('(prefers-reduced-motion: reduce)').matches;
  const canvas = opt.canvas;
  const renderer = new THREE.WebGLRenderer({ canvas, antialias: true, alpha: true, powerPreference: 'high-performance' });
  renderer.setPixelRatio(Math.min(devicePixelRatio, 1.75));
  renderer.toneMapping = THREE.ACESFilmicToneMapping;
  renderer.toneMappingExposure = opt.exposure;
  const scene = new THREE.Scene();
  const pmrem = new THREE.PMREMGenerator(renderer);
  scene.environment = pmrem.fromScene(opt.studio ? studioRoom(opt.studio) : new RoomEnvironment(), 0.02).texture;
  const camera = new THREE.PerspectiveCamera(30, 1, 0.01, 100);
  const key = new THREE.DirectionalLight(opt.key.color, opt.key.intensity); key.position.set(...opt.key.pos); scene.add(key);
  const rim = new THREE.DirectionalLight(opt.rim.color, opt.rim.intensity); rim.position.set(...opt.rim.pos); scene.add(rim);
  const holder = new THREE.Group(); scene.add(holder);
  renderer.setClearColor(0x000000, 0);
  const fx = opt.bloom ? makeBloom(renderer, scene, camera, opt.bloom) : null;

  const ctx = { THREE, scene, camera, renderer, holder, key, rim, anchors: { center: new THREE.Vector3() }, model: null, size: null, pose: { ...BASE_POSE }, opt, ready: null };

  /* ---------- load (base64 text or binary) ---------- */
  const loader = new GLTFLoader();
  if (opt.draco) loader.setDRACOLoader(new DRACOLoader().setDecoderPath(opt.draco));
  ctx.ready = new Promise((resolve, reject) => {
    const fail = (e) => { console.error(e); document.documentElement.classList.add('stage-error'); reject(e); };
    const done = (g) => { try { onModel(g); resolve(ctx); } catch (e) { fail(e); } };
    const prog = (e) => { if (e.total) opt.onProgress?.(e.loaded / e.total); };
    if (/\.txt$/.test(opt.url)) {
      new THREE.FileLoader().setResponseType('text').load(opt.url, (txt) => {
        const bin = atob(txt.trim()); const buf = new Uint8Array(bin.length);
        for (let i = 0; i < bin.length; i++) buf[i] = bin.charCodeAt(i);
        loader.parse(buf.buffer, '', done, fail);
      }, prog, fail);
    } else loader.load(opt.url, done, prog, fail);
  });

  function onModel(gltf) {
    const model = gltf.scene;
    model.updateMatrixWorld(true);
    // measured on the vertices: a rotated part's own box can reach well below its real shape (the Chiron stood 13 cm up)
    const box = new THREE.Box3().setFromObject(model, true);
    const size = box.getSize(new THREE.Vector3()), c = box.getCenter(new THREE.Vector3());
    const L = Math.max(size.x, size.y, size.z);
    const s = 1 / L;
    const wrap = new THREE.Group();
    model.position.set(-c.x, opt.ground ? -box.min.y : -c.y, -c.z);
    wrap.add(model); wrap.scale.setScalar(s); holder.add(wrap);
    wrap.updateMatrixWorld(true);
    ctx.model = model; ctx.wrap = wrap; ctx.scale = s;
    ctx.size = size.clone().multiplyScalar(s);
    ctx.anchors.center.set(0, opt.ground ? ctx.size.y / 2 : 0, 0);
    model.traverse((m) => { if (m.isMesh) { m.frustumCulled = true; } });
    opt.onModel?.(ctx, gltf);
    if (opt.shadow !== false) addShadow();
    document.documentElement.classList.add('stage-ready');
    measure();
  }

  /* ---------- soft contact shadow ---------- */
  function addShadow() {
    const { x: w, z: l } = ctx.size;
    const c = document.createElement('canvas'); c.width = 256; c.height = 512; const g = c.getContext('2d');
    // soft shapes drawn through a shadow (canvas filters are missing on some browsers)
    const soft = (blur, draw) => { g.save(); g.shadowColor = 'rgba(0,0,0,.5)'; g.shadowBlur = blur; g.shadowOffsetX = 10000; g.translate(-10000, 0); g.fillStyle = '#000'; g.beginPath(); draw(); g.fill(); g.restore(); };
    soft(26, () => g.roundRect(56, 52, 144, 408, 70));
    for (const a of ctx.wheels || []) { const u = 128 + a.x / w * 175, v = 256 + a.z / l * 440; soft(12, () => g.ellipse(u, v, 20, 46, 0, 0, Math.PI * 2)); }
    const mat = new THREE.MeshBasicMaterial({ map: new THREE.CanvasTexture(c), transparent: true, depthWrite: false, toneMapped: false });
    const plane = new THREE.Mesh(new THREE.PlaneGeometry(w * 1.45, l * 1.14), mat);
    plane.rotation.x = -Math.PI / 2; plane.position.y = opt.ground ? 0.001 : -ctx.size.y / 2 - 0.02; plane.renderOrder = 1;
    holder.add(plane); ctx.shadow = plane;
  }

  /* ---------- stops ---------- */
  let stops = [];
  const isMobile = () => innerWidth < opt.mobile;
  function parse(el) {
    try {
      const p = JSON.parse(el.dataset.pose || '{}');
      if (isMobile() && el.dataset.poseM) Object.assign(p, JSON.parse(el.dataset.poseM));
      return p;
    } catch (e) { console.warn('bad pose', el, e); return {}; }
  }
  function measure() {
    const els = [...document.querySelectorAll('[data-pose]')];
    let prev = { ...BASE_POSE, ...(opt.basePose || {}) };
    stops = els.map((el) => {
      const r = el.getBoundingClientRect();
      const anchor = parseFloat(el.dataset.anchor || '0.5');
      const y = r.top + scrollY + r.height * anchor - innerHeight / 2;
      const p = { ...prev, ...parse(el) }; prev = p; // a stop inherits whatever it does not set
      return { el, y, p };
    }).sort((a, b) => a.y - b.y);
  }
  new ResizeObserver(() => { resize(); measure(); }).observe(document.body);
  addEventListener('load', measure);
  document.fonts?.ready.then(measure);

  /* ---------- target pose for the current scroll ---------- */
  const smooth = (t) => t * t * (3 - 2 * t);
  function targetPose() {
    const y = scrollY;
    if (!stops.length) return { ...BASE_POSE };
    if (y <= stops[0].y) return stops[0].p;
    const last = stops[stops.length - 1];
    if (y >= last.y) return last.p;
    let k = 0; while (k < stops.length - 1 && stops[k + 1].y <= y) k++;
    const a = stops[k], b = stops[k + 1];
    const t = (y - a.y) / Math.max(1, b.y - a.y);
    const h = opt.hold, e = smooth(Math.min(Math.max((t - h) / (1 - 2 * h), 0), 1));
    const out = { at: e < 0.5 ? a.p.at : b.p.at, _a: a.p.at, _b: b.p.at, _e: e };
    for (const k2 of POSE_KEYS) out[k2] = a.p[k2] + (b.p[k2] - a.p[k2]) * e;
    ctx.stopIndex = e < 0.5 ? k : k + 1; ctx.stopT = k + e;
    return out;
  }

  /* ---------- camera ---------- */
  const cur = { ...BASE_POSE }, curAt = new THREE.Vector3(), tmpA = new THREE.Vector3(), tmpB = new THREE.Vector3();
  let first = true;
  const pointer = { x: 0, y: 0, tx: 0, ty: 0 };
  addEventListener('pointermove', (e) => { if (e.pointerType === 'mouse') { pointer.tx = e.clientX / innerWidth * 2 - 1; pointer.ty = e.clientY / innerHeight * 2 - 1; } }, { passive: true });
  let lastY = scrollY, vel = 0;
  function anchorPoint(name, out) { const a = ctx.anchors[name] || ctx.anchors.center; return out.copy(a); }

  function resize() {
    const w = innerWidth, h = innerHeight;
    renderer.setSize(w, h, false); camera.aspect = w / h; fx?.composer.setSize(w, h);
  }
  resize();

  const clock = new THREE.Clock();
  let time = 0;
  function frame() {
    requestAnimationFrame(frame);
    const dt = Math.min(clock.getDelta(), 0.05); time += dt;
    const tp = targetPose();
    const k = (first || window.__stageSnap) ? 1 : 1 - Math.exp(-dt * (reduce ? 12 : opt.damp));
    for (const key2 of POSE_KEYS) cur[key2] += (tp[key2] - cur[key2]) * k;
    // the look-at point blends between the two stops' anchors
    anchorPoint(tp._a ?? tp.at, tmpA); anchorPoint(tp._b ?? tp.at, tmpB);
    tmpA.lerp(tmpB, tp._e ?? 0);
    curAt.lerp(tmpA, k); if (first || window.__stageSnap) curAt.copy(tmpA);
    first = !ctx.model;

    vel += ((scrollY - lastY) / Math.max(dt, 1e-3) - vel) * 0.1; lastY = scrollY;
    pointer.x += (pointer.tx - pointer.x) * 0.05; pointer.y += (pointer.ty - pointer.y) * 0.05;
    const drift = reduce ? 0 : cur.drift;
    const yaw = cur.yaw + Math.sin(time * 0.31) * 1.6 * drift + pointer.x * 5 * drift + THREE.MathUtils.clamp(vel * 0.004, -4, 4) * drift;
    const pitch = cur.pitch + Math.sin(time * 0.23) * 0.7 * drift - pointer.y * 2.5 * drift;
    const F = new THREE.Vector3(0, 0, opt.front);
    const dir = F.applyAxisAngle(new THREE.Vector3(0, 1, 0), yaw * DEG);
    const tgt = curAt.clone().add(new THREE.Vector3(cur.tx, cur.ty, cur.tz));
    const cp = Math.cos(pitch * DEG), sp = Math.sin(pitch * DEG);
    camera.position.set(tgt.x + dir.x * cp * cur.dist, tgt.y + sp * cur.dist, tgt.z + dir.z * cp * cur.dist);
    camera.up.set(0, 1, 0); camera.lookAt(tgt);
    if (cur.roll) camera.rotateZ(cur.roll * DEG);
    camera.fov = cur.fov;
    const W = innerWidth, H = innerHeight;
    camera.setViewOffset(W, H, -cur.sx * W, cur.sy * H, W, H);
    camera.updateProjectionMatrix();
    scene.environmentIntensity = opt.envIntensity * cur.env;
    key.intensity = opt.key.intensity * (0.15 + 0.85 * cur.env); rim.intensity = opt.rim.intensity * (0.3 + 0.7 * cur.env);
    if (ctx.shadow) ctx.shadow.material.opacity = cur.shadow;
    opt.onFrame?.(ctx, cur, dt, time);
    if (fx) fx.composer.render(dt); else renderer.render(scene, camera);
  }
  frame();
  ctx.measure = measure; ctx.fx = fx;
  ctx.loadModel = (url) => /\.glb$/.test(url) ? new Promise((res, rej) => loader.load(url, (g) => res(g.scene), undefined, rej)) : new Promise((res, rej) => new THREE.FileLoader().setResponseType('text').load(url, (txt) => {
    const bin = atob(txt.trim()); const buf = new Uint8Array(bin.length);
    for (let i = 0; i < bin.length; i++) buf[i] = bin.charCodeAt(i);
    loader.parse(buf.buffer, '', (g) => res(g.scene), rej);
  }, undefined, rej));
  return ctx;
}

// Scale a word so it fills its container's content width (optionally capped by a share of the viewport height).
function fitWord(el, maxVh) {
  const fit = () => { const p = el.parentElement, cs = getComputedStyle(p);
    el.style.fontSize = '100px';
    const avail = p.clientWidth - parseFloat(cs.paddingLeft) - parseFloat(cs.paddingRight);
    let fs = 100 * avail / el.scrollWidth;
    if (maxVh) fs = Math.min(fs, innerHeight * maxVh);
    el.style.fontSize = fs + 'px'; };
  fit(); document.fonts?.ready.then(fit); new ResizeObserver(fit).observe(el.parentElement); el._fit = fit;
}

// Reveal: elements with .rv rise and fade in when they enter the viewport (visible at rest if observers are unavailable).
function reveals() {
  const els = document.querySelectorAll('.rv');
  if (!('IntersectionObserver' in window) || matchMedia('(prefers-reduced-motion: reduce)').matches) { els.forEach(e => e.classList.add('in')); return; }
  document.documentElement.classList.add('rv-on');
  const io = new IntersectionObserver((es) => es.forEach(e => { if (e.isIntersecting) { e.target.classList.add('in'); io.unobserve(e.target); } }), { rootMargin: '0px 0px -8% 0px' });
  els.forEach(e => io.observe(e));
}
