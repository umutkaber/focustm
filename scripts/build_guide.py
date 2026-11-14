"""Rebuild the Turkish student PDF from verified project evidence; no remote fetches."""
from pathlib import Path
import json
import math
import xml.etree.ElementTree as ET
from html import escape

import pandas as pd
from plotly.colors import sample_colorscale
from reportlab.lib import colors
from reportlab.lib.enums import TA_LEFT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak, Image, KeepTogether

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'docs/FocusTM_Ogrenci_Rehberi.pdf'
W,H=A4
INK=colors.HexColor('#17324A');TEAL=colors.HexColor('#137E91');PALE=colors.HexColor('#EAF2F6');MUTED=colors.HexColor('#536779')
pdfmetrics.registerFont(TTFont('DejaVu',str(ROOT/'docs/fonts/DejaVuSans.ttf')))
pdfmetrics.registerFont(TTFont('DejaVuBold',str(ROOT/'docs/fonts/DejaVuSans-Bold.ttf')))
pdfmetrics.registerFontFamily('DejaVu',normal='DejaVu',bold='DejaVuBold',italic='DejaVu',boldItalic='DejaVuBold')
ST={
 'body':ParagraphStyle('Body',fontName='DejaVu',fontSize=10,leading=15,textColor=INK,spaceAfter=8),
 'small':ParagraphStyle('Small',fontName='DejaVu',fontSize=8.4,leading=12,textColor=MUTED,spaceAfter=6),
 'cell':ParagraphStyle('Cell',fontName='DejaVu',fontSize=8.3,leading=11.5,textColor=INK),
 'headcell':ParagraphStyle('HeadCell',fontName='DejaVuBold',fontSize=8.4,leading=11.5,textColor=colors.white),
 'h1':ParagraphStyle('H1',fontName='DejaVuBold',fontSize=20,leading=25,textColor=INK,spaceAfter=16),
 'h2':ParagraphStyle('H2',fontName='DejaVuBold',fontSize=12,leading=17,textColor=TEAL,spaceBefore=8,spaceAfter=7),
 'cover':ParagraphStyle('Cover',fontName='DejaVuBold',fontSize=32,leading=39,textColor=INK,spaceAfter=18),
 'code':ParagraphStyle('Code',fontName='DejaVu',fontSize=8,leading=12,textColor=INK,backColor=PALE,borderPadding=9,spaceAfter=12)
}
story=[]
def p(t,style='body'):
    story.append(Paragraph(t,ST[style]))
def h(t):p(t,'h2')
def page(title):
    if story:story.append(PageBreak())
    p(title,'h1')
def tab(headers,rows,widths=None):
    data=[[Paragraph(str(v),ST['headcell']) for v in headers]]+[[Paragraph(str(v),ST['cell']) for v in r] for r in rows]
    t=Table(data,colWidths=widths or [499/len(headers)]*len(headers),repeatRows=1,hAlign='LEFT')
    t.setStyle(TableStyle([('BACKGROUND',(0,0),(-1,0),INK),('VALIGN',(0,0),(-1,-1),'TOP'),('ROWBACKGROUNDS',(0,1),(-1,-1),[colors.white,PALE]),('LINEBELOW',(0,0),(-1,0),0.5,TEAL),('BOTTOMPADDING',(0,0),(-1,-1),7),('TOPPADDING',(0,0),(-1,-1),7),('LEFTPADDING',(0,0),(-1,-1),7),('RIGHTPADDING',(0,0),(-1,-1),7)]))
    story.append(t);story.append(Spacer(1,9))
def code(t):p(escape(t).replace('\n','<br/>'),'code')
def fmt(n):return f'{int(n):,}'.replace(',','.')
def link(label,url):return f'<link href="{escape(url,quote=True)}" color="#137E91">{escape(label)}</link>'
def footer(canvas,doc):
    canvas.saveState();canvas.setStrokeColor(colors.HexColor('#D5E0E7'));canvas.line(48,42,W-48,42)
    canvas.setFont('DejaVu',7);canvas.setFillColor(MUTED)
    canvas.drawString(48,29,'FocusTM | Öğrenci rehberi | v1.1 | 14/11/2026')
    canvas.drawRightString(W-48,29,str(doc.page));canvas.restoreState()


def build():
    a=json.loads((ROOT/'reports/audit.json').read_text(encoding='utf-8'))
    ex=json.loads((ROOT/'reports/overlap_experiment.json').read_text(encoding='utf-8'))
    data=pd.read_parquet(ROOT/'data/processed/detections.parquet')
    m=pd.read_csv(ROOT/'data/processed/monthly.csv')
    pairs=pd.read_csv(ROOT/'reports/overlap_pairs.csv')
    tests=ET.parse(ROOT/'reports/test_results.xml').getroot()
    nt=sum(int(x.attrib.get('tests',0)) for x in tests.iter('testsuite'))
    nf=sum(int(x.attrib.get('failures',0))+int(x.attrib.get('errors',0)) for x in tests.iter('testsuite'))

    # 1 - Cover and decision.
    p('FOCUSTM / UYGULAMALI VERİ BİLİMİ','small');story.append(Spacer(1,26))
    p('Yangın aktivitesini<br/>veriden okumak','cover')
    p('NASA MODIS ve VIIRS sıcak nokta verileriyle<br/><b>Türkçe web prototipi ve öğrenci rehberi</b>')
    story.append(Spacer(1,20))
    tab(['12 ZIP','29.640 tespit','5 platform'],[['CSV + JSON + Shapefile','Dosya kopyaları bir kez sayıldı','Terra, Aqua, S-NPP, NOAA-20/21']])
    h('Bu sürüm ne yapıyor?')
    p('Kullanıcının sağladığı NASA FIRMS dosyalarını Python ile okur; kaynak izini korur, tarih ve bölgeye göre filtreler, platform bazında aylık aktivite takvimi üretir. Öğrenci verinin nereden geldiğini, hangi işlemden geçtiğini ve hangi sınırlar içinde yorumlanabileceğini gösterebilir.')
    h('Karar: prototip için GO, doğrulanmış birleşik seri için HOLD')
    p('Veri şeması ve UTC takvimi ortaklaştırıldı. Ancak MODIS ile VIIRS algılama özelliklerinin eşitlendiği kanıtlanmadı. Deneysel ölçekleme sınandı ve ana takvime uygulanmadı. Boş aylar sıfır yangın olarak doldurulmadı.')
    p('<b>Ölçtüğümüz:</b> uydu sıcak nokta tespit kaydı.<br/><b>Bu veriden çıkarmadığımız:</b> benzersiz yangın sayısı, yanan hektar, doğrulanmış erken uyarı, kesin algılama doğruluğu.')
    h('Belge bilgisi')
    p('Sürüm: 1.1 · İnceleme: 14/11/2026 · Zaman standardı: UTC.<br/>Antalya odaklı çalışma alanı: batı 29.5, güney 36.1, doğu 32.8, kuzey 37.5.<br/>Son paket tespiti: 09/11/2026. 2026 kısmi yıldır.<br/>Yeni: harita, GeoJSON, aynı ay karşılaştırması ve ortak renk seçeneği. Resmî teslim kontrolü ve dört kişilik konuşma son bölümlerdedir.','small')

    # 2 - Contents.
    page('Rehberin kullanım yolu')
    tab(['Bölüm','Sayfa','Öğrencinin kazanımı'],[
        ['Veri denetimi','3','12 ZIP ve sekiz mantıksal veri kümesini ayırmak'],
        ['Sensörler ve bölge','4','Çözünürlük, platform ve dönem farkını açıklamak'],
        ['Alan sözlüğü','5','Bir tespit satırını okumak'],
        ['Python işleme hattı','6','Veriyi tekrar üretmek ve kaynağa dönmek'],
        ['Takvim ve eksik dönemler','7','Boş hücreyi sıfır yangından ayırmak'],
        ['Uyumlaştırma yöntemi','8','Bir adayı eğitim/test ayrımıyla sınamak'],
        ['Deney sonuçları','9','Modelin kabul edilmemesinin gerekçesi'],
        ['Web kullanımı ve CSV','10','Filtreleme, indirme ve demo'],
        ['Windows kurulumu','11','Sanal ortamda adım adım çalıştırmak'],
        ['Mac ve yeniden üretim','12','Kod/veri ayrımı ve klasörler'],
        ['Test ve ham veri kontrolü','13','Gerçekte nelerin sınandığını göstermek'],
        ['Jüri soruları','14','Kısa ve doğru yanıtlar hazırlamak'],
        ['Kaynaklar ve açık konular','15','Doğrulanmış bilgiyle belirsizliği ayırmak'],
        ['Lisanslar ve AI katkısı','16','Katkıları ve yeniden kullanımı açıklamak']], [165,45,289])
    h('Önerilen öğrenme sırası')
    p('Önce 3-7. sayfalardaki veri mantığını okuyun. Sonra işletim sisteminize uygun kurulumu yapıp 10. sayfadaki örneği uygulayın. Jüri sunumundan önce yöntem ve test bölümlerini birlikte gözden geçirin.')
    p('<b>Dosya önceliği:</b> PDF öğretici açıklamadır; sayısal denetimin makineyle okunur kanıtı reports/audit.json ve CSV raporlarıdır. Daha ayrıntılı yöntem docs/YONTEM.md, kurulum KURULUM.md, test kanıtları TEST_RAPORU.md içindedir.')
    p('<b>v1.1 ekleri:</b> s.17 harita ve aynı ay örneği; s.18 en küçük sonraki yöntem; s.19 dört kişilik konuşma; s.20 lisans/teslim ve test kontrolü.','small')

    # 3 - Audit.
    page('1. Dosyaları gerçekten açtık')
    p('12 ZIP içindeki 68 üye okundu. CSV, JSON ve Shapefile kayıtları normalize edilen bütün alanları ve satır çoklukları üzerinden karşılaştırıldı. Sekiz veri kümesinin üç biçimi eşit; sıralama farkı sayıma etki etmez.')
    tab(['Ürün kodu','Shapefile ZIP ID','CSV ZIP ID','JSON ZIP ID'],[
        ['M-C61','847413','847528','847598'],['SV-C2','847416','847531','847601'],
        ['J1V-C2','847414','847529','847599'],['J2V-C2','847415','847530','847600']], [125,125,125,124])
    p('Tam ZIP adı: DL_FIRE_&lt;ürün kodu&gt;_&lt;ID&gt;.zip. Her ZIP arşiv ve NRT katmanlarını içerir. Shapefile başına SHP, SHX, DBF, PRJ, CPG bulunur; WGS84/EPSG:4326 ve UTF-8 doğrulandı. JSON, GeoJSON olmayan bir kayıt dizisidir.','small')
    rows=[]
    for prod in ['M-C61','SV-C2','J1V-C2','J2V-C2']:
        for stage in ['archive','nrt']:
            r=next(x for x in a['inventory'] if x['format']=='csv' and x['product']==prod and x['processing']==stage)
            rows.append([prod,'Arşiv' if stage=='archive' else 'NRT',fmt(r['rows']),r['first_date'],r['last_date']])
    tab(['Ürün','İşleme','Tespit','İlk kayıt (UTC)','Son kayıt (UTC)'],rows,[75,60,65,149,150])
    p('<b>88.920 fiziksel satır kopyası - 59.280 tekrar = 29.640 tespit.</b> Arşiv toplamı 28.308, NRT toplamı 1.332. Reddedilen kayıt ve kutu dışında kalan kayıt: 0. Aynı anahtarda arşiv/NRT örtüşmesi: 0.')
    p('Arşiv dosyaları 15, NRT 14 sütun taşır; type NRT’de yoktur. Bütün dosya adları, sütunlar, tarih/sürüm bilgileri file_inventory.csv ve audit.json içinde; ZIP üyelerinin SHA-256 özeti zip_members.csv içindedir. ZIP içi Readme.txt yalnız NASA çevrimiçi README adresini verir. [S1, S2]','small')

    # 4 - Platforms and geographic scope.
    page('2. Sensör, uydu ve bölge')
    tab(['Platform','Nominal piksel','Paket ilk/son tespit günü','Projede rolü'],[
        ['Terra / MODIS','~1 km','02/11/2000 - 07/10/2026','En uzun tarihsel platform'],
        ['Aqua / MODIS','~1 km','04/07/2002 - 25/10/2026','Tarihsel seri; deneyde tek referans'],
        ['Suomi-NPP / VIIRS','~375 m','20/01/2012 - 29/10/2026','MODIS ile en uzun VIIRS örtüşmesi'],
        ['NOAA-20 / VIIRS','~375 m','01/04/2018 - 09/11/2026','Daha yeni süreklilik ve karşılaştırma'],
        ['NOAA-21 / VIIRS','~375 m','02/03/2023 - 09/11/2026','Kısa yeni seri; sınırlı test dönemi']], [104,66,156,173])
    p('Tablodaki tarihler yerel dosyada tespit görülen günlerdir. Sensörün işletime giriş/çıkışını veya kutunun her gün gözlendiğini göstermez. NASA indirme sayfası S-NPP ürün dönemini 02/11/2026’da bitirir; bu kutudaki son S-NPP tespiti 29/10/2026’dır. [S1]')
    h('Neden sayıları doğrudan toplayamıyoruz?')
    p('VIIRS daha küçük sıcak noktaları ve büyük olayın daha çok pikselini yakalayabilir. Uyduların geçiş zamanı, tarama geometrisi, bulut/duman durumu ve ürün algoritmaları farklıdır. Terra ile Aqua da aynı gözlem akışı değildir. Aynı olay birden fazla uyduda ve günde tekrar görülebilir. [S3-S5]')
    p('1 km / 375 m, algılama çözünürlüğü karşılaştırmasıdır. Piksel alanı oranı yaklaşık 7,11 olsa da MODIS sayısını 7,11 ile çarpmak bilimsel bir dönüşüm yöntemi değildir. Piksel içindeki alanın tamamı yanmış olmak zorunda değildir.')
    h('Dikdörtgenin açık tanımı')
    tab(['Batı (boylam)','Güney (enlem)','Doğu (boylam)','Kuzey (enlem)'],[['26.0','36.0','45.0','42.0']])
    p('Bu kutu <b>Antalya ilinin idari sınırı değildir</b>. Komşu alanlar ve deniz içerebilir. Nokta merkezleri sınırlar dahil filtrelenir. Uygulama yalnız bu kutunun alt bölgelerini seçer; olmayan dış bölge verisini üretmez. İdari il analizi için doğrulanmış il sınırı geometrisi ve ayrı kesim gerekir.')
    h('Kanıt seviyeleri')
    p('A: resmî NASA açıklamasıyla doğrulanan ürün özelliği. Yerel kanıt: ham dosyada doğrudan gözlenen değer. C: proje içi analitik seçim/kurulum varsayımı. D: DOĞRULANAMADI. Yerel ilk tespit tarihi, resmî kapsam başlangıcıyla aynı şey değildir.','small')

    # 5 - Fields.
    page('3. Bir tespit satırını okumak')
    tab(['Ham alan','Anlam / birim','Dikkat'],[
        ['latitude, longitude','Piksel merkezinin enlem/boylamı; WGS84 derece','Olay sınırı ve yanan alan değildir.'],
        ['acq_date','Tespit günü; YYYY-MM-DD','UTC gününe göre ay atanır.'],
        ['acq_time','Geçiş zamanı; HHMM UTC','0054 gibi baştaki sıfır korunur.'],
        ['satellite','Terra, Aqua, SNPP, N20, N21','Beş platform ayrı tutulur.'],
        ['instrument','MODIS, VIIRS veya bu pakette SNPP','Ham alan korunur; SNPP için standart sensor=VIIRS.'],
        ['brightness','Parlaklık sıcaklığı; Kelvin','MODIS 21/22; VIIRS I4 açıklaması. Aynı fiziksel bant değildir.'],
        ['bright_t31','İkinci parlaklık sıcaklığı alanı; Kelvin','MODIS kanal 31. VIIRS’te bu dışa aktarım adının I5 eşlemesi ayrıca doğrulanmalı; analizde kullanılmaz.'],
        ['scan, track','Tarama yönlerinde piksel boyutu; km','Gerçek ayak izi değişebilir; yanmış alan değildir.'],
        ['confidence','MODIS 0-100; VIIRS l/n/h','Sensörler arasında aynı güven ölçeği değildir.'],
        ['version','Koleksiyon/işleme sürümü; metin','2, 2.0NRT, 6.03, 61.03, 6.1NRT korunur.'],
        ['frp','Piksele ait radyatif güç; MW','Anlık güç; hektar veya toplam enerji değildir.'],
        ['daynight','D: gündüz; N: gece','Aylık toplamada korunur.'],
        ['type','0 bitki örtüsü varsayımı; 1 volkan; 2 sabit kara; 3 su üstü','NRT’de yoktur. Yer doğrulaması değildir.']], [96,192,211])
    p('Alan açıklamaları [S3, S4, S6] ve ham dosya başlıklarıyla birlikte okunmalıdır. VIIRS Type düzeltme geçmişinin bu dosyalara uygulanıp uygulanmadığı doğrulanamadı. Bu nedenle varsayılan bütün türleri gösterir. NRT’de eksik türü type=0 yapmayız.')
    h('Uygulamanın eklediği alanlar')
    p('timestamp_utc, sensor, platform, product, processing, month, year; kayıt kimliği record_id; ham instrument_raw; kaynak source_zip, source_member, source_row ve source_copy_count. Aylık tabloda durum ve kısmi dönem bayrakları bulunur. Kimlik yalnız dosya tekrarını izler; yangın olay numarası değildir.','small')

    # 6 - Processing.
    page('4. Python ile neyi, nasıl yaptık?')
    tab(['Aşama','İşlem','Neden'],[
        ['1 / Envanter','ZIP ve tüm üyelerinin SHA-256 özeti; biçim okuma','Ham kaynağın değişmediğini göstermek'],
        ['2 / Standart şema','Alan adları, sayı gösterimi, platform kodları, UTC','Biçim farklarını analitik fark sanmamak'],
        ['3 / Denetim','Geçerli tarih/koordinat, sensör, güven, NRT, geometri','Bozuk kayıtları sessizce kullanmamak'],
        ['4 / Tekilleştirme','Bütün alanları eşit kayıt kopyalarını birleştirme','CSV/JSON/SHP’yi üç kez saymamak'],
        ['5 / Seçim','UTC tarih, sınırlar dahil kutu, platform, filtreler','Kullanıcının sorgusunu açık tanımlamak'],
        ['6 / Aylık sayım','Platform + UTC ay grupları; boş aya NA','Gözlenmeyeni sıfır yangına çevirmemek'],
        ['7 / Sunum','Streamlit + Plotly; CSV ve seçim JSON’u','Sonucu incelemek ve tekrar üretmek']], [72,234,193])
    p('core.py hesap işlevlerini, pipeline.py tekrar üretimi, app.py ekranı yönetir. Aynı işlevler testlerde de kullanılır. Ayrı JavaScript sunucusu, veritabanı veya GPU gerekmez. NASA’nın sensör işleme algoritması yeniden yazılmadı; FIRMS’in ürettiği tespit kayıtları analiz edildi.')
    code('Ham ZIP → Python / core.py → detections.csv + monthly.csv\n                                  ↓\n                           Streamlit / app.py\n                                  ↓\n                      Filtrelenmiş CSV + seçim JSON')
    h('Gerçek ham kayıt örneği')
    r=data[(data.platform=='Aqua')&(data.month=='2021-07')].iloc[0]
    p(f"Kaynak: <b>{r.source_zip}</b><br/>Üye: {r.source_member}<br/>Veri satırı: {int(r.source_row)} (CSV fiziksel satırı {int(r.source_row)+1})<br/>UTC: {r.timestamp_utc}; enlem {r.latitude}, boylam {r.longitude}; platform Aqua.",'small')
    p('provenance.csv aynı kaydın JSON ve Shapefile içindeki yerlerini de korur. Koordinatlar yuvarlanarak yakın noktalar birleştirilmez. Çelişen aynı gözlem anahtarında işlem durur; bu pakette çelişki bulunmadı.')

    # 7 - Calendar.
    page('5. Takvimi doğru yorumlamak')
    p('Aylık sayı, o platform için seçim koşullarına uyan tespit kayıtlarının adedidir. Hiç kayıt olmayan hücre <b>NA</b> kalır. Pozitif hücre bile tam gözlem kapsamını kanıtlamaz. Paket bulut maskesi, geçiş çizelgesi veya geçerli gözlem sayısını içermez.')
    h('Aqua örneği: 2018-2026')
    years=list(range(2018,2027));months=['Oca','Şub','Mar','Nis','May','Haz','Tem','Ağu','Eyl','Eki','Kas','Ara']
    vals=m[(m.platform=='Aqua')&m.year.isin(years)].pivot(index='year',columns='month_number',values='detection_count').reindex(index=years,columns=range(1,13))
    heat=[['Yıl']+months]+[[str(y)+('*' if y==2026 else '')]+[str(int(v)) if pd.notna(v) else '-' for v in vals.loc[y]] for y in years]
    t=Table(heat,colWidths=[43]+[38]*12,rowHeights=24)
    commands=[('FONTNAME',(0,0),(-1,-1),'DejaVu'),('FONTSIZE',(0,0),(-1,-1),7),('ALIGN',(0,0),(-1,-1),'CENTER'),('VALIGN',(0,0),(-1,-1),'MIDDLE'),('BACKGROUND',(0,0),(-1,0),INK),('TEXTCOLOR',(0,0),(-1,0),colors.white),('GRID',(0,0),(-1,-1),1.6,colors.white)]
    maximum=math.log1p(float(vals.max().max()))
    for iy,y in enumerate(years,1):
        commands.append(('BACKGROUND',(0,iy),(0,iy),PALE))
        for ix,v in enumerate(vals.loc[y],1):
            f=math.log1p(v)/maximum if pd.notna(v) else 0
            rgb=sample_colorscale('Cividis',[f])[0] if pd.notna(v) else 'rgb(230, 235, 239)'
            nums=[float(n.strip())/255 for n in rgb[4:-1].split(',')]
            commands.append(('BACKGROUND',(ix,iy),(ix,iy),colors.Color(*nums)))
            commands.append(('TEXTCOLOR',(ix,iy),(ix,iy),colors.white if pd.notna(v) and f<0.5 else INK))
    t.setStyle(TableStyle(commands));story.append(t);story.append(Spacer(1,9))
    p('Sayılar gerçek tespit adedi; bu basılı tabloda yalnız renk log(1+n) ölçeğindedir. Gri “-” hücre kayıt yok/kapsam bilinmiyor anlamındadır; sıfır yangın değildir. 2026* kısmi yıldır. Kaynak: işlenmiş aylık tablo, ham CSV sayımıyla karşılaştırıldı.','small')
    h('Kısmi dönem nasıl işaretlenir?')
    p('Tarih filtresi ayı keserse selection_partial_month; ilk/son tespit ayıysa record_extent_boundary; 2026 ise partial_reference_year işaretlenir. Bunlar veri çekim kapsamının belgesi değildir. Başlangıç yılları da platforma göre kısmi olabilir.')
    p('Örnek: Temmuz 2021 Aqua 426, Ağustos 339 tespit; aritmetik fark 87’dir. Bu, 87 ayrı yangın farkı değildir. Aynı olay günlerce sürmüş veya birçok piksel üretmiş olabilir. 2026 Kasım NOAA-21’de beş kayıt vardır; bütün Kasım’ın beş yangını demek yanlıştır.')
    p('2000-2026 takviminde beş platform için 1.620 platform-ay hücresi; 825 pozitif, 795 NA. NA hücrelerinin çoğunda platform henüz başlamamış veya paket tespit aralığı dışındadır. Bu oran veri kaybı ya da yangınsızlık oranı olarak kullanılmaz.','small')

    # 8 - Method.
    page('6. Uyumlaştırmayı nasıl sınadık?')
    p('Bir dosya tablosunu ortak şemaya çevirmek ile iki sensörü eşdeğer yapmak farklı işlemlerdir. Gerçek bir uyumlaştırma, bulutsuz geçerli gözlem kapsamını ve gözlem zamanını da ele almalıdır. Bu girdiler pakette yoktur.')
    h('Önce gözlem kapsamı')
    p('Sonraki bilimsel aşama için yangın maskeleri, bulut/geçerli gözlem maskeleri ve geçiş bilgisi gerekir. Uygun ortak projeksiyonda hücre-gün veya yakın geçiş çiftleri oluşturulabilir. Hücre boyu, zaman toleransı, kalite ve mevsim seçimi ayrıca sınanmalıdır. Bağımsız yangın kayıtları da olay düzeyinde doğrulama sağlayabilir.')
    h('Bu veriyle yapılabilen açıklanabilir deney')
    p('Yalnız arşiv kullanıldı; 2026 dışlandı. Her VIIRS platformu ayrı ayrı Aqua ile eşleştirildi. Yalnız iki platformun da pozitif kaydı bulunan aylar alındı. Bu koşul eksik ayları sıfır saymayı önler, fakat seçilim yanlılığı yaratır; tüm aylar için geçerlilik sağlamaz.')
    code('x = VIIRS platformunun aylık kayıt sayısı\ny = Aqua aylık kayıt sayısı\nk = toplam(x*y) / toplam(x*x)   [yalnız eğitim ayları]\ndeneysel tahmin = k*x\nMAE = toplam(|tahmin - Aqua kaydı|) / test ayı sayısı')
    tab(['Platform','Eğitim sonu','Ayrılmış test yılları'],[['Suomi-NPP','2021','2022-2025'],['NOAA-20','2022','2023-2025'],['NOAA-21','2024','2025']],[170,120,209])
    p('Model başlangıçtan geçen en küçük kareler ölçeklemesidir. Örneklemdeki büyük aylara duyarlı olduğu için 2021 çıkarılarak tekrar sınandı. Ayrıca bütün güven değerleri ile MODIS ≥30 / VIIRS n-h filtresi karşılaştırıldı. Test verisi katsayı öğreniminde kullanılmadı.')
    h('Gerçek katsayı hesabı')
    train=pairs[(pairs.target=='Suomi-NPP')&(pairs.confidence=='all')&(pairs.split=='train')]
    sx=int(train.target_count@train.aqua_count);sxx=int(train.target_count@train.target_count)
    p(f'S-NPP/Aqua eğitim çiftlerinde Σxy={fmt(sx)}; Σx²={fmt(sxx)}. Dolayısıyla k={sx/sxx:.6f}. Ara hesaplar reports/overlap_pairs.csv dosyasından yeniden üretilebilir. Bu katsayı doğrulanmış bir sensör dönüşüm sabiti değildir.','small')

    # 9 - Experimental results.
    page('7. Deney sonucu: temkinli karar')
    p('MAE, test aylarında Aqua tespit sayısına göre ortalama mutlak farktır. Düşük olması yalnız bu karşılaştırmada daha küçük sayısal hatayı gösterir; gerçek yangın algılama doğruluğunu ölçmez.')
    tab(['Hedef / güven','Eğitim / test ayı','k','Model MAE','Mevsimsel MAE'],[[x['target']+' / '+('tümü' if x['confidence']=='all' else 'filtreli'),f"{x['train_months']} / {x['test_months']}",f"{x['coefficient']:.4f}",f"{x['heldout_mae']:.3f}",f"{x['seasonal_baseline_mae']:.3f}"] for x in ex],[149,85,65,100,100])
    p('Temel model: eğitim dönemindeki aynı takvim ayının Aqua medyanı; o ay yoksa genel eğitim medyanı. Ölçeklenmemiş VIIRS, genel medyan, yanlılık ve korelasyon da deney JSON’unda yer alır. Bunların hiçbiri doğruluk yüzdesi olarak sunulmaz.','small')
    h('2021 çıkarıldığında ne oluyor?')
    tab(['Platform','Bütün eğitimde k','2021 hariç k','Yorum'],[[x['target'],f"{x['coefficient']:.6f}",f"{x['coefficient_without_2021']:.6f}",'Belirgin duyarlılık'] for x in ex if x['confidence']=='all' and x['target']!='NOAA-21'],[125,110,110,154])
    p('S-NPP katsayısı yaklaşık 0,192’den 0,115’e; NOAA-20 yaklaşık 0,167’den 0,077’ye iner. 2021 büyük tespit ayları sonucu güçlü biçimde etkiler. Bu durum tek katsayının mevsim, olay büyüklüğü ve gözlem değişkenliğini açıklamakta yetersiz kalabileceğini gösterir.')
    h('Neden takvimde bu katsayıyı kullanmıyoruz?')
    p('S-NPP ve NOAA-20 test hatası basit mevsimsel modelden daha yüksek. NOAA-21’de daha küçük hata görülse de test sadece 11 ortak pozitif ay içeriyor. Bütün modellerde gözlem kapsamı bilinmiyor. Sonuç: <b>DENEYSEL / DOĞRULANMADI</b>. Uygulama gerçek platform kayıtlarını korur, sahte bir sensörden bağımsız süreklilik üretmez.')
    p('Takımın savunabileceği yaklaşım: “Uyumlaştırma adayını tanımladık, ayrılmış dönemde sınadık, sınırlılığını gösterdik ve kanıt yetmediği için birleşik takvime uygulamadık.”')

    # 10 - App.
    page('8. Web uygulaması ve CSV')
    p('Yan menüde UTC başlangıç/bitiş tarihi, sensör ailesi, platform ve işleme türünü seçin. Bölge alanında dört koordinatla alt dikdörtgen tanımlayın. Ana ekranda tespit adedi, NRT sayısı ve son tespit tarihi görünür.')
    tab(['Sekme','İşlev'],[['Takvim ve grafik','Platform takvimi; ortak renk seçeneği; ayrı platform çizgileri'],['Tespitler ve indirme','Koordinatlı CSV, GeoJSON, aylık CSV ve seçim JSON’u'],['Veri denetimi','Kopya eşitliği; platform/arşiv/NRT özetleri'],['Yöntem ve kaynaklar','Deney sonuçları, sınırlılıklar ve NASA bağlantıları'],['Harita','Seçili noktalar; çalışma kutusu; isteğe bağlı OSM'],['Aynı ayı karşılaştır','Bir platformun aynı UTC ayı; yıllar, NA ve kısmi yıl']],[134,365])
    h('Jüri önünde uygulanabilecek kısa demo')
    for t in ['1. Varsayılan açılışta 29.640 kaydı ve 2026 kısmi yıl uyarısını gösterin.','2. Sensör MODIS; platform yalnız Aqua; 01/07/2021-31/07/2021: 426 tespit.','3. Aynı ayda S-NPP seçilirse 2.268 tespit. Farkın neden tek başına yangın farkı olmadığını açıklayın.','4. CSV’yi indirin. timestamp_utc, platform ve kaynak satır sütunlarını açın.','5. Deney tablosundaki “doğrulanmadı” kararının gerekçesini iki cümleyle anlatın.']:p(t)
    h('İndirme sözleşmesi')
    p('CSV virgülle ayrılır ve Türkçe karakterler için UTF-8 BOM içerir. UTC zaman damgasında +00:00 korunur. Boş aylık sayı boş hücredir. Boş bir tespit sorgusu yalnız sütun başlıklı CSV üretir. Excel’de gerekirse Veri &gt; Metin/CSV’den menüsünü kullanın.')
    p('Seçim JSON’u tarih, kutu, platform, güven/tür filtresi ve ham ZIP SHA-256 özetlerini saklar. Aynı seçim daha sonra yeniden kurulabilir. Arşiv/NRT ayrımı tespit CSV’sinde kalır. Tam kaynak satır eşlemesi reports/provenance.csv içindedir.')
    p('v1.1 tarayıcı testinde 426 Aqua kaydı görüldü; CSV ve GeoJSON indirildi. Koordinatlar, platform ve kaynak alanları eşleşti. CSV v1 çıktısıyla aynıdır. Harita ve karşılaştırma ekran kanıtları reports/ içindedir.','small')

    # 11 - Windows.
    page('9. Windows kurulumu')
    p('<b>PLANLAMA VARSAYIMI:</b> Windows 10/11, 64 bit Python 3.12, modern tarayıcı, ilk kurulum için internet ve yazılabilir klasör. Kullanıcı cihazları bilinmiyor. Windows’ta test yapılmadı; burada uygulama adımları veriliyor.')
    p('1. ZIP’i bilgisayara indirin. Sağ tık &gt; Tümünü ayıkla ile çıkarın. İçte app.py bulunan focustm_fire_v1_1 klasörüne girin. ZIP içinden çalıştırmayın.')
    p('2. '+link('Resmî Python Windows sayfasından','https://www.python.org/downloads/windows/')+' Python 3.12 64 bit sürümünü kurun. Python Launcher (py) seçeneği bulunmalı. Mevcut Python’u kaldırmanız gerekmez.')
    p('3. Komut İstemi (cmd) açın. Aşağıdaki ilk yolu kendi klasörünüze göre uyarlayın:')
    code('cd /d C:\\FocusTM\\focustm_fire_v1_1\npy -3.12 --version\npy -3.12 -m venv .venv\n.venv\\Scripts\\python.exe -m pip install -r requirements.txt\n.venv\\Scripts\\python.exe -m streamlit run app.py')
    p('4. Terminalin yazdığı http://127.0.0.1:8501 adresini tarayıcıya girin. Terminal açık kalmalı. Durdurmak için Ctrl+C.')
    p('5. Sonraki açılışlarda CALISTIR_WINDOWS.bat dosyasını kullanabilirsiniz. İlk kurulum yardımcı dosyası KUR_WINDOWS.bat’tir. Sanal ortam doğrudan çağrıldığı için PowerShell yürütme politikası değiştirilmez.')
    h('En sık karşılaşılan durumlar')
    tab(['Durum','Çözüm'],[['py bulunamadı','Python Launcher kurulumunu doğrulayın, yeni terminal açın.'],['Kütüphane eksik','Pip ve Streamlit için aynı .venv Python’unu kullanın.'],['Port 8501 dolu','Komuta --server.port 8502 ekleyin, yeni adresi açın.'],['Paket indirme hatası','İnternet/proxy durumunu sistem sorumlusuyla kontrol edin.'],['Telefon/WhatsApp içinde açılmıyor','ZIP’i bilgisayarda çıkarın; bu bir telefon uygulaması değildir.']],[140,359])
    p('Donanım alt sınırı bu çalışmada ölçülmedi. GPU gerekmez. İlk kurulum kütüphaneleri internetten indirir; çalışma verileri ZIP içinde hazırdır. Ayrıntı KURULUM.md.','small')

    # 12 - Mac and reproduce.
    page('10. Mac ve yeniden üretim')
    p('Gerçek çalışma testi: macOS 26.7, arm64, Python 3.12.14. Bu, bütün Mac modellerinin veya sıfırdan Python kurulumunun test edildiği anlamına gelmez. Intel Mac ve Linux test edilmedi.')
    p('ZIP’i çıkarın. '+link('Resmî Python macOS sayfasından','https://www.python.org/downloads/macos/')+' Python 3.12 kurun veya mevcut 3.12’yi kullanın. Terminal’de cd komutuyla app.py bulunan klasöre geçin:')
    code('python3.12 --version\npython3.12 -m venv .venv\n.venv/bin/python -m pip install -r requirements.txt\n.venv/bin/python -m streamlit run app.py')
    p('Sonraki açılış: bash calistir_mac.sh. İlk kurulum yardımcı komutu: bash kur_mac.sh. Sistem Python 3.9 bu bağımlılık setinin hedefi değildir.')
    h('Ham dosyadan sonuca yeniden gitmek')
    code('.venv/bin/python pipeline.py\n.venv/bin/python -m pip install -r requirements-dev.txt\n.venv/bin/python -m pytest -q\n.venv/bin/python scripts/verify_sources.py\n.venv/bin/python scripts/build_guide.py')
    p('Windows’ta aynı komutlarda .venv/bin/python yerine .venv\\Scripts\\python.exe kullanılır. PDF üretimi isteğe bağlıdır; hazır PDF pakettedir. Görsel PDF denetimi için Poppler ayrıca gerekir.')
    tab(['Dosya/klasör','Sorumluluk'],[['data/raw','Değiştirilmemiş 12 ZIP'],['core.py / pipeline.py','Doğrulama, tekilleştirme, filtre, aylık hesap ve deney'],['data/processed','detections.csv ve monthly.csv'],['app.py','Türkçe arayüz; hesap mantığı core.py içinde'],['reports','Denetim, kaynak izi, deney ve test kanıtı'],['docs / tests / licenses','Rehber, kaynaklar, testler ve lisanslar']],[170,329])
    p('Yerel sunucu 127.0.0.1’e bağlanır. Veri ve grafikler yereldir; isteğe bağlı OpenStreetMap altlığı internet ister. Harita WebGL2 ister. Ağ tamamen kapalı senaryo test edilmedi. Canlı NASA API’si veya API anahtarı yoktur.')

    # 13 - Tests.
    page('11. Gerçekte hangi testler yapıldı?')
    p(f'<b>{nt} otomatik test; {nf} başarısızlık/hata.</b> Çalıştırma çıktısı reports/pytest_output.txt ve test_results.xml içindedir. Test sayısı bir bilimsel doğruluk yüzdesi değildir.')
    tab(['Kontrol','Kanıt'],[['Koordinat ve tarih','Sınırlar dahil; UTC; 0054; artık gün; hatalı saat/tarih reddi'],['Tekrar sayım','CSV/JSON/SHP eşitliği; aynı ZIP iki kez verilince 29.640 sabit'],['Platform ve eksik veri','Terra/Aqua ayrımı; SNPP normalizasyonu; NA aylar; NRT türü'],['İndirme','BOM, UTC, boş sonuç başlığı; gerçek tarayıcıdan 426 kayıt'],['Ham kaynak karşılaştırması','825 platform-ay grubu tam eşleşti; bütün satırlar kaynağa izlenir'],['Deney ayrımı','Test yılları eğitime karışmaz; test verisi değişince eğitim k sabit'],['Arayüz','AppTest açılış ve filtreler; gerçek tarayıcı seçimi ve görsel kontrol']],[147,352])
    h('Ham veri örnekleri')
    tab(['Platform / ay','Ham CSV','İşlenmiş sonuç'],[['Aqua / 2021-07','426','426'],['Terra / 2021-07','364','364'],['S-NPP / 2021-07','2.268','2.268'],['NOAA-20 / 2021-07','2.580','2.580'],['NOAA-21 / 2026-11','5','5']],[239,130,130])
    p('verify_sources.py, core.py’deki toplama işlevini çağırmadan Python standart csv kütüphanesiyle ham CSV’leri sayar. Böylece aynı uygulama mantığının kendi kendini onaylamasıyla yetinilmez. Tüm pozitif aylar eşleştirilir, eksik hücrelerin boş kaldığı kontrol edilir.')
    h('Test edilmemiş olanlar')
    p('Windows, Linux, Intel Mac; sıfırdan işletim sistemi/Python yükleyici akışı; çok kullanıcılı internet yayını; mobil cihaz; ekran okuyucuyla kapsamlı erişilebilirlik testi; bağımsız yangın yer doğrulaması ve canlı NASA API akışı. Bu sınırlar başarı iddiasına dönüştürülmez.')
    p('Testlerdeki küçük sentetik sınır örnekleri yalnız yazılım kontrolü içindir, analitik veri setine eklenmez. PDF sayfaları üretim sonrası PNG’ye çevrilip görsel olarak incelenir; son kontrol kaydı reports/pdf_qa.json içindedir.','small')

    # 14 - Jury Q/A.
    page('12. Jüri soruları ve kısa cevaplar')
    qa=[
        ('Veriyi hangi yazılım/işlemciyle çözdünüz?','Python 3.12 ile; pandas/NumPy hesap, PyShp coğrafi dosya okuma, Streamlit/Plotly arayüz ve grafik için kullanıldı. Bu test Mac arm64 CPU’da yapıldı. Özel GPU gerekmiyor.'),
        ('Sıfırdan NASA yangın algılama algoritması yazdınız mı?','Hayır. NASA FIRMS’in hazır sıcak nokta ürünlerini analiz eden veri hattı ve web prototipi kurduk.'),
        ('Kodlamayı neye göre sınırlandırdınız?','Sağlanan dikdörtgen, gerçek kayıt tarihleri, platform/işleme etiketleri ve açık kalite seçenekleriyle. Kutu dışı veri üretmiyoruz; 2026’yı kısmi gösteriyoruz.'),
        ('29.640 yangın mı var?','29.640 tespit kaydı var. Bir yangın çok sayıda piksel, geçiş ve uydu kaydı üretebilir; olay sayısı çıkarılmadı.'),
        ('MODIS ve VIIRS niçin farklı sayılar veriyor?','Çözünürlük, küçük sıcak noktalara duyarlılık, geçiş zamanı, bulut ve algoritma farkları nedeniyle.'),
        ('Neden tek bir uyumlu seri sunmadınız?','Aday dönüşümü test ettik; katsayı kararsız ve gözlem kapsamı eksik. Kanıt yetmediğinde sensör farkını gizlemedik.'),
        ('Boş ay sıfır yangın değil mi?','Hayır. Paket o ay kayıt içermeyebilir; gözlem olup olmadığını bilmiyoruz. NA ile işaretliyoruz.'),
        ('Arşiv ve NRT aynı mı?','Dosya etiketlerini ve version değerlerini ayrı tutuyoruz. NRT geçici üründür, bu dosyalarda type alanı yoktur.'),
        ('Yanmış alanı ölçtünüz mü?','Hayır. Bu aktif sıcak nokta ürünüdür; yanmış alan için ayrı ürün/metodoloji gerekir.'),
        ('Ne kadar doğru?','Uyduların algılama doğruluğu burada ölçülmedi. Veri işleme testleri ve ham kaynak sayım eşitliği doğrulandı; bunları doğruluk yüzdesi diye sunmuyoruz.'),
        ('AI kullanıldı mı?','Evet. Kod/doküman/test taslağında Codex desteği kullanıldı. Gerçek hesaplar Python ile ham dosyalardan üretildi; katkı ve karar kaydı açık.'),
        ('Sonraki bilimsel adım ne?','Geçerli gözlem/bulut/geçiş verisini eklemek; aynı mekân-zaman biriminde platform karşılaştırmasını ve bağımsız doğrulamayı yapmak.')]
    for q,ans in qa:p('<b>'+q+'</b><br/>'+ans,'small')
    p('Takım, öğrencilerin gerçekte yaptığı veri seçimi, yorumlama, kod değişikliği ve sunum katkılarını ayrıca kaydetmelidir. Yapılmayan işi yapılmış gibi anlatmayın.','small')

    # 15 - References & conflicts.
    page('13. Kaynaklar ve açık konular')
    sources=[
        ('S1','NASA FIRMS arşiv indirme / ürün dönemleri','https://firms.modaps.eosdis.nasa.gov/download/'),
        ('S2','NASA FIRMS README / ZIP biçimleri ve kullanım notları','https://firms.modaps.eosdis.nasa.gov/download/Readme.txt'),
        ('S3','NASA MODIS alan açıklamaları','https://firms.modaps.eosdis.nasa.gov/content/descriptions/FIRMS_MODIS_Firehotspots.html'),
        ('S4','NASA VIIRS alan açıklamaları','https://firms.modaps.eosdis.nasa.gov/content/descriptions/FIRMS_VIIRS_Firehotspots.html'),
        ('S5','NASA FIRMS uyarı ve tespit sınırlılığı notları','https://firms.modaps.eosdis.nasa.gov/alerts/notes.php'),
        ('S6','NASA VIIRS C2 kullanıcı rehberi v1.2','https://www.earthdata.nasa.gov/s3fs-public/2025-06/VIIRS_C2_AF-375m_User_Guide_1.2.pdf'),
        ('S7','NASA FIRMS kesinti ve Type düzeltme bildirimleri','https://firms2.modaps.eosdis.nasa.gov/content/notifications/firms/outages.html')]
    p('Kontrol tarihi 14/11/2026. Aşağıdaki başlıklar tıklanabilir. Tam bağlantılar docs/KAYNAKLAR.md içinde de yer alır. Analitik kayıtlar yalnız kullanıcı tarafından sağlanan 12 ZIP’ten alınmıştır.','small')
    for sid,label,url in sources:p(f'<b>{sid}</b> · '+link(label,url),'small')
    h('Resmî sayfalardaki farkları saklamadık')
    p('S2’de NOAA-20/21 standart arşivinin henüz olmadığı yazarken sağlanan ZIP’ler arşiv dosyası ve type alanı içeriyor. S2 yaklaşık üç aylık; S1 yaklaşık beş aylık arşive geçiş gecikmesi belirtiyor. S4’ün NOAA-20/21 başlangıçları S1’den farklı. S3 Aqua için 03/07/2002; görsel 04/07/2002 der. Pakette ilk Aqua tespiti 04/07/2002’dir. Yerel tarih ve dosya etiketleri kullanıldı; kesintisiz resmî kapsam iddiası kurulmadı.')
    h('DOĞRULANAMADI')
    p('Tam indirme isteğinin tarih/bölge parametreleri; bulutsuz geçerli gözlem kapsamı; bütün günlerin eksiksizliği; VIIRS Type düzeltmesinin bu ZIP’lere uygulanması; MODIS 6.03/61.03 sürüm geçmişi; bağımsız yangın envanteri; teslim rehberi ve AI’ye özgü kesin kurallar. Katılımcı koşulları için s.20 kontrol notuna bakın.')
    p('S7, VIIRS aylık ürünlerde Type alanına ilişkin eski bir hatayı ve Mayıs 2025 düzeltmesini bildirir. Paketteki version=2 koleksiyon etiketinden üretim yazılımının düzeltme sürümü çıkarılamaz. Type filtreleri bu nedenle ihtiyatla sunulur. Earthdata birleşik alan ve FAQ sayfaları bu oturumda 403 verdi; erişilebilir NASA FIRMS açıklamaları kullanıldı.','small')
    p('NASA FIRMS/ESDIS veri kullanımı kabulü: NASA’nın açık veri katkısı kaynak gösterilir. '+link('NASA atıf ve veri kullanımı','https://www.earthdata.nasa.gov/engage/open-data-services-software-policies/data-use-policy')+' ve S2 kullanım sorumluluğu korunur. Prototip NASA onaylı değildir; operasyonel müdahale kararında tek başına kullanılacak şekilde doğrulanmamıştır.','small')

    # 16 - Licenses and AI.
    page('14. Lisanslar, kararlar ve AI katkısı')
    tab(['Bileşen','Lisans','Rol'],[['Python','PSF','Çalıştırıcı'],['pandas / NumPy','BSD-3-Clause','Veri ve sayısal hesap'],['Streamlit','Apache-2.0','Web arayüzü'],['Plotly / PyShp / pytest','MIT','Grafik / Shapefile / test'],['ReportLab / pypdf','BSD / BSD-3-Clause','PDF üretim ve kontrol'],['Pillow','MIT-CMU','Kontrol görselleri'],['DejaVu Sans','Bitstream Vera / DejaVu','Türkçe PDF yazı tipi'],['Poppler','GPL-2.0-or-later','PDF görüntüleme; ikili paketlenmedi']],[165,155,179])
    p('Sabitlenmiş doğrudan bağımlılıklar requirements.txt ve requirements-dev.txt içinde. Lisans metinleri ve kurulu metadata licenses/ içinde; kaynak bağlantıları THIRD_PARTY_NOTICES.md’dedir. Kütüphane ikilileri/sanal ortam WhatsApp ZIP’ine dahil değildir. NASA verisi bu yazılım lisanslarıyla lisanslanmaz. FocusTM koduna kullanıcı adına ayrıca bir açık kaynak lisansı atanmadı.','small')
    h('Karar kaydı')
    p('Ham kaynaklar korunacak; üç biçim tekilleştirilecek; platformlar saklanacak; boş ay NA olacak; 2026 kısmi işaretlenecek; tür/güven filtresi açık olacak; deneysel katsayı ana takvime uygulanmayacak. Gözlem kapsamı sağlanmadan anomali alarmı ve doğrulanmış erken uyarı eklenmeyecek. Bu kararlar docs/KARARLAR_AI.md içinde izlenebilir.')
    h('AI hangi işi yaptı?')
    p('Codex, veri denetimi kodu, işleme hattı, Streamlit ekranı, testler ve rehber taslağının hazırlanmasına katkı verdi; araçlarla kodu çalıştırdı ve sonuçları kontrol etti. NASA’nın algılama algoritmaları veya bağımsız saha doğrulaması üretilmedi. Sahte analitik veri ve uydurma doğruluk oranı kullanılmadı.')
    h('Öğrencinin sunum sorumluluğu')
    p('Takım gerçek katkılarını açıklamalı, kaynakları göstermeli ve yöntemi kendi sözcükleriyle anlatabilmelidir. AI kullanımı gizlenmemelidir. Önerilen beyan: “NASA FIRMS verisini Python ile analiz eden tekrarlanabilir bir prototip hazırladık. Kod ve dokümantasyonda AI desteği kullandık. Veri kaynaklarını, denemeleri ve sınırlılıkları açıkça raporluyoruz.”')
    p('Jüriye verilecek temel mesaj: Değerli bir veri ürünü yalnız renkli grafik değildir; doğru sayım, kaynak izi, test ve belirsizliğin dürüst gösterimidir. Bir sonraki adım sensörleri görünmez yapmak değil, karşılaştırılabilirliği kanıtlamaktır.')

    page('15. v1.1: harita ve betimsel örnek')
    p('<b>Antalya odaklı çalışma alanı</b> haritası, yan menüde seçilen bütün tespit noktalarını sensör/platform bilgisiyle gösterir. Örnekleme yapılmaz; üst üste gelen noktalar ayrı kayıtlardır. Koyu çerçeve 29.5, 36.1, 32.8, 37.5 kutusu, turuncu çerçeve varsa seçili alt bölgedir. İl sınırı, olay çevresi veya yanmış alan değildir.')
    p('Varsayılan beyaz zemin harici karo istemez; yol/kıyı çizmez. OpenStreetMap altlığı isteğe bağlıdır ve internet ister. WebGL2 desteklenmezse harita çalışmayabilir; koordinatlı CSV/GeoJSON ve tablolar kullanılabilir. Ağ tamamen kapalı test yapılmadı. Kaynak: NASA FIRMS; altlık © OpenStreetMap contributors / ODbL. [E1-E3]','small')
    h('GeoJSON ve ortak renk ölçeği')
    p('Her seçili tespit bir Point olarak indirilir; sıra <b>[boylam, enlem]</b>, WGS84’tür. Platform, UTC ve kaynak izi korunur. Çalışma kutusu metadata içindedir; tespit sayısına poligon eklenmez. [E4]')
    p('Takvimde ortak renk seçeneği varsayılan açıktır: seçili tarih/bölge ve platform kümesinde tek üst sınır kullanılır. Kapatılırsa aynı renk farklı sayılara karşılık gelebilir. Filtreler değişirse üst sınır yeniden hesaplanır. Ortak renk, ortak algılama ölçeği değildir.')
    h('Gerçek örnek: Aqua / Temmuz / 2018-2026')
    example=pd.read_csv(ROOT/'reports/Aqua_Temmuz_2018_2026.csv')
    tab(['Yıl','Tespit','Gözlem kapsamı / yıl'],[[str(int(r.year))+('*' if r.year==2026 else ''),str(int(r.detection_count)),'Bilinmiyor / '+('kısmi yıl' if r.year==2026 else 'takvim yılı')] for r in example.itertuples()],[90,100,309])
    p('Aynı ayı karşılaştır sekmesi, yan menüdeki tarihlerin <b>yıllarını</b> kullanıp tam UTC aylarını alır; gün/ay kesmelerini kullanmaz. Diğer filtreler korunur. 2021’de 426 tespit bulunduğunu söyleriz; bunun 426 yangın olayı olduğunu söylemeyiz. Boş hücre NA kalır.','small')

    page('16. HOLD sonrası en küçük yöntem')
    h('Şema birleştirme ile sensör düzeltmesi ayrı işlerdir')
    p('Alan adları, UTC ve kaynak izi ortaklaştırıldı. Çözünürlük, geçiş ve algılama farklarının düzeltildiği kanıtlanmadı. Mevcut S-NPP/NOAA-20 deneyleri mevsimsel karşılaştırmayı geçmedi; NOAA-21 testi kısadır. Katsayılar takvime uygulanmaz. Harita eklemek bu açığı çözmez.')
    h('Bu sürümde yapılan savunulabilir adım')
    p('Aynı platformun aynı ayını, sabit bölge ve seçili işleme/kalite koşullarıyla yıllar arasında betimsel göstermek. Geçerli gözlem sayısı bilinmediğinden artış oranını olay artışı, istatistiksel anomali veya alarm olarak sunmamak.')
    h('Ek veri gelirse küçük pilot - henüz yapılmadı')
    for t in [
      '1. Aqua ve S-NPP için kapsamı belgelenmiş kısa ortak arşiv dönemi seçin; ürün sürümlerini kaydedin.',
      '2. Tam yangın/kalite/bulut maskeleri, piksel konumları ve geçiş zamanlarını alın. İki platformun da geçerli gözlem yaptığı örnekleri belirleyin.',
      '3. Ortak eş-alanlı hücrelerde yakın geçişleri eşleştirin. 1/2/5 km ve 30/60 dakika yalnız tasarım/duyarlılık seçenekleridir; doğrulanmış eşikler değildir.',
      '4. Eşleşmiş hücre-geçişte en az bir tespit var/yok bilgisini ve pozitif uyum/uyumsuzluğu karşılaştırın. Geçerli gözlem yoksa sıfır kodlamayın.',
      '5. Ayar ve sonraki test dönemlerini ayırın; hücre/zaman seçimine duyarlılığı ve belirsizliği raporlayın. Kısa pilotu 25 yıllık ortak serinin doğrulanması saymayın.']:p(t)
    h('Gereken ek kanıt')
    p('Geçerli gözlem paydası ve ayak izi; bulut/kalite maskesi; geçiş zamanı ve ürün sürümü; tespit olmayan geçerli gözlemler. Olay düzeyinde iddia için bağımsız, zaman/konum bilgili olay envanteri de gerekir.')
    p('Detay ve uygulanmayan tasarım varsayımları docs/EN_KUCUK_YONTEM.txt içindedir. Bu öneriden sahte sonuç veya doğrulanmış sensör katsayısı üretilmedi.','small')

    page('17. Dört kişilik jüri konuşması')
    p('Hedef yaklaşık üç dakika; süre prova varsayımıdır. Tam metin ve ekran adımları docs/JURI_KONUSMALARI.txt içindedir. Konuşmacılar kendi gerçek katkılarını eklemelidir.','small')
    h('1 / Sorun ve kullanıcı')
    p('“Geçmiş sıcak nokta kayıtlarını tek tek okumak, yoğun dönemleri görmeyi zorlaştırıyor. FocusTM, acil durum ve arazi yönetimi ekipleriyle araştırmacıların bu geçmişi incelemesi için hazırlanmış öğrenci prototipi. Tarih, bölge ve platform seçerek aylık kayıtları görebiliyoruz. Saydığımız şey uydu tespiti; bağımsız yangın olayı veya yanmış alan değil.”')
    p('Ekran: ana sayfa, sayım birimi ve 2026 uyarısı.','small')
    h('2 / Veri ve çalışma alanı')
    p('“12 NASA FIRMS ZIP’ini açtık. Aynı kayıtların CSV, JSON ve Shapefile kopyalarını bir kez sayınca 29.640 tespit kaldı. S-NPP toplamı 12.562. Antalya odaklı çalışma alanımız 29.5, 36.1, 32.8, 37.5 sınırlarıyla tanımlanan dikdörtgen; il sınırı değil. Harita seçili noktaları ve bu çerçeveyi gösteriyor.”')
    p('Ekran: Veri denetimi, ardından Harita.','small')
    h('3 / Python ve sensör farkları')
    p('“Python ile UTC tarihleri ayrıştırdık, kaynak izini koruduk ve platform bazında aylık sayım yaptık. Kod ve belgelerde AI desteği kullandık. MODIS yaklaşık 1 km, VIIRS yaklaşık 375 m nominal piksele sahip; geçişleri de farklı. Şemayı birleştirmek bu farkları düzeltmez. Katsayı deneyimiz yeterli kanıt sağlamadı; takvime uygulamadık.”')
    p('Ekran: Yöntem ve kaynaklar; doğrulanmadı kararı.','small')
    h('4 / Demo, sınırlar ve sonraki adım')
    p('“MODIS, Aqua ve 1-31 Temmuz 2021 seçince 426 tespit görüyoruz. CSV ve boylam/enlem sıralı GeoJSON indirebiliyoruz. Yıl aralığını genişletip aynı ayı karşılaştırabiliriz. Boş hücre sıfır yangın değil; kapsam bilinmiyor, 2026 kısmi. Harita bu eksikliği çözmez. Sonraki adım geçerli gözlem ve bulut/geçiş verisiyle küçük eşleşmiş pilot. Bu sürüm tam CBS veya canlı uyarı sistemi değil.”')
    p('Ekran: 426 -> indirme -> 2018-2026 yıl aralığı -> Aynı ayı karşılaştır / Aqua / Tem.','small')

    page('18. Teslim ve lisans kontrolü')
    p('<b>FocusTM proje lisansı seçilmedi.</b> Hak sahipleri karar vermeden MIT/Apache-2.0 atanmaz. Kütüphane lisansları ayrı tutulur. Kullanıcıdan gelen referans görselleri, kamusal dağıtım izni doğrulanmadığı için yeni ZIP’e konmaz; eski v1 korunur.')
    p('2026 katılımcı koşullarının arama dizini, lisans belirtilmezse NASA’nın Apache 2.0 ile dağıtacağını ve kaynak/lisans belgelerini istediğini bildiriyor. Bu, ekip onayı değildir. Doğrudan sayfa ve teslim rehberi 502 verdi; nihai form yeniden kontrol edilmeli. [E5, E6]','small')
    tab(['Ekip kontrolü','Durum'],[['Proje lisansı / hak sahipleri','Karar bekliyor'],['Resmî challenge ve ekip kaydı','Ekip doğrulamalı'],['Teslim saati, biçimi ve AI özel kuralı','DOĞRULANAMADI'],['Yaş, ad/ses/görüntü ve materyal izinleri','Teslimden önce denetlenecek'],['Windows kurulumu','Test edilmedi; gerçek cihazda prova gerekli']],[245,254])
    h('v1.1 doğrulama ve sınırları')
    p(f'{nt} otomatik test geçti. Önceki 25 test değişmedi; 10 ek kontrol GeoJSON, harita, renk ve ay karşılaştırmasını sınadı. Gerçek tarayıcıda 29.640 ve 426, altlıksız/OSM harita, karşılaştırma, CSV/GeoJSON indirme doğrulandı. Ağ kapalı senaryo, Windows, bütün tarayıcılar ve tam CBS yazılımında içe aktarma test edilmedi.','small')
    h('Ek kaynaklar - 14/11/2026')
    for sid,label,url in [
      ('E1','Plotly harita katmanları / white-bg','https://plotly.com/python/tile-map-layers/'),
      ('E2','OpenStreetMap telif / ODbL','https://www.openstreetmap.org/copyright'),
      ('E3','OSM karo kullanım politikası','https://operations.osmfoundation.org/policies/tiles/'),
      ('E4','RFC 7946 GeoJSON standardı','https://www.rfc-editor.org/rfc/rfc7946'),
      ('E5','2026 katılımcı koşulları - erişim notuyla','https://www.spaceappschallenge.org/legal/'),
      ('E6','Teslim rehberi - bu oturumda açılamadı','https://www.spaceappschallenge.org/resources/project-submission-guide/'),
      ('E7','MapLibre GL JS lisansları','https://github.com/maplibre/maplibre-gl-js/blob/main/LICENSE.txt')]:p(sid+' · '+link(label,url),'small')
    p('Plotly MIT, MapLibre BSD-3-Clause; altlık OSM/ODbL. Harita altlığı internet ister ve hizmet garantisi yoktur. Kaynak/izin listesi docs/LISANS_VE_TESLIM_KONTROLU.txt; katkı kaydı docs/KARARLAR_AI.md.','small')

    doc=SimpleDocTemplate(str(OUT),pagesize=A4,rightMargin=48,leftMargin=48,topMargin=45,bottomMargin=55,
        title='FocusTM - MODIS VIIRS Öğrenci Rehberi',author='FocusTM; Codex destekli hazırlık',subject='NASA FIRMS veri denetimi, Python Streamlit prototipi ve bilimsel sınırlar')
    doc.build(story,onFirstPage=footer,onLaterPages=footer)
    print(OUT)

if __name__=='__main__':build()
