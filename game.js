
import * as THREE from
'https://cdn.jsdelivr.net/npm/three@0.160.0/build/three.module.js';

// SCENE
const scene = new THREE.Scene();
scene.background = new THREE.Color(0x87ceeb);
scene.fog = new THREE.Fog(0x87ceeb, 20, 75);

// CAMERA
const camera = new THREE.PerspectiveCamera(
    65,
    window.innerWidth / window.innerHeight,
    0.1,
    1000
);
camera.position.set(0, 6, 10);
camera.lookAt(0, 1, -8);

// RENDERER
const renderer = new THREE.WebGLRenderer({ antialias: true });
renderer.setSize(window.innerWidth, window.innerHeight);
renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
renderer.shadowMap.enabled = true;
document.body.appendChild(renderer.domElement);

// LIGHTS
scene.add(new THREE.HemisphereLight(0xffffff, 0x45602a, 2));

const sunlight = new THREE.DirectionalLight(0xffffff, 2);
sunlight.position.set(-5, 12, 8);
sunlight.castShadow = true;
scene.add(sunlight);

// GROUND
const ground = new THREE.Mesh(
    new THREE.PlaneGeometry(200, 200),
    new THREE.MeshStandardMaterial({ color: 0x276b25 })
);
ground.rotation.x = -Math.PI / 2;
ground.position.z = -40;
ground.receiveShadow = true;
scene.add(ground);

// ROAD
const road = new THREE.Mesh(
    new THREE.PlaneGeometry(8, 200),
    new THREE.MeshStandardMaterial({ color: 0x8b6842 })
);
road.rotation.x = -Math.PI / 2;
road.position.y = 0.02;
road.position.z = -40;
scene.add(road);

// LANE MARKINGS
for (let x of [-1.35, 1.35]) {
    const line = new THREE.Mesh(
        new THREE.BoxGeometry(0.06, 0.03, 200),
        new THREE.MeshStandardMaterial({ color: 0xffffff })
    );
    line.position.set(x, 0.05, -40);
    scene.add(line);
}

// TREES
function createTree(x, z) {
    const tree = new THREE.Group();

    const trunk = new THREE.Mesh(
        new THREE.CylinderGeometry(0.25, 0.35, 2.5),
        new THREE.MeshStandardMaterial({ color: 0x704020 })
    );
    trunk.position.y = 1.25;
    tree.add(trunk);

    const leaves = new THREE.Mesh(
        new THREE.SphereGeometry(1.5, 12, 12),
        new THREE.MeshStandardMaterial({ color: 0x146b27 })
    );
    leaves.position.y = 3;
    tree.add(leaves);

    tree.position.set(x, 0, z);
    scene.add(tree);
}

for (let z = -100; z < 15; z += 8) {
    createTree(-7, z);
    createTree(7, z);
}

// PLAYER
const player = new THREE.Group();

const body = new THREE.Mesh(
    new THREE.CylinderGeometry(0.38, 0.42, 1.1, 16),
    new THREE.MeshStandardMaterial({ color: 0x1565c0 })
);
body.position.y = 1.1;
body.castShadow = true;
player.add(body);

const head = new THREE.Mesh(
    new THREE.SphereGeometry(0.35, 20, 20),
    new THREE.MeshStandardMaterial({ color: 0xffcc99 })
);
head.position.y = 1.9;
player.add(head);

const legs = [];
for (let x of [-0.18, 0.18]) {
    const leg = new THREE.Mesh(
        new THREE.BoxGeometry(0.18, 0.7, 0.2),
        new THREE.MeshStandardMaterial({ color: 0x222244 })
    );
    leg.position.set(x, 0.35, 0);
    player.add(leg);
    legs.push(leg);
}

player.position.set(0, 0, 4);
scene.add(player);

// GAME VARIABLES
let lane = 1;
const lanes = [-2.5, 0, 2.5];

let jumpVelocity = 0;
let score = 0;
let bunCount = 0;
let speed = 0.25;
let gameOver = false;

const obstacles = [];
const buns = [];

const scoreText = document.getElementById("score");
const bunText = document.getElementById("buns");
const gameOverScreen = document.getElementById("game-over");

// BUILDING OBSTACLE
function createBuilding() {
    const building = new THREE.Group();

    const base = new THREE.Mesh(
        new THREE.BoxGeometry(1.7, 3.8, 1.7),
        new THREE.MeshStandardMaterial({ color: 0x888477 })
    );
    base.position.y = 1.9;
    building.add(base);

    // Windows
    for (let y of [1.3, 2.5]) {
        for (let x of [-0.4, 0.4]) {
            const windowMesh = new THREE.Mesh(
                new THREE.BoxGeometry(0.3, 0.45, 0.05),
                new THREE.MeshStandardMaterial({ color: 0x263b4b })
            );
            windowMesh.position.set(x, y, 0.87);
            building.add(windowMesh);
        }
    }

    building.position.set(
        lanes[Math.floor(Math.random() * 3)],
        0,
        -55
    );

    scene.add(building);
    obstacles.push(building);
}

// BUN COLLECTIBLE
function createBun() {
    const bun = new THREE.Group();

    const bread = new THREE.Mesh(
        new THREE.SphereGeometry(0.4, 16, 12),
        new THREE.MeshStandardMaterial({
            color: 0xf5a623,
            roughness: 0.8
        })
    );
    bread.scale.set(1, 0.65, 0.85);
    bun.add(bread);

    bun.position.set(
        lanes[Math.floor(Math.random() * 3)],
        1,
        -55
    );

    scene.add(bun);
    buns.push(bun);
}

// CONTROLS
function moveLeft() {
    if (!gameOver) lane = Math.max(0, lane - 1);
}

function moveRight() {
    if (!gameOver) lane = Math.min(2, lane + 1);
}

function jump() {
    if (!gameOver && player.position.y === 0) {
        jumpVelocity = 0.23;
    }
}

document.addEventListener("keydown", (event) => {
    if (event.key === "ArrowLeft" || event.key === "a") moveLeft();
    if (event.key === "ArrowRight" || event.key === "d") moveRight();
    if (event.code === "Space" || event.key === "ArrowUp") jump();
});

// SPAWN TIMERS
let obstacleTimer = 0;
let bunTimer = 0;

// GAME OVER
function endGame() {
    gameOver = true;
    document.getElementById("final-score").textContent = score;
    gameOverScreen.style.display = "block";
}

// ANIMATION
const clock = new THREE.Clock();

function animate() {
    requestAnimationFrame(animate);

    if (gameOver) {
        renderer.render(scene, camera);
        return;
    }

    const delta = Math.min(clock.getDelta(), 0.05);

    // PLAYER MOVEMENT
    player.position.x +=
        (lanes[lane] - player.position.x) * 0.15;

    // JUMP
    player.position.y += jumpVelocity;
    jumpVelocity -= 0.012;

    if (player.position.y < 0) {
        player.position.y = 0;
        jumpVelocity = 0;
    }

    // RUNNING ANIMATION
    const time = performance.now() * 0.012;
    legs.forEach((leg, i) => {
        leg.rotation.x = Math.sin(time + i * Math.PI) * 0.5;
    });

    // INCREASE SPEED
    speed = Math.min(0.25 + score * 0.001, 0.55);

    // SPAWN BUILDINGS
    obstacleTimer += delta;
    if (obstacleTimer > 2.5) {
        createBuilding();
        obstacleTimer = 0;
    }

    // SPAWN BUNS
    bunTimer += delta;
    if (bunTimer > 1.1) {
        createBun();
        bunTimer = 0;
    }

    // MOVE BUILDINGS
    for (let i = obstacles.length - 1; i >= 0; i--) {
        const obstacle = obstacles[i];
        obstacle.position.z += speed * delta * 60;

        const hit =
            Math.abs(obstacle.position.z - player.position.z) < 1 &&
            Math.abs(obstacle.position.x - player.position.x) < 1.3;

        if (hit) {
            endGame();
        }

        if (obstacle.position.z > 12) {
            scene.remove(obstacle);
            obstacles.splice(i, 1);
            score += 5;
        }
    }

    // MOVE AND COLLECT BUNS
    for (let i = buns.length - 1; i >= 0; i--) {
        const bun = buns[i];

        bun.position.z += speed * delta * 60;
        bun.rotation.y += 0.05;

        const collected =
            Math.abs(bun.position.z - player.position.z) < 1 &&
            Math.abs(bun.position.x - player.position.x) < 1.1;

        if (collected) {
            bunCount++;
            score += 10;
            scene.remove(bun);
            buns.splice(i, 1);
        } else if (bun.position.z > 12) {
            scene.remove(bun);
            buns.splice(i, 1);
        }
    }

    score += delta * 2;
    scoreText.textContent = Math.floor(score);
    bunText.textContent = bunCount;

    renderer.render(scene, camera);
}

// RESTART
document.getElementById("restart").addEventListener("click", () => {
    location.reload();
});

// RESIZE
window.addEventListener("resize", () => {
    camera.aspect = window.innerWidth / window.innerHeight;
    camera.updateProjectionMatrix();
    renderer.setSize(window.innerWidth, window.innerHeight);
});

animate();
import { GLTFLoader } from
'https://cdn.jsdelivr.net/npm/three@0.160.0/examples/jsm/loaders/GLTFLoader.js';
