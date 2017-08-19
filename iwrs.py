#! /usr/bin/env python
# -*- coding:utf-8 -*-

""" [NAME] YOLP(気象情報) を使用して60分以内に雨が降るかどうかを知らせる.

[DESCRIPTION] YOLP(気象情報) から降水強度を取得し,
指定時間後(設定ファイル)の降水強度が0.0を超える場合に,
指定のメッセージ(設定ファイル)を発話する.
YOLP(気象情報):
    https://developer.yahoo.co.jp/webapi/map/openlocalplatform/v1/weather.html
"""

from datetime import datetime
import argparse
import json
import logging
import logging.config
import os
import requests
import time
import configparser


class ItWillRainSoon:
    """ [CLASS] YOLP(気象情報)を利用して雨が降るかどうかをチェックするクラス.
    """

    def __init__(self):
        """ [FUNCTIONS] コンストラクタ.
        """
        self.abspath = os.path.abspath(os.path.dirname(__file__))
        logging.config.fileConfig(os.path.join(self.abspath, "logging.conf"))
        self.logger = logging.getLogger()

    def start(self, setting_file_path):
        """ [FUNCTIONS]
        """
        # 設定ファイル読み込み
        settings = self.load_setting_file(setting_file_path)

        # YOLP(気象情報呼び出し)
        weather_json = self.get_weather_information(settings)

        # 気象情報解析
        self.parse_weather_information(weather_json, settings)

    def load_setting_file(self, file_path):
        """ [FUNCTIONS] INI形式の設定ファイルを読み込んでConfigParserオブジェクト化し,
        必須パラメタ有無のチェック, 値の範囲チェックを実施し, ConfigParserオブジェクトを返す.
        必須パラメタ有無チェックおよび値の範囲チェックに問題がある場合は、
        ValueErrorをraiseする.

        Keyword arguments:
        file_path -- 設定ファイル(INI形式)パス(絶対パス, あるいはコマンド実行場所からの相対パス)

        Return value: 設定値(ConfigParserオブジェクト)
        """

        self.logger.info(
            "Start load_setting_file. (file_path={})".format(file_path))

        if not os.path.exists(file_path):
            self.logger.fatal(
                "file_path is not found. (file_path={})".format(file_path))
            raise OSError

        self.logger.info(
            "Start inifile.read.(file_path={})".format(file_path))
        inifile = configparser.SafeConfigParser()
        inifile.read(file_path)
        self.logger.info("Finished inifile.read.")

        self.logger.info(
            "Finished load_setting_file.(file_path={})".format(file_path))
        return inifile

    def get_weather_information(self, settings):
        """ [FUNCTIONS] YOLP(気象情報)から気象情報をJSON形式で取得し返す.
        取得したJSONは指定ディレクトリ(設定ファイル)に保存する.

        Keyword arguments:
        settings -- 設定値(ConfigParserオブジェクト)

        Return value: YOLP(気象情報)から取得したJSONデータ
        """
        self.logger.info("Start get_weather_information.")

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

        self.logger.info("Start HTTP GET request.(url={})".format(url))
        weather_json = requests.get(url).json()
        self.logger.info(
            "Finished HTTP GET request.(res={})".format(
                json.dumps(
                    weather_json,
                    indent=4, separators=(',', ': '), ensure_ascii=False)))

        self.logger.info("Finished get_weather_information.")

        return weather_json

    def parse_weather_information(self, weather_information_json, settings):
        """ [FUNCTIONS] YOLP(気象情報)のデータ(JSON形式)を解析し、降水強度をチェックする.
        指定時間後の降水強度が0.0を超える場合, 指定のメッセージ(設定ファイル)を発話する.

        Keywork arguments:
        weather_information_json -- YOLP(気象情報)のデータ(辞書オブジェクト)
        settings -- 設定値(ConfigParserオブジェクト)
        """
        self.logger.info("Start parse_weather_information.")

        message = settings.get('audio', 'message')
        repeat = int(settings.get('audio', 'repeat'))
        weather_list = \
            weather_information_json["Feature"][0]["Property"]["WeatherList"]

        self.logger.info("Check rainfall larger than 0.0...")
        for weather in weather_list["Weather"]:
            if float(weather["Rainfall"]) > 0.0:
                self.logger.info(
                    "Found rainfall(>0.0).(weather={})".format(weather))
                if os.access(os.path.join(self.abspath, '.raining'),
                   os.F_OK):
                    self.logger.info("Exist {}. It is raining now.".format(
                        os.path.join(self.abspath, '.raining')
                    ))
                    return 2
                else:
                    self.logger.info("It will rain soon!")
                    cmd = '/opt/aquestalkpi/AquesTalkPi -b {}|aplay'.format(
                        message)
                    for var in range(0, repeat):
                        self.logger.info(
                            "Exec command.(cmd={}, repeat={}, now={})".format(
                                cmd, repeat, var+1
                            ))
                        os.system(cmd)
                        time.sleep(5)

                    self.logger.info("Make {}.".format(
                            os.path.join(self.abspath, '.raining')
                    ))
                    open(os.path.join(self.abspath, '.raining'), 'w').close()
                    return 1
                break

        self.logger.info("It won't rain.")

        if os.access(os.path.join(self.abspath, '.raining'), os.F_OK):
            self.logger.info("Remove {}.".format(
                    os.path.join(self.abspath, '.raining')
            ))
            os.remove(os.path.join(self.abspath, '.raining'))

        self.logger.info("Finished parse_weather_information.")
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

    iwrs = ItWillRainSoon()
    iwrs.start(args.conf)
