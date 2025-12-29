import pymongo

# --- BAĞLANTI AYARLARI ---
client = pymongo.MongoClient("mongodb://localhost:27017/")
db = client["CafeOtomasyon"]

# Tablolar (Collections)
uyeler_tablosu = db["uyeler"]
ayarlar_tablosu = db["ayarlar"]

# ============================================
# 1. ÜYE İŞLEMLERİ
# ============================================
def uye_ekle(ad, tel, sifre):
    # Aynı numara var mı diye bakmak iyi olur ama basit tutuyoruz
    uyeler_tablosu.insert_one({"ad": ad, "tel": tel, "sifre": sifre})

def uye_kontrol(tel, girilen_sifre):
    kisi = uyeler_tablosu.find_one({"tel": tel})
    
    if kisi:
        if kisi["sifre"] == girilen_sifre:
            return True, kisi["ad"] # Giriş Başarılı, Adını gönder
        else:
            return False, "Şifre Yanlış!"
    
    return False, "Böyle bir kullanıcı bulunamadı!"

# ============================================
# 2. AYAR İŞLEMLERİ (Fiyatlar vs.)
# ============================================
def ayarlari_getir():
    ayar = ayarlar_tablosu.find_one({})
    
    # Eğer veritabanı boşsa (İlk kurulum), varsayılanları oluştur
    if ayar is None:
        varsayilan = {
            "normal_ucret": 50.0,      # Normal Saatlik
            "uye_ucret": 40.0,      # Üye Saatlik (Normal)
            "ucret_vip": 100.0,     # VIP Normal
            "ucret_vip_uye": 80.0,  # VIP Üye
            "fiyat_cay": 10, 
            "fiyat_kahve": 25, 
            "fiyat_tost": 50, 
            "fiyat_kola": 30
        }
        ayarlar_tablosu.insert_one(varsayilan)
        return varsayilan
    
    # MongoDB "_id"yi de getirir, onu ayıklayıp gönderebiliriz ama
    # Main.py'de dict olarak kullandığımız için sorun olmaz.
    return ayar

def ayarlari_guncelle(yeni_veriler):
    # Önce mevcut ayarı bulalım ki ID'sini alabilelim
    eski = ayarlar_tablosu.find_one({})
    
    if eski:
        # Eski ID üzerinden güncelleme yapıyoruz
        ayarlar_tablosu.update_one({"_id": eski["_id"]}, {"$set": yeni_veriler})
    else:
        # Eğer hiç yoksa yeni ekle
        ayarlar_tablosu.insert_one(yeni_veriler)

# ============================================
# 3. ADMIN İŞLEMLERİ
# ============================================
admin_tablosu = db["adminler"]

def admin_kontrol(kadi, sifre):
    # Önce sistemde hiç admin var mı bakalım? Yoksa varsayılanı oluşturalım.
    if admin_tablosu.count_documents({}) == 0:
        admin_tablosu.insert_one({"kadi": "admin", "sifre": "1234"})
    
    # Şimdi kontrol edelim
    kisi = admin_tablosu.find_one({"kadi": kadi, "sifre": sifre})
    if kisi:
        return True
    return False