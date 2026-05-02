# 🌐 Erişim Bilgileri

## Web Arayüzüne Erişim

Sunucu başlatıldıktan sonra aşağıdaki adreslerden erişebilirsiniz:

### Yerel Erişim (Aynı Bilgisayar)
- **Web Arayüzü:** http://localhost:8000
- **API:** http://localhost:8000/api

### Ağ Erişimi (Diğer Cihazlardan)
- **Web Arayüzü:** http://[BILGISAYAR_IP]:8000
- **API:** http://[BILGISAYAR_IP]:8000/api

Bilgisayarınızın IP adresini öğrenmek için:
```powershell
ipconfig
```
veya
```bash
ipconfig | findstr IPv4
```

## Erişim Sorunları ve Çözümleri

### 1. "Bağlanılamıyor" Hatası
**Çözüm:**
- Sunucunun çalıştığından emin olun
- `.env` dosyasında `API_PORT=8000` olduğunu kontrol edin
- Firewall'un 8000 portunu engellemediğinden emin olun

### 2. "Sunucuya bağlanılamadı" Hatası (RCON)
**Çözüm:**
- `.env` dosyasında `RCON_PASSWORD` değerini kontrol edin
- Minecraft sunucunuzun çalıştığından emin olun
- `server.properties` dosyasında RCON'un etkin olduğunu kontrol edin:
  ```
  enable-rcon=true
  rcon.port=25575
  rcon.password=your_password
  ```

### 3. Diğer Cihazlardan Erişemiyorum
**Çözüm:**
- Windows Firewall'da 8000 portunu açın:
  ```powershell
  New-NetFirewallRule -DisplayName "Minecraft API" -Direction Inbound -LocalPort 8000 -Protocol TCP -Action Allow
  ```
- `.env` dosyasında `CORS_ORIGINS=*` olduğundan emin olun
- Bilgisayarınızın IP adresini doğru kullandığınızdan emin olun

### 4. Port Zaten Kullanımda
**Çözüm:**
- Farklı bir port kullanın (örn: 8080)
- `.env` dosyasında `API_PORT=8080` yapın
- Sunucuyu yeniden başlatın

## Hızlı Test

Tarayıcınızda şu adresi açın:
```
http://localhost:8000
```

Eğer yönetim paneli görünüyorsa, her şey çalışıyor demektir! 🎉

## API Test

Terminal'de test edin:
```powershell
curl http://localhost:8000/api/status
```

veya tarayıcıda:
```
http://localhost:8000/api/status
```

## Sunucuyu Başlatma

```bash
python main.py
```

Sunucu başladığında şu mesajları göreceksiniz:
```
============================================================
Minecraft Sunucu Yönetim Sistemi Başlatılıyor...
============================================================
🌐 Web arayüzü: http://localhost:8000
📡 API: http://localhost:8000/api
============================================================
```

