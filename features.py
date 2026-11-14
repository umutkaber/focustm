"""Small presentation/export additions; the v1 scientific pipeline is unchanged."""
import json
import math

import pandas as pd
import plotly.graph_objects as go

from core import AS_OF, BBOX, PLATFORMS, filter_data, monthly_counts

COLORS = {"Terra": "#4477AA", "Aqua": "#228833", "Suomi-NPP": "#AA3377", "NOAA-20": "#AA7711", "NOAA-21": "#007799"}

def geojson_bytes(frame, selection):
    """RFC 7946 point features: [longitude, latitude], JSON null for missing fields."""
    records = json.loads(frame.to_json(orient="records", date_format="iso", double_precision=15))
    features = []
    for row in records:
        lon, lat = row["longitude"], row["latitude"]
        if lon is None or lat is None or not math.isfinite(lon) or not math.isfinite(lat):
            raise ValueError("GeoJSON için geçerli koordinat gerekir.")
        if not -180 <= lon <= 180 or not -90 <= lat <= 90:
            raise ValueError("GeoJSON koordinatı WGS84 sınırları dışında.")
        features.append(dict(type="Feature", id=row["record_id"],
            geometry=dict(type="Point", coordinates=[lon, lat]), properties=row))
    result = dict(type="FeatureCollection", features=features, selection=selection,
        work_area=dict(name="Antalya odaklı çalışma alanı", bbox=list(BBOX), administrative_boundary=False),
        unit="satellite hotspot detections, not unique fires", harmonization="not_validated")
    if features:
        xy = [f["geometry"]["coordinates"] for f in features]
        result["bbox"] = [min(x[0] for x in xy), min(x[1] for x in xy), max(x[0] for x in xy), max(x[1] for x in xy)]
    return json.dumps(result, ensure_ascii=False, allow_nan=False, separators=(",", ":")).encode("utf-8")

def calendar_max(monthly, platform, logarithmic=False, shared=False):
    values = monthly.detection_count if shared else monthly.loc[monthly.platform.eq(platform), "detection_count"]
    maximum = float(values.max()) if values.notna().any() else 0.0
    return max(1.0, math.log1p(maximum) if logarithmic else maximum)

def map_figure(frame, selection_bbox=BBOX, online=False):
    fig = go.Figure()
    for platform in PLATFORMS:
        g = frame[frame.platform.eq(platform)]
        if g.empty:
            continue
        details = g[["sensor", "platform", "processing", "timestamp_utc", "confidence"]].astype(str).values.tolist()
        fig.add_trace(go.Scattermap(lon=g.longitude.tolist(), lat=g.latitude.tolist(), mode="markers",
            name=f"{platform} / {g.sensor.iloc[0]}", marker=dict(size=7, color=COLORS[platform], opacity=0.65),
            customdata=details,
            hovertemplate="%{customdata[1]} · %{customdata[0]}<br>%{customdata[3]}<br>İşleme: %{customdata[2]} · Güven: %{customdata[4]}<br>Boylam: %{lon:.5f} · Enlem: %{lat:.5f}<extra></extra>"))
    def box(bounds, name, color, width):
        west, south, east, north = bounds
        fig.add_trace(go.Scattermap(lon=[west,east,east,west,west], lat=[south,south,north,north,south],
            mode="lines", name=name, line=dict(color=color,width=width), hovertemplate=name+"<extra></extra>"))
    box(BBOX, "Antalya odaklı çalışma alanı", "#152E46", 3)
    if tuple(selection_bbox) != tuple(BBOX):
        box(selection_bbox, "Seçili alt bölge", "#DD6600", 2)
    fig.update_layout(map=dict(style="open-street-map" if online else "white-bg",
        center=dict(lon=(BBOX[0]+BBOX[2])/2,lat=(BBOX[1]+BBOX[3])/2),zoom=6.7),
        height=550,margin=dict(l=0,r=0,t=5,b=0),legend=dict(orientation="h",y=1.02),
        uirevision="focustm-work-area",font=dict(family="Arial",color="#193047"))
    return fig

def same_month_comparison(full, platform, month_number, first_year, last_year,
                          bbox=BBOX, processing=("archive","nrt"), confidence="all", type_mode="all"):
    """Whole UTC months across requested years; missing is NA, never imputed zero."""
    if platform not in PLATFORMS or not 1 <= month_number <= 12 or first_year > last_year:
        raise ValueError("Karşılaştırma platformu, ayı veya yıl aralığı geçersiz.")
    start, end = f"{first_year}-01-01", f"{last_year}-12-31"
    selected = filter_data(full,start,end,bbox,[platform],processing,confidence,type_mode)
    months = monthly_counts(selected,full,start,end,[platform])
    result = months[months.month_number.eq(month_number)].copy()
    result["interpretation"] = result.apply(lambda r:
        "Kayıt yok; gözlem kapsamı bilinmiyor" if pd.isna(r.detection_count)
        else "Tespit sayısı; gözlem kapsamı bilinmiyor",axis=1)
    result["year_label"] = result.year.astype(str) + result.year.eq(AS_OF.year).map({True:"*",False:""})
    return result.reset_index(drop=True)
