import * as THREE from 'three';
import { OrbitControls } from 'three/examples/jsm/controls/OrbitControls.js';
import { STLLoader } from 'three/examples/jsm/loaders/STLLoader.js';
const stage=document.querySelector('#stage'),status=document.querySelector('#status');
const scene=new THREE.Scene();scene.background=new THREE.Color('#e8eef2');
const renderer=new THREE.WebGLRenderer({antialias:true,preserveDrawingBuffer:true});renderer.setPixelRatio(Math.min(devicePixelRatio,2));renderer.outputColorSpace=THREE.SRGBColorSpace;renderer.setSize(stage.clientWidth,stage.clientHeight);stage.appendChild(renderer.domElement);
const camera=new THREE.PerspectiveCamera(36,stage.clientWidth/stage.clientHeight,.001,10);camera.up.set(0,0,1);
const controls=new OrbitControls(camera,renderer.domElement);controls.enableDamping=true;controls.minDistance=.1;controls.maxDistance=2;
scene.add(new THREE.HemisphereLight(0xffffff,0x83939a,2.2));const sun=new THREE.DirectionalLight(0xffffff,3);sun.position.set(.5,-.7,1);scene.add(sun);const fill=new THREE.DirectionalLight(0xe9f9ff,1.5);fill.position.set(-.5,.2,.4);scene.add(fill);
const grid=new THREE.GridHelper(.8,40,0xb5c5ce,0xd0dbe1);grid.rotation.x=Math.PI/2;grid.position.z=-.001;scene.add(grid);
const robot=new THREE.Group();scene.add(robot);const links=new Map(),moving=[],visuals=[],arrows=[];let loaded=false;
const palette=['#9baebd','#47a8ae','#7f94d0','#d8a468','#8ab19a','#b28bb7','#60a4c2'];
const nums=(s,fallback='0 0 0')=>(s||fallback).trim().split(/\s+/).map(Number);
function pose(node,el){const xyz=nums(el?.getAttribute('xyz'));const rpy=nums(el?.getAttribute('rpy'));node.position.fromArray(xyz);node.rotation.set(rpy[0],rpy[1],rpy[2],'ZYX');}
async function text(url){const r=await fetch(url);if(!r.ok)throw Error(`${r.status}: ${url}`);return r.text();}
function home(){const box=new THREE.Box3().setFromObject(robot),center=box.getCenter(new THREE.Vector3()),size=box.getSize(new THREE.Vector3()).length();controls.target.copy(center);camera.position.copy(center).add(new THREE.Vector3(.9,-1.25,.8).normalize().multiplyScalar(size*1.7));controls.update();}
try{
 const url=new URL('../touch_r1_description/urdf/touch-r1.urdf',location.href);
 const xml=new DOMParser().parseFromString(await text(url),'application/xml');if(xml.querySelector('parsererror'))throw Error('URDF XML 解析失败');
 for(const el of xml.querySelectorAll('robot > link')){const group=new THREE.Group();group.name=el.getAttribute('name');links.set(group.name,group);}
 const children=new Set();
 for(const el of xml.querySelectorAll('robot > joint')){
  const parent=links.get(el.querySelector('parent').getAttribute('link')),child=links.get(el.querySelector('child').getAttribute('link'));if(!parent||!child)throw Error('URDF 连接关系不完整');children.add(child.name);
  const origin=new THREE.Group();pose(origin,el.querySelector('origin'));parent.add(origin);const rotation=new THREE.Group();origin.add(rotation);rotation.add(child);
  if(el.getAttribute('type')!=='fixed'){
   const axis=new THREE.Vector3(...nums(el.querySelector('axis')?.getAttribute('xyz'),'1 0 0')).normalize();const name=el.getAttribute('name');const arrow=new THREE.ArrowHelper(axis,new THREE.Vector3(),.035,0x008b91,.008,.004);origin.add(arrow);arrows.push(arrow);
   const entry={name,rotation,axis,value:0};moving.push(entry);const row=document.createElement('div');row.className='joint';const id=`angle-${name}`;row.innerHTML=`<label for="${id}">J${moving.length} · ${name}<output>0°</output></label><input id="${id}" aria-label="J${moving.length} 关节角度" type="range" min="-90" max="90" value="0" step="1">`;document.querySelector('#joints').appendChild(row);entry.input=row.querySelector('input');entry.output=row.querySelector('output');entry.input.addEventListener('input',()=>{entry.value=Number(entry.input.value);entry.rotation.quaternion.setFromAxisAngle(entry.axis,THREE.MathUtils.degToRad(entry.value));entry.output.value=entry.value+'°';document.querySelector('.caption b').textContent=moving.some(x=>x.value)?'运动学预览 / 自定义姿态':'装配姿态 / 关节零位';});
  }
 }
 for(const [name,link] of links)if(!children.has(name))robot.add(link);
 const loader=new STLLoader();let count=0;const tasks=[];
 for(const [index,el] of Array.from(xml.querySelectorAll('robot > link')).entries()){
  const group=links.get(el.getAttribute('name'));
  for(const visual of el.querySelectorAll(':scope > visual')){
   const meshEl=visual.querySelector('geometry > mesh');if(!meshEl)continue;
   const filename=meshEl.getAttribute('filename');const meshUrl=filename.startsWith('package://touch_r1_description/')?new URL('../touch_r1_description/'+filename.slice('package://touch_r1_description/'.length),location.href):new URL(filename,url);
   tasks.push(loader.loadAsync(meshUrl.href).then(geometry=>{geometry.computeVertexNormals();const rgba=nums(visual.querySelector('material > color')?.getAttribute('rgba'),'0.7 0.7 0.7 1');const color=new THREE.Color(...rgba.slice(0,3));const material=new THREE.MeshStandardMaterial({color,roughness:.58,metalness:.12});const mesh=new THREE.Mesh(geometry,material);pose(mesh,visual.querySelector('origin'));mesh.scale.fromArray(nums(meshEl.getAttribute('scale'),'1 1 1'));group.add(mesh);visuals.push({mesh,color:color.clone(),linkColor:new THREE.Color(palette[index%palette.length])});status.textContent=`已载入 ${++count} / 21 个网格`;}));
  }
 }
 await Promise.all(tasks);loaded=true;home();status.textContent='已就绪 · 7 个连杆 · 6 个活动关节';document.body.dataset.ready='true';
}catch(error){status.textContent='加载失败：'+error.message;status.classList.add('error');console.error(error);document.body.dataset.ready='error';}
document.querySelector('#reset').onclick=()=>{for(const x of moving){x.input.value=0;x.input.dispatchEvent(new Event('input'));}};
document.querySelector('#fit').onclick=()=>{if(loaded)home();};
document.querySelector('#axes').onchange=e=>arrows.forEach(a=>a.visible=e.target.checked);
document.querySelector('#colors').onchange=e=>visuals.forEach(v=>v.mesh.material.color.copy(e.target.checked?v.linkColor:v.color));
new ResizeObserver(()=>{renderer.setSize(stage.clientWidth,stage.clientHeight);camera.aspect=stage.clientWidth/stage.clientHeight;camera.updateProjectionMatrix();}).observe(stage);
renderer.setAnimationLoop(()=>{controls.update();renderer.render(scene,camera);});
// 开放只读状态供自动化核对滑块与真实 URDF 变换；界面交互仍通过标准控件。
window.previewState=()=>({ready:loaded,joints:moving.map(x=>({name:x.name,value:x.value,quaternion:x.rotation.quaternion.toArray()})),links:links.size,meshes:visuals.length});
