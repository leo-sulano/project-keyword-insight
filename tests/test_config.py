import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
import config


def test_sites_list_length():
    assert len(config.SITES) == 27


def test_countries_filter():
    assert config.COUNTRIES == ["SAU", "KWT"]


def test_min_impressions_positive():
    assert config.MIN_IMPRESSIONS > 0


def test_brand_terms_nonempty():
    assert len(config.BRAND_TERMS) >= 10


def test_all_sites_are_strings():
    assert all(isinstance(s, str) for s in config.SITES)


def test_date_format():
    import re
    pattern = re.compile(r"^\d{4}-\d{2}-\d{2}$")
    assert pattern.match(config.START_DATE)
    assert pattern.match(config.END_DATE)
