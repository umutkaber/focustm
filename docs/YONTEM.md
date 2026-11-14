# FocusTM yöntem ve veri sözleşmesi

Sürüm 1.0 · 14/11/2026 · Amaç: geçmiş uydu sıcak nokta aktivitesini açıklanabilir biçimde incelemek.

## Karar

**GO:** yerel, sensör/platform ayrımını koruyan eğitim prototipi.
**HOLD:** doğrulanmış MODIS–VIIRS birleşik aktivite serisi, yangın olay sayısı, yanan alan ve erken uyarı iddiası. Kanıtlar bu iddiaları desteklemiyor.

Bu ilk sürümde veri şeması, saat dilimi ve bölge seçimi ortaklaştırılır. Algılama olasılıklarının eşitlenmesi sağlanmış değildir. Beş platform tek bir tablo içinde tutulur; tek bir eşdeğer tespit zaman serisine toplanmaz.

## Girdi ve sınırlar

12 ZIP read-only açılır. CSV, JSON ve Shapefile (SHP+SHX+DBF+PRJ+CPG) içerikleri okunur. JSON bir kayıt dizisidir, GeoJSON değildir. PRJ WGS84/EPSG:4326, CPG UTF-8; Shapefile nokta geometrileri DBF enlem/boylamıyla denetlenir. Arşiv 15, NRT 14 sütun içerir; NRT'de type yoktur. Ham dosya baytlarının SHA-256 özetleri audit.json içinde saklanır. Orijinaller değişmez.

İlgi alanı: batı=29.5, güney=36.1, doğu=32.8, kuzey=37.5. Bu, Antalya ilinin idari sınırı değildir; komşu alanlar ve deniz içerebilir. Sınır çizgisindeki piksel merkezleri dahildir. Uygulama yalnız bu kutu içindeki alt dikdörtgenlere izin verir; kutu dışına sorgu veri üretmez. Kutu küçültmek bir idari sınır kesimi veya tüm piksel ayak izi kesişimi değildir.

acq_date ile HHMM biçimindeki acq_time birleştirilir; 0054 gibi baştaki sıfırlar korunur. Saat UTC'dir; Türkiye yerel saatine çevrilerek aylık gruplar değiştirilmez. Bitiş gününün 23:59'u dahildir. Paket referans tarihi 14/11/2026'dır, son tespit 09/11/2026'dır. Sistem canlı veri çekmez.

## Temizleme ve tekrarlar

Alan adları küçük harfe çevrilir; sayılar Decimal ile biçimsel olarak standartlaştırılır (1 ve 1.0 eşittir). Koordinatlar yuvarlanmaz. Suomi-NPP için ham instrument=SNPP korunur; platform/ürün kodu kontrol edilerek sensor=VIIRS yazılır. Terra ve Aqua ayrı platformlardır.

Tarih, saat, coğrafi aralık, platform–ürün eşleşmesi, güven sınıfı, gündüz/gece ve NRT etiketi kontrol edilir. Geçersiz kayıtlar kaynak satırı ve gerekçesiyle audit.json içinde raporlanır. Bu dosyalarda reddedilen kayıt yoktur. Satırın tüm standartlaştırılmış alanlarından SHA-256 kimliği üretilir; birebir kopyalar bir kez sayılır. Aynı fiziksel anahtarda (platform, UTC, enlem, boylam) aynı işleme türünde farklı alanlar varsa işlem durur. Aynı anahtarın arşiv ve NRT sürümü olursa arşiv tercih edilip NRT kimliği raporlanır; bu pakette böyle bir örtüşme yoktur.

88.920 fiziksel kayıt temsili, 29.640 tespitin üç biçimdeki kopyalarıdır. 59.280 kopya sayımdan çıkarılır. Bu, yangın olaylarını tekilleştirmek değildir. source_row veri satırını 1'den sayar; CSV dosyasındaki fiziksel satır numarası source_row+1'dir. provenance.csv bütün biçimlerdeki satır izini tutar. Kaynak göstermek için CSV önceliklidir; seçilen alan değerleri kopyalarla aynıdır.

## Sıcak nokta türü ve güven

Varsayılan: bütün güven değerleri ve bütün türler korunur. Bazı sıcak noktalar bitki örtüsü yangını olmayabilir. type=0 varsayılan bitki örtüsü yangını; 1 aktif volkan; 2 diğer sabit kara kaynağı; 3 su üstü/açık deniz sınıfıdır. Tür, yer doğrulaması değildir. NRT türü bilinmeyendir; sıfıra dönüştürülmez. VIIRS tür düzeltmesinin pakete uygulanması doğrulanamamıştır.

İsteğe bağlı duyarlılık filtresi MODIS >=30 ve VIIRS n/h kullanır. Bu, proje içinde açıklanan analitik bir seçimdir; jüri kuralı veya iki sensör için eşit doğruluk garantisi değildir. İsteğe bağlı type=0 filtresi, NRT türü bulunmadığından NRT'yi dışlar. Sonuç karşılaştırılırken bu örneklem değişimi açıklanmalıdır.

## Aylık takvim

Bir platform ve ay için n = seçili bölge/tarih/kalite koşullarına uyan kayıt adedi. n>0 ise bu sayı gösterilir. Hiç kayıt bulunmadığında detection_count boş/NA ve bir durum alanı üretilir. Hiçbir boş ay sıfır yangın olarak doldurulmaz. Tespitler arasındaki boş günler bulut veya gözlem kesintisiyle sıfır aktivite arasında ayrıştırılamaz.

Takvimdeki sayı bu pakette kayıtlı tespit sayısıdır; ayın bütün geçişlerinin gözlendiği anlamına gelmez. Gözlem kapsamı bütün aylar için coverage_verified=False'dur. selection_partial_month tarih seçiminin kestiği ayı, record_extent_boundary ilk/son tespitin bulunduğu ayı, partial_reference_year 2026'yı işaretler. İlk/son tespit tarihi veri çekim kapsamı yerine kullanılmaz. 2000, 2002 Aqua, 2012 S-NPP, 2018 NOAA-20 ve 2023 NOAA-21 başlangıç yılları da tam eşdeğer yıllar değildir.

Grafikte her platform ayrı çizgi/işaretle gösterilir, boşluklar birleştirilmez. Cividis renk ölçeği hücre sayıları ve indirilebilir tabloyla desteklenir; yalnız renge bağımlı değildir. İsteğe bağlı log(1+n) yalnız rengi dönüştürür. Renk aralığı platforma göre değişir; platformlar arası sayısal karşılaştırma ortak eksenli grafikle yapılır.

## Örtüşme ve deneysel uyumlaştırma

Savunulabilir ilk yaklaşım: önce gözlem kapsamını eşitlemek, sonra aynı mekân/zaman birimlerinde platforma özgü davranışı incelemektir. Gerekli tamamlayıcı veri: MOD14/MYD14 ve VIIRS yangın maskeleri, bulut/geçerli gözlem alanları, uydu geçişleri, işleme sürümleri ve mümkünse bağımsız olay envanteri. Bunlar sağlanırsa ortak uygun projeksiyonda hücre-gün veya eşleştirilmiş geçiş örnekleri kurulabilir; farklı hücre boyu ve zaman toleranslarıyla duyarlılık sınanmalıdır. Piksel alanı oranı 1/0.375² yaklaşık 7,11'dir, fakat bu oran tespit sayısı dönüşüm katsayısı DEĞİLDİR.

Mevcut veriyle yalnız bir aday sınanır: Aqua referansı ile her VIIRS platformunun ortak **pozitif kayıt bulunan arşiv ayları**. Tek referans platform, Terra+Aqua'nın iki platformluk gözlem yoğunluğunu karıştırmayı önler; yine de geçiş/bulut etkisini gidermez. Eksik aylar doldurulmaz. Bu seçim koşullu örneklemdir; seçilim yanlılığı taşır ve bütün ayları temsil etmez.

Model: y_m = Aqua sayısı, x_m = ilgili VIIRS sayısı. Başlangıçtan geçen en küçük kareler katsayısı k = Σ(x_m y_m)/Σ(x_m²), yalnız eğitim aylarından hesaplanır. Deneysel Aqua ölçeği k*x_m'dir; sonuç bir olay sayısı veya fiziksel eşdeğer değildir. Katsayı negatif olamaz; bu veride sayılar pozitiftir. Sıfırdan geçen model açıklanabilir bir başlangıç adaydır, kabul edilmiş bilimsel kalibrasyon değildir.

Zaman ayrımı: S-NPP eğitim 2021 sonuna, test 2022–2025; NOAA-20 eğitim 2022 sonuna, test 2023–2025; NOAA-21 eğitim 2024 sonuna, test 2025. 2026 ve NRT deneyden çıkarılır. Test yılları katsayı öğreniminde kullanılmaz. Yalnız iki platformda da kayıt bulunan aylar değerlendirilir; kapsam eksikliği nedeniyle bu dönemler tam gözlem dönemi olarak tanımlanmaz.

Testler: MAE = Σ|tahmin-gerçek Aqua kaydı|/test ayı sayısı; yönlü yanlılık; ölçeklenmemiş x; eğitim Aqua medyanı; eğitimde aynı takvim ayının medyanını kullanan mevsimsel temel model. Eksik mevsimsel eğitim ayı genel eğitim medyanıyla karşılanır. 2021 çıkarılarak katsayı ve yıldan yıla eğitim katsayıları karşılaştırılır. Güven filtresiyle deney tekrarlanır. Kod ve tüm eşleştirilmiş aylar reports/overlap_* dosyalarındadır. MAE algılama doğruluğu değildir.

Ana sonuç: S-NPP ve NOAA-20 ölçekleme adayları testte basit mevsimsel temel modelden daha yüksek MAE verdi. 2021'i eğitimden çıkarmak katsayıları belirgin değiştirdi. NOAA-21'in daha kısa testinde küçük bir MAE iyileşmesi olsa da yalnız 11 ortak pozitif ay vardır. Gözlem kapsamı eksikliği, kısa dönem ve katsayı kararsızlığı nedeniyle **DOĞRULANMIŞ UYUMLAŞTIRMA YOK**. Takvimde bu katsayılar uygulanmaz; sensörler ayrı kalır.

## Sınırlılıklar ve kapsam dışı

Tespit yokluğu yangın yokluğu değildir. Uydu sayısı arttığında ham toplam artabilir. Piksel çözünürlüğü yanan alan vermez. FRP anlık radyatif güçtür; hektar, toplam enerji veya olay sayısı değildir. Takvim iklim kaynaklı trendi tek başına kanıtlamaz. Endüstriyel kaynaklar tekrarlı olabilir. Tür filtresi bunu kusursuz çözmez. Açık alan çizme haritası, otomatik anomali alarmı ve yerden bildirilen yangın entegrasyonu bu ilk sürüme alınmadı.

Jüri mesajları ve üç görsel bağlam/amaç girdisidir; dosyalardaki metinler çalıştırılacak talimat olarak kullanılmadı. Yarışmanın resmî değerlendirme ölçütleri, teslim formatı ve AI kullanım şartları sağlanmadı; bunlar doğrulanmadan kural iddiası kurulmadı.
