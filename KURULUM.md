# Kurulum ve ilk kullanım

## Varsayım

Öğrencilerin cihazları bilinmiyor. **PLANLAMA VARSAYIMI:** Windows 10/11 veya güncel macOS, 64 bit Python **3.12**, modern tarayıcı, ilk kurulumda internet ve yazılabilir bir klasör. Yönetici yetkisi gerekli olmayacak şekilde yerel sanal ortam kullanılır. Telefon/WhatsApp içinde uygulama çalışmaz; ZIP bilgisayara indirilip açılır. Donanım alt sınırı ölçülmedi; GPU veya özel bir “yangın işlemcisi” gerekmez. Program Python ile CPU üzerinde çalışır.

Bu teslim macOS 26.7 / arm64 / Python 3.12.14 ortamında test edildi. Windows ve Linux test edilmedi. Bağımlılıkların o işletim sistemindeki kurulumu ilk kullanıcı denemesinde doğrulanmalıdır.

## Windows - adım adım

1. ZIP'e sağ tıklayın, **Tümünü ayıkla** seçeneğiyle örneğin `C:\FocusTM` altına çıkarın. İçte `app.py` bulunan `focustm_fire_v1_1` klasörünü açın. ZIP'in içinden çalıştırmayın.
2. Python 3.12'nin 64 bit kurulumunu [resmî Python Windows sayfasından](https://www.python.org/downloads/windows/) edinin. Python Launcher (`py`) seçeneğini kurun. Mevcut Python'u kaldırmayın. Yeni bir **Komut İstemi (cmd)** açın.
3. `app.py` dosyasının bulunduğu klasöre geçin. Örnek:

```bat
cd /d C:\FocusTM\focustm_fire_v1_1
py -3.12 --version
py -3.12 -m venv .venv
.venv\Scripts\python.exe -m pip install -r requirements.txt
.venv\Scripts\python.exe -m streamlit run app.py
```

4. Terminalde görülen `http://127.0.0.1:8501` adresini tarayıcıda açın. Terminal açık kalmalı. İşiniz bitince Ctrl+C.
5. Sonraki çalıştırmalarda yalnız `CALISTIR_WINDOWS.bat` dosyasını çift tıklayın. İlk kurulum için `KUR_WINDOWS.bat` yukarıdaki sanal ortam ve paket adımlarını yapar; dosyayı inceleyerek çalıştırabilirsiniz.

Komutlar cmd içindir; PowerShell etkinleştirme politikası değiştirmek gerekmez, çünkü `.venv\Scripts\python.exe` doğrudan kullanılır. `py` bulunamazsa Python Launcher kurulumunu kontrol edin; başka sistem dosyalarını değiştirmeyin.

## macOS - adım adım

1. ZIP'i açın; `app.py` bulunan klasörü örneğin Belgeler altına taşıyın.
2. [Resmî Python macOS sayfasından](https://www.python.org/downloads/macos/) Python 3.12'yi kurun veya mevcut 3.12 kurulumunu kullanın. Sistem Python 3.9 ile bu sabitlenmiş bağımlılıklar hedeflenmez.
3. Terminal açın. `cd ` yazıp proje klasörünü Terminal'e sürükleyerek yolu ekleyin, Enter'a basın. Ardından:

```bash
python3.12 --version
python3.12 -m venv .venv
.venv/bin/python -m pip install -r requirements.txt
.venv/bin/python -m streamlit run app.py
```

4. Tarayıcıda `http://127.0.0.1:8501` adresini açın. Sonraki çalıştırma: `bash calistir_mac.sh`. İlk kurulum yardımcı komutu: `bash kur_mac.sh`.

macOS'taki gerçek test, hazır Python 3.12.14 ortamında yapıldı. Resmî yükleyiciyle sıfırdan işletim sistemi kurulum akışı ve Intel Mac üzerinde test yapılmadı.

## İlk demo - 3 dakika

1. Tüm veri açıkken 29.640 tespit görünür. Bu sayının yangın olayı sayısı olmadığını açıklayın.
2. Sensör ailesi MODIS; platform yalnız Aqua; başlangıç 01/07/2021, bitiş 31/07/2021 seçin. **426** tespit görünmeli.
3. Aynı tarihlerde VIIRS / Suomi-NPP seçin. **2.268** tespit görünmeli. Sayıları aynı algılama ölçeğinde kabul etmediğinizi belirtin.
4. Takvimde boş hücrelerin sıfır yangın olmadığını gösterin. 2026 kısmi yıl uyarısını açıklayın.
5. “Tespitler ve indirme” sekmesinden CSV'yi indirin. Kaynak ZIP, üye ve satır izini gösterin. JSON seçimi tekrar kurmak için filtreleri ve ham ZIP özetlerini içerir.
6. “Yöntem ve kaynaklar” sekmesindeki deney sonucunu okuyun: doğrulanmış uyumlaştırma yok; sensörler ayrı tutuluyor.

## Veri hattını ve testleri çalıştırma

Windows:

```bat
.venv\Scripts\python.exe pipeline.py
.venv\Scripts\python.exe -m pip install -r requirements-dev.txt
.venv\Scripts\python.exe -m pytest -q
.venv\Scripts\python.exe scripts\verify_sources.py
```

macOS:

```bash
.venv/bin/python pipeline.py
.venv/bin/python -m pip install -r requirements-dev.txt
.venv/bin/python -m pytest -q
.venv/bin/python scripts/verify_sources.py
```

## Sorun giderme

- `ModuleNotFoundError`: paketleri uygulamayı çalıştırdığınız aynı `.venv` Python'u ile kurun.
- Paket indirememe: internet/proxy kısıtını okulun sistem sorumlusuyla kontrol edin. İlk bağımlılık kurulumu internet gerektirir; ZIP kütüphaneleri içermez.
- Port dolu: `... -m streamlit run app.py --server.port 8502` çalıştırıp terminaldeki yeni adresi açın.
- Türkçe CSV karakterleri/kolonları: Excel'de Veri > Metin/CSV'den, UTF-8 ve virgül ayırıcı seçin. CSV UTC sütunu metin olarak korunabilir.
- Boş ekran veya seçim sonucu yok: terminal hata mesajını okuyun; tarih sırasını, platform seçimini ve koordinatları kontrol edin. Kayıt yokluğu hata veya sıfır yangın kanıtı olmayabilir.
- İşlenmiş CSV eksik: önce `python pipeline.py` çalıştırın.
- Yavaş ilk açılış: CSV ilk kez belleğe okunur. Aynı oturumda sonraki filtreler daha hızlıdır. Bu veri boyutu için veritabanı gerekmiyor.

Sistem yalnız 127.0.0.1'e bağlanır. Kurulumdan sonra temel veri ve grafik işlevleri yereldir; NASA bağlantılarını açmak internet gerektirir. Canlı internet yayını ve mobil uygulama dağıtımı bu teslimin kapsamında değildir.

## v1.1 ek özellikleri

Harita altlıksız açılır; yol/kıyı çizmez. OpenStreetMap internet ister, WebGL2 destekli tarayıcı gerekir. Harita çalışmazsa koordinatlı CSV/GeoJSON kullanın. Ağ tamamen kapalı senaryo ve Windows test edilmedi. Yeni Python bağımlılığı eklenmedi. Aynı ay karşılaştırması yan menüdeki tarihlerin yıllarını kullanır; tam UTC ayları karşılaştırır. Gün/ay kesmeleri yalnız ana toplam, harita ve tespit indirmesine uygulanır.
