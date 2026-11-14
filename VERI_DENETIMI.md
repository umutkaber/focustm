# FocusTM veri denetimi - 14/11/2026

Karar: sensör bazlı prototip için GO; doğrulanmış birleşik seri için HOLD.

12 ZIP, 24 veri temsili, 8 mantıksal veri kümesi, 88.920 fiziksel satır kopyası. Normalize edilmiş tüm alanlar ve satır çoklukları karşılaştırıldı: CSV, JSON ve Shapefile 8/8 kümede eşit. Kopyalar çıkarılınca **29.640 tespit** kalır; 59.280 kopya yeniden sayılmaz. Reddedilen kayıt: 0. İlgi alanı dışında: 0. Birebir aynı gözlem anahtarında arşiv/NRT tekrar sayımı: 0.

## Tüm ZIP'ler

| ZIP | Biçim | Ham satır | Veri üyeleri |
|---|---|---|---|
| DL_FIRE_J1V-C2_847414.zip | shp | 9899 | fire_archive_J1V-C2_847414.shp; fire_nrt_J1V-C2_847414.shp |
| DL_FIRE_J1V-C2_847529.zip | csv | 9899 | fire_archive_J1V-C2_847529.csv; fire_nrt_J1V-C2_847529.csv |
| DL_FIRE_J1V-C2_847599.zip | json | 9899 | fire_archive_J1V-C2_847599.json; fire_nrt_J1V-C2_847599.json |
| DL_FIRE_J2V-C2_847415.zip | shp | 2579 | fire_archive_J2V-C2_847415.shp; fire_nrt_J2V-C2_847415.shp |
| DL_FIRE_J2V-C2_847530.zip | csv | 2579 | fire_archive_J2V-C2_847530.csv; fire_nrt_J2V-C2_847530.csv |
| DL_FIRE_J2V-C2_847600.zip | json | 2579 | fire_archive_J2V-C2_847600.json; fire_nrt_J2V-C2_847600.json |
| DL_FIRE_M-C61_847413.zip | shp | 4600 | fire_archive_M-C61_847413.shp; fire_nrt_M-C61_847413.shp |
| DL_FIRE_M-C61_847528.zip | csv | 4600 | fire_archive_M-C61_847528.csv; fire_nrt_M-C61_847528.csv |
| DL_FIRE_M-C61_847598.zip | json | 4600 | fire_archive_M-C61_847598.json; fire_nrt_M-C61_847598.json |
| DL_FIRE_SV-C2_847416.zip | shp | 12562 | fire_archive_SV-C2_847416.shp; fire_nrt_SV-C2_847416.shp |
| DL_FIRE_SV-C2_847531.zip | csv | 12562 | fire_archive_SV-C2_847531.csv; fire_nrt_SV-C2_847531.csv |
| DL_FIRE_SV-C2_847601.zip | json | 12562 | fire_archive_SV-C2_847601.json; fire_nrt_SV-C2_847601.json |

Shapefile ZIP'leri her arşiv ve NRT katmanı için .shp, .shx, .dbf, .prj, .cpg içerir. 4 Shapefile ZIP'inde 11'er üye, CSV/JSON ZIP'lerinde 3'er üye vardır (toplam 68 üye). PRJ: WGS84/EPSG:4326; CPG: UTF-8. Sekiz katmanın tüm nokta geometrileri DBF koordinatlarıyla karşılaştırıldı, uyumsuzluk yok. JSON kayıt dizisidir; GeoJSON değildir. Her ZIP'teki Readme.txt 89 bayttır ve NASA README bağlantısına yönlendirir.

## Tek kez sayılan sekiz veri kümesi

Tarihler ham kayıtlarda görülen ilk/son UTC tespit günüdür; kesintisiz kapsam değildir.

| Ürün | İşleme | Tespit | İlk gün | Son gün | Ham version |
|---|---|---|---|---|---|
| J1V-C2 | archive | 9530 | 2018-04-01 | 2026-07-31 | 2 |
| J1V-C2 | nrt | 369 | 2026-08-01 | 2026-11-09 | 2.0NRT |
| J2V-C2 | archive | 2150 | 2023-03-02 | 2026-07-31 | 2 |
| J2V-C2 | nrt | 429 | 2026-08-01 | 2026-11-09 | 2.0NRT |
| M-C61 | archive | 4488 | 2000-11-02 | 2026-08-29 | 6.03, 61.03 |
| M-C61 | nrt | 112 | 2026-09-06 | 2026-10-25 | 6.1NRT |
| SV-C2 | archive | 12140 | 2012-01-20 | 2026-07-31 | 2 |
| SV-C2 | nrt | 422 | 2026-08-01 | 2026-10-29 | 2.0NRT |

## Sütunlar

Arşivde 15 alan: latitude, longitude, brightness, scan, track, acq_date, acq_time, satellite, instrument, confidence, version, bright_t31, frp, daynight, type.

NRT'de aynı alanlar type hariç 14 sütun. Shapefile alan adları büyük harftir; CSV/JSON küçük harftir. Veri türleri ve tüm sütun listeleri reports/file_inventory.csv içindedir. NRT türü boş/NA korunur. Suomi-NPP ham instrument=SNPP etiketi değiştirilmeden instrument_raw alanına alınır, sensor=VIIRS üretilir. MODIS 6.03 ve 61.03 sürümleri korunur; dışa aktarımın tarihsel işleme sürümü açıklaması DOĞRULANAMADI.

## Bölge ve kapsam

Batı=29.5, güney=36.1, doğu=32.8, kuzey=37.5. Antalya idari sınırı değildir. 2000-01–2026-12 takviminde 5 platform için 1.620 platform-ay hücresi bulunur: 825'inde kayıt, 795'inde NA vardır. NA hücrelerinin bir bölümü platform başlamadan önce veya son kayıt sonrasındadır; bir bölümü kayıt aralığı içindeki boş aylardır. Bu toplam gözlem kaybı oranı değildir.

ZIP'ler geçerli gözlem sayısı, bulut maskesi, geçiş çizelgesi, tam indirme isteği kapsamını içermez. Bunlar DOĞRULANAMADI. Bütün aylarda coverage_verified=False. 2026 kısmi; son tespit 09/11/2026. Tür=2 sabit kaynak tespitleri MODIS'te 363, VIIRS'te 6.273; bunlar kayıttaki sınıflardır ve bağımsız yer doğrulaması değildir.

## Deney sonucu

| Hedef | Güven | Eğitim ayı | Test ayı | k | Test MAE | Mevsimsel MAE |
|---|---|---|---|---|---|---|
| Suomi-NPP | all | 102 | 44 | 0.191690 | 5.729 | 3.386 |
| NOAA-20 | all | 55 | 34 | 0.167310 | 4.827 | 4.250 |
| NOAA-21 | all | 22 | 11 | 0.108011 | 3.775 | 4.227 |
| Suomi-NPP | screened | 100 | 44 | 0.204950 | 5.914 | 3.307 |
| NOAA-20 | screened | 55 | 34 | 0.178099 | 4.924 | 4.044 |
| NOAA-21 | screened | 22 | 11 | 0.108268 | 3.777 | 4.045 |

MAE birimi Aqua tespit kaydı/aydır; algılama doğruluk yüzdesi değildir. Model yalnız ortak pozitif arşiv aylarında, eğitim/test yılları ayrılarak sınandı. Eksik aylar dışlandığından seçilim yanlılığı vardır. S-NPP ve NOAA-20 mevsimsel temel modelden kötü; NOAA-21'in testi kısa (11 ay). Katsayılar doğrulanmış sayılmaz ve takvimde kullanılmaz. Ayrıntı docs/YONTEM.md.

## Eksik bilgiler ve resmî kaynak çelişkileri

Tam indirme isteği; bulutsuz gözlem kapsamı; bağımsız olay envanteri; tür düzeltmesi uygulama geçmişi; MODIS version yorumunun ayrıntısı ve resmî 2026 yarışma/AI kuralları DOĞRULANAMADI. NASA README, indirme sayfası ve bazı sensör açıklamalarında başlangıç ve NRT arşive geçiş bilgilerinin farklılaştığı görüldü. Kaynakların hangisinin hangi iddiayı taşıdığı docs/KAYNAKLAR.md'de açıklandı.

## Ham veriyle kontrol

825 platform-ay grubunun tamamı Python standart kütüphanesiyle doğrudan ham CSV'lerden yeniden sayılıp işlenmiş verilerle eşleştirildi. Örnek: Temmuz 2021 Aqua 426, Terra 364, S-NPP 2.268, NOAA-20 2.580. Her işlenmiş satır kaynak CSV satırına geri izlenebilir. Kanıt: reports/raw_crosscheck.json, reports/provenance.csv, tests/test_core.py.
