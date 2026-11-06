import streamlit as st
import streamlit.components.v1 as components

st.set_page_config(
    page_title="Flappy Bird Pro - Streamlit", page_icon="🐦", layout="centered"
)

st.title("🐦 Flappy Bird - Phiên Bản Nâng Cấp")
st.caption(
    "💡 Nhấn **Phím SPACE** hoặc bấm nút **BAY LÊN / BẮT ĐẦU** để điều khiển!"
)

# Mã nguồn HTML, CSS và JavaScript hoàn chỉnh cho game
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
            background: linear-gradient(to bottom, #70c5ce, #b0e0e6);
        }
        .btn-container {
            margin-top: 12px;
            display: flex;
            gap: 10px;
        }
        .action-btn {
            background: linear-gradient(to bottom, #ffbb33, #ff8800);
            color: white;
            border: none;
            padding: 12px 35px;
            font-size: 18px;
            font-weight: bold;
            border-radius: 25px;
            cursor: pointer;
            box-shadow: 0 4px #c66900;
            transition: 0.1s;
        }
        .action-btn:active {
            box-shadow: 0 1px #c66900;
            transform: translateY(3px);
        }
    </style>
</head>
<body>

    <div class="game-container">
        <canvas id="canvas" width="360" height="520"></canvas>
    </div>
    
    <div class="btn-container">
        <button class="action-btn" id="mainBtn" onclick="handleAction()">CHƠI NGAY 🚀</button>
    </div>

    <script>
        const cvs = document.getElementById("canvas");
        const ctx = cvs.getContext("2d");
        const mainBtn = document.getElementById("mainBtn");

        // Trạng thái game: 'MENU', 'PLAYING', 'GAMEOVER'
        let gameState = "MENU";

        // Biến thông số chim
        let bird = {
            x: 70,
            y: 220,
            radius: 14,
            gravity: 0.32,
            velocity: 0,
            jump: -6.0,
            rotation: 0
        };

        // Biến ống nước
        let pipes = [];
        let pipeWidth = 55;
        let pipeGap = 135;
        let frameCount = 0;
        let score = 0;
        let highScore = 0;

        // Âm thanh sử dụng Web Audio API (Không cần file ngoài)
        const audioCtx = new (window.AudioContext || window.webkitAudioContext)();
        
        function playSound(type) {
            if (audioCtx.state === 'suspended') {
                audioCtx.resume();
            }
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
                osc.start();
                osc.stop(audioCtx.currentTime + 0.1);
            } else if (type === 'score') {
                osc.type = 'triangle';
                osc.frequency.setValueAtTime(600, audioCtx.currentTime);
                osc.frequency.setValueAtTime(900, audioCtx.currentTime + 0.08);
                gain.gain.setValueAtTime(0.2, audioCtx.currentTime);
                gain.gain.linearRampToValueAtTime(0.01, audioCtx.currentTime + 0.2);
                osc.start();
                osc.stop(audioCtx.currentTime + 0.2);
            } else if (type === 'hit') {
                osc.type = 'sawtooth';
                osc.frequency.setValueAtTime(200, audioCtx.currentTime);
                osc.frequency.linearRampToValueAtTime(80, audioCtx.currentTime + 0.2);
                gain.gain.setValueAtTime(0.3, audioCtx.currentTime);
                gain.gain.linearRampToValueAtTime(0.01, audioCtx.currentTime + 0.2);
                osc.start();
                osc.stop(audioCtx.currentTime + 0.2);
            }
        }

        // Bắt sự kiện phím Space
        document.addEventListener("keydown", function(e) {
            if (e.code === "Space") {
                e.preventDefault();
                handleAction();
            }
        });

        function handleAction() {
            if (gameState === "MENU") {
                startGame();
            } else if (gameState === "PLAYING") {
                bird.velocity = bird.jump;
                playSound('jump');
            } else if (gameState === "GAMEOVER") {
                startGame();
            }
        }

        function startGame() {
            gameState = "PLAYING";
            mainBtn.innerText = "BAY LÊN 🚀";
            bird.y = 220;
            bird.velocity = 0;
            pipes = [];
            score = 0;
            frameCount = 0;
            // Tạo sẵn ống đầu tiên
            pipes.push({
                x: cvs.width,
                top: Math.floor(Math.random() * (cvs.height - pipeGap - 140)) + 40,
                passed: false
            });
        }

        function drawBackground() {
            // Vẽ mây nền trang trí
            ctx.fillStyle = "rgba(255, 255, 255, 0.4)";
            ctx.beginPath();
            ctx.arc(80, 100, 30, 0, Math.PI * 2);
            ctx.arc(110, 95, 40, 0, Math.PI * 2);
            ctx.arc(140, 105, 25, 0, Math.PI * 2);
            ctx.fill();

            ctx.beginPath();
            ctx.arc(280, 160, 25, 0, Math.PI * 2);
            ctx.arc(310, 150, 35, 0, Math.PI * 2);
            ctx.fill();
        }

        function drawBird() {
            ctx.save();
            ctx.translate(bird.x, bird.y);
            
            // Xoay góc theo vận tốc rơi/nhảy
            let targetRot = Math.min(Math.PI / 4, Math.max(-Math.PI / 4, (bird.velocity * 0.1)));
            bird.rotation += (targetRot - bird.rotation) * 0.2;
            ctx.rotate(bird.rotation);

            // Thân chim
            ctx.beginPath();
            ctx.arc(0, 0, bird.radius, 0, Math.PI * 2);
            ctx.fillStyle = "#f8d71c";
            ctx.fill();
            ctx.lineWidth = 2;
            ctx.strokeStyle = "#222";
            ctx.stroke();

            // Mắt chim
            ctx.beginPath();
            ctx.arc(5, -4, 4, 0, Math.PI * 2);
            ctx.fillStyle = "#fff";
            ctx.fill();
            ctx.stroke();
            ctx.beginPath();
            ctx.arc(6, -4, 1.5, 0, Math.PI * 2);
            ctx.fillStyle = "#000";
            ctx.fill();

            // Mỏ chim
            ctx.fillStyle = "#ff5722";
            ctx.beginPath();
            ctx.moveTo(10, -2);
            ctx.lineTo(18, 2);
            ctx.lineTo(10, 6);
            ctx.closePath();
            ctx.fill();
            ctx.stroke();

            // Cánh chim nhỏ
            ctx.fillStyle = "#e0b400";
            ctx.beginPath();
            ctx.ellipse(-4, 2, 6, 4, Math.PI / 6, 0, Math.PI * 2);
            ctx.fill();
            ctx.stroke();

            ctx.restore();
        }

        function drawPipes() {
            for (let i = 0; i < pipes.length; i++) {
                let p = pipes[i];
                let bottomY = p.top + pipeGap;
                let bottomHeight = cvs.height - bottomY - 30;

                // Màu sắc ống nước hiện đại (Gradient xanh lá)
                let pipeColor = "#73bf2e";
                let pipeBorder = "#3b7a12";

                // Ống trên
                ctx.fillStyle = pipeColor;
                ctx.fillRect(p.x, 0, pipeWidth, p.top);
                ctx.lineWidth = 2;
                ctx.strokeStyle = pipeBorder;
                ctx.strokeRect(p.x, 0, pipeWidth, p.top);
                // Miệng ống trên
                ctx.fillRect(p.x - 3, p.top - 20, pipeWidth + 6, 20);
                ctx.strokeRect(p.x - 3, p.top - 20, pipeWidth + 6, 20);

                // Ống dưới
                ctx.fillRect(p.x, bottomY, pipeWidth, bottomHeight);
                ctx.strokeRect(p.x, bottomY, pipeWidth, bottomHeight);
                // Miệng ống dưới
                ctx.fillRect(p.x - 3, bottomY, pipeWidth + 6, 20);
                ctx.strokeRect(p.x - 3, bottomY, pipeWidth + 6, 20);

                if (gameState === "PLAYING") {
                    p.x -= 2.2; // Tốc độ di chuyển của ống
                }

                // Kiểm tra vượt qua để tính điểm
                if (!p.passed && p.x + pipeWidth < bird.x) {
                    score++;
                    if (score > highScore) highScore = score;
                    playSound('score');
                    p.passed = true;
                }

                // Xử lý va chạm chuẩn xác (Bounding box)
                if (
                    bird.x + bird.radius > p.x && 
                    bird.x - bird.radius < p.x + pipeWidth &&
                    (bird.y - bird.radius < p.top || bird.y + bird.radius > bottomY)
                ) {
                    playSound('hit');
                    gameState = "GAMEOVER";
                    mainBtn.innerText = "CHƠI LẠI 🔄";
                }
            }

            // Xóa ống cũ đi ra ngoài màn hình
            if (pipes.length > 0 && pipes[0].x < -pipeWidth) {
                pipes.shift();
            }

            // Sinh ống mới định kỳ
            if (gameState === "PLAYING" && frameCount % 95 === 0) {
                pipes.push({
                    x: cvs.width,
                    top: Math.floor(Math.random() * (cvs.height - pipeGap - 140)) + 40,
                    passed: false
                });
            }
        }

        function drawGround() {
            // Đất nền phía dưới
            ctx.fillStyle = "#ded895";
            ctx.fillRect(0, cvs.height - 30, cvs.width, 30);
            ctx.fillStyle = "#5c8a3c";
            ctx.fillRect(0, cvs.height - 30, cvs.width, 6);

            // Hiệu ứng sọc đường đi
            ctx.fillStyle = "#b5ad6e";
            for (let i = 0; i < cvs.width; i += 20) {
                let offsetX = gameState === "PLAYING" ? (frameCount * 2.2) % 20 : 0;
                ctx.fillRect(i - offsetX, cvs.height - 24, 10, 4);
            }
        }

        function update() {
            ctx.clearRect(0, 0, cvs.width, cvs.height);

            drawBackground();
            drawPipes();
            drawGround();
            drawBird();

            if (gameState === "MENU") {
                // Màn hình Menu Bắt Đầu
                ctx.fillStyle = "rgba(0, 0, 0, 0.35)";
                ctx.fillRect(0, 0, cvs.width, cvs.height);

                ctx.fillStyle = "#FFF";
                ctx.font = "bold 32px sans-serif";
                ctx.textAlign = "center";
                ctx.shadowColor = "rgba(0, 0, 0, 0.7)";
                ctx.shadowBlur = 6;
                ctx.fillText("FLAPPY BIRD", cvs.width / 2, 170);

                ctx.font = "16px sans-serif";
                ctx.fillText("Bấm nút bên dưới để bắt đầu", cvs.width / 2, 220);
                ctx.shadowBlur = 0; // Reset shadow

            } else if (gameState === "PLAYING") {
                bird.velocity += bird.gravity;
                bird.y += bird.velocity;

                // Kiểm tra chạm sàn hoặc bay quá cao
                if (bird.y + bird.radius >= cvs.height - 30) {
                    bird.y = cvs.height - 30 - bird.radius;
                    playSound('hit');
                    gameState = "GAMEOVER";
                    mainBtn.innerText = "CHƠI LẠI 🔄";
                }
                if (bird.y - bird.radius <= 0) {
                    bird.y = bird.radius;
                    bird.velocity = 0;
                }

                frameCount++;

                // Hiển thị điểm số hiện tại
                ctx.fillStyle = "#FFF";
                ctx.strokeStyle = "#000";
                ctx.lineWidth = 4;
                ctx.font = "bold 38px sans-serif";
                ctx.textAlign = "center";
                ctx.strokeText(score, cvs.width / 2, 60);
                ctx.fillText(score, cvs.width / 2, 60);

            } else if (gameState === "GAMEOVER") {
                // Bảng thông báo Game Over
                ctx.fillStyle = "rgba(0, 0, 0, 0.55)";
                ctx.fillRect(0, 0, cvs.width, cvs.height);

                ctx.fillStyle = "#ff4d4d";
                ctx.font = "bold 30px sans-serif";
                ctx.textAlign = "center";
                ctx.shadowColor = "rgba(0, 0, 0, 0.8)";
                ctx.shadowBlur = 8;
                ctx.fillText("GAME OVER", cvs.width / 2, 160);

                // Bảng điểm kết quả
                ctx.fillStyle = "#FFF";
                ctx.font = "18px sans-serif";
                ctx.fillText(`Điểm số: ${score}`, cvs.width / 2, 215);
                ctx.fillText(`Kỷ lục cao nhất: ${highScore}`, cvs.width / 2, 250);
                ctx.shadowBlur = 0;
            }

            requestAnimationFrame(update);
        }

        update();
    </script>
</body>
</html>
"""

# Nhúng vào giao diện Streamlit
components.html(game_html, height=600)
