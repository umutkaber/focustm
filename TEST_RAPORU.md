# FocusTM test ve doğrulama raporu

14/11/2026 · Yerel ortam: macOS-26.7-arm64-arm-64bit; Python 3.12.14.

**v1.1 otomatik sonuç:** 35 test, 0 hata/başarısızlık, 0 atlanan test (26,37 saniye). Eski 25 test değiştirilmedi; 10 ek kontrol eklendi. Komut: `python -m pytest -q --junitxml=reports/test_results.xml`. Ayrıntılar reports/pytest_output.txt ve XML'de.

| Kontrol | Sonuç |
|---|---|
| UTC, HHMM baştaki sıfır, artık gün, bozuk saat | Geçti |
| Dikdörtgen sınırları dahil, kutu dışı engeli, tarih sırası | Geçti |
| Bütün CSV/JSON/Shapefile kopyaları ve aynı ZIP'i iki kez ekleme | 29.640 tespit değişmedi |
| Beş platform ayrımı; ham SNPP etiketi | Geçti |
| Boş ay NA, NRT type eksik, kısmi 2026 | Geçti |
| CSV UTF-8 BOM, UTC ve boş sonuç başlıkları | Geçti |
| Ham CSV'deki 825 platform-ay grubuyla eşitlik | Tam eşleşme |
| Bütün 29.640 satırın tercih edilen ham CSV satırına izi | Geçti |
| Eğitim/test ayrımı; test değişince eğitim katsayısının sabitliği | Geçti |
| Geçersiz satırın denetim kaydı; çelişen gözlemde durma | Geçti |
| Streamlit AppTest: açılış, filtre, boş seçim, yanlış tarih/kutu | Geçti |
| Gerçek yerel tarayıcı: açılış, MODIS/Aqua ve Temmuz 2021 | Ekranda 426 tespit |
| Gerçek tarayıcıdan CSV indirme | Dosya açıldı; 426 Aqua satırı, yalnız 2021-07, UTC, BOM doğrulandı |

Tarayıcı kanıtları: reports/browser_check.json, browser_download_Aqua_2021_07.csv, uygulama_genel.png ve uygulama_takvim.png. Son arayüzde tek ay seçiminin eksen biçimi iyileştirildi; standart takvim yeniden açılarak görsel kontrol yapıldı.

**Test edilmedi:** Windows, Linux, Intel Mac, resmî Python yükleyicisiyle sıfırdan kurulum, çok kullanıcılı internet yayını, mobil cihaz, ekran okuyucuyla kapsamlı erişilebilirlik denetimi, bağımsız yangın yer doğrulaması, bulut/geçiş kapsamı ve canlı NASA API akışı. Bunlar başarı olarak sunulmaz.

İlk ağ/yerel port girişimleri çalışma ortamının sandbox kısıtına takıldı; izinli proje paket kurulumu ve yalnız 127.0.0.1 yerel sunucuyla test tamamlandı. Kodun gerçek analitik verisi yalnız sağlanan ZIP'lerden geldi. Test sınır örnekleri üretim verisine katılmadı.

PDF okunabilirliği, yeniden üretim ve son paket bütünlük kontrolleri ayrıca reports/pdf_qa.json, reports/reproducibility.json ve paket SHA-256 dosyasıyla belgelenir.

Son görsel düzeltme: dar tarayıcıda kısalan dört özet kutusu iki sütun/iki satıra alındı. 29.640, 1.332 ve 09/11/2026 değerleri tam görünür olarak tarayıcıda doğrulandı. Değişiklikten sonra iki Streamlit AppTest testi yeniden geçti; kanıt reports/app_final_check.txt.

## v1.1 ek kontrolleri

- Değişiklikten önce v1'de 25 test (19,59 s), mevcut ZIP'in yeni çıkarılan kopyasında 2 AppTest (2,48 s) geçti. 29.640 ve 426 korundu.
- GeoJSON: 426 Point, boylam/enlem, kaynak kimliği, UTC, eksik type=null, boş FeatureCollection ve geçersiz koordinat reddi.
- Harita: bütün seçili noktalar, sensör/platform etiketi, kapalı çalışma kutusu, seçili alt kutu, beyaz/OSM stili ve boş seçim.
- Ortak renk: platformlar arasında aynı üst sınır; doğrusal ve log ölçeği.
- Karşılaştırma: Aqua Temmuz 2018-2026 her yılı bağımsız ham CSV sayımına eşit; eksik aylar NA, NRT filtresi ve 2026 bayrağı korundu.
- Gerçek tarayıcı (v1.1): 29.640 -> MODIS 4.600 -> Aqua/Temmuz 2021 426; altlıksız ve OSM harita çizildi; aynı ay grafiği açıldı.
- Gerçek indirme: 426 satır CSV ve 426 Point GeoJSON dosyaları yeniden okundu. CSV v1 örneğiyle bayt düzeyinde aynı; GeoJSON koordinat/platform/kaynak izi CSV ile eşleşti.
- Yeni kanıt: reports/browser_v11.json, browser_Aqua_2021_07.csv/.geojson, harita_altliksiz.png, harita_osm.png, ay_karsilastirma.png ve indirme_v11.png.

Ek sınırlar: ağ tamamen kapatılarak çalıştırma, bütün WebGL2 tarayıcıları, QGIS/ArcGIS içe aktarımı, Windows kurulumu ve kapsamlı performans/yük testi yapılmadı. OSM hizmet erişimi garanti edilmez. Eski ekran kanıtları v1 geçmişi olarak korunur.
