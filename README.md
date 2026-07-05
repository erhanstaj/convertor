# Kurumsal XML Otomasyon ve Mimari Analiz Aracı
**(Enterprise XML Aggregator & Architecture Analyzer)**

Bu araç, gömülü yazılım sistemleri (DDS, ROS vb.) için karmaşık JSON haberleşme paketlerini standartlaştırılmış XML şemalarına dönüştüren; aynı zamanda eski (legacy) XML sistemleriyle akıllı kıyaslama (Diff Analysis) yaparak **veri kayıplarını, tip uyuşmazlıklarını ve mimari değişiklikleri** Linter (SonarQube) seviyesinde raporlayan kurumsal bir otomasyon yazılımıdır.

---

## Temel Özellikler (Features)

- **Veri Kümeleme (Data Aggregation):** Aynı `groupName`'e sahip farklı JSON dosyalarını zekice birleştirir. Ortak değişkenlerde tekrara (duplicate) düşmez, farklı olanları tek bir Master XML altında harmanlar.
- **Akıllı Kıyaslama (Smart Analyzer):** Üretilen yeni XML ile eski sistemdeki XML'i Set (Küme) teorisiyle karşılaştırır. Kayıp verileri (Kritik), Tip değişimlerini (Uyarı) ve Yeni eklenen verileri (İyileştirme) anında bulur.
- **HTML ve Terminal Raporlama:** Yöneticiler ve CI/CD süreçleri için renk kodlu, okunabilir HTML raporları üretir.
- **Config-Driven Mimari:** Sistemin isimlendirme kuralları (`msg` ön ekini silme vb.) ve dosya yolları koda gömülü değildir. `company_rules.json` dosyasından dinamik olarak yönetilir. Koda dokunmadan şirket standartları değiştirilebilir.
- **Çoklu Çalışma Modu:** Hem şık bir Masaüstü Arayüzü (PyQt6 Dark Mode) hem de CI/CD sunucuları için Arayüzsüz (Headless) mod barındırır.

---

## Kurulum (Installation)

Sistemi kaynak kodundan çalıştırmak istiyorsanız aşağıdaki adımları izleyin:

### Gereksinimler
- Bilgisayarınızda **Python 3.10 veya üzeri** bir sürüm kurulu olmalıdır.
- Sadece masaüstü arayüzü (GUI) için dış kütüphane gereklidir.

Terminali açın ve gerekli kütüphaneyi indirin:
```bash
pip install PyQt6

### Nasıl Çalıştırılır

1.Terminalde çalıştırma yöntemi
python gui.py

2.Arayüzsüz (Headless / Script) Modda Çalıştırma
python main.py

3.Docker ile Çalıştırma (CI/CD Süreçleri)
Bilgisayara Python kurmadan, izole bir Linux sunucusunda (Jenkins/GitLab) otomasyonu tetiklemek için:
docker-compose up --build

4.EXE Olarak Nasıl Derlenir? (Build Instructions)
python -m PyInstaller --onefile --windowed --name KurumsalXmlAraci gui.py

### Yazılımcı Notu
Bu sistem SOLID prensiplerine sadık kalınarak modüler (core, helpers, interfaces) bir yapıda kurgulanmıştır. Sistem JSON dosyalarını metin olarak manipüle etmez; AST (Abstract Syntax Tree) benzeri bir sözlüğe dönüştürür. İleride C++ veya ROS2 formatlarına dönüşüm gerekirse, IConverter arayüzünden yeni bir sınıf türetilmesi yeterlidir.
