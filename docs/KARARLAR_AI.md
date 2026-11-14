# Karar ve AI katkısı kaydı

14/11/2026 · FocusTM v1.0

| Karar | Gerekçe | Kanıt / statü |
|---|---|---|
| Python 3.12 + pandas + Streamlit + Plotly | Öğrenciler için az sayıda kurulum adımı ve okunabilir veri hattı | Bu ortamda çalıştırılacak; işletim sistemi kaydı TEST_RAPORU.md'de |
| Ham dosyaları kopyalamak, değiştirmemek | Kaynağa geri dönebilmek | ZIP SHA-256 ve provenance.csv |
| CSV/JSON/Shapefile eşitliğini sınamak | 3 kat sayım hatasını önlemek | 8/8 mantıksal veri kümesinde eşit kayıt çoklukları |
| Terra ve Aqua dahil 5 platformu ayrı tutmak | Farklı uydu, çözünürlük ve gözlem yoğunluğu | Paket alanları + NASA açıklamaları |
| instrument=SNPP'yi saklayıp sensor=VIIRS üretmek | Kaynak alanındaki standart dışı adlandırmayı açıklamak | Ürün SV-C2, satellite=SNPP; ham alan korunur |
| Boş ayları NA tutmak | Gözlem kapsamı kanıtı yok | Kapsam doğrulanamadı |
| Bütün türleri varsayılan olarak korumak | NRT türü yok; Type düzeltme geçmişi belirsiz | Açık etiket ve isteğe bağlı filtre |
| Ölçeklemeyi deneysel tutmak | Test sonucu ve kapsam eksikliği | Yöntem ve deney dosyaları |
| Harita çizimi ve anomali alarmı eklememek | Sağlam ilk sürüm ve kanıt sınırı | Bölge seçimi dört koordinatla mevcut |
| 2026'yı kısmi işaretlemek | Son kayıt 09/11/2026, bütün yıl yok | Ham kayıtlarla doğrulandı |

AI katkısı: Codex dosya okuma/denetim kodunu, Python işleme hattını, Streamlit arayüzünü, test taslağını, kurulum belgelerini ve PDF rehber taslağını oluşturdu; araçlarla çalıştırdı ve sonuçları kontrol etti. NASA sensör algoritmaları yeniden geliştirilmedi; hazır FIRMS tespit ürünleri analiz edildi. Yapay tespit verisi analitik çıktılara eklenmedi. Birim testlerinde yalnız yazılım sınır koşullarını sınamak için açıkça belirtilmiş küçük sentetik örnekler vardır; üretim verisine karışmaz.

Öğrencilerin katkısı bu oturumda doğrulanamaz. Jüriye öğrencilerin yazmadığı kodu tamamen kendileri yazmış gibi sunmaları önerilmez. Kullanılabilecek beyan: “NASA FIRMS verilerini Python ile işleyen, tekrarlanabilir ve test edilmiş bir eğitim prototipi geliştirdik. Kod ve dokümantasyon hazırlığında AI desteği kullandık; veri kaynaklarını, sınırlılıkları ve test sonuçlarını açıkça belgeliyoruz.” Takım gerçekten yaptığı veri seçimi, yorumlama, sunum ve kod değişikliklerini kendi adlarıyla ayrıca eklemelidir.

Resmî yarışmanın AI beyan biçimi veya kısıtları bu oturumda doğrulanmadı. Jüri mesajları dışında bir puanlama kuralı, doğruluk yüzdesi veya NASA onayı ileri sürülmedi.
# v1.1 ek kararı - 14/11/2026

Çalışan v1 ayrı tutuldu. core.py, pipeline.py, ham/işlenmiş veri ve önceki 25 test korunarak app.py + features.py ile küçük ek yapıldı. Yeni Python bağımlılığı yok. Harita, GeoJSON, ortak renk ve aynı platform/ay karşılaştırması eklendi. Harita sensör uyumlaştırması sayılmaz; HOLD kararı ve mevcut katsayıların uygulanmaması korunur.

Yeni kod, test ve belge taslağında Codex desteği kullanıldı. Sentetik test örnekleri gerçek analitik verilere katılmadı. Proje adına lisans seçilmedi, başvuru yapılmadı. Kamuya dağıtım hakkı doğrulanmayan üç kullanıcı görseli yeni ZIP'ten hariç tutuldu; v1 kaynakları değiştirilmedi. Öğrenciler kendi gerçek katkılarını ayrıca kaydetmelidir.

