import * as THREE from 'three';
import { OrbitControls } from 'three/examples/jsm/controls/OrbitControls.js';
import { STLLoader } from 'three/examples/jsm/loaders/STLLoader.js';
import { resolveJointAngles } from './joint-motion.mjs';
const stage = document.querySelector('#stage'), status = document.querySelector('#status');
const scene = new THREE.Scene(); scene.background = new THREE.Color('#e8eef2');
const renderer = new THREE.WebGLRenderer({ antialias: true, preserveDrawingBuffer: true });
renderer.setPixelRatio(Math.min(devicePixelRatio, 2)); renderer.outputColorSpace = THREE.SRGBColorSpace;
renderer.setSize(stage.clientWidth, stage.clientHeight); stage.appendChild(renderer.domElement);
const camera = new THREE.PerspectiveCamera(36, stage.clientWidth / stage.clientHeight, .001, 10);
camera.up.set(0, 0, 1);
const controls = new OrbitControls(camera, renderer.domElement); controls.enableDamping = true;
controls.minDistance = .1; controls.maxDistance = 2;
scene.add(new THREE.HemisphereLight(0xffffff, 0x83939a, 2.2));
for (const [color, power, position] of [[0xffffff, 3, [.5, -.7, 1]], [0xe9f9ff, 1.5, [-.5, .2, .4]]]) {
  const light = new THREE.DirectionalLight(color, power); light.position.fromArray(position); scene.add(light);
}
const grid = new THREE.GridHelper(.8, 40, 0xb5c5ce, 0xd0dbe1);
grid.rotation.x = Math.PI / 2; grid.position.z = -.001; scene.add(grid);
const robot = new THREE.Group(); scene.add(robot);
const links = new Map(), moving = [], visuals = [], arrows = [];
let loaded = false;
const palette = ['#9baebd', '#47a8ae', '#7f94d0', '#d8a468', '#8ab19a', '#b28bb7', '#60a4c2', '#df984e', '#e6b762'];
const nums = (s, fallback = '0 0 0') => (s || fallback).trim().split(/\s+/).map(Number);
function pose(node, el) {
  node.position.fromArray(nums(el?.getAttribute('xyz')));
  const rpy = nums(el?.getAttribute('rpy')); node.rotation.set(...rpy, 'ZYX');
}
async function text(url) { const r = await fetch(url, { cache: 'no-store' }); if (!r.ok) throw Error(`${r.status}: ${url}`); return r.text(); }
function home() {
  const box = new THREE.Box3().setFromObject(robot), center = box.getCenter(new THREE.Vector3());
  controls.target.copy(center);
  camera.position.copy(center).add(new THREE.Vector3(.9, 1.25, .8).normalize().multiplyScalar(box.getSize(new THREE.Vector3()).length() * 1.7));
  controls.update();
}
function updatePose() {
  const inputs = Object.fromEntries(moving.filter(j => !j.mimic).map(j => [j.name, THREE.MathUtils.degToRad(Number(j.input.value))]));
  const angles = resolveJointAngles(moving, inputs);
  for (const j of moving) {
    j.value = THREE.MathUtils.radToDeg(angles.get(j.name));
    j.rotation.quaternion.setFromAxisAngle(j.axis, angles.get(j.name));
    if (j.output) j.output.value = `${Math.round(j.value)}°`;
  }
  document.querySelector('.caption b').textContent = moving.some(j => Math.abs(j.value) > 1e-8)
    ? '运动学预览 / 自定义姿态' : '装配姿态 / 关节零位';
}
try {
  const url = new URL('../touch_r1_description/urdf/touch-r1.urdf', location.href);
  const metadata = JSON.parse(await text(new URL('../kinematics.json', location.href)));
  const xml = new DOMParser().parseFromString(await text(url), 'application/xml');
  if (xml.querySelector('parsererror')) throw Error('URDF XML 解析失败');
  for (const el of xml.querySelectorAll('robot > link')) {
    const group = new THREE.Group(); group.name = el.getAttribute('name'); links.set(group.name, group);
  }
  const children = new Set();
  for (const el of xml.querySelectorAll('robot > joint')) {
    const parent = links.get(el.querySelector('parent').getAttribute('link'));
    const child = links.get(el.querySelector('child').getAttribute('link'));
    if (!parent || !child) throw Error('URDF 连接关系不完整'); children.add(child.name);
    const origin = new THREE.Group(); pose(origin, el.querySelector('origin')); parent.add(origin);
    const rotation = new THREE.Group(); origin.add(rotation); rotation.add(child);
    if (el.getAttribute('type') === 'fixed') continue;
    const axis = new THREE.Vector3(...nums(el.querySelector('axis')?.getAttribute('xyz'), '1 0 0')).normalize();
    const name = el.getAttribute('name'), mimicEl = el.querySelector('mimic');
    const mimic = mimicEl ? { joint: mimicEl.getAttribute('joint'), multiplier: Number(mimicEl.getAttribute('multiplier') ?? 1), offset: Number(mimicEl.getAttribute('offset') ?? 0) } : null;
    const arrow = new THREE.ArrowHelper(axis, new THREE.Vector3(), .035, mimic ? 0xc2933c : 0x008b91, .008, .004);
    origin.add(arrow); arrows.push(arrow);
    const entry = { name, rotation, axis, mimic, value: 0 }; moving.push(entry);
    if (mimic) continue;
    const number = moving.filter(j => !j.mimic).length;
    const row = document.createElement('div'); row.className = 'joint';
    const label = document.createElement('label'), output = document.createElement('output'), input = document.createElement('input');
    label.htmlFor = `angle-${name}`; label.textContent = number === 7 ? 'J7 · Finger 开合' : `J${number} · ${name}`;
    output.value = '0°'; label.appendChild(output);
    input.id = label.htmlFor; input.setAttribute('aria-label', `J${number} 关节角度`); input.type = 'range';
    const range = metadata.joints.find(j => j.name === name)?.preview_range_deg ?? [-90, 90];
    input.min = range[0]; input.max = range[1]; input.step = 1; input.value = 0;
    row.append(label, input); document.querySelector('#joints').appendChild(row);
    entry.input = input; entry.output = output; input.addEventListener('input', updatePose);
  }
  for (const [name, link] of links) if (!children.has(name)) robot.add(link);
  const loader = new STLLoader(); const tasks = [];
  const total = xml.querySelectorAll('robot > link > visual > geometry > mesh').length;
  let count = 0;
  for (const [index, el] of Array.from(xml.querySelectorAll('robot > link')).entries()) {
    const group = links.get(el.getAttribute('name'));
    for (const visual of el.querySelectorAll(':scope > visual')) {
      const meshEl = visual.querySelector('geometry > mesh'); if (!meshEl) continue;
      const meshUrl = new URL(meshEl.getAttribute('filename'), url);
      // 用生成记录的哈希区分网格版本，刷新预览不会混用旧模型缓存。
      const metric = metadata.meshes.find(m => new URL('../touch_r1_description/' + m.file, location.href).pathname === meshUrl.pathname);
      if (metric) meshUrl.searchParams.set('v', metric.sha256.slice(0, 12));
      tasks.push(loader.loadAsync(meshUrl.href).then(geometry => {
        geometry.computeVertexNormals();
        const rgba = nums(visual.querySelector('material > color')?.getAttribute('rgba'), '0.7 0.7 0.7 1');
        const color = new THREE.Color(...rgba.slice(0, 3));
        const mesh = new THREE.Mesh(geometry, new THREE.MeshStandardMaterial({ color, roughness: .58, metalness: .12 }));
        pose(mesh, visual.querySelector('origin')); mesh.scale.fromArray(nums(meshEl.getAttribute('scale'), '1 1 1')); group.add(mesh);
        visuals.push({ mesh, color: color.clone(), linkColor: new THREE.Color(palette[index % palette.length]) });
        status.textContent = `已载入 ${++count} / ${total} 个网格`;
      }));
    }
  }
  await Promise.all(tasks); updatePose(); loaded = true; home();
  status.textContent = `已就绪 · ${links.size} 个连杆 · ${moving.filter(j => !j.mimic).length} 个控制轴 · 双 finger 联动`;
  document.body.dataset.ready = 'true';
} catch (error) {
  status.textContent = '加载失败：' + error.message; status.classList.add('error'); console.error(error); document.body.dataset.ready = 'error';
}
document.querySelector('#reset').onclick = () => { for (const j of moving) if (j.input) j.input.value = 0; updatePose(); };
document.querySelector('#fit').onclick = () => { if (loaded) home(); };
document.querySelector('#axes').onchange = e => arrows.forEach(a => a.visible = e.target.checked);
document.querySelector('#colors').onchange = e => visuals.forEach(v => v.mesh.material.color.copy(e.target.checked ? v.linkColor : v.color));
new ResizeObserver(() => { renderer.setSize(stage.clientWidth, stage.clientHeight); camera.aspect = stage.clientWidth / stage.clientHeight; camera.updateProjectionMatrix(); }).observe(stage);
renderer.setAnimationLoop(() => { controls.update(); renderer.render(scene, camera); });
window.previewState = () => ({ ready: loaded, joints: moving.map(j => ({ name: j.name, value: j.value, mimic: j.mimic })), links: links.size, meshes: visuals.length });
