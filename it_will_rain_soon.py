#! /usr/bin/env python
# -*- coding:utf-8 -*-

""" [NAME] YOLP(気象情報) を使用して指定時間後(設定ファイル)に雨が降るかどうかを知らせる.

[DESCRIPTION] YOLP(気象情報) から降水強度を取得し,
指定時間後(設定ファイル)の降水強度が閾値(設定ファイル)以上である場合に,
指定の音声ファイル(設定ファイル)を再生する.
YOLP(気象情報):
    https://developer.yahoo.co.jp/webapi/map/openlocalplatform/v1/weather.html
"""

import requests


def load_setting_file(file_path):
    """ [FUNCTIONS] INI形式の設定ファイルを読み込んで辞書オブジェクト化し,
    必須パラメタ有無のチェック, 値の範囲チェックを実施し, 辞書オブジェクトを返す.
    必須パラメタ有無チェックおよび値の範囲チェックに問題がある場合は、
    ValueErrorをraiseする.

    Keyword arguments:
    file_path -- 設定ファイル(INI形式)パス(絶対パス, あるいはコマンド実行場所からの相対パス)

    Return value: 設定値(辞書オブジェクト)
    """


def get_weather_information(settings):
    """ [FUNCTIONS] YOLP(気象情報)から気象情報をJSON形式で取得し,
    辞書オブジェクト化して返す.

    Keyword arguments:
    settings -- 辞書オブジェクト化した設定値(load_setting_file関数にて得られる値)

    Return value: YOLP(気象情報)から取得したデータ(辞書オブジェクト)
    """


def parse_weather_information(weather_information_json, settings):
    """ [FUNCTIONS] YOLP(気象情報)のデータ(JSON形式)を解析し、降水強度をチェックする.
    指定時間後の降水強度が閾値以上の場合, 指定の音声ファイルを再生する.

    Keywork arguments:
    weather_information_json -- YOLP(気象情報)のデータ(辞書オブジェクト)
    settings -- 辞書オブジェクト化した設定値(load_setting_file関数にて得られる値)
    """


if __name__ == '__main__':
    # TODO 引数処理
    # 設定ファイル読み込み
    # YOLP(気象情報呼び出し)
    # 気象情報解析
    print "c"
