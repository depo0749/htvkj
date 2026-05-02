# Minecraft 1.21.11 Sunucu Yönetim Sistemi

Minecraft 1.21.11 sunucularınızı dışarıdan yönetebileceğiniz web tabanlı bir yönetim paneli.

## Özellikler

- 🌐 Web tabanlı yönetim arayüzü
- 🔌 RCON protokolü ile sunucu bağlantısı
- 📊 Sunucu durumu ve oyuncu bilgileri
- ⚡ Komut gönderme ve yönetim
- 🔒 Güvenli API erişimi (API Key ve IP whitelist desteği)
- 🌍 CORS desteği (cross-origin istekler için)
- 📱 Responsive tasarım
- 🔄 Otomatik bağlantı yenileme
- ⚙️ Gelişmiş hata yönetimi

## Kurulum

1. Bağımlılıkları yükleyin:
```bash
pip install -r requirements.txt
```

2. `.env` dosyasını oluşturun ve yapılandırın:
```
# Minecraft Sunucu Yapılandırması
SERVER_HOST=localhost
SERVER_PORT=25575
RCON_PASSWORD=your_rcon_password

# API Yapılandırması
API_PORT=8000

# Güvenlik Ayarları (Opsiyonel)
API_KEY=your_api_key_here
ALLOWED_IPS=127.0.0.1,::1

# CORS Ayarları
ENABLE_CORS=true
CORS_ORIGINS=*

# Loglama
LOG_LEVEL=INFO
```

3. Sunucuyu başlatın:
```bash
python main.py
```

4. Tarayıcınızda `http://localhost:8000` adresine gidin.

## Minecraft Sunucu Yapılandırması

`server.properties` dosyanızda şunları etkinleştirin:
```
enable-rcon=true
rcon.port=25575
rcon.password=your_secure_password
```

## API Kullanımı

### Sunucu Durumu
```
GET /api/status
```

### Komut Gönderme
```
POST /api/command
Body: {"command": "say Merhaba!"}
```

### Oyuncu Listesi
```
GET /api/players
```

### Mesaj Gönderme
```
POST /api/message
Body: {"player": "OyuncuAdı", "message": "Mesajınız"}
```

### Oyuncu Atma
```
POST /api/kick
Body: {"player": "OyuncuAdı", "reason": "Sebep (opsiyonel)"}
```

### Oyuncu Yasaklama
```
POST /api/ban
Body: {"player": "OyuncuAdı", "reason": "Sebep (opsiyonel)"}
```

## Güvenlik

### API Key Kullanımı
API key ayarlandığında, tüm API isteklerinde `X-API-Key` header'ı gönderilmelidir:
```
X-API-Key: your_api_key_here
```

### IP Whitelist
Sadece belirli IP adreslerinden erişime izin vermek için:
```
ALLOWED_IPS=192.168.1.100,10.0.0.50
```

### CORS Ayarları
Farklı domain'lerden erişim için:
```
ENABLE_CORS=true
CORS_ORIGINS=http://localhost:3000,https://example.com
```

## Lisans

MIT

