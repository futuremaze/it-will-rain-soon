#! /usr/bin/env python
# -*- coding:utf-8 -*-

""" [NAME] YOLP(気象情報) を使用して指定時間後(設定ファイル)に雨が降るかどうかを知らせる.

[DESCRIPTION] YOLP(気象情報) から降水強度を取得し,
指定時間後(設定ファイル)の降水強度が閾値(設定ファイル)以上である場合に,
指定の音声ファイル(設定ファイル)を再生する.
YOLP(気象情報):
    https://developer.yahoo.co.jp/webapi/map/openlocalplatform/v1/weather.html
"""

from datetime import datetime
from datetime import timedelta
import argparse
import json
import os
import requests
import time
import configparser


def load_setting_file(file_path):
    """ [FUNCTIONS] INI形式の設定ファイルを読み込んでConfigParserオブジェクト化し,
    必須パラメタ有無のチェック, 値の範囲チェックを実施し, ConfigParserオブジェクトを返す.
    必須パラメタ有無チェックおよび値の範囲チェックに問題がある場合は、
    ValueErrorをraiseする.

    Keyword arguments:
    file_path -- 設定ファイル(INI形式)パス(絶対パス, あるいはコマンド実行場所からの相対パス)

    Return value: 設定値(ConfigParserオブジェクト)
    """

    if not os.path.exists(file_path):
        raise OSError

    inifile = configparser.SafeConfigParser()
    inifile.read(file_path)

    download_dir = inifile.get('yolp', 'download_dir')
    if not (os.access(download_dir, os.W_OK)):
        raise ValueError

    after_minutes = int(inifile.get('weather', 'after_minutes'))
    if after_minutes < 0 or after_minutes > 60:
        raise ValueError

    rainfall_threshold = float(inifile.get('weather', 'rainfall_threshold'))
    if rainfall_threshold < 0.0:
        raise ValueError

    return inifile


def get_weather_information(settings):
    """ [FUNCTIONS] YOLP(気象情報)から気象情報をJSON形式で取得し,
    辞書オブジェクト化して返す.
    取得したJSONは指定ディレクトリ(設定ファイル)に保存する.

    Keyword arguments:
    settings -- 設定値(ConfigParserオブジェクト)

    Return value: YOLP(気象情報)から取得したデータ(辞書オブジェクト)
    """

    appid = settings.get('yolp', 'appid')
    coordinates = settings.get('yolp', 'coordinates')
    date_now = datetime.now().strftime('%Y%m%d%H%M')

    url = \
        "https://map.yahooapis.jp/weather/V1/place?" \
        "appid={appid}&" \
        "coordinates={coordinates}&" \
        "output=json&" \
        "date_now={date_now}&" \
        "past=0&" \
        "interval=10".format(
            appid=appid, coordinates=coordinates, date_now=date_now)

    weather_json = requests.get(url).json()

#     output_json_file = open(
#         settings.get('yolp', 'download_dir') + "/%s.json" % date_now, 'w')
#     json.dump(
#         weather_json,
#         output_json_file,
#         indent=4, separators=(',', ': '), ensure_ascii=False)
# 
#     output_json_file.close

    return weather_json


def parse_weather_information(weather_information_json, settings):
    """ [FUNCTIONS] YOLP(気象情報)のデータ(JSON形式)を解析し、降水強度をチェックする.
    指定時間後の降水強度が閾値以上の場合, 指定の音声ファイルを再生する.

    Keywork arguments:
    weather_information_json -- YOLP(気象情報)のデータ(辞書オブジェクト)
    settings -- 設定値(ConfigParserオブジェクト)
    """
    date_now = datetime.now()
    after_minutes = int(settings.get('weather', 'after_minutes'))
    target_time = date_now + timedelta(minutes=after_minutes)
    rainfall_threshold = float(settings.get('weather', 'rainfall_threshold'))
    message = settings.get('audio', 'message')
    repeat = int(settings.get('audio', 'repeat'))
    weather_list = \
        weather_information_json["Feature"][0]["Property"]["WeatherList"]

    for weather in weather_list["Weather"]:
        date = datetime.strptime(weather["Date"], '%Y%m%d%H%M')

        if date >= target_time:
            rainfall = float(weather["Rainfall"])
            if rainfall >= rainfall_threshold:
                if os.access('./.raining', os.F_OK):
                    # print("It is raining now.")
                    return 2
                else:
                    # playback sound.
                    # print("{}\n".format(message))
                    for var in range(1, repeat):
                        os.system('/opt/aquestalkpi/AquesTalkPi -b "{}" | aplay'.format(
                            message))
                        time.sleep(5)

                    open('./.raining', 'w').close()
                    return 1
            break

    # print("Not Rainfall")
    # os.system('/opt/aquestalkpi/AquesTalkPi "この先、しばらく雨は降らないよ" | aplay')

    if os.access('./.raining', os.F_OK):
        os.remove('./.raining')

    return 0


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
                prog=__file__,
                usage="python3 {} -f config.ini".format(__file__),
                add_help=True
                )
    parser.add_argument(
        '-f',
        '--conf',
        required=True,
        help='config file'
        )

    args = parser.parse_args()

    # 設定ファイル読み込み
    settings = load_setting_file(args.conf)

    # YOLP(気象情報呼び出し)
    weather_json = get_weather_information(settings)

    # 気象情報解析
    parse_weather_information(weather_json, settings)
