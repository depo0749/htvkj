"""
Minecraft Sunucu Yönetim Modülü
RCON protokolü ile Minecraft sunucusuna bağlanır ve yönetim işlemleri yapar.
"""
import mcrcon
from typing import Optional, Dict, List
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class MinecraftServerManager:
    """Minecraft sunucusu için RCON bağlantı yöneticisi"""
    
    def __init__(self, host: str, port: int, password: str):
        """
        Args:
            host: Sunucu IP adresi veya hostname
            port: RCON port numarası (varsayılan: 25575)
            password: RCON şifresi
        """
        self.host = host
        self.port = port
        self.password = password
        self.connection: Optional[mcrcon.MCRcon] = None
    
    def connect(self) -> bool:
        """Sunucuya bağlan"""
        if not self.password:
            logger.warning("RCON şifresi belirtilmemiş!")
            return False
        
        try:
            self.connection = mcrcon.MCRcon(self.host, self.password, port=self.port)
            self.connection.connect()
            logger.info(f"Sunucuya başarıyla bağlanıldı: {self.host}:{self.port}")
            return True
        except ConnectionRefusedError:
            logger.error(f"Bağlantı reddedildi: {self.host}:{self.port} - Sunucu çalışıyor mu?")
            self.connection = None
            return False
        except TimeoutError:
            logger.error(f"Bağlantı zaman aşımı: {self.host}:{self.port} - Sunucu erişilebilir mi?")
            self.connection = None
            return False
        except Exception as e:
            logger.error(f"Bağlantı hatası: {str(e)}")
            self.connection = None
            return False
    
    def disconnect(self):
        """Sunucu bağlantısını kapat"""
        if self.connection:
            try:
                self.connection.disconnect()
                logger.info("Bağlantı kapatıldı")
            except:
                pass
            finally:
                self.connection = None
    
    def send_command(self, command: str) -> Optional[str]:
        """Sunucuya komut gönder"""
        if not command or not command.strip():
            logger.warning("Boş komut gönderilemez")
            return None
            
        if not self.connection:
            if not self.connect():
                logger.error("Sunucuya bağlanılamadı, komut gönderilemedi")
                return None
        
        try:
            response = self.connection.command(command)
            logger.info(f"Komut gönderildi: {command[:50]}...")
            return response
        except Exception as e:
            logger.error(f"Komut gönderme hatası: {str(e)}")
            # Bağlantı kopmuş olabilir, yeniden dene
            try:
                self.disconnect()
                if self.connect():
                    response = self.connection.command(command)
                    logger.info("Bağlantı yenilendi, komut tekrar gönderildi")
                    return response
            except Exception as retry_error:
                logger.error(f"Yeniden deneme hatası: {str(retry_error)}")
            return None
    
    def get_status(self) -> Dict:
        """Sunucu durumunu al"""
        try:
            # Önce bağlantıyı kontrol et
            if not self.connection:
                if not self.connect():
                    return {
                        "connected": False,
                        "host": self.host,
                        "port": self.port,
                        "error": "Sunucuya bağlanılamadı. Lütfen .env dosyasındaki ayarları kontrol edin."
                    }
            
            # TPS ve oyuncu sayısı için komutlar
            tps_response = self.send_command("tps")
            list_response = self.send_command("list")
            
            status = {
                "connected": self.connection is not None,
                "host": self.host,
                "port": self.port,
                "tps_info": tps_response if tps_response else "Bilinmiyor",
                "player_list": list_response if list_response else "Bilinmiyor"
            }
            return status
        except Exception as e:
            logger.error(f"Durum alma hatası: {str(e)}")
            return {
                "connected": False,
                "host": self.host,
                "port": self.port,
                "error": str(e)
            }
    
    def get_players(self) -> List[Dict]:
        """Oyuncu listesini al"""
        try:
            response = self.send_command("list")
            if not response:
                return []
            
            # "There are X of a max of Y players online: player1, player2"
            # formatını parse et
            players = []
            if "online:" in response:
                parts = response.split("online:")
                if len(parts) > 1:
                    player_names = parts[1].strip().split(", ")
                    for name in player_names:
                        if name.strip():
                            players.append({"name": name.strip()})
            
            return players
        except Exception as e:
            logger.error(f"Oyuncu listesi alma hatası: {str(e)}")
            return []
    
    def send_message(self, player: str, message: str) -> bool:
        """Oyuncuya mesaj gönder"""
        command = f"tell {player} {message}"
        response = self.send_command(command)
        return response is not None
    
    def broadcast_message(self, message: str) -> bool:
        """Tüm oyunculara mesaj gönder"""
        command = f"say {message}"
        response = self.send_command(command)
        return response is not None
    
    def kick_player(self, player: str, reason: str = "") -> bool:
        """Oyuncuyu at"""
        if reason:
            command = f"kick {player} {reason}"
        else:
            command = f"kick {player}"
        response = self.send_command(command)
        return response is not None
    
    def ban_player(self, player: str, reason: str = "") -> bool:
        """Oyuncuyu yasakla"""
        if reason:
            command = f"ban {player} {reason}"
        else:
            command = f"ban {player}"
        response = self.send_command(command)
        return response is not None
    
    def __enter__(self):
        """Context manager giriş"""
        self.connect()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager çıkış"""
        self.disconnect()

