#! /usr/bin/env python
# -*- coding:utf-8 -*-

""" [NAME] iwrs.py テストコード
"""


from datetime import datetime
from datetime import timedelta
import json
import os
import pytest
from iwrs import ItWillRainSoon


def test_load_setting_file():
    """ [FUNCTIONS] iwrs.load_setting_file テストコード
    """
    iwrs = ItWillRainSoon()

    # 通常の設定ファイル
    settings = iwrs.load_setting_file("./tests/data/settings_normal.ini")
    assert settings.get('yolp', 'appid')
    assert settings.get('yolp', 'coordinates')
    assert settings.get('audio', 'message')
    assert settings.get('audio', 'repeat')

    # 存在しない設定ファイルパス
    with pytest.raises(OSError):
        iwrs.load_setting_file("")


def test_get_weather_information():
    iwrs = ItWillRainSoon()
    settings = iwrs.load_setting_file("./tests/data/settings_normal.ini")
    settings.set('yolp', 'appid', os.environ["YOLP_APPID"])
    settings.set('yolp', 'coordinates', os.environ["YOLP_COORDINATES"])

    weather_json = iwrs.get_weather_information(settings)
    assert weather_json["ResultInfo"]["Status"] == 200


def test_parse_weather_information():
    iwrs = ItWillRainSoon()
    settings = iwrs.load_setting_file("./tests/data/settings_normal.ini")
    settings.set('yolp', 'appid', os.environ["YOLP_APPID"])
    settings.set('yolp', 'coordinates', os.environ["YOLP_COORDINATES"])

    if os.access('./.raining', os.F_OK):
        os.remove('./.raining')

    f = open('./tests/data/yolp_will_rain_1.json', 'r')
    weather_json = json.load(f)
    f.close()

    date_at = datetime.now() + timedelta(minutes=1)
    weather_list = \
        weather_json["Feature"][0]["Property"]["WeatherList"]

    for weather in weather_list["Weather"]:
        weather["Date"] = date_at.strftime("%Y%m%d%H%M")
        date_at = date_at + timedelta(minutes=10)

    assert iwrs.parse_weather_information(weather_json, settings) == 1
    assert os.access('./.raining', os.F_OK)

    assert iwrs.parse_weather_information(weather_json, settings) == 2
    assert os.access('./.raining', os.F_OK)

    if os.access('./.raining', os.F_OK):
        os.remove('./.raining')

    f = open('./tests/data/yolp_will_rain_2.json', 'r')
    weather_json = json.load(f)
    f.close()

    date_at = datetime.now() + timedelta(minutes=1)
    weather_list = \
        weather_json["Feature"][0]["Property"]["WeatherList"]

    for weather in weather_list["Weather"]:
        weather["Date"] = date_at.strftime("%Y%m%d%H%M")
        date_at = date_at + timedelta(minutes=10)

    assert iwrs.parse_weather_information(weather_json, settings) == 1
    assert os.access('./.raining', os.F_OK)

    assert iwrs.parse_weather_information(weather_json, settings) == 2
    assert os.access('./.raining', os.F_OK)

    f = open('./tests/data/yolp_wont_rain.json', 'r')
    weather_json = json.load(f)
    f.close()

    assert iwrs.parse_weather_information(weather_json, settings) == 0
    assert not os.access('./.raining', os.F_OK)

    date_at = datetime.now() + timedelta(minutes=1)
    weather_list = \
        weather_json["Feature"][0]["Property"]["WeatherList"]

    for weather in weather_list["Weather"]:
        weather["Date"] = date_at.strftime("%Y%m%d%H%M")
        date_at = date_at + timedelta(minutes=10)

    assert iwrs.parse_weather_information(weather_json, settings) == 0
    assert not os.access('./.raining', os.F_OK)
