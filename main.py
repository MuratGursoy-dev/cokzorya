import sys
import veritabani as db
from PyQt5.QtWidgets import QApplication, QMainWindow, QDialog, QMessageBox, QPushButton
from PyQt5.QtGui import QIntValidator
from PyQt5.QtCore import QTimer
from PyQt5 import uic
from datetime import datetime 

class AyarlarPenceresi(QDialog):
    def __init__(self, ana_ekran):
        super().__init__()
        try:
            uic.loadUi("ayarlar.ui", self)
            self.ana_ekran = ana_ekran #kanka burda ayarları actıgın zaman güncel verilere ulasması ıcın yazdık
            self.kutulari_doldur()
            self.btn_ayar_kaydet.clicked.connect(self.kaydet) #kaydet butonuna bastıgımızda kaydet fonksıyonubu çalıştır
        except Exception as e: print(f"Ayarlar UI Hatası: {e}")

    def kutulari_doldur(self):
        f = self.ana_ekran.fiyatlar
        self.txt_normal_ucret.setText(str(f.get("normal_ucret", 50.0))) #VERİ TABANINDA Bİ DEĞER OLMADGIĞI İÇİN VARSAYILAN DEĞERİ ATADIK.
        self.txt_uye_ucret.setText(str(f.get("uye_ucret", 40.0))) #AYNISI
        self.txt_ucret_vip.setText(str(f.get("ucret_vip", 100.0)))
        self.txt_ucret_vip_uye.setText(str(f.get("ucret_vip_uye", 80.0)))
        self.txt_ucret_vip.setText(str(f.get("ucret_vip", 100.0)))
        self.txt_fiyat_cay.setText(str(f.get("fiyat_cay", 10)))
        self.txt_fiyat_kahve.setText(str(f.get("fiyat_kahve", 25)))
        self.txt_fiyat_tost.setText(str(f.get("fiyat_tost", 50)))
        self.txt_fiyat_kola.setText(str(f.get("fiyat_kola", 30)))

    def kaydet(self):
        try:
            yeni = {
                "normal_ucret": float(self.txt_normal_ucret.text()),
                "uye_ucret": float(self.txt_uye_ucret.text()),
                "fiyat_cay": int(self.txt_fiyat_cay.text()),
                "fiyat_kahve": int(self.txt_fiyat_kahve.text()),              #BURDA AYARLAR PENCERİSİNE GİRDİGİMİZ YENİ DEGERLERİ KAYIT EYLİYORUZ.
                "fiyat_tost": int(self.txt_fiyat_tost.text()),
                "fiyat_kola": int(self.txt_fiyat_kola.text()),
                "txt_ucret_vip": float(self.txt_ucret_vip.text()),
                "txt_ucret_vip_uye": float(self.txt_ucret_vip_uye.text())
            }

            db.ayarlari_guncelle(yeni) #VERİTABANINA KAYIT EYLIYORUZ.
            self.ana_ekran.fiyatlar = yeni #ANLIK AÇIK OLAN PROGRAMI DA GÜNCEL TUTUYORUZ.
            QMessageBox.information(self, "YAA SEN BİTANESİNN", "Fiyatlar güncellendi.")
            self.close()
        except ValueError: 
            QMessageBox.warning(self, "HAYIR Bİ YANLIŞLIK VAR", "Lütfen kutulara sadece SAYI giriniz.")


class SiparisEklePenceresi(QDialog):
    def __init__(self, ana_ekran):
        super().__init__()
        try:
            uic.loadUi("siparis_ekle.ui", self)#burda siprais ekle.ui yi tanıttık 
            self.ana_ekran = ana_ekran   #güncelledik
            self.acik_masalari_yukle()
            
            f = self.ana_ekran.fiyatlar
            self.btn_cay.clicked.connect(lambda: self.siparis_ver("Çay", f.get("fiyat_cay", 10)))
            self.btn_kahve.clicked.connect(lambda: self.siparis_ver("Kahve", f.get("fiyat_kahve", 25))) #AYARLARDAN AYARLADIGIMIZ GÜNCEL FİYATI ÇEKİYORUZ.
            self.btn_tost.clicked.connect(lambda: self.siparis_ver("Tost", f.get("fiyat_tost", 50)))
            self.btn_kola.clicked.connect(lambda: self.siparis_ver("Kola", f.get("fiyat_kola", 30)))
            
            if hasattr(self, "btn_kapat"):
                self.btn_kapat.clicked.connect(self.close)
        except Exception as e: print(f"Sipariş UI Hatası: {e}")

    def acik_masalari_yukle(self):   #acık masaları yukleyen fonksıyonumuz
        self.cmb_masalar.clear()
        if len(self.ana_ekran.acik_masalar) == 0:
            self.cmb_masalar.addItem("Açık Masa Yok!")
            self.setEnabled(False)
            if hasattr(self, "btn_kapat"): self.btn_kapat.setEnabled(True)
            return
        
        self.setEnabled(True)
        for buton in self.ana_ekran.acik_masalar:
            ham_isim = buton.objectName()
            temiz_isim = ham_isim.replace("btn_", "").replace("_", " ").upper()  #BURDA COMBOBOXTAKİ BTN MASA1 İ SAKLIYORUZ YPYZKA
            self.cmb_masalar.addItem(temiz_isim, userData=ham_isim) 

    def siparis_ver(self, urun_adi, fiyati):
        if self.cmb_masalar.currentText() == "Açık Masa Yok!": return
        
        secilen_index = self.cmb_masalar.currentIndex()
        hedef_masa_adi = self.cmb_masalar.itemData(secilen_index)
        
        hedef_buton = None
        for buton in self.ana_ekran.acik_masalar:
            if buton.objectName() == hedef_masa_adi:
                hedef_buton = buton
                break
        
        if hedef_buton:
            self.ana_ekran.acik_masalar[hedef_buton]["ekstra"] += fiyati
            self.ana_ekran.saat_guncelle(hedef_buton, hedef_masa_adi)
            toplam = self.ana_ekran.acik_masalar[hedef_buton]["ekstra"]
            self.lbl_sonuc.setText(f"{urun_adi} Eklendi! (+{fiyati} TL)\nMasa Toplam Ekstra: {toplam} TL")

class UyeGirisPenceresi(QDialog):
    def __init__(self):
        super().__init__()
        try:
            uic.loadUi("uye_giris.ui", self)
            self.giris_basarili = False  #BUNU TRUE YAPIP YAPMADIGINI SORCAZ DBYE KONTROL ET KKISMINA GIDIYORUZ.
            self.btn_giris_yap.clicked.connect(self.kontrol_et) #FONKSIYONA BAGLADIK.
        except Exception: pass

    def kontrol_et(self):
        durum, mesaj = db.uye_kontrol(self.txt_tel.text(), self.txt_sifre.text())
        if durum:
            QMessageBox.information(self, "Oturum Açıldı.", f"Hoşgeldiniz {mesaj}!")
            self.giris_basarili = True  #Başarılı ise true yaptık.
            self.close()
        else:
            QMessageBox.warning(self, "Telefon numarası veya şifre hatalı.", mesaj)

class MasaDetayPenceresi(QDialog):
    def __init__(self):
        super().__init__()
        try:
            uic.loadUi("masa_detay.ui", self)
            self.sonuc = None 
            self.btn_normal.clicked.connect(lambda: self.secim_yap("Normal"))
            self.btn_uye.clicked.connect(self.uye_secildi)
        except Exception: pass

    def secim_yap(self, tur):
        secilen = "PS4" 
        self.sonuc = {"musteri_tipi": tur, "cihaz_tipi": secilen}
        self.close()

    def uye_secildi(self):
        p = UyeGirisPenceresi()
        p.exec_() 
        if p.giris_basarili: self.secim_yap("Uye")

class UyeKayitPenceresi(QDialog):
    def __init__(self):
        super().__init__()
        try:
            uic.loadUi("uye_kayit.ui", self)
            self.txt_yeni_ad.setMaxLength(20) #max uzunlugu verdık
            self.txt_yeni_tel.setValidator(QIntValidator()) #sadece sayı olaacak dedık
            self.txt_yeni_tel.setMaxLength(11) #tel numarasının hanesını verdık
            self.btn_kaydet.clicked.connect(self.kayit_ol)
        except Exception: pass

    def kayit_ol(self):
        if len(self.txt_yeni_ad.text()) < 3 or len(self.txt_yeni_tel.text()) < 10:
             QMessageBox.warning(self, "Kayıt Yapılamadı.", "İsim çok kısa veya telefon eksik!")#anlatmama gerek yok herhalde
             return
        try:
            db.uye_ekle(self.txt_yeni_ad.text(), self.txt_yeni_tel.text(), self.txt_yeni_sifre.text())
            QMessageBox.information(self, "Üye Kaydı Başarılı.", "Yeni üye kaydedildi!")
            self.close()
        except Exception as e:
            QMessageBox.warning(self, "Hata", f"Kayıt hatası: {e}")

class AdminGirisPenceresi(QDialog):
    def __init__(self):
        super().__init__()
        try:
            uic.loadUi("admin_giris.ui", self)
            self.setFixedSize(400, 300) # Pencere boyunu sabitledik
            self.btn_giris.clicked.connect(self.giris_yap)
        except Exception as e: 
            print(f"Admin UI Hatası: {e}")

    def giris_yap(self):
        kadi = self.txt_kadi.text()
        sifre = self.txt_sifre.text()
        
        if db.admin_kontrol(kadi, sifre):
            self.accept() # Pencereyi "Onaylandı" diyerek kapatır
        else:
            QMessageBox.warning(self, "ÇOK ZOR YAAA!", "Kullanıcı adı veya şifre yanlış!\n(admin / 1234)")

class AnaEkran(QMainWindow):
    def __init__(self):
        super().__init__()
        try: uic.loadUi("ana_ekran.ui", self)
        except Exception as e: 
            QMessageBox.critical(self, "Hata", f"Tasarım hatası: {e}")
            return
        self.acik_masalar = {} 
        self.fiyatlar = db.ayarlari_getir()

        tum_elemanlar = self.findChildren(QPushButton)
        for buton in tum_elemanlar:
            isim = buton.objectName()
            if isim.startswith("btn_masa") or isim.startswith("btn_vip"):
                buton.clicked.connect(lambda checked, b=buton: self.masa_islemleri(b))
        
        try:
            self.btn_uye_kayit.clicked.connect(lambda: UyeKayitPenceresi().exec_())
            self.btn_siparis_ekle.clicked.connect(lambda: SiparisEklePenceresi(self).exec_())
            self.btn_ayarlar.clicked.connect(lambda: AyarlarPenceresi(self).exec_())
        except AttributeError: pass

    def masa_islemleri(self, tiklanan_buton):
        masa_adi = tiklanan_buton.objectName()
        
        #MASA KAPATMA
        if tiklanan_buton in self.acik_masalar:
            masa = self.acik_masalar[tiklanan_buton]
            _, saat_ucret, ekstra, toplam = self.hesapla(masa, masa_adi)
            
            bilgi = f"Süre Ücreti: {saat_ucret:.2f} TL\nEkstra (Yiyecek): {ekstra:.2f} TL\n------------------\nTOPLAM: {toplam:.2f} TL"
            
            if QMessageBox.question(self, "Hesap Kes", bilgi + "\n\nMasa kapatılsın mı?", QMessageBox.Yes|QMessageBox.No) == QMessageBox.Yes:
                masa["timer"].stop()
                del self.acik_masalar[tiklanan_buton]
                tiklanan_buton.setStyleSheet("") 
                temiz_isim = masa_adi.replace("btn_", "").replace("_", " ").upper()
                tiklanan_buton.setText(temiz_isim)
            return

        #MASA ACMA
        pencere = MasaDetayPenceresi()
        pencere.exec_()
        
        if pencere.sonuc:
            t = QTimer()
            t.timeout.connect(lambda: self.saat_guncelle(tiklanan_buton, masa_adi))
            t.start(1000)
            
            self.acik_masalar[tiklanan_buton] = {
                "timer": t, 
                "baslangic": datetime.now(), 
                "tarife": pencere.sonuc["musteri_tipi"], 
                "ekstra": 0.0
            }
            
            if "vip" in masa_adi:
                stil = "background-color: #ffd700; color: black; border: 2px solid #ffffff;"
            else:
                stil = "background-color: #00d2ff; color: black; border: 2px solid #ffffff;"
            
            tiklanan_buton.setStyleSheet(f"{stil} font-weight: bold; font-size: 14px;")

    def saat_guncelle(self, buton, masa_adi):
        if buton not in self.acik_masalar: return
        _, saat_ucret, ekstra, toplam = self.hesapla(self.acik_masalar[buton], masa_adi)
        buton.setText(f"DOLU\n{toplam:.1f} TL")

    def hesapla(self, masa_bilgisi, masa_adi):
        gecen = datetime.now() - masa_bilgisi["baslangic"]
        dakika = gecen.total_seconds() / 60
        saat_suresi = dakika / 60 
        
        if "vip" in masa_adi.lower():
            if masa_bilgisi["tarife"] == "Uye":
                baz_fiyat = self.fiyatlar.get("ucret_vip_uye", 80.0) 
            else:
                baz_fiyat = self.fiyatlar.get("ucret_vip", 100.0) 
        else:
            baz_fiyat = self.fiyatlar.get("normal_ucret", 50.0) 
            if masa_bilgisi["tarife"] == "Uye":
                baz_fiyat = self.fiyatlar.get("uye_ucret", 40.0) 

        saat_ucreti = saat_suresi * baz_fiyat
        ekstra = masa_bilgisi["ekstra"]
        return gecen, saat_ucreti, ekstra, saat_ucreti + ekstra

if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyleSheet("""
        QMessageBox { background-color: #0f0c29; }
        QMessageBox QLabel { color: #ffffff; font-size: 14px; font-weight: bold; }
        QMessageBox QPushButton { background-color: #1a1a2e; color: #00ff00; border: 2px solid #00ff00; border-radius: 10px; padding: 5px 15px; font-weight: bold; }
        QMessageBox QPushButton:hover { background-color: #00ff00; color: black; }
    """)#Burda mesaj kutalarının tipini ayarlattık.

    login_penceresi = AdminGirisPenceresi()
    
    if login_penceresi.exec_() == QDialog.Accepted:    # Eğer giriş başarılıysa Ana Ekranı aç
        ana_pencere = AnaEkran()
        ana_pencere.show()
        sys.exit(app.exec_())
    else:                                             # Giriş yapılmadan çarpıya basıldıysa programı kapat
        sys.exit()