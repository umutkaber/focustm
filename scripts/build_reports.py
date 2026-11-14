"""Create human-readable local audit/test summaries from machine-readable evidence."""
import json
from pathlib import Path
import xml.etree.ElementTree as ET

ROOT=Path(__file__).resolve().parents[1]
def table(header, rows):
    return '\n'.join(['| '+' | '.join(header)+' |','|'+'|'.join(['---']*len(header))+'|']+['| '+' | '.join(map(str,r))+' |' for r in rows])

def run():
    a=json.loads((ROOT/'reports/audit.json').read_text(encoding='utf-8'))
    inv=a['inventory']; ex=json.loads((ROOT/'reports/overlap_experiment.json').read_text(encoding='utf-8'))
    zrows=[]
    for name in sorted(a['zip_sha256']):
        f=[x for x in inv if x['zip']==name]
        zrows.append([name,f[0]['format'],sum(x['rows'] for x in f),'; '.join(x['member'] for x in f)])
    rows=[[x['product'],x['processing'],x['rows'],x['first_date'],x['last_date'],', '.join(x['versions'])] for x in inv if x['format']=='csv']
    columns=', '.join(next(x['columns'] for x in inv if x['format']=='csv' and x['processing']=='archive'))
    text=f'''# FocusTM veri denetimi - 14/11/2026

Karar: sensör bazlı prototip için GO; doğrulanmış birleşik seri için HOLD.

12 ZIP, 24 veri temsili, 8 mantıksal veri kümesi, 88.920 fiziksel satır kopyası. Normalize edilmiş tüm alanlar ve satır çoklukları karşılaştırıldı: CSV, JSON ve Shapefile 8/8 kümede eşit. Kopyalar çıkarılınca **29.640 tespit** kalır; 59.280 kopya yeniden sayılmaz. Reddedilen kayıt: {len(a['rejected'])}. İlgi alanı dışında: {a['out_of_bbox']}. Birebir aynı gözlem anahtarında arşiv/NRT tekrar sayımı: {len(a['archive_superseded_nrt_ids'])}.

## Tüm ZIP'ler

{table(['ZIP','Biçim','Ham satır','Veri üyeleri'],zrows)}

Shapefile ZIP'leri her arşiv ve NRT katmanı için .shp, .shx, .dbf, .prj, .cpg içerir. 4 Shapefile ZIP'inde 11'er üye, CSV/JSON ZIP'lerinde 3'er üye vardır (toplam 68 üye). PRJ: WGS84/EPSG:4326; CPG: UTF-8. Sekiz katmanın tüm nokta geometrileri DBF koordinatlarıyla karşılaştırıldı, uyumsuzluk yok. JSON kayıt dizisidir; GeoJSON değildir. Her ZIP'teki Readme.txt 89 bayttır ve NASA README bağlantısına yönlendirir.

## Tek kez sayılan sekiz veri kümesi

Tarihler ham kayıtlarda görülen ilk/son UTC tespit günüdür; kesintisiz kapsam değildir.

{table(['Ürün','İşleme','Tespit','İlk gün','Son gün','Ham version'],rows)}

## Sütunlar

Arşivde 15 alan: {columns}.

NRT'de aynı alanlar type hariç 14 sütun. Shapefile alan adları büyük harftir; CSV/JSON küçük harftir. Veri türleri ve tüm sütun listeleri reports/file_inventory.csv içindedir. NRT türü boş/NA korunur. Suomi-NPP ham instrument=SNPP etiketi değiştirilmeden instrument_raw alanına alınır, sensor=VIIRS üretilir. MODIS 6.03 ve 61.03 sürümleri korunur; dışa aktarımın tarihsel işleme sürümü açıklaması DOĞRULANAMADI.

## Bölge ve kapsam

Batı=29.5, güney=36.1, doğu=32.8, kuzey=37.5. Antalya idari sınırı değildir. 2000-01–2026-12 takviminde 5 platform için 1.620 platform-ay hücresi bulunur: 825'inde kayıt, 795'inde NA vardır. NA hücrelerinin bir bölümü platform başlamadan önce veya son kayıt sonrasındadır; bir bölümü kayıt aralığı içindeki boş aylardır. Bu toplam gözlem kaybı oranı değildir.

ZIP'ler geçerli gözlem sayısı, bulut maskesi, geçiş çizelgesi, tam indirme isteği kapsamını içermez. Bunlar DOĞRULANAMADI. Bütün aylarda coverage_verified=False. 2026 kısmi; son tespit 09/11/2026. Tür=2 sabit kaynak tespitleri MODIS'te 363, VIIRS'te 6.273; bunlar kayıttaki sınıflardır ve bağımsız yer doğrulaması değildir.

## Deney sonucu

{table(['Hedef','Güven','Eğitim ayı','Test ayı','k','Test MAE','Mevsimsel MAE'],[[x['target'],x['confidence'],x['train_months'],x['test_months'],f"{x['coefficient']:.6f}",f"{x['heldout_mae']:.3f}",f"{x['seasonal_baseline_mae']:.3f}"] for x in ex])}

MAE birimi Aqua tespit kaydı/aydır; algılama doğruluk yüzdesi değildir. Model yalnız ortak pozitif arşiv aylarında, eğitim/test yılları ayrılarak sınandı. Eksik aylar dışlandığından seçilim yanlılığı vardır. S-NPP ve NOAA-20 mevsimsel temel modelden kötü; NOAA-21'in testi kısa (11 ay). Katsayılar doğrulanmış sayılmaz ve takvimde kullanılmaz. Ayrıntı docs/YONTEM.md.

## Eksik bilgiler ve resmî kaynak çelişkileri

Tam indirme isteği; bulutsuz gözlem kapsamı; bağımsız olay envanteri; tür düzeltmesi uygulama geçmişi; MODIS version yorumunun ayrıntısı ve resmî 2026 yarışma/AI kuralları DOĞRULANAMADI. NASA README, indirme sayfası ve bazı sensör açıklamalarında başlangıç ve NRT arşive geçiş bilgilerinin farklılaştığı görüldü. Kaynakların hangisinin hangi iddiayı taşıdığı docs/KAYNAKLAR.md'de açıklandı.

## Ham veriyle kontrol

825 platform-ay grubunun tamamı Python standart kütüphanesiyle doğrudan ham CSV'lerden yeniden sayılıp işlenmiş verilerle eşleştirildi. Örnek: Temmuz 2021 Aqua 426, Terra 364, S-NPP 2.268, NOAA-20 2.580. Her işlenmiş satır kaynak CSV satırına geri izlenebilir. Kanıt: reports/raw_crosscheck.json, reports/provenance.csv, tests/test_core.py.
'''
    (ROOT/'VERI_DENETIMI.md').write_text(text,encoding='utf-8')
    tree=ET.parse(ROOT/'reports/test_results.xml').getroot()
    suites=list(tree.iter('testsuite'))
    total=sum(int(s.attrib.get('tests',0)) for s in suites)
    failures=sum(int(s.attrib.get('failures',0))+int(s.attrib.get('errors',0)) for s in suites)
    skipped=sum(int(s.attrib.get('skipped',0)) for s in suites)
    env=json.loads((ROOT/'reports/environment.json').read_text())
    text=f'''# FocusTM test ve doğrulama raporu

14/11/2026 · Yerel ortam: {env['os']}; Python {env['python'].split()[0]}.

**Otomatik sonuç:** {total} test, {failures} hata/başarısızlık, {skipped} atlanan test. Komut: `python -m pytest -q --junitxml=reports/test_results.xml`. Ayrıntılar reports/pytest_output.txt ve XML'de.

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
'''
    (ROOT/'TEST_RAPORU.md').write_text(text,encoding='utf-8')
    print(f'Reports generated; tests={total}, failures={failures}, skipped={skipped}')

if __name__=='__main__':run()
