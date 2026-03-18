import * as THREE from "https://unpkg.com/three@0.160.0/build/three.module.js";

const container = document.getElementById("three-container");

/* =====================================
Scene
===================================== */

const scene = new THREE.Scene();

scene.background = new THREE.Color(0x020617);

/* =====================================
Camera
===================================== */

const camera = new THREE.PerspectiveCamera(
  60,
  window.innerWidth / window.innerHeight,
  0.1,
  1000,
);

camera.position.set(0, 2, 8);

/* =====================================
Renderer
===================================== */

const renderer = new THREE.WebGLRenderer({
  antialias: true,
});

renderer.setSize(window.innerWidth, window.innerHeight);

container.appendChild(renderer.domElement);

/* =====================================
Light
===================================== */

const light = new THREE.PointLight(0x88aaff, 2, 200);

light.position.set(10, 10, 10);

scene.add(light);

/* =====================================
Star Particles
===================================== */

const starGeo = new THREE.BufferGeometry();

const starCount = 2000;

const positions = [];

for (let i = 0; i < starCount; i++) {
  positions.push(
    (Math.random() - 0.5) * 200,
    (Math.random() - 0.5) * 200,
    (Math.random() - 0.5) * 200,
  );
}

starGeo.setAttribute(
  "position",
  new THREE.Float32BufferAttribute(positions, 3),
);

const starMat = new THREE.PointsMaterial({
  size: 0.25,
  color: 0x9bbcff,
});

const stars = new THREE.Points(starGeo, starMat);

scene.add(stars);

/* =====================================
Orbit Camera
===================================== */

let angle = 0;

const radius = 8;

function updateCamera() {
  angle += 0.002;

  camera.position.x = Math.cos(angle) * radius;
  camera.position.z = Math.sin(angle) * radius;

  camera.lookAt(0, 0, 0);
}

/* =====================================
Animation
===================================== */

function animate() {
  requestAnimationFrame(animate);

  updateCamera();

  renderer.render(scene, camera);
}

animate();

/* =====================================
Resize
===================================== */

window.addEventListener("resize", () => {
  camera.aspect = window.innerWidth / window.innerHeight;

  camera.updateProjectionMatrix();

  renderer.setSize(window.innerWidth, window.innerHeight);
});
