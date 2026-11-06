import streamlit as st
import streamlit.components.v1 as components

st.set_page_config(
    page_title="Flappy Bird Pro - Đã Sửa Lỗi Ống", page_icon="🐦", layout="centered"
)

st.title("🐦 Flappy Bird - Đã Sửa Lỗi Khoảng Trống Ống")
st.caption(
    "💡 **Điện thoại / Máy tính:** Chạm tay hoặc Click chuột trực tiếp vào màn"
    " hình game để bay / bắt đầu!"
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
            background: linear-gradient(to bottom, #4ec0ca, #87ceeb);
            cursor: pointer;
        }
        .controls-panel {
            margin-top: 12px;
            display: flex;
            flex-direction: column;
            align-items: center;
            gap: 10px;
        }
        .difficulty-container {
            display: flex;
            gap: 8px;
        }
        .diff-btn {
            background-color: #555;
            color: white;
            border: none;
            padding: 8px 14px;
            font-size: 14px;
            font-weight: bold;
            border-radius: 6px;
            cursor: pointer;
            transition: 0.1s;
        }
        .diff-btn.active {
            background-color: #ff8800;
            box-shadow: 0 2px #c66900;
        }
    </style>
</head>
<body>

    <div class="game-container">
        <canvas id="canvas" width="360" height="520"></canvas>
    </div>
    
    <div class="controls-panel">
        <div class="difficulty-container">
            <button class="diff-btn active" id="diff-0" onclick="setDifficulty(0)">Dễ</button>
            <button class="diff-btn" id="diff-1" onclick="setDifficulty(1)">Thường</button>
            <button class="diff-btn" id="diff-2" onclick="setDifficulty(2)">Khó</button>
            <button class="diff-btn" id="diff-3" onclick="setDifficulty(3)">Siêu Khó</button>
        </div>
    </div>

    <script>
        const cvs = document.getElementById("canvas");
        const ctx = cvs.getContext("2d");

        let gameState = "MENU"; // MENU, PLAYING, GAMEOVER

        // Cấu hình chuẩn cho 4 chế độ với khoảng hở (gap) thoáng rộng
        const difficulties = [
            { name: "Dễ", gravity: 0.22, jump: -4.8, speed: 1.6, gap: 175, interval: 130 },
            { name: "Thường", gravity: 0.26, jump: -5.2, speed: 1.9, gap: 160, interval: 115 },
            { name: "Khó", gravity: 0.30, jump: -5.6, speed: 2.3, gap: 145, interval: 100 },
            { name: "Siêu Khó", gravity: 0.34, jump: -6.0, speed: 2.7, gap: 130, interval: 90 }
        ];
        let currentDiffIndex = 1;

        let bird = {
            x: 70,
            y: 220,
            radius: 13,
            velocity: 0,
            rotation: 0
        };

        let pipes = [];
        let pipeWidth = 55;
        let frameCount = 0;
        let score = 0;
        let highScore = 0;
        let cloudX = 0;
        let hillX = 0;

        const audioCtx = new (window.AudioContext || window.webkitAudioContext)();
        function playSound(type) {
            if (audioCtx.state === 'suspended') audioCtx.resume();
            const osc = audioCtx.createOscillator();
            const gain = audioCtx.createGain();
            osc.connect(gain);
            gain.connect(audioCtx.destination);

            if (type === 'jump') {
                osc.type = 'sine';
                osc.frequency.setValueAtTime(400, audioCtx.currentTime);
                osc.frequency.exponentialRampToValueAtTime(700, audioCtx.currentTime + 0.1);
                gain.gain.setValueAtTime(0.15, audioCtx.currentTime);
                gain.gain.linearRampToValueAtTime(0.01, audioCtx.currentTime + 0.1);
                osc.start(); osc.stop(audioCtx.currentTime + 0.1);
            } else if (type === 'score') {
                osc.type = 'triangle';
                osc.frequency.setValueAtTime(600, audioCtx.currentTime);
                osc.frequency.setValueAtTime(900, audioCtx.currentTime + 0.08);
                gain.gain.setValueAtTime(0.2, audioCtx.currentTime);
                gain.gain.linearRampToValueAtTime(0.01, audioCtx.currentTime + 0.2);
                osc.start(); osc.stop(audioCtx.currentTime + 0.2);
            } else if (type === 'hit') {
                osc.type = 'sine';
                osc.frequency.setValueAtTime(150, audioCtx.currentTime);
                osc.frequency.exponentialRampToValueAtTime(60, audioCtx.currentTime + 0.15);
                gain.gain.setValueAtTime(0.1, audioCtx.currentTime);
                gain.gain.linearRampToValueAtTime(0.001, audioCtx.currentTime + 0.15);
                osc.start(); osc.stop(audioCtx.currentTime + 0.15);
            }
        }

        function setDifficulty(index) {
            currentDiffIndex = index;
            for (let i = 0; i < 4; i++) {
                document.getElementById(`diff-${i}`).classList.remove("active");
            }
            document.getElementById(`diff-${index}`).classList.add("active");
            if (gameState === "MENU") {
                draw();
            }
        }

        document.addEventListener("keydown", function(e) {
            if (e.code === "Space") {
                e.preventDefault();
                handleAction();
            }
        });

        cvs.addEventListener("click", function(e) {
            handleAction();
        });
        cvs.addEventListener("touchstart", function(e) {
            e.preventDefault();
            handleAction();
        }, { passive: false });

        function handleAction() {
            if (gameState === "MENU") {
                startGame();
            } else if (gameState === "PLAYING") {
                bird.velocity = difficulties[currentDiffIndex].jump;
                playSound('jump');
            } else if (gameState === "GAMEOVER") {
                startGame();
            }
        }

        function createNewPipe() {
            let diff = difficulties[currentDiffIndex];
            // Giới hạn chiều cao ống trên an toàn tuyệt đối, không bị kẹt hay bịt kín màn hình
            let minTop = 50;
            let maxTop = cvs.height - diff.gap - 80;
            let topHeight = Math.floor(Math.random() * (maxTop - minTop + 1)) + minTop;
            
            pipes.push({
                x: cvs.width,
                top: topHeight,
                passed: false
            });
        }

        function startGame() {
            gameState = "PLAYING";
            bird.y = 220;
            bird.velocity = 0;
            pipes = [];
            score = 0;
            frameCount = 0;
            createNewPipe();
        }

        function drawBackground() {
            let diff = difficulties[currentDiffIndex];
            if (gameState === "PLAYING") {
                cloudX -= diff.speed * 0.2;
                hillX -= diff.speed * 0.5;
                if (cloudX <= -cvs.width) cloudX = 0;
                if (hillX <= -cvs.width) hillX = 0;
            }

            ctx.fillStyle = "#558022";
            for (let i = 0; i < 2; i++) {
                let currentX = hillX + (i * cvs.width);
                ctx.beginPath();
                ctx.arc(currentX + 60, cvs.height - 30, 80, Math.PI, 0, false);
                ctx.arc(currentX + 200, cvs.height - 30, 110, Math.PI, 0, false);
                ctx.arc(currentX + 330, cvs.height - 30, 70, Math.PI, 0, false);
                ctx.fill();
            }

            ctx.fillStyle = "rgba(255, 255, 255, 0.6)";
            for (let i = 0; i < 2; i++) {
                let currentX = cloudX + (i * cvs.width);
                ctx.beginPath();
                ctx.arc(currentX + 60, 90, 22, 0, Math.PI * 2);
                ctx.arc(currentX + 80, 85, 30, 0, Math.PI * 2);
                ctx.arc(currentX + 105, 95, 20, 0, Math.PI * 2);
                ctx.fill();

                ctx.beginPath();
                ctx.arc(currentX + 260, 140, 25, 0, Math.PI * 2);
                ctx.arc(currentX + 285, 130, 35, 0, Math.PI * 2);
                ctx.fill();
            }
        }

        function drawBird() {
            ctx.save();
            ctx.translate(bird.x, bird.y);
            let targetRot = Math.min(Math.PI / 4, Math.max(-Math.PI / 4, (bird.velocity * 0.1)));
            bird.rotation += (targetRot - bird.rotation) * 0.2;
            ctx.rotate(bird.rotation);

            ctx.beginPath();
            ctx.arc(0, 0, bird.radius, 0, Math.PI * 2);
            ctx.fillStyle = "#f8d71c";
            ctx.fill();
            ctx.lineWidth = 2;
            ctx.strokeStyle = "#222";
            ctx.stroke();

            ctx.beginPath();
            ctx.arc(4, -4, 3.5, 0, Math.PI * 2);
            ctx.fillStyle = "#fff";
            ctx.fill();
            ctx.stroke();
            ctx.beginPath();
            ctx.arc(5, -4, 1.5, 0, Math.PI * 2);
            ctx.fillStyle = "#000";
            ctx.fill();

            ctx.fillStyle = "#ff5722";
            ctx.beginPath();
            ctx.moveTo(9, -2);
            ctx.lineTo(16, 2);
            ctx.lineTo(9, 6);
            ctx.closePath();
            ctx.fill();
            ctx.stroke();

            let wingAngle = Math.sin(frameCount * 0.4) * 0.6 - 0.2;
            ctx.save();
            ctx.translate(-3, 2);
            ctx.rotate(wingAngle);
            ctx.fillStyle = "#e0b400";
            ctx.strokeStyle = "#222";
            ctx.lineWidth = 1.5;
            ctx.beginPath();
            ctx.ellipse(0, 0, 7, 4, 0, 0, Math.PI * 2);
            ctx.fill();
            ctx.stroke();
            ctx.restore();

            ctx.restore();
        }

        function drawPipes() {
            let diff = difficulties[currentDiffIndex];
            for (let i = 0; i < pipes.length; i++) {
                let p = pipes[i];
                let topHeight = p.top;
                let bottomY = p.top + diff.gap;
                let bottomHeight = cvs.height - bottomY - 30;

                let pipeColor = "#73bf2e";
                let pipeBorder = "#3b7a12";

                ctx.fillStyle = pipeColor;
                ctx.strokeStyle = pipeBorder;
                ctx.lineWidth = 2;

                // Ống trên
                if (topHeight > 20) {
                    ctx.fillRect(p.x, 0, pipeWidth, topHeight - 20);
                    ctx.strokeRect(p.x, 0, pipeWidth, topHeight - 20);
                }
                ctx.fillRect(p.x - 3, topHeight - 20, pipeWidth + 6, 20);
                ctx.strokeRect(p.x - 3, topHeight - 20, pipeWidth + 6, 20);

                // Ống dưới
                ctx.fillRect(p.x - 3, bottomY, pipeWidth + 6, 20);
                ctx.strokeRect(p.x - 3, bottomY, pipeWidth + 6, 20);
                if (bottomHeight > 20) {
                    ctx.fillRect(p.x, bottomY + 20, pipeWidth, bottomHeight - 20);
                    ctx.strokeRect(p.x, bottomY + 20, pipeWidth, bottomHeight - 20);
                }

                if (gameState === "PLAYING") {
                    p.x -= diff.speed;
                }

                if (!p.passed && p.x + pipeWidth < bird.x) {
                    score++;
                    if (score > highScore) highScore = score;
                    playSound('score');
                    p.passed = true;
                }

                // Va chạm chuẩn xác
                if (
                    bird.x + bird.radius - 3 > p.x && 
                    bird.x - bird.radius + 3 < p.x + pipeWidth &&
                    (bird.y - bird.radius + 3 < topHeight || bird.y + bird.radius - 3 > bottomY)
                ) {
                    playSound('hit');
                    gameState = "GAMEOVER";
                }
            }

            if (pipes.length > 0 && pipes[0].x < -pipeWidth) {
                pipes.shift();
            }

            if (gameState === "PLAYING" && frameCount % diff.interval === 0) {
                createNewPipe();
            }
        }

        function drawGround() {
            let diff = difficulties[currentDiffIndex];
            ctx.fillStyle = "#ded895";
            ctx.fillRect(0, cvs.height - 30, cvs.width, 30);
            ctx.fillStyle = "#5c8a3c";
            ctx.fillRect(0, cvs.height - 30, cvs.width, 6);

            ctx.fillStyle = "#b5ad6e";
            for (let i = 0; i < cvs.width; i += 20) {
                let offsetX = gameState === "PLAYING" ? (frameCount * diff.speed) % 20 : 0;
                ctx.fillRect(i - offsetX, cvs.height - 24, 10, 4);
            }
        }

        function draw() {
            ctx.clearRect(0, 0, cvs.width, cvs.height);

            drawBackground();
            drawPipes();
            drawGround();
            drawBird();

            if (gameState === "MENU") {
                ctx.fillStyle = "rgba(0, 0, 0, 0.4)";
                ctx.fillRect(0, 0, cvs.width, cvs.height);

                ctx.fillStyle = "#FFF";
                ctx.font = "bold 28px sans-serif";
                ctx.textAlign = "center";
                ctx.shadowColor = "rgba(0, 0, 0, 0.8)";
                ctx.shadowBlur = 6;
                ctx.fillText("FLAPPY BIRD", cvs.width / 2, 140);

                ctx.font = "16px sans-serif";
                ctx.fillText(`Chế độ: ${difficulties[currentDiffIndex].name}`, cvs.width / 2, 185);
                ctx.fillText("CHẠM MÀN HÌNH HOẶC BẤM SPACE", cvs.width / 2, 230);
                ctx.fillText("ĐỂ BẮT ĐẦU", cvs.width / 2, 255);
                ctx.shadowBlur = 0;

            } else if (gameState === "PLAYING") {
                let diff = difficulties[currentDiffIndex];
                bird.velocity += diff.gravity;
                bird.y += bird.velocity;

                if (bird.y + bird.radius >= cvs.height - 30) {
                    bird.y = cvs.height - 30 - bird.radius;
                    playSound('hit');
                    gameState = "GAMEOVER";
                }
                if (bird.y - bird.radius <= 0) {
                    bird.y = bird.radius;
                    bird.velocity = 0;
                }

                frameCount++;

                ctx.fillStyle = "#FFF";
                ctx.strokeStyle = "#000";
                ctx.lineWidth = 4;
                ctx.font = "bold 38px sans-serif";
                ctx.textAlign = "center";
                ctx.strokeText(score, cvs.width / 2, 60);
                ctx.fillText(score, cvs.width / 2, 60);

            } else if (gameState === "GAMEOVER") {
                ctx.fillStyle = "rgba(0, 0, 0, 0.6)";
                ctx.fillRect(0, 0, cvs.width, cvs.height);

                ctx.fillStyle = "#ff4d4d";
                ctx.font = "bold 28px sans-serif";
                ctx.textAlign = "center";
                ctx.shadowColor = "rgba(0, 0, 0, 0.8)";
                ctx.shadowBlur = 8;
                ctx.fillText("GAME OVER", cvs.width / 2, 140);

                ctx.fillStyle = "#FFF";
                ctx.font = "16px sans-serif";
                ctx.fillText(`Điểm số: ${score}`, cvs.width / 2, 195);
                ctx.fillText(`Kỷ lục: ${highScore}`, cvs.width / 2, 225);
                
                ctx.fillStyle = "#ffbb33";
                ctx.font = "bold 15px sans-serif";
                ctx.fillText("CHẠM MÀN HÌNH ĐỂ CHƠI LẠI", cvs.width / 2, 275);
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
