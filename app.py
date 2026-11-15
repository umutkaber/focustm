"""Turkish local Streamlit prototype. Run: python -m streamlit run app.py"""
import json
from datetime import timedelta
from datetime import date
from pathlib import Path

import numpy as np
import pandas as pd
import plotly.graph_objects as go
import streamlit as st

from core import BBOX, PLATFORMS, AS_OF, filter_data, monthly_counts, csv_bytes
from features import geojson_bytes, calendar_max, map_figure, same_month_comparison

ROOT = Path(__file__).resolve().parent
MONTHS = ["Oca", "Şub", "Mar", "Nis", "May", "Haz", "Tem", "Ağu", "Eyl", "Eki", "Kas", "Ara"]
COLORS = {"Terra": "#4477AA", "Aqua": "#228833", "Suomi-NPP": "#AA3377", "NOAA-20": "#CCBB44", "NOAA-21": "#66CCEE"}
st.set_page_config(page_title="FocusTM | Yangın Aktivite Takvimi", page_icon="🔥", layout="wide")


@st.cache_resource
def load_outputs(signature):
    df = pd.read_parquet(ROOT / "data/processed/detections.parquet")
    df["timestamp_utc"] = pd.to_datetime(df.timestamp_utc, utc=True)
    df["type"] = df["type"].astype("Int64")
    audit = json.loads((ROOT / "reports/audit.json").read_text(encoding="utf-8"))
    return df, audit


def calendar_figure(monthly, platform, logarithmic, shared=False):
    m = monthly[monthly.platform.eq(platform)]
    years = sorted(m.year.unique())
    z = np.full((len(years), 12), np.nan)
    text = np.full((len(years), 12), "—", dtype=object)
    hover = np.full((len(years), 12), "Seçim dışında", dtype=object)
    for r in m.itertuples():
        iy, im = years.index(r.year), r.month_number - 1
        if pd.notna(r.detection_count):
            value = int(r.detection_count)
            z[iy, im] = np.log1p(value) if logarithmic else value
            text[iy, im] = f"{value:,}".replace(",", ".") + ("*" if r.selection_partial_month or r.record_extent_boundary else "")
        hover[iy, im] = f"{r.month} · {platform}<br>Tespit: {text[iy, im]}<br>{r.status}<br>Gözlem kapsamı: doğrulanmadı"
    fig = go.Figure(go.Heatmap(z=z, x=MONTHS, y=[str(y) + ("*" if y == AS_OF.year else "") for y in years],
        text=text, texttemplate="%{text}", customdata=hover, hovertemplate="%{customdata}<extra></extra>",
        colorscale="Cividis", zmin=0, zmax=calendar_max(monthly, platform, logarithmic, shared),
        colorbar=dict(title="log(1+n)" if logarithmic else "Tespit", tickformat=".1f" if logarithmic else ",.0f"),
        xgap=3, ygap=3, hoverongaps=False))
    fig.update_layout(height=max(300, len(years)*28 + 100), margin=dict(l=10,r=10,t=20,b=20),
        paper_bgcolor="white", plot_bgcolor="#e8edf1", font=dict(family="Arial", color="#193047"))
    fig.update_yaxes(autorange="reversed", title="Yıl (UTC)", type="category")
    fig.update_xaxes(side="top", title=None)
    return fig


def main():
    st.markdown("""<style>
    .stApp {background:#f7f9fc;} .block-container {padding-top:4rem;}
    h1,h2,h3 {color:#142e46;} [data-testid="stMetric"] {background:white;border:1px solid #dfe7ee;padding:16px;border-radius:10px;}
    [data-testid="stMetricValue"] > div {font-size:1.7rem;white-space:normal;overflow:visible;text-overflow:clip;}
    [data-testid="stMetricLabel"] p {white-space:normal;}
    [data-testid="stSidebar"] {background:#eef3f7;}
    </style>""", unsafe_allow_html=True)
    st.caption("FOCUSTM  /  NASA FIRMS  /  ÖĞRENCİ PROTOTİPİ · v1.1")
    st.title("Yangın Aktivite Takvimi")
    st.markdown("**Türkiye odaklı çalışma alanı · 2000–2026**  \nMODIS ve VIIRS sıcak nokta kayıtlarını platform bazında keşfedin. Çalışma alanı bir dikdörtgendir; Türkiye il sınırı değildir.")
    if not (ROOT / "data/processed/detections.parquet").exists():
        st.error("İşlenmiş veri bulunamadı. Proje klasöründe `python pipeline.py` çalıştırın.")
        st.stop()
    sig = tuple((ROOT / p).stat().st_mtime_ns for p in ["data/processed/detections.parquet", "reports/audit.json"])
    full, audit = load_outputs(sig)
    with st.sidebar:
        st.header("Analiz seçimi")
        st.caption("Tüm tarihler UTC. Paket canlı güncellenmez. Tarih aralığı en fazla 5 yıl olabilir.")
        default_end = AS_OF
        default_start = AS_OF - timedelta(days=7)

        start = st.date_input("Başlangıç (UTC)", default_start, min_value=date(2000,1,1), max_value=AS_OF, key="start")
        end_max = min(AS_OF, start + timedelta(days=1827))
        st.session_state["end"] = min(st.session_state.get("end", default_end), end_max)
        end = st.date_input("Bitiş (UTC, gün dahil)", min_value=date(2000,1,1), max_value=end_max, key="end")
        sensor = st.selectbox("Sensör ailesi", ["Tümü", "MODIS", "VIIRS"], key="sensor")
        available = PLATFORMS if sensor == "Tümü" else PLATFORMS[:2] if sensor == "MODIS" else PLATFORMS[2:]
        platforms = st.multiselect("Uydu / platform", available, default=available, key=f"platforms_{sensor}")
        stages = st.multiselect("İşleme türü", ["archive", "nrt"], default=["archive", "nrt"],
                               format_func=lambda x: "Arşiv (dosya etiketi)" if x == "archive" else "NRT (geçici ürün)")
        quality = st.selectbox("Güven filtresi", ["Tüm güven değerleri", "Duyarlılık: MODIS ≥30; VIIRS n/h"], key="quality")
        type_mode = st.selectbox("Sıcak nokta türü", ["Tüm türler ve bilinmeyen", "Yalnız type=0 (arşiv)"], key="type_mode")
        with st.expander("Bölge koordinatları (WGS84)"):
            st.caption("Bu dikdörtgen Türkiye idari sınırı değildir. Yalnız paket içindeki alt bölgeler seçilebilir; nokta ondalık ayracıdır.")
            west = st.number_input("Batı / boylam", value=BBOX[0], min_value=BBOX[0], max_value=BBOX[2], step=0.01, format="%.4f", key="west")
            south = st.number_input("Güney / enlem", value=BBOX[1], min_value=BBOX[1], max_value=BBOX[3], step=0.01, format="%.4f", key="south")
            east = st.number_input("Doğu / boylam", value=BBOX[2], min_value=BBOX[0], max_value=BBOX[2], step=0.01, format="%.4f", key="east")
            north = st.number_input("Kuzey / enlem", value=BBOX[3], min_value=BBOX[1], max_value=BBOX[3], step=0.01, format="%.4f", key="north")
        st.caption("Kaynak: kullanıcı tarafından sağlanan 12 NASA FIRMS ZIP'i. Son paket tespiti: 09/11/2026; inceleme: 14/11/2026.")
    if not platforms or not stages:
        st.info("Analiz için en az bir platform ve işleme türü seçin.")
        st.stop()
    if (end - start).days > 1827:
        st.error("Tarih aralığı en fazla 5 yıl olabilir. Başlangıç veya bitiş tarihini değiştirerek aralığı daraltın.")
        st.stop()
    try:
        filtered = filter_data(full, start, end, (west,south,east,north), platforms, stages,
            "all" if quality.startswith("Tüm") else "screened", "all" if type_mode.startswith("Tüm") else "vegetation")
    except ValueError as exc:
        st.error(str(exc))
        st.stop()
    monthly = monthly_counts(filtered, full, start, end, platforms)
    st.info("Sayılar uydu sıcak nokta tespitleridir. Benzersiz yangın, yanan alan veya doğrulanmış erken uyarı sayısı değildir. Platformların sayıları doğrudan eşdeğer değildir.")
    if end.year == 2026:
        st.warning("2026 KISMİ YIL · Son kayıt tarihi platforma göre değişir. Tam yıllarla ham toplam üzerinden karşılaştırmayın.")
    if quality != "Tüm güven değerleri":
        st.caption("Güven filtresi bir duyarlılık denemesidir; MODIS ve VIIRS için eşit algılama kalitesi sağlamaz.")
    if type_mode != "Tüm türler ve bilinmeyen":
        st.warning("type=0 yalnız varsayılan bitki örtüsü yangını sınıfıdır. NRT türü eksik olduğundan dışlanır. VIIRS tür alanının düzeltme geçmişi bu paket için doğrulanamadı.")
    a,b = st.columns(2)
    c,d = st.columns(2)
    a.metric("Seçili tespit kaydı", f"{len(filtered):,}".replace(",", "."))
    b.metric("Seçili platform", len(platforms))
    c.metric("NRT tespit kaydı", f"{int(filtered.processing.eq('nrt').sum()):,}".replace(",", "."))
    d.metric("Seçimde son tespit (UTC)", filtered.timestamp_utc.max().strftime("%d/%m/%Y") if len(filtered) else "Kayıt yok")
    st.caption(f"Bölge: batı {west:g} · güney {south:g} · doğu {east:g} · kuzey {north:g}. Sınırlar dahil. Platform toplamı bağımsız yangın sayısı vermez.")
    tabs = st.tabs(["Takvim ve grafik", "Tespitler ve indirme", "Veri denetimi", "Yöntem ve kaynaklar", "Harita", "Aynı ayı karşılaştır"])
    with tabs[0]:
        st.subheader("Aylık sıcak nokta takvimi")
        platform = st.selectbox("Takvim platformu", platforms, index=platforms.index("Aqua") if "Aqua" in platforms else 0, key="calendar_platform")
        log_color = st.checkbox("Renkleri logaritmik ölçekle göster (sayılar değişmez)", value=False)
        shared_color = st.checkbox("Seçili platformlar için ortak renk ölçeği", value=True, key="shared_color")
        st.caption("Ortak ölçek açıksa bu tarih/bölge seçiminde bütün seçili platformlar aynı üst sınırı kullanır. Kapalıysa aynı renk farklı sayılara karşılık gelebilir. Filtre veya platform kümesi değişirse ortak üst sınır da yeniden hesaplanır.")
        st.caption("Cividis renk ölçeği ve hücredeki sayı birlikte okunur. Gri / —: kayıt yok veya seçim dışında; sıfır yangın anlamına gelmez. *: seçim/tespit aralığı sınır ayı veya kısmi 2026. Her ayın gözlem kapsamı bilinmiyor.")
        st.plotly_chart(calendar_figure(monthly, platform, log_color, shared_color), width="stretch", key="calendar")
        st.subheader("Platformlara göre aylık kayıtlar")
        fig = go.Figure()
        for i,p in enumerate(platforms):
            data = monthly[monthly.platform.eq(p)]
            fig.add_trace(go.Scatter(x=data.month, y=data.detection_count.astype(float), mode="lines+markers", name=p,
                connectgaps=False, line=dict(color=COLORS[p], dash=["solid","dash","dot","dashdot","longdash"][PLATFORMS.index(p)]),
                marker=dict(size=4, symbol=["circle","square","diamond","cross","triangle-up"][PLATFORMS.index(p)]),
                hovertemplate="%{x}<br>%{y} tespit<extra>"+p+"</extra>"))
        fig.update_layout(height=380, template="plotly_white", yaxis_title="Tespit kaydı", xaxis_title="Ay (UTC)", legend=dict(orientation="h",y=1.18), margin=dict(l=10,r=10,t=50,b=10))
        fig.update_xaxes(type="category", nticks=12)
        fig.update_yaxes(rangemode="tozero", tickformat=",.0f")
        st.plotly_chart(fig, width="stretch")
        st.caption("Çizgi boşlukları doldurulmaz. Ortak renk ölçeği sayısal okumayı kolaylaştırır; sensörlerin algılama özelliklerini eşitlemez.")
        with st.expander("Erişilebilir aylık veri tablosu"):
            st.dataframe(monthly, hide_index=True, width="stretch")
    with tabs[1]:
        st.subheader("Seçiminizi indirin")
        st.markdown("CSV: UTF-8 BOM, virgül ayırıcı, UTC zaman damgası. Kaynak ZIP, üye dosya ve 1'den başlayan **veri satırı** numarası her tespitte korunur; CSV fiziksel satırı bu numara + 1'dir.")
        col1,col2,col3 = st.columns(3)
        col1.download_button("Filtrelenmiş tespitleri indir (CSV)", csv_bytes(filtered), "focustm_tespitler.csv", "text/csv", key="download_detections")
        col2.download_button("Aylık takvimi indir (CSV)", csv_bytes(monthly), "focustm_aylik.csv", "text/csv", key="download_monthly")
        metadata = dict(start_utc=str(start), end_utc_inclusive=str(end), bbox=[west,south,east,north],
            platforms=platforms, processing=stages, confidence_filter=quality, type_filter=type_mode,
            count=len(filtered), coverage_verified=False, harmonization="not_validated", reference_date=str(AS_OF),
            raw_zip_sha256=audit["zip_sha256"], unit="satellite hotspot detections, not unique fires")
        col3.download_button("Seçim ve kaynak bilgisi (JSON)", json.dumps(metadata,ensure_ascii=False,indent=2), "focustm_secim.json", "application/json")
        st.download_button("Filtrelenmiş tespitleri indir (GeoJSON)", geojson_bytes(filtered,metadata), "focustm_tespitler.geojson", "application/geo+json", key="download_geojson")
        st.caption("GeoJSON: her tespit bir Point; koordinat sırası [boylam, enlem] (WGS84). Kaynak ve sensör/platform alanları korunur. Çalışma kutusu metadata içindedir; nokta sayısına bir poligon eklenmez. Tam CBS veya canlı uyarı sistemi değildir.")
        st.dataframe(filtered[["timestamp_utc","sensor","platform","latitude","longitude","processing","confidence","type","frp","source_zip","source_row"]], width="stretch", hide_index=True)
        if filtered.empty:
            st.info("Bu filtrelerde kayıt bulunamadı. Bu sonuç yangın olmadığına dair kanıt değildir; indirilen CSV yine sütun başlıklarını içerir.")
    with tabs[2]:
        st.subheader("12 ZIP → 8 mantıksal veri kümesi")
        st.write(f"{audit['physical_rows']:,} fiziksel kayıt kopyası → {audit['canonical_records']:,} tekil tespit kaydı. Aynı verinin CSV, JSON ve Shapefile kopyaları bir kez sayıldı.")
        st.dataframe(pd.DataFrame(audit["format_equivalence"]), hide_index=True, width="stretch")
        st.dataframe(pd.DataFrame(audit["platform_summary"]), hide_index=True, width="stretch")
        st.warning("İlk/son tespit ile tespit görülen gün sayısı, gözlem kapsamı değildir. ZIP'lerde bulut maskesi, geçiş kaydı, geçerli gözlem sayacı ve indirme istek kapsamı yoktur.")
        st.caption("Suomi-NPP ham instrument=SNPP değeri saklanarak sensor=VIIRS üretildi. Arşiv/NRT dosya etiketi ile version alanı kontrol edildi. Ayrıntılı envanter reports klasöründedir.")
    with tabs[3]:
        st.subheader("Neyi ölçüyoruz?")
        st.markdown("""Bir kayıt, belirli uydu geçişinde algılanan bir sıcak nokta pikselidir. Aynı olay birden çok pikselde, zamanda ve platformda görülebilir. **Alan standardizasyonu ve zaman standardizasyonu yapıldı; doğrulanmış sensör uyumlaştırması yapılmadı.**

MODIS yaklaşık 1 km, VIIRS yaklaşık 375 m nominal çözünürlüğe sahiptir. Terra/Aqua ile üç VIIRS platformu farklı gözlem zamanlarına ve veri dönemlerine sahiptir. Piksel boyutlarının oranı tespit sayısı dönüştürme katsayısı olarak kullanılamaz.

Arşiv ve NRT ayrı tutulur. `type` NRT'de yoktur; arşivdeki `type=0` doğrulanmış yangın olayı değildir. 2026 eksiktir. Raporlanmış yer yangını envanteri veya yanan alan ürünü bu pakette bulunmaz.
""")
        st.subheader("Uyumlaştırma deneyi")
        ex = json.loads((ROOT / "reports/overlap_experiment.json").read_text(encoding="utf-8"))
        st.dataframe(pd.DataFrame(ex)[["target","confidence","train_months","test_months","coefficient","heldout_mae","seasonal_baseline_mae","status"]], hide_index=True, width="stretch")
        st.markdown("Aqua referans alınarak yalnız iki platformda da kayıt bulunan arşiv ayları eşleştirildi. Katsayı eğitim yıllarından öğrenildi; sonraki yıllarda MAE ile sınandı. Eksik ayların dışlanması seçilim yanlılığı yaratabilir. Bulutsuz geçerli gözlem kapsamı ve bağımsız yangın doğrulaması yoktur. **Deneysel katsayılar takvime uygulanmaz.** Ayrıntı: docs/YONTEM.md ve PDF rehberi.")
        st.subheader("NASA kaynakları ve açık sorular")
        st.markdown((ROOT / "docs/KAYNAKLAR.md").read_text(encoding="utf-8"))
        st.subheader("AI katkısı")
        st.write("Kod taslağı, belge taslağı ve test tasarımı Codex yardımıyla hazırlandı. Sayılar paket içindeki gerçek dosyalardan Python ile üretildi. Veri bilimsel olarak bağımsız doğrulanmış veya NASA tarafından onaylanmış bir ürün olarak sunulmaz. Karar kaydı: docs/KARARLAR_AI.md.")
        st.info("Şema birleştirme tamamlandı; sensör etkisini düzeltme HOLD. Harita ve ortak renk ölçeği bu bilimsel açığı çözmez. Kalan kısa sürede savunulabilir adım: aynı platformun aynı UTC aylarını, mevcut filtrelerle betimsel karşılaştırmak. Sensörler arası yeni deney için eşleşen geçerli gözlem/geçiş ve bulut maskeleri gerekir; kanıtlanmamış katsayıyla ortak seri üretilmez.")
    with tabs[4]:
        st.subheader("Türkiye odaklı çalışma alanı")
        st.caption("Nokta merkezleri gösterilir; il sınırı, yangın çevresi veya yanan alan çizilmez. Koyu çerçeve batı 29.5 / güney 36.1 / doğu 32.8 / kuzey 37.5 kutusudur. Alt bölge seçilirse ikinci çerçeve görünür.")
        online_map = st.checkbox("OpenStreetMap altlığını aç (internet gerekir)", value=False, key="online_map")
        st.plotly_chart(map_figure(filtered,(west,south,east,north),online_map),width="stretch",key="detection_map")
        st.caption(f"Haritaya gönderilen tespit: {len(filtered):,}. Örnekleme yapılmaz; üst üste binen noktalar ayrı kayıtları temsil edebilir. Açılır bilgide sensör, platform, UTC zamanı, arşiv/NRT ve güven değeri bulunur.")
        st.markdown("Nokta kaynağı: **NASA FIRMS / paket içindeki dosyalar**. Görselleştirme: **Plotly (MIT), MapLibre GL JS (BSD-3-Clause)**. İsteğe bağlı altlık: [© OpenStreetMap contributors — ODbL](https://www.openstreetmap.org/copyright); [karo kullanım politikası](https://operations.osmfoundation.org/policies/tiles/).")
        st.info("Varsayılan beyaz zemin dış harita karosu istemez; yol/kıyı çizmez. OpenStreetMap seçilirse altlık internet veya servis erişimi olmadan yüklenmeyebilir. Harita WebGL2 destekli tarayıcı ister. Çizim çalışmazsa koordinatlı CSV/GeoJSON ve tablolar kullanılabilir. Ağ tamamen kapalı senaryo ve bütün tarayıcılar test edilmedi.")
        if filtered.empty:
            st.info("Seçimde tespit yok; yalnız çalışma alanı çizilir. Bu sonuç sıfır yangın kanıtı değildir.")
    with tabs[5]:
        st.subheader("Aynı platform, aynı ay: yıllar arası kayıtlar")
        st.caption("Bu bölüm tam UTC aylarını karşılaştırır. Yan çubuktaki tarihlerin yalnız YILLARI kullanılır; gün/ay kesmeleri kullanılmaz. Bölge, platform kümesi, arşiv/NRT, güven ve tür filtreleri korunur. Üstteki toplam ve harita ise yan çubuktaki kesin tarih aralığını kullanır.")
        compare_platform = st.selectbox("Karşılaştırma platformu",platforms,index=platforms.index("Aqua") if "Aqua" in platforms else 0,key="compare_platform")
        compare_month = st.selectbox("Karşılaştırılacak ay",range(1,13),index=6,format_func=lambda n:MONTHS[n-1],key="compare_month")
        comparison = same_month_comparison(full,compare_platform,compare_month,start.year,end.year,
            (west,south,east,north),stages,"all" if quality.startswith("Tüm") else "screened","all" if type_mode.startswith("Tüm") else "vegetation")
        fig = go.Figure(go.Bar(x=comparison.year_label.tolist(),y=[None if pd.isna(x) else int(x) for x in comparison.detection_count],
            marker_color=COLORS[compare_platform],text=["" if pd.isna(x) else str(int(x)) for x in comparison.detection_count],textposition="outside",
            hovertemplate="Yıl: %{x}<br>Tespit kaydı: %{y}<extra></extra>"))
        fig.update_layout(height=350,template="plotly_white",xaxis_title="Yıl (UTC); * kısmi 2026",yaxis_title="Tespit kaydı",xaxis_type="category",margin=dict(t=25,b=30))
        st.plotly_chart(fig,width="stretch",key="same_month_chart")
        display = comparison[["year","platform","month","detection_count","coverage_verified","partial_reference_year","record_extent_boundary","interpretation"]].rename(columns={"year":"Yıl","platform":"Platform","month":"UTC ay","detection_count":"Tespit kaydı","coverage_verified":"Gözlem kapsamı doğrulandı mı","partial_reference_year":"Kısmi yıl","record_extent_boundary":"Tespit aralığı sınır ayı","interpretation":"Yorum"})
        st.dataframe(display,hide_index=True,width="stretch")
        st.warning("Boş/None hücre ve eksik çubuk: kayıt yok, gözlem kapsamı bilinmiyor; sıfır yangın değildir. 2026* kısmi yıldır. Sayıların farkı gerçek olay sayısı, orman yangını, yanmış alan veya istatistiksel anomali olarak yorumlanamaz. Tam takvim yılı da tam gözlem kapsamı demek değildir.")
        st.download_button("Aynı ay karşılaştırmasını indir (CSV)",csv_bytes(comparison),"focustm_ay_karsilastirma.csv","text/csv",key="download_comparison")
    st.caption("FocusTM · Eğitim ve geçmiş aktivite inceleme prototipi · NASA Space Apps 2026 bağlamı kullanıcı/jüri mesajlarına dayanır; resmî yarışma şartları ayrıca doğrulanmalıdır.")


if __name__ == "__main__":
    main()
