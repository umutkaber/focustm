import csv
import io
import json
import zipfile
from datetime import date

import pandas as pd
import pytest
from streamlit.testing.v1 import AppTest

from core import BBOX, PLATFORMS, filter_data, monthly_counts
from features import geojson_bytes, calendar_max, map_figure, same_month_comparison


def test_geojson_aqua_source_and_coordinate_order(data):
    selected=filter_data(data,'2021-07-01','2021-07-31',platforms=['Aqua'])
    geo=json.loads(geojson_bytes(selected,{'start_utc':'2021-07-01'}))
    assert geo['type']=='FeatureCollection' and len(geo['features'])==426
    assert geo['work_area']['bbox']==list(BBOX)
    for f,r in zip(geo['features'],selected.itertuples()):
        assert f['geometry']['coordinates']==[r.longitude,r.latitude]
        assert f['properties']['platform']=='Aqua' and f['properties']['sensor']=='MODIS'
        assert f['properties']['source_row']==r.source_row and f['id']==r.record_id
        assert f['properties']['timestamp_utc'].endswith('Z')
    assert geo['harmonization']=='not_validated' and not geo['work_area']['administrative_boundary']


def test_geojson_empty_and_missing_values(data):
    empty=json.loads(geojson_bytes(data.iloc[:0],{}))
    assert empty['features']==[] and 'bbox' not in empty
    nrt=data[data.processing.eq('nrt')].iloc[:1]
    result=geojson_bytes(nrt,{})
    assert b'NaN' not in result
    assert json.loads(result)['features'][0]['properties']['type'] is None


def test_geojson_rejects_invalid_coordinates(data):
    bad=data.iloc[:1].copy();bad['longitude']=181
    with pytest.raises(ValueError):geojson_bytes(bad,{})


def test_map_all_points_boundary_and_subset(data):
    subset=filter_data(data,'2021-07-01','2021-07-31',platforms=['Aqua','Suomi-NPP'])
    fig=map_figure(subset,(30,36.3,32,37.2))
    points=[t for t in fig.data if t.mode=='markers']
    assert sum(len(t.lon) for t in points)==426+2268
    assert {t.name for t in points}=={'Aqua / MODIS','Suomi-NPP / VIIRS'}
    boundary=fig.data[-2]
    assert list(boundary.lon)==[29.5,32.8,32.8,29.5,29.5]
    assert list(boundary.lat)==[36.1,36.1,37.5,37.5,36.1]
    assert fig.data[-1].name=='Seçili alt bölge'
    assert fig.layout.map.style=='white-bg'


def test_map_online_and_empty(data):
    fig=map_figure(data.iloc[:0],online=True)
    assert fig.layout.map.style=='open-street-map'
    assert len(fig.data)==1 and fig.data[0].mode=='lines'


@pytest.mark.parametrize('logarithmic',[False,True])
def test_shared_calendar_scale_is_identical_across_platforms(data,logarithmic):
    m=monthly_counts(data,data,'2021-07-01','2021-07-31',PLATFORMS)
    values=[calendar_max(m,p,logarithmic,True) for p in PLATFORMS]
    assert len(set(values))==1
    assert calendar_max(m,'Aqua',logarithmic,False)<calendar_max(m,'Suomi-NPP',logarithmic,False)


def test_same_month_matches_independent_raw_csv(root,data):
    with zipfile.ZipFile(root/'data/raw/DL_FIRE_M-C61_847528.zip') as z:
        raw=[r for name in z.namelist() if name.endswith('.csv') for r in csv.DictReader(io.StringIO(z.read(name).decode('utf-8-sig')))]
    result=same_month_comparison(data,'Aqua',7,2018,2026)
    assert len(result)==9 and not result.coverage_verified.any()
    for row in result.itertuples():
        expected=sum(r['satellite']=='Aqua' and r['acq_date'].startswith(f'{row.year}-07') for r in raw)
        assert row.detection_count==expected if expected else pd.isna(row.detection_count)
    assert result.loc[result.year.eq(2021),'detection_count'].iloc[0]==426
    assert result.loc[result.year.eq(2026),'year_label'].iloc[0]=='2026*'


def test_same_month_missing_year_not_zero_and_filters(data):
    result=same_month_comparison(data,'NOAA-21',7,2020,2026,processing=['nrt'])
    assert result.loc[result.year.lt(2026),'detection_count'].isna().all()
    # NRT starts August 2026, so July also cannot be inferred as zero.
    assert result.detection_count.isna().all()
    assert result.loc[result.year.eq(2026),'partial_reference_year'].all()


def test_app_additions_and_existing_filters(root):
    at=AppTest.from_file(str(root/'app.py'),default_timeout=60).run()
    assert not at.exception and at.metric[0].value=='29.640'
    assert at.checkbox(key='shared_color').value is True
    assert at.checkbox(key='online_map').value is False
    at.date_input(key='start').set_value(date(2018,7,1))
    at.date_input(key='end').set_value(date(2026,11,9))
    at.selectbox(key='sensor').select('MODIS').run()
    at.multiselect(key='platforms_MODIS').set_value(['Aqua']).run()
    comparison=at.dataframe[-1].value
    assert comparison.loc[comparison['Yıl'].eq(2021),'Tespit kaydı'].iloc[0]==426
    assert not comparison['Gözlem kapsamı doğrulandı mı'].any()
    at.checkbox(key='shared_color').uncheck().run()
    at.checkbox(key='online_map').check().run()
    assert not at.exception
    assert at.get('download_button')[-1].label=='Aynı ay karşılaştırmasını indir (CSV)'
