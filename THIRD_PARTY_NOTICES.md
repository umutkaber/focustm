# Kullanılan yazılım ve veri lisansları

Bu liste 14/11/2026 tarihinde kurulan paketlerin metadata ve lisans dosyalarıyla kontrol edildi. Runtime bağımlılıkları `requirements.txt`, test/PDF bağımlılıkları `requirements-dev.txt` içindedir. Python sanal ortamı ve kütüphane ikilileri ZIP'e dahil değildir. `licenses/` klasörü, kurulu paketlerden okunan mevcut lisans metinlerini ve metadata kaydını içerir.

| Bileşen | Sürüm | İşlev | Lisans / kaynak |
|---|---|---|---|
| Python | 3.12.14 test ortamı | Çalıştırıcı | [PSF License](https://docs.python.org/3/license.html) |
| pandas | 2.2.3 | Tablo işleme | [BSD-3-Clause](https://github.com/pandas-dev/pandas/blob/main/LICENSE) |
| NumPy | 2.3.5 | Sayısal hesap | [BSD-3-Clause](https://github.com/numpy/numpy/blob/main/LICENSE.txt); dağıtım bileşenlerinin bildirimleri kendi lisans dosyasında |
| Streamlit | 1.67.0 | Yerel web arayüzü | [Apache-2.0](https://github.com/streamlit/streamlit/blob/develop/LICENSE); kurulu metadata ile doğrulandı |
| Plotly.py | 7.1.0 | Etkileşimli grafik | [MIT](https://github.com/plotly/plotly.py/blob/main/LICENSE.txt) |
| PyShp | 3.1.8 | Shapefile okuma | [MIT](https://github.com/GeospatialPython/pyshp) |
| pytest | 9.2.0 | Testler | [MIT](https://github.com/pytest-dev/pytest/blob/main/LICENSE) |
| ReportLab | 4.4.9 | PDF üretimi | BSD; kurulu LICENSE metni `licenses/` içinde |
| pypdf | 6.21.4 | PDF metin/sayfa kontrolü | BSD-3-Clause; kurulu lisans `licenses/` içinde |
| Pillow | 13.0.0 | PDF kontrol görselleri | MIT-CMU; kurulu lisans `licenses/` içinde |
| DejaVu Sans | Paketlenmiş yazı tipi | Türkçe PDF karakterleri | Bitstream Vera/DejaVu lisans bildirimi `licenses/DejaVu-LICENSE.txt` içinde |
| Poppler | QA ortamındaki araç | PDF'yi PNG'ye dönüştürme | [GPL-2.0-or-later](https://gitlab.freedesktop.org/poppler/poppler); ikili araç pakete dahil değil |

Dolaylı bağımlılıklar kendi lisanslarına tabidir. Bu ortamda çözümlenen 42 doğrudan/dolaylı paket için sürüm ve lisans metadata envanteri `licenses/dependency_inventory.csv` ve `.json` içindedir. Kurulu ortamın `pip freeze` çıktısı `reports/environment_freeze.txt` içindedir; bu dosya Windows kurulum kilidi değildir. Paketlerin kendi lisans metinleri nihai lisans kaynağıdır.

NASA verisi: Kullanıcının sağladığı FIRMS dosyaları kaynak gösterilerek yeniden paketlenmiştir. Yazılım kütüphanelerinin lisansları NASA verisine uygulanmaz. [NASA FIRMS README](https://firms.modaps.eosdis.nasa.gov/download/Readme.txt) ve [NASA veri kullanımı/atıf](https://www.earthdata.nasa.gov/engage/open-data-services-software-policies/data-use-policy) bağlantıları korunur. Üç referans görseli kullanıcı tarafından sağlanmıştır; üçüncü taraf belge parçalarıdır, yeni bir telif/lisans iddiası yapılmaz.

FocusTM için bu oturumda hazırlanan proje koduna kullanıcı adına ayrıca bir açık kaynak lisansı atanmadı. Bu durum yukarıdaki bağımlılıkların lisanslarını değiştirmez; dışarıya açık kaynak yayımlanacaksa takım kendi kodu için lisans kararı vermelidir.
# v1.1 harita ve format kaynakları

Yeni Python bağımlılığı yoktur. Plotly'nin MapLibre harita motoru BSD-3-Clause ve kendi üçüncü taraf notlarına tabidir: https://github.com/maplibre/maplibre-gl-js/blob/main/LICENSE.txt . Plotly MIT lisansı korunur.

İsteğe bağlı altlık: © OpenStreetMap contributors; veriler ODbL, https://www.openstreetmap.org/copyright . Karo hizmet politikası ayrıca geçerlidir: https://operations.osmfoundation.org/policies/tiles/ . Karo dosyaları pakete alınmaz; toplu indirme/çevrimdışı karo önbelleği eklenmez.

GeoJSON standardı: RFC 7946, https://www.rfc-editor.org/rfc/rfc7946 . GeoJSON'a geçiş NASA verisini OSM lisansına dönüştürmez. Proje lisansı henüz seçilmedi; docs/LISANS_VE_TESLIM_KONTROLU.txt ekip kararı için hazırlanmıştır.

