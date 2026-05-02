"""
Minecraft Sunucu Yönetim API
FastAPI ile web tabanlı sunucu yönetim arayüzü
"""
from fastapi import FastAPI, HTTPException, Request, Header
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, List
import os
from dotenv import load_dotenv
from server_manager import MinecraftServerManager
import uvicorn

# Ortam değişkenlerini yükle
load_dotenv()

app = FastAPI(
    title="Minecraft Sunucu Yönetim API",
    description="Minecraft 1.21.11 sunucu yönetim sistemi",
    version="1.0.0"
)

# CORS ayarları
if ENABLE_CORS:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=CORS_ORIGINS,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

# Yapılandırma
SERVER_HOST = os.getenv("SERVER_HOST", "localhost")
SERVER_PORT = int(os.getenv("SERVER_PORT", "25575"))
RCON_PASSWORD = os.getenv("RCON_PASSWORD", "")
API_PORT = int(os.getenv("API_PORT", "8000"))
API_KEY = os.getenv("API_KEY", "")
ALLOWED_IPS = os.getenv("ALLOWED_IPS", "").split(",") if os.getenv("ALLOWED_IPS") else []
ENABLE_CORS = os.getenv("ENABLE_CORS", "true").lower() == "true"
CORS_ORIGINS = os.getenv("CORS_ORIGINS", "*").split(",") if os.getenv("CORS_ORIGINS") else ["*"]
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")

# Sunucu yöneticisi instance'ı
server_manager = MinecraftServerManager(SERVER_HOST, SERVER_PORT, RCON_PASSWORD)

# Request modelleri
class CommandRequest(BaseModel):
    command: str

class MessageRequest(BaseModel):
    player: Optional[str] = None
    message: str

class PlayerActionRequest(BaseModel):
    player: str
    reason: Optional[str] = None


# Güvenlik fonksiyonları
def check_api_key(x_api_key: Optional[str] = Header(None)) -> bool:
    """API anahtarı kontrolü"""
    if not API_KEY:
        return True  # API key ayarlanmamışsa kontrol etme
    return x_api_key == API_KEY

def check_ip_allowed(request: Request) -> bool:
    """IP adresi kontrolü"""
    if not ALLOWED_IPS or not ALLOWED_IPS[0]:
        return True  # IP kısıtlaması yoksa izin ver
    
    client_ip = request.client.host if request.client else "unknown"
    return client_ip in ALLOWED_IPS or "127.0.0.1" in ALLOWED_IPS or "::1" in ALLOWED_IPS


@app.on_event("startup")
async def startup_event():
    """Uygulama başlangıcında sunucuya bağlan"""
    print("\n" + "="*60)
    print("Minecraft Sunucu Yönetim Sistemi Başlatılıyor...")
    print("="*60)
    
    if not RCON_PASSWORD:
        print("⚠️  UYARI: RCON_PASSWORD .env dosyasında tanımlanmamış!")
        print("📝 Lütfen .env dosyası oluşturun ve RCON_PASSWORD değerini ayarlayın.")
        print("   Örnek: RCON_PASSWORD=your_secure_password")
    else:
        print(f"🔌 Sunucuya bağlanılıyor: {SERVER_HOST}:{SERVER_PORT}")
        if server_manager.connect():
            print("✅ Sunucuya başarıyla bağlanıldı!")
        else:
            print("❌ Sunucuya bağlanılamadı. Lütfen ayarları kontrol edin.")
    
    print(f"🌐 Web arayüzü: http://localhost:{API_PORT}")
    print(f"📡 API: http://localhost:{API_PORT}/api")
    print(f"🔒 CORS: {'Etkin' if ENABLE_CORS else 'Devre Dışı'}")
    if API_KEY:
        print(f"🔑 API Key: Etkin")
    if ALLOWED_IPS and ALLOWED_IPS[0]:
        print(f"🌍 İzin Verilen IP'ler: {', '.join(ALLOWED_IPS)}")
    print("="*60 + "\n")


@app.on_event("shutdown")
async def shutdown_event():
    """Uygulama kapanışında bağlantıyı kapat"""
    server_manager.disconnect()


@app.get("/", response_class=HTMLResponse)
async def root():
    """Ana sayfa - Web arayüzü"""
    html_content = """
<!DOCTYPE html>
<html lang="tr">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Minecraft Sunucu Yönetim Paneli</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            padding: 20px;
        }
        .container {
            max-width: 1200px;
            margin: 0 auto;
        }
        .header {
            background: rgba(255, 255, 255, 0.95);
            padding: 30px;
            border-radius: 15px;
            margin-bottom: 20px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.2);
            text-align: center;
        }
        .header h1 {
            color: #333;
            margin-bottom: 10px;
        }
        .header p {
            color: #666;
        }
        .status-card {
            background: rgba(255, 255, 255, 0.95);
            padding: 25px;
            border-radius: 15px;
            margin-bottom: 20px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.2);
        }
        .status-indicator {
            display: inline-block;
            width: 12px;
            height: 12px;
            border-radius: 50%;
            margin-right: 8px;
        }
        .status-online { background: #4CAF50; }
        .status-offline { background: #f44336; }
        .grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
            gap: 20px;
            margin-bottom: 20px;
        }
        .card {
            background: rgba(255, 255, 255, 0.95);
            padding: 25px;
            border-radius: 15px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.2);
        }
        .card h2 {
            color: #333;
            margin-bottom: 15px;
            font-size: 1.3em;
        }
        .form-group {
            margin-bottom: 15px;
        }
        label {
            display: block;
            margin-bottom: 5px;
            color: #555;
            font-weight: 500;
        }
        input, textarea, select {
            width: 100%;
            padding: 12px;
            border: 2px solid #e0e0e0;
            border-radius: 8px;
            font-size: 14px;
            transition: border-color 0.3s;
        }
        input:focus, textarea:focus, select:focus {
            outline: none;
            border-color: #667eea;
        }
        button {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            border: none;
            padding: 12px 24px;
            border-radius: 8px;
            cursor: pointer;
            font-size: 16px;
            font-weight: 600;
            transition: transform 0.2s, box-shadow 0.2s;
            width: 100%;
        }
        button:hover {
            transform: translateY(-2px);
            box-shadow: 0 5px 15px rgba(102, 126, 234, 0.4);
        }
        button:active {
            transform: translateY(0);
        }
        .player-list {
            list-style: none;
        }
        .player-item {
            padding: 10px;
            background: #f5f5f5;
            margin-bottom: 8px;
            border-radius: 6px;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }
        .player-name {
            font-weight: 500;
            color: #333;
        }
        .btn-small {
            padding: 6px 12px;
            font-size: 12px;
            width: auto;
            margin-left: 10px;
        }
        .response-box {
            background: #f5f5f5;
            padding: 15px;
            border-radius: 8px;
            margin-top: 15px;
            min-height: 50px;
            font-family: 'Courier New', monospace;
            font-size: 13px;
            color: #333;
            white-space: pre-wrap;
            word-wrap: break-word;
        }
        .success { background: #d4edda; color: #155724; }
        .error { background: #f8d7da; color: #721c24; }
        .loading {
            display: inline-block;
            width: 20px;
            height: 20px;
            border: 3px solid rgba(255,255,255,.3);
            border-radius: 50%;
            border-top-color: #fff;
            animation: spin 1s ease-in-out infinite;
        }
        @keyframes spin {
            to { transform: rotate(360deg); }
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🎮 Minecraft Sunucu Yönetim Paneli</h1>
            <p>Minecraft 1.21.11 Sunucu Yönetim Sistemi</p>
        </div>

        <div class="status-card">
            <h2>Sunucu Durumu</h2>
            <div id="status-info">
                <span class="status-indicator status-offline"></span>
                <span>Yükleniyor...</span>
            </div>
            <button onclick="refreshStatus()" style="margin-top: 15px;">🔄 Durumu Yenile</button>
        </div>

        <div class="grid">
            <div class="card">
                <h2>⚡ Komut Gönder</h2>
                <div class="form-group">
                    <label>Komut:</label>
                    <input type="text" id="command-input" placeholder="Örn: say Merhaba!" onkeypress="if(event.key==='Enter') sendCommand()" />
                </div>
                <button onclick="sendCommand()">Komut Gönder</button>
                <div id="command-response" class="response-box" style="display:none;"></div>
            </div>

            <div class="card">
                <h2>💬 Mesaj Gönder</h2>
                <div class="form-group">
                    <label>Oyuncu (boş bırakırsanız tüm sunucuya gönderilir):</label>
                    <input type="text" id="message-player" placeholder="Oyuncu adı (opsiyonel)" />
                </div>
                <div class="form-group">
                    <label>Mesaj:</label>
                    <textarea id="message-text" rows="3" placeholder="Mesajınızı yazın..." onkeypress="if(event.key==='Enter' && event.ctrlKey) sendMessage()"></textarea>
                    <small style="color: #666; font-size: 0.85em;">💡 İpucu: Ctrl+Enter ile gönderebilirsiniz</small>
                </div>
                <button onclick="sendMessage()">Mesaj Gönder</button>
                <div id="message-response" class="response-box" style="display:none;"></div>
            </div>
        </div>

        <div class="card">
            <h2>👥 Oyuncular</h2>
            <button onclick="refreshPlayers()" style="margin-bottom: 15px;">🔄 Oyuncu Listesini Yenile</button>
            <ul id="player-list" class="player-list">
                <li>Yükleniyor...</li>
            </ul>
        </div>
    </div>

    <script>
        const API_BASE = window.location.origin;

        async function apiCall(endpoint, method = 'GET', body = null) {
            try {
                const options = {
                    method,
                    headers: { 'Content-Type': 'application/json' }
                };
                if (body) options.body = JSON.stringify(body);
                
                const response = await fetch(`${API_BASE}${endpoint}`, options);
                return await response.json();
            } catch (error) {
                return { error: error.message };
            }
        }

        async function refreshStatus() {
            const statusInfo = document.getElementById('status-info');
            statusInfo.innerHTML = '<span class="status-indicator status-offline"></span><span>Yükleniyor...</span>';
            
            const data = await apiCall('/api/status');
            const indicator = data.connected ? 'status-online' : 'status-offline';
            const text = data.connected ? 'Çevrimiçi' : 'Çevrimdışı';
            
            let errorMsg = '';
            if (data.error) {
                errorMsg = `<br><br><span style="color: #f44336; font-size: 0.9em;">⚠️ ${data.error}</span>`;
            }
            
            statusInfo.innerHTML = `
                <span class="status-indicator ${indicator}"></span>
                <span><strong>${text}</strong></span>
                <br><br>
                <small>Host: ${data.host || 'N/A'}:${data.port || 'N/A'}</small>
                ${data.tps_info ? '<br><small>TPS: ' + data.tps_info + '</small>' : ''}
                ${data.player_list ? '<br><small>' + data.player_list + '</small>' : ''}
                ${errorMsg}
            `;
        }

        async function sendCommand() {
            const commandInput = document.getElementById('command-input');
            const command = commandInput.value.trim();
            if (!command) {
                alert('Lütfen bir komut girin!');
                return;
            }

            const responseDiv = document.getElementById('command-response');
            responseDiv.style.display = 'block';
            responseDiv.className = 'response-box';
            responseDiv.textContent = 'Gönderiliyor...';
            
            // Butonu devre dışı bırak
            const button = event.target;
            button.disabled = true;

            const data = await apiCall('/api/command', 'POST', { command });
            
            // Butonu tekrar etkinleştir
            button.disabled = false;
            
            if (data.success) {
                responseDiv.className = 'response-box success';
                responseDiv.textContent = data.response || 'Komut başarıyla gönderildi!';
                commandInput.value = ''; // Komut alanını temizle
            } else {
                responseDiv.className = 'response-box error';
                responseDiv.textContent = data.error || 'Bir hata oluştu!';
            }
        }

        async function sendMessage() {
            const player = document.getElementById('message-player').value.trim();
            const message = document.getElementById('message-text').value.trim();
            
            if (!message) {
                alert('Lütfen bir mesaj yazın!');
                return;
            }

            const responseDiv = document.getElementById('message-response');
            responseDiv.style.display = 'block';
            responseDiv.className = 'response-box';
            responseDiv.textContent = 'Gönderiliyor...';

            const data = await apiCall('/api/message', 'POST', { player: player || null, message });
            
            if (data.success) {
                responseDiv.className = 'response-box success';
                responseDiv.textContent = 'Mesaj başarıyla gönderildi!';
                document.getElementById('message-text').value = '';
            } else {
                responseDiv.className = 'response-box error';
                responseDiv.textContent = data.error || 'Bir hata oluştu!';
            }
        }

        async function refreshPlayers() {
            const playerList = document.getElementById('player-list');
            playerList.innerHTML = '<li>Yükleniyor...</li>';

            const data = await apiCall('/api/players');
            
            if (data.error) {
                playerList.innerHTML = `<li style="color: #f44336;">Hata: ${data.error}</li>`;
                return;
            }
            
            if (data.players && data.players.length > 0) {
                playerList.innerHTML = data.players.map(player => {
                    const safeName = player.name.replace(/'/g, "\\'");
                    return `
                    <li class="player-item">
                        <span class="player-name">${player.name}</span>
                        <div>
                            <button class="btn-small" onclick="kickPlayer('${safeName}')">At</button>
                            <button class="btn-small" onclick="banPlayer('${safeName}')">Yasakla</button>
                        </div>
                    </li>
                `;
                }).join('');
            } else {
                playerList.innerHTML = '<li style="color: #666; font-style: italic;">Çevrimiçi oyuncu yok</li>';
            }
        }

        async function kickPlayer(player) {
            if (!confirm(`${player} oyuncusunu atmak istediğinize emin misiniz?`)) return;
            
            const data = await apiCall('/api/kick', 'POST', { player });
            if (data.success) {
                alert('Oyuncu başarıyla atıldı!');
                refreshPlayers();
            } else {
                alert('Hata: ' + (data.error || 'Bilinmeyen hata'));
            }
        }

        async function banPlayer(player) {
            if (!confirm(`${player} oyuncusunu yasaklamak istediğinize emin misiniz?`)) return;
            
            const data = await apiCall('/api/ban', 'POST', { player });
            if (data.success) {
                alert('Oyuncu başarıyla yasaklandı!');
                refreshPlayers();
            } else {
                alert('Hata: ' + (data.error || 'Bilinmeyen hata'));
            }
        }

        // Sayfa yüklendiğinde durumu ve oyuncuları yükle
        window.onload = function() {
            refreshStatus();
            refreshPlayers();
            setInterval(refreshStatus, 30000); // Her 30 saniyede bir durumu güncelle
        };
    </script>
</body>
</html>
    """
    return HTMLResponse(content=html_content)


# API Endpoints
@app.get("/api/status")
async def get_status(request: Request):
    """Sunucu durumunu döndür"""
    # IP kontrolü
    if not check_ip_allowed(request):
        raise HTTPException(status_code=403, detail="IP adresi yetkili değil")
    
    try:
        status = server_manager.get_status()
        # Bağlantı durumunu kontrol et ve güncelle
        if not status.get("connected") and server_manager.connection:
            status["connected"] = True
        return JSONResponse(content=status)
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={
                "connected": False,
                "error": f"Durum alınamadı: {str(e)}",
                "host": SERVER_HOST,
                "port": SERVER_PORT
            }
        )


@app.post("/api/command")
async def send_command(request: CommandRequest, http_request: Request, x_api_key: Optional[str] = Header(None)):
    """Sunucuya komut gönder"""
    # Güvenlik kontrolleri
    if not check_ip_allowed(http_request):
        raise HTTPException(status_code=403, detail="IP adresi yetkili değil")
    if not check_api_key(x_api_key):
        raise HTTPException(status_code=401, detail="Geçersiz API anahtarı")
    
    if not request.command or not request.command.strip():
        return JSONResponse(
            status_code=400,
            content={"success": False, "error": "Komut boş olamaz"}
        )
    
    try:
        response = server_manager.send_command(request.command.strip())
        if response is not None:
            return JSONResponse(content={
                "success": True,
                "response": response
            })
        else:
            return JSONResponse(
                status_code=500,
                content={
                    "success": False, 
                    "error": "Komut gönderilemedi. Sunucuya bağlanılamıyor olabilir."
                }
            )
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={"success": False, "error": f"Komut gönderme hatası: {str(e)}"}
        )


@app.get("/api/players")
async def get_players(http_request: Request):
    """Oyuncu listesini döndür"""
    # IP kontrolü
    if not check_ip_allowed(http_request):
        raise HTTPException(status_code=403, detail="IP adresi yetkili değil")
    
    try:
        players = server_manager.get_players()
        return JSONResponse(content={"players": players})
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/message")
async def send_message(request: MessageRequest, http_request: Request, x_api_key: Optional[str] = Header(None)):
    """Oyuncuya veya tüm sunucuya mesaj gönder"""
    # Güvenlik kontrolleri
    if not check_ip_allowed(http_request):
        raise HTTPException(status_code=403, detail="IP adresi yetkili değil")
    if not check_api_key(x_api_key):
        raise HTTPException(status_code=401, detail="Geçersiz API anahtarı")
    
    try:
        if request.player:
            success = server_manager.send_message(request.player, request.message)
        else:
            success = server_manager.broadcast_message(request.message)
        
        if success:
            return JSONResponse(content={"success": True})
        else:
            return JSONResponse(
                status_code=500,
                content={"success": False, "error": "Mesaj gönderilemedi"}
            )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/kick")
async def kick_player(request: PlayerActionRequest, http_request: Request, x_api_key: Optional[str] = Header(None)):
    """Oyuncuyu at"""
    # Güvenlik kontrolleri
    if not check_ip_allowed(http_request):
        raise HTTPException(status_code=403, detail="IP adresi yetkili değil")
    if not check_api_key(x_api_key):
        raise HTTPException(status_code=401, detail="Geçersiz API anahtarı")
    
    try:
        success = server_manager.kick_player(request.player, request.reason or "")
        if success:
            return JSONResponse(content={"success": True})
        else:
            return JSONResponse(
                status_code=500,
                content={"success": False, "error": "Oyuncu atılamadı"}
            )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/ban")
async def ban_player(request: PlayerActionRequest, http_request: Request, x_api_key: Optional[str] = Header(None)):
    """Oyuncuyu yasakla"""
    # Güvenlik kontrolleri
    if not check_ip_allowed(http_request):
        raise HTTPException(status_code=403, detail="IP adresi yetkili değil")
    if not check_api_key(x_api_key):
        raise HTTPException(status_code=401, detail="Geçersiz API anahtarı")
    
    try:
        success = server_manager.ban_player(request.player, request.reason or "")
        if success:
            return JSONResponse(content={"success": True})
        else:
            return JSONResponse(
                status_code=500,
                content={"success": False, "error": "Oyuncu yasaklanamadı"}
            )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    print(f"""
    ╔══════════════════════════════════════════════════════╗
    ║   Minecraft Sunucu Yönetim Sistemi Başlatılıyor    ║
    ╚══════════════════════════════════════════════════════╝
    
    🌐 Web Arayüzü: http://localhost:{API_PORT}
    📡 API: http://localhost:{API_PORT}/api
    🎮 Sunucu: {SERVER_HOST}:{SERVER_PORT}
    
    Çıkmak için Ctrl+C tuşlarına basın.
    """)
    
    uvicorn.run(app, host="0.0.0.0", port=API_PORT)

