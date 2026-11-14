from datetime import date
from streamlit.testing.v1 import AppTest


def test_app_default_and_filter(root):
    at=AppTest.from_file(str(root/"app.py"),default_timeout=60).run()
    assert not at.exception
    assert at.metric[0].value=="29.640"
    at.date_input(key="start").set_value(date(2021,7,1))
    at.date_input(key="end").set_value(date(2021,7,31))
    at.selectbox(key="sensor").select("MODIS").run()
    at.multiselect(key="platforms_MODIS").set_value(["Aqua"]).run()
    assert not at.exception
    assert at.metric[0].value=="426"
    # Invalid region and date range must be explained, never silently corrected.
    at.number_input(key="west").set_value(32.8).run()
    assert at.error and not at.exception
    at.number_input(key="west").set_value(29.5)
    at.date_input(key="start").set_value(date(2022,1,1)).run()
    assert at.error and not at.exception


def test_app_empty_platform_selection(root):
    at=AppTest.from_file(str(root/"app.py"),default_timeout=60).run()
    at.multiselect(key="platforms_Tümü").set_value([]).run()
    assert not at.exception
    assert any("en az bir" in i.value for i in at.info)
