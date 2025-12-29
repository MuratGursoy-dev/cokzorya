import pymongo
client = pymongo.MongoClient("mongodb://localhost:27017/")#baglantı
db = client["CafeOtomasyon"]

uyeler_tablosu = db["uyeler"]# Tablolar 
ayarlar_tablosu = db["ayarlar"]

def uye_ekle(ad, tel, sifre):
    uyeler_tablosu.insert_one({"ad": ad, "tel": tel, "sifre": sifre})

def uye_kontrol(tel, girilen_sifre):
    kisi = uyeler_tablosu.find_one({"tel": tel})
    
    if kisi:
        if kisi["sifre"] == girilen_sifre:
            return True, kisi["ad"] # Giriş Başarılı, Adını gönder
        else:
            return False, "Şifre Yanlış!"
    
    return False, "Böyle bir kullanıcı bulunamadı!"


def ayarlari_getir():
    ayar = ayarlar_tablosu.find_one({})
    
    #veritabanı boş oldugu ıcın varsayılanları oluştur
    if ayar is None:
        varsayilan = {
            "normal_ucret": 50.0,      
            "uye_ucret": 40.0,      
            "ucret_vip": 100.0,     
            "ucret_vip_uye": 80.0,  
            "fiyat_cay": 10, 
            "fiyat_kahve": 25, 
            "fiyat_tost": 50, 
            "fiyat_kola": 30
        }
        ayarlar_tablosu.insert_one(varsayilan)
        return varsayilan
    
    return ayar

def ayarlari_guncelle(yeni_veriler):
    eski = ayarlar_tablosu.find_one({}) # Önce mevcut ayarı bulalım ki ID'sini alabilelim
    
    if eski:
        ayarlar_tablosu.update_one({"_id": eski["_id"]}, {"$set": yeni_veriler})# Eski ID üzerinden güncelleme yapıyoruz
    else:
        ayarlar_tablosu.insert_one(yeni_veriler) # Eğer hiç yoksa yeni ekle

admin_tablosu = db["adminler"]

def admin_kontrol(kadi, sifre):  # Önce sistemde hiç admin yoksa varsayılan olusturduk
    if admin_tablosu.count_documents({}) == 0:
        admin_tablosu.insert_one({"kadi": "admin", "sifre": "1234"})
    
    # Şimdi kontrol edelim
    kisi = admin_tablosu.find_one({"kadi": kadi, "sifre": sifre})
    if kisi:
        return True
    return False