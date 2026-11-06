import streamlit as st
import streamlit.components.v1 as components

st.set_page_config(
    page_title="Game Hứng Táo - Streamlit", page_icon="🍎", layout="centered"
)

st.title("🍎 Game Hứng Táo (Catch the Apples)")
st.caption(
    "💡 **Cách chơi:**<br>• **Máy tính:** Dùng phím mũi tên ⬅️ ➡️ hoặc phím A"
    " / D (hoặc di chuyển chuột).<br>• **Điện thoại:** Vuốt hoặc chạm sang trái /"
    " phải trên màn hình để di chuyển giỏ!",
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
            { name: "Dễ", initialSpeed: 2.2, speedInc: 0.15, maxLives: 4 },
            { name: "Thường", initialSpeed: 3.0, speedInc: 0.25, maxLives: 3 },
            { name: "Khó", initialSpeed: 4.2, speedInc: 0.35, maxLives: 2 }
        ];
        let currentDiff = 1;

        // Giỏ hứng
        let basket = {
            width: 75,
            height: 25,
            x: 142.5,
            y: 465,
            speed: 7
        };

        // Vật thể rơi (Táo đỏ & Sâu)
        let apples = [];
        let score = 0;
        let highScore = 0;
        let lives = 3;
        let frameCount = 0;

        // Điều khiển phím
        let leftPressed = false;
        let rightPressed = false;

        // Âm thanh Web Audio API
        const audioCtx = new (window.AudioContext || window.webkitAudioContext)();
        function playSound(type) {
            if (audioCtx.state === 'suspended') audioCtx.resume();
            const osc = audioCtx.createOscillator();
            const gain = audioCtx.createGain();
            osc.connect(gain);
            gain.connect(audioCtx.destination);

            if (type === 'catch') {
                osc.type = 'sine';
                osc.frequency.setValueAtTime(523, audioCtx.currentTime); // C5
                osc.frequency.setValueAtTime(659, audioCtx.currentTime + 0.08); // E5
                gain.gain.setValueAtTime(0.15, audioCtx.currentTime);
                gain.gain.linearRampToValueAtTime(0.01, audioCtx.currentTime + 0.15);
                osc.start(); osc.stop(audioCtx.currentTime + 0.15);
            } else if (type === 'miss') {
                osc.type = 'triangle';
                osc.frequency.setValueAtTime(220, audioCtx.currentTime);
                osc.frequency.linearRampToValueAtTime(110, audioCtx.currentTime + 0.2);
                gain.gain.setValueAtTime(0.2, audioCtx.currentTime);
                gain.gain.linearRampToValueAtTime(0.01, audioCtx.currentTime + 0.2);
                osc.start(); osc.stop(audioCtx.currentTime + 0.2);
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

        // Sự kiện bàn phím
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

        // Sự kiện chuột & Cảm ứng di động
        function handlePointerMove(e) {
            let rect = cvs.getBoundingClientRect();
            let clientX = e.clientX || (e.touches && e.touches[0].clientX);
            if (clientX) {
                let touchX = clientX - rect.left;
                basket.x = touchX - basket.width / 2;
                // Giữ giỏ trong khung hình
                if (basket.x < 0) basket.x = 0;
                if (basket.x + basket.width > cvs.width) basket.x = cvs.width - basket.width;
            }
        }

        cvs.addEventListener("mousemove", handlePointerMove);
        cvs.addEventListener("touchmove", (e) => {
            e.preventDefault();
            handlePointerMove(e);
        }, { passive: false });

        cvs.addEventListener("click", () => {
            if (gameState !== "PLAYING") startGame();
        });
        cvs.addEventListener("touchstart", (e) => {
            if (gameState !== "PLAYING") {
                e.preventDefault();
                startGame();
            }
        }, { passive: false });

        function startGame() {
            gameState = "PLAYING";
            score = 0;
            lives = difficulties[currentDiff].maxLives;
            apples = [];
            frameCount = 0;
            basket.x = (cvs.width - basket.width) / 2;
        }

        function spawnApple() {
            let diffConfig = difficulties[currentDiff];
            let currentSpeed = diffConfig.initialSpeed + (score * diffConfig.speedInc * 0.1);
            let isBomb = Math.random() < 0.18; // 18% cơ hội ra Táo Độc (Màu Xám/Sâu)

            apples.push({
                x: Math.random() * (cvs.width - 24) + 12,
                y: -15,
                radius: 12,
                speed: currentSpeed,
                isBomb: isBomb
            });
        }

        function drawBasket() {
            // Thân giỏ đan tre
            ctx.fillStyle = "#8B4513";
            ctx.beginPath();
            ctx.roundRect(basket.x, basket.y, basket.width, basket.height, 6);
            ctx.fill();
            ctx.lineWidth = 2;
            ctx.strokeStyle = "#5c2c09";
            ctx.stroke();

            // Sọc trang trí trên giỏ
            ctx.fillStyle = "#A0522D";
            ctx.fillRect(basket.x + 5, basket.y + 5, basket.width - 10, 4);
            ctx.fillRect(basket.x + 5, basket.y + 14, basket.width - 10, 4);
        }

        function drawApples() {
            for (let i = 0; i < apples.length; i++) {
                let a = apples[i];

                ctx.beginPath();
                ctx.arc(a.x, a.y, a.radius, 0, Math.PI * 2);

                if (a.isBomb) {
                    // Táo Độc (Trừ mạng)
                    ctx.fillStyle = "#555";
                    ctx.fill();
                    ctx.strokeStyle = "#111";
                    ctx.stroke();

                    // X trên táo độc
                    ctx.strokeStyle = "#ff4d4d";
                    ctx.lineWidth = 2;
                    ctx.beginPath();
                    ctx.moveTo(a.x - 4, a.y - 4); ctx.lineTo(a.x + 4, a.y + 4);
                    ctx.moveTo(a.x + 4, a.y - 4); ctx.lineTo(a.x - 4, a.y + 4);
                    ctx.stroke();
                } else {
                    // Táo Đỏ Thường (Cộng điểm)
                    ctx.fillStyle = "#ff3333";
                    ctx.fill();
                    ctx.lineWidth = 1.5;
                    ctx.strokeStyle = "#b30000";
                    ctx.stroke();

                    // Cuống táo & lá xanh
                    ctx.fillStyle = "#2e8b57";
                    ctx.beginPath();
                    ctx.ellipse(a.x + 3, a.y - 12, 4, 2, Math.PI / 4, 0, Math.PI * 2);
                    ctx.fill();
                }

                if (gameState === "PLAYING") {
                    a.y += a.speed;
                }

                // Xử lý Hứng thành công
                if (
                    a.y + a.radius >= basket.y &&
                    a.y - a.radius <= basket.y + basket.height &&
                    a.x >= basket.x - 5 &&
                    a.x <= basket.x + basket.width + 5
                ) {
                    if (a.isBomb) {
                        playSound('miss');
                        lives--;
                        if (lives <= 0) gameState = "GAMEOVER";
                    } else {
                        playSound('catch');
                        score += 10;
                        if (score > highScore) highScore = score;
                    }
                    apples.splice(i, 1);
                    i--;
                    continue;
                }

                // Rơi xuống đất
                if (a.y - a.radius > cvs.height) {
                    if (!a.isBomb) {
                        playSound('miss');
                        lives--;
                        if (lives <= 0) gameState = "GAMEOVER";
                    }
                    apples.splice(i, 1);
                    i--;
                }
            }

            // Sinh táo mới theo định kỳ
            let spawnInterval = Math.max(35, 75 - Math.floor(score / 30));
            if (gameState === "PLAYING" && frameCount % spawnInterval === 0) {
                spawnApple();
            }
        }

        function drawUI() {
            // Mạng sống (Trái tim)
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

            // Di chuyển giỏ bằng phím
            if (gameState === "PLAYING") {
                if (leftPressed && basket.x > 0) basket.x -= basket.speed;
                if (rightPressed && basket.x + basket.width < cvs.width) basket.x += basket.speed;
                frameCount++;
            }

            drawBasket();
            drawApples();
            drawUI();

            if (gameState === "MENU") {
                ctx.fillStyle = "rgba(0, 0, 0, 0.45)";
                ctx.fillRect(0, 0, cvs.width, cvs.height);

                ctx.fillStyle = "#FFF";
                ctx.font = "bold 28px sans-serif";
                ctx.textAlign = "center";
                ctx.shadowColor = "rgba(0,0,0,0.8)";
                ctx.shadowBlur = 6;
                ctx.fillText("HỨNG TÁO MAY MẮN", cvs.width / 2, 160);

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
