#! /usr/bin/env python
# -*- coding:utf-8 -*-

""" [NAME] iwrs.py テストコード
"""


from datetime import datetime
from datetime import timedelta
import json
import os
import pytest
import iwrs


def test_load_setting_file():
    """ [FUNCTIONS] iwrs.load_setting_file テストコード
    """
    # 通常の設定ファイル
    settings = iwrs.load_setting_file("./tests/data/settings_normal.ini")
    assert settings.get('yolp', 'appid')

    assert settings.get('yolp', 'coordinates')

    download_dir = settings.get('yolp', 'download_dir')
    assert os.access(download_dir, os.W_OK)

    assert settings.get('audio', 'message')
    assert settings.get('audio', 'repeat')

    # 存在しない設定ファイルパス
    with pytest.raises(OSError):
        iwrs.load_setting_file("")

    with pytest.raises(ValueError):
        iwrs.load_setting_file(
            "./tests/data/settings_cant_write_download_dir.ini")


def test_get_weather_information():
    settings = iwrs.load_setting_file("./tests/data/settings_normal.ini")
    settings.set('yolp', 'appid', os.environ["YOLP_APPID"])
    settings.set('yolp', 'coordinates', os.environ["YOLP_COORDINATES"])

    date = datetime.now().strftime('%Y%m%d%H%M')
    weather_json = iwrs.get_weather_information(settings)
    assert weather_json["ResultInfo"]["Status"] == 200
    assert os.access(
        settings.get('yolp', 'download_dir') + "/%s.json" % date, os.F_OK)


def test_parse_weather_information():
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
