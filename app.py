import streamlit as st
import streamlit.components.v1 as components

st.set_page_config(
    page_title="Hứng Táo Pro - Nam Châm & Bom Nổ",
    page_icon="🍎",
    layout="centered",
)

st.title("🍎 Game Hứng Táo: Bom Nổ & Nam Châm 🧲")
st.caption(
    "💡 **Vật phẩm đặc biệt:**<br>• 🧲 **Nam Châm:** Hút tất cả táo đỏ về giỏ"
    " trong 5 giây!<br>• 💣 **Quả Bom:** Tránh xa kẻo nổ mất mạng!",
    unsafe_allow_html=True,
)

game_html = """
<!DOCTYPE html>
<html>
<head>
    <style>
        body {
            margin: 0;
            padding: 0;
            background-color: #222;
            display: flex;
            justify-content: center;
            align-items: center;
            flex-direction: column;
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            user-select: none;
            touch-action: none;
        }
        .game-container {
            position: relative;
            box-shadow: 0 10px 25px rgba(0,0,0,0.5);
            border-radius: 12px;
            overflow: hidden;
            border: 3px solid #444;
        }
        canvas {
            display: block;
            background: linear-gradient(to bottom, #a1c4fd, #c2e9fb);
            cursor: pointer;
        }
        .controls-panel {
            margin-top: 12px;
            display: flex;
            gap: 10px;
        }
        .diff-btn {
            background-color: #555;
            color: white;
            border: none;
            padding: 8px 16px;
            font-size: 14px;
            font-weight: bold;
            border-radius: 6px;
            cursor: pointer;
        }
        .diff-btn.active {
            background-color: #ff8800;
        }
    </style>
</head>
<body>

    <div class="game-container">
        <canvas id="canvas" width="360" height="520"></canvas>
    </div>
    
    <div class="controls-panel">
        <button class="diff-btn active" id="diff-0" onclick="setDifficulty(0)">Dễ</button>
        <button class="diff-btn" id="diff-1" onclick="setDifficulty(1)">Thường</button>
        <button class="diff-btn" id="diff-2" onclick="setDifficulty(2)">Khó</button>
    </div>

    <script>
        const cvs = document.getElementById("canvas");
        const ctx = cvs.getContext("2d");

        let gameState = "MENU"; // MENU, PLAYING, GAMEOVER

        const difficulties = [
            { name: "Dễ", initialSpeed: 2.5, spawnRate: 35, maxLives: 4 },
            { name: "Thường", initialSpeed: 3.3, spawnRate: 25, maxLives: 3 },
            { name: "Khó", initialSpeed: 4.2, spawnRate: 18, maxLives: 2 }
        ];
        let currentDiff = 1;

        let basket = {
            width: 75,
            height: 24,
            x: 142.5,
            y: 465,
            speed: 7.5
        };

        let items = [];
        let particles = [];
        let score = 0;
        let highScore = 0;
        let lives = 3;
        let frameCount = 0;

        // Trạng thái Nam Châm
        let magnetTimer = 0;

        let leftPressed = false;
        let rightPressed = false;

        const audioCtx = new (window.AudioContext || window.webkitAudioContext)();
        function playSound(type) {
            if (audioCtx.state === 'suspended') audioCtx.resume();
            const osc = audioCtx.createOscillator();
            const gain = audioCtx.createGain();
            osc.connect(gain);
            gain.connect(audioCtx.destination);

            if (type === 'catch') {
                osc.type = 'sine';
                osc.frequency.setValueAtTime(523, audioCtx.currentTime);
                osc.frequency.setValueAtTime(659, audioCtx.currentTime + 0.08);
                gain.gain.setValueAtTime(0.15, audioCtx.currentTime);
                gain.gain.linearRampToValueAtTime(0.01, audioCtx.currentTime + 0.15);
                osc.start(); osc.stop(audioCtx.currentTime + 0.15);
            } else if (type === 'magnet') {
                osc.type = 'triangle';
                osc.frequency.setValueAtTime(300, audioCtx.currentTime);
                osc.frequency.linearRampToValueAtTime(800, audioCtx.currentTime + 0.25);
                gain.gain.setValueAtTime(0.2, audioCtx.currentTime);
                gain.gain.linearRampToValueAtTime(0.01, audioCtx.currentTime + 0.25);
                osc.start(); osc.stop(audioCtx.currentTime + 0.25);
            } else if (type === 'explosion') {
                // Âm thanh Bom nổ trầm êm
                osc.type = 'sawtooth';
                osc.frequency.setValueAtTime(180, audioCtx.currentTime);
                osc.frequency.exponentialRampToValueAtTime(40, audioCtx.currentTime + 0.3);
                gain.gain.setValueAtTime(0.3, audioCtx.currentTime);
                gain.gain.linearRampToValueAtTime(0.01, audioCtx.currentTime + 0.3);
                osc.start(); osc.stop(audioCtx.currentTime + 0.3);
            }
        }

        function setDifficulty(idx) {
            currentDiff = idx;
            for (let i = 0; i < 3; i++) {
                document.getElementById(`diff-${i}`).classList.remove("active");
            }
            document.getElementById(`diff-${idx}`).classList.add("active");
            if (gameState === "MENU") draw();
        }

        document.addEventListener("keydown", (e) => {
            if (e.code === "ArrowLeft" || e.code === "KeyA") leftPressed = true;
            if (e.code === "ArrowRight" || e.code === "KeyD") rightPressed = true;
            if (e.code === "Space") {
                e.preventDefault();
                if (gameState !== "PLAYING") startGame();
            }
        });
        document.addEventListener("keyup", (e) => {
            if (e.code === "ArrowLeft" || e.code === "KeyA") leftPressed = false;
            if (e.code === "ArrowRight" || e.code === "KeyD") rightPressed = false;
        });

        function handlePointerMove(e) {
            let rect = cvs.getBoundingClientRect();
            let clientX = e.clientX || (e.touches && e.touches[0].clientX);
            if (clientX) {
                let touchX = clientX - rect.left;
                basket.x = touchX - basket.width / 2;
                if (basket.x < 0) basket.x = 0;
                if (basket.x + basket.width > cvs.width) basket.x = cvs.width - basket.width;
            }
        }

        cvs.addEventListener("mousemove", handlePointerMove);
        cvs.addEventListener("touchmove", (e) => {
            e.preventDefault();
            handlePointerMove(e);
        }, { passive: false });

        cvs.addEventListener("click", () => { if (gameState !== "PLAYING") startGame(); });
        cvs.addEventListener("touchstart", (e) => {
            if (gameState !== "PLAYING") { e.preventDefault(); startGame(); }
        }, { passive: false });

        function startGame() {
            gameState = "PLAYING";
            score = 0;
            lives = difficulties[currentDiff].maxLives;
            items = [];
            particles = [];
            frameCount = 0;
            magnetTimer = 0;
            basket.x = (cvs.width - basket.width) / 2;
        }

        function createExplosion(x, y) {
            // Tạo 15 mảnh văng nhỏ khi bom nổ
            for (let i = 0; i < 15; i++) {
                particles.push({
                    x: x,
                    y: y,
                    vx: (Math.random() - 0.5) * 8,
                    vy: (Math.random() - 0.5) * 8,
                    color: Math.random() < 0.5 ? "#ff4d4d" : "#ff9900",
                    size: Math.random() * 5 + 3,
                    life: 20
                });
            }
        }

        function spawnItem() {
            let diffConfig = difficulties[currentDiff];
            let currentSpeed = diffConfig.initialSpeed + (score * 0.02);
            let rand = Math.random();

            let type = "APPLE"; // Mặc định là Táo đỏ
            if (rand < 0.20) type = "BOMB";      // 20% ra Bom
            else if (rand < 0.26) type = "MAGNET"; // 6% ra Nam Châm

            items.push({
                x: Math.random() * (cvs.width - 24) + 12,
                y: -15,
                radius: 12,
                speed: currentSpeed,
                type: type
            });
        }

        function drawBasket() {
            ctx.fillStyle = magnetTimer > 0 ? "#4a90e2" : "#8B4513";
            ctx.beginPath();
            ctx.roundRect(basket.x, basket.y, basket.width, basket.height, 6);
            ctx.fill();
            ctx.lineWidth = 2;
            ctx.strokeStyle = magnetTimer > 0 ? "#1f4ba8" : "#5c2c09";
            ctx.stroke();

            // Vẽ ký hiệu Nam châm trên giỏ nếu đang bật hiệu ứng
            if (magnetTimer > 0) {
                ctx.fillStyle = "#FFF";
                ctx.font = "bold 13px sans-serif";
                ctx.textAlign = "center";
                ctx.fillText("🧲 MAGNET", basket.x + basket.width / 2, basket.y + 17);
            } else {
                ctx.fillStyle = "#A0522D";
                ctx.fillRect(basket.x + 5, basket.y + 5, basket.width - 10, 4);
                ctx.fillRect(basket.x + 5, basket.y + 14, basket.width - 10, 4);
            }
        }

        function drawItems() {
            for (let i = 0; i < items.length; i++) {
                let item = items[i];

                // Hiệu ứng Nam Châm hút Táo đỏ về giỏ
                if (magnetTimer > 0 && item.type === "APPLE") {
                    let basketCenterX = basket.x + basket.width / 2;
                    let dx = basketCenterX - item.x;
                    item.x += dx * 0.08; // Kéo dần táo theo trục X
                }

                ctx.beginPath();

                if (item.type === "BOMB") {
                    // Vẽ Quả Bom
                    ctx.arc(item.x, item.y, item.radius, 0, Math.PI * 2);
                    ctx.fillStyle = "#333";
                    ctx.fill();
                    ctx.lineWidth = 1.5;
                    ctx.strokeStyle = "#000";
                    ctx.stroke();

                    // Kíp nổ
                    ctx.strokeStyle = "#ff9900";
                    ctx.beginPath();
                    ctx.moveTo(item.x, item.y - item.radius);
                    ctx.lineTo(item.x + 4, item.y - item.radius - 5);
                    ctx.stroke();

                } else if (item.type === "MAGNET") {
                    // Vẽ Vật phẩm Nam Châm
                    ctx.fillStyle = "#ff3333";
                    ctx.font = "18px sans-serif";
                    ctx.textAlign = "center";
                    ctx.fillText("🧲", item.x, item.y + 6);

                } else {
                    // Vẽ Táo Đỏ
                    ctx.arc(item.x, item.y, item.radius, 0, Math.PI * 2);
                    ctx.fillStyle = "#ff3333";
                    ctx.fill();
                    ctx.lineWidth = 1.5;
                    ctx.strokeStyle = "#b30000";
                    ctx.stroke();

                    // Lá xanh
                    ctx.fillStyle = "#2e8b57";
                    ctx.beginPath();
                    ctx.ellipse(item.x + 3, item.y - 12, 4, 2, Math.PI / 4, 0, Math.PI * 2);
                    ctx.fill();
                }

                if (gameState === "PLAYING") {
                    item.y += item.speed;
                }

                // Xử lý Hứng vật phẩm
                if (
                    item.y + item.radius >= basket.y &&
                    item.y - item.radius <= basket.y + basket.height &&
                    item.x >= basket.x - 5 &&
                    item.x <= basket.x + basket.width + 5
                ) {
                    if (item.type === "BOMB") {
                        playSound('explosion');
                        createExplosion(item.x, item.y);
                        lives--;
                        if (lives <= 0) gameState = "GAMEOVER";

                    } else if (item.type === "MAGNET") {
                        playSound('magnet');
                        magnetTimer = 300; // Khởi tạo 5 giây nam châm (60fps * 5)

                    } else { // Táo đỏ
                        playSound('catch');
                        score += 10;
                        if (score > highScore) highScore = score;
                    }

                    items.splice(i, 1);
                    i--;
                    continue;
                }

                // Rơi quá màn hình
                if (item.y - item.radius > cvs.height) {
                    if (item.type === "APPLE" && magnetTimer <= 0) {
                        lives--;
                        if (lives <= 0) gameState = "GAMEOVER";
                    }
                    items.splice(i, 1);
                    i--;
                }
            }

            // Sinh vật phẩm dồn dập hơn
            let rate = difficulties[currentDiff].spawnRate;
            if (gameState === "PLAYING" && frameCount % rate === 0) {
                spawnItem();
            }
        }

        function updateParticles() {
            for (let i = 0; i < particles.length; i++) {
                let p = particles[i];
                ctx.fillStyle = p.color;
                ctx.beginPath();
                ctx.arc(p.x, p.y, p.size, 0, Math.PI * 2);
                ctx.fill();

                p.x += p.vx;
                p.y += p.vy;
                p.life--;

                if (p.life <= 0) {
                    particles.splice(i, 1);
                    i--;
                }
            }
        }

        function drawUI() {
            // Mạng sống
            ctx.fillStyle = "#ff4d4d";
            ctx.font = "bold 18px sans-serif";
            ctx.textAlign = "left";
            let heartStr = "❤️ ".repeat(Math.max(0, lives));
            ctx.fillText(heartStr, 15, 30);

            // Điểm số
            ctx.fillStyle = "#222";
            ctx.font = "bold 20px sans-serif";
            ctx.textAlign = "right";
            ctx.fillText(`Điểm: ${score}`, cvs.width - 15, 30);
        }

        function draw() {
            ctx.clearRect(0, 0, cvs.width, cvs.height);

            if (gameState === "PLAYING") {
                if (leftPressed && basket.x > 0) basket.x -= basket.speed;
                if (rightPressed && basket.x + basket.width < cvs.width) basket.x += basket.speed;
                frameCount++;
                if (magnetTimer > 0) magnetTimer--;
            }

            drawBasket();
            drawItems();
            updateParticles();
            drawUI();

            if (gameState === "MENU") {
                ctx.fillStyle = "rgba(0, 0, 0, 0.45)";
                ctx.fillRect(0, 0, cvs.width, cvs.height);

                ctx.fillStyle = "#FFF";
                ctx.font = "bold 26px sans-serif";
                ctx.textAlign = "center";
                ctx.shadowColor = "rgba(0,0,0,0.8)";
                ctx.shadowBlur = 6;
                ctx.fillText("HỨNG TÁO: BOM & NAM CHÂM", cvs.width / 2, 160);

                ctx.font = "16px sans-serif";
                ctx.fillText(`Chế độ: ${difficulties[currentDiff].name}`, cvs.width / 2, 205);
                ctx.fillText("CHẠM MÀN HÌNH HOẶC BẤM SPACE", cvs.width / 2, 255);
                ctx.fillText("ĐỂ BẮT ĐẦU CHƠI", cvs.width / 2, 280);
                ctx.shadowBlur = 0;

            } else if (gameState === "GAMEOVER") {
                ctx.fillStyle = "rgba(0, 0, 0, 0.65)";
                ctx.fillRect(0, 0, cvs.width, cvs.height);

                ctx.fillStyle = "#ff4d4d";
                ctx.font = "bold 30px sans-serif";
                ctx.textAlign = "center";
                ctx.shadowColor = "rgba(0,0,0,0.8)";
                ctx.shadowBlur = 8;
                ctx.fillText("GAME OVER", cvs.width / 2, 160);

                ctx.fillStyle = "#FFF";
                ctx.font = "17px sans-serif";
                ctx.fillText(`Điểm của bạn: ${score}`, cvs.width / 2, 210);
                ctx.fillText(`Kỷ lục cao nhất: ${highScore}`, cvs.width / 2, 240);

                ctx.fillStyle = "#ffbb33";
                ctx.font = "bold 15px sans-serif";
                ctx.fillText("CHẠM MÀN HÌNH ĐỂ CHƠI LẠI 🔄", cvs.width / 2, 290);
                ctx.shadowBlur = 0;
            }

            requestAnimationFrame(draw);
        }

        draw();
    </script>
</body>
</html>
"""

components.html(game_html, height=600)
