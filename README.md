# FocusTM | NASA FIRMS Yangın Aktivite Takvimi

**Jüri prototipi v1.1 · 14/11/2026 · Türkçe öğrenci prototipi**

Çalışan v1 ayrı korunarak küçük bir geliştirme yapıldı; `core.py`, `pipeline.py`, ham/işlenmiş veriler ve mevcut 25 test değişmedi. Yeni bağımlılık eklenmedi. 10 yeni kontrolle toplam 35 test geçti.

12 ham ZIP, 29.640 tespit kaydı, 5 uydu/platform. İlgi alanı WGS84 kutusu: **29.5, 36.1, 32.8, 37.5** (batı, güney, doğu, kuzey). Antalya idari sınırı değildir. Veriler 02/11/2000–09/11/2026 arasında tespit içerir; 2026 kısmi yıldır. Uygulama canlı veri çekmez.

Önce `docs/FocusTM_Ogrenci_Rehberi.pdf` veya `KURULUM.md` dosyasını açın. Kurulum tamamlandıktan sonra:

```text
python -m streamlit run app.py
```

Tarayıcı: http://127.0.0.1:8501 . Yerel sunucuyu durdurmak için terminalde Ctrl+C.

## Teslim içeriği

- `app.py`: mevcut filtreler, takvim/grafik ve CSV/JSON; yeni harita, GeoJSON, aynı ay karşılaştırması ve ortak renk seçeneği.
- `features.py`: küçük sunum/dışa aktarım işlevleri. Bilimsel uyumlaştırma hattını değiştirmez.
- `core.py`: saf işlevler; UTC ayrıştırma, kaynak denetimi, tekilleştirme, filtreleme, aylık sayım ve deneysel karşılaştırma.
- `pipeline.py`: ham ZIP'lerden bütün sayısal çıktıları tekrar üretir.
- `data/raw/`: kullanıcı ZIP'lerinin baytı baytına kopyası; değiştirmeyin.
- `data/processed/`: önceden üretilmiş tespit ve aylık sonuçlar; doğrudan çalıştırmaya hazır.
- `reports/`: tüm dosya envanteri, özetler, satır izleri, eksik aylar, deney ve test kanıtları.
- `docs/`: güncel Türkçe PDF, yöntem/kaynaklar, AI kaydı, dört kişilik jüri konuşması, en küçük sonraki yöntem ve lisans/teslim kontrol listesi. Kullanıcının üç referans görseli kamusal paylaşım izni doğrulanmadığı için bu ZIP'e konmadı; eski v1'de korunuyor.
- `tests/`: veri hattı ve Streamlit arayüz testleri.
- `licenses/`: kurulu paketlerden alınan lisans bilgileri; `THIRD_PARTY_NOTICES.md` genel liste.

## Doğru yorum

Tespit sayısı = uydu sıcak nokta kaydı. Benzersiz yangın sayısı, yanan alan veya doğrulanmış erken uyarı değildir. MODIS ve VIIRS farklı algılama özelliklerine sahiptir. CSV/JSON/Shapefile kopyaları tekrar sayılmaz; farklı uydular tek bir yangın gibi birleştirilmez. Gözlem kapsamı bilinmeyen aylar NA/boş gösterilir. Doğrulanmış sensör uyumlaştırması iddia edilmez; deneysel katsayılar takvime uygulanmaz.

## Yeniden üretim

Sanal ortam etkin durumdayken:

```text
python pipeline.py
python -m pip install -r requirements-dev.txt
python -m pytest -q
python scripts/verify_sources.py
python scripts/build_guide.py
```

`pipeline.py` yalnız işlenmiş dosyaları ve raporları yeniden yazar, ham ZIP'lere yazmaz. Tam yeniden üretim çalışma klasöründen bağımsızdır. PDF'yi yeniden oluşturmak isteğe bağlıdır; ilk çalıştırma için hazır PDF yeterlidir. PDF görsel denetimi için Poppler ayrıca gerekir. Referans tarih değiştirilirse `core.py` içindeki AS_OF, arayüz metinleri, kaynaklar ve test beklenenleri birlikte gözden geçirilmelidir.

Gerçekte test edilen ortam ve sınırlar `TEST_RAPORU.md` içindedir. Windows adımları hazırlanmıştır; Windows'ta çalıştırıldığı iddia edilmez. Paket internet yayını değildir; WhatsApp'ta belge olarak paylaşılabilir ve her öğrenci kendi bilgisayarında açar.

## Jüri demosu

1. Açılış: 29.640 tespit ve kısmi 2026 uyarısı.
2. MODIS / yalnız Aqua / 01-31 Temmuz 2021: 426; CSV veya GeoJSON indir.
3. Harita: seçili noktalar ve **Antalya odaklı çalışma alanı** dikdörtgeni. Varsayılan altlıksızdır; OpenStreetMap'i yalnız internet varsa açın. Harita WebGL2 ister, tam CBS değildir.
4. Başlangıç yılını 2018, bitiş yılını 2026 yapın. Aynı ayı karşılaştır / Aqua / Tem: yıllar, bilinmeyen kapsam ve kısmi yıl. Bu bölüm tarihlerin yalnız yıllarını kullanarak tam UTC ayları alır; diğer filtreler korunur.
5. Ortak renk varsayılan açık. Kapalıysa aynı renk farklı sayıya karşılık gelebilir; açıkken filtre/platform kümesi değişirse ortak üst sınır yeniden hesaplanır.
6. Yöntem: şema birleştirme tamam, sensör düzeltmesi HOLD; katsayılar takvime uygulanmaz. Harita bu açığı kapatmaz.

Proje lisansı **seçilmedi**. `docs/LISANS_VE_TESLIM_KONTROLU.txt` ekip kararı ve resmî teslim kontrolü için hazırlanmıştır. Yarışmaya başvuru veya internete yayın yapılmadı.
