from pyicloud import PyiCloudService
import psycopg2

import datetime
import os
import sys

from time import sleep

from psql import PSQL
import logging


def main():
    # ログ設定
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
    logger = logging.getLogger(__name__)
    
    logger.info("GPSトラッカーアプリケーションを起動しました。")

    # 環境変数からユーザー名とパスワードを取得
    user_name = os.environ.get('USER_NAME')
    password = os.environ.get('PASSWORD')
    logger.info("環境変数からユーザー認証情報を取得しました。")

    # PyiCloudServiceのインスタンスを作成
    api = PyiCloudService(user_name, password, cookie_directory="./.pyicloud", verify=True)
    logger.info("PyiCloudServiceのインスタンスを初期化しました。")

    # 2要素認証または2段階認証が必要か確認
    if api.requires_2fa:
        logger.info("2要素認証が必要です。認証コードを確認してください。")
        # ユーザーに認証コードの入力を促す
        # code = input("承認済みデバイスの1つで受信したコードを入力してください: ")

        # 設定ファイルから認証コードを取得
        while True:
            try:
                with open('.2fa_code', 'r') as f:
                    code = f.readline()
                    if code == "":
                        logger.warning("コードが空です。")
                    else:
                        logger.info(f"2要素認証コードを取得しました: {code.strip()}")
                        break
            except FileNotFoundError:
                logger.error("2要素認証コードファイルが見つかりません。")
                sys.exit(1)
          
            sleep(30)

        # 認証コードを検証
        result = api.validate_2fa_code(code)
        logger.info(f"2要素認証コードの検証結果: {'成功' if result else '失敗'}")

        if not result:
            logger.error("2要素認証コードの検証に失敗しました。")
            sys.exit(1)

        # セッションが信頼されているか確認
        if not api.is_trusted_session:
            logger.info("セッションが信頼されていません。信頼をリクエストします...")
            # セッションの信頼をリクエスト
            result = api.trust_session()
            logger.info(f"セッション信頼の結果: {'成功' if result else '失敗'}")

            if not result:
                logger.error("信頼のリクエストに失敗しました。今後数週間で再度コードを求められる可能性があります。")

    # 2段階認証が必要な場合
    elif api.requires_2sa:
        import click

        logger.info("2段階認証が必要です。信頼されたデバイスを一覧表示します。")

        # 信頼されたデバイスのリストを取得
        devices = api.trusted_devices
        for i, device in enumerate(devices):
            phoneNumber = device.get('phoneNumber')
            logger.info(f"デバイス {i}: {device.get('deviceName', f'SMS to {phoneNumber}')}")
        
        # 使用するデバイスを選択するようユーザーに促す
        device = click.prompt('どのデバイスを使用しますか?', default=0)
        device = devices[device]
        # 認証コードを送信
        if not api.send_verification_code(device):
            logger.error("認証コードの送信に失敗しました。")
            sys.exit(1)

        logger.info("認証コードを送信しました。コードを入力してください。")
        # ユーザーに認証コードの入力を促す
        code = click.prompt('認証コードを入力してください')
        # 認証コードを検証
        if not api.validate_verification_code(device, code):
            logger.error("認証コードの検証に失敗しました。")
            sys.exit(1)

        logger.info("認証コードの検証が完了しました。")

    # データベース接続のインスタンスを作成
    psql = PSQL(os.getenv('DATABASE_URL'))
    logger.info("データベースに接続しました。")

    today = datetime.datetime.min

    while True:
        today = datetime.datetime.today()
        logger.info(f"現在の日付と時刻: {today.strftime('%Y-%m-%d %H:%M:%S')}")

        # 今日が祝日かどうか確認
        is_holiday = psql.holidays.is_holiday_date(today)
        logger.info(f"今日は祝日ですか? {'はい' if is_holiday else 'いいえ'}")

        if is_holiday:
            logger.info("現在の時間は祝日期間内です。")
            # 祝日終了までの秒数を取得
            seconds = psql.holidays.seconds_until_holiday_end(datetime.datetime.today())
            logger.info(f"祝日期間が終了するまでスリープします。({seconds}秒)")
            for _ in range(86400): sleep(seconds / 86400)
            continue
        
        logger.info("今日の期間は祝日ではありません。")

        # 現在の時間が授業期間内かどうか確認
        is_within_class_time = psql.schedules.get_current_period(today.time())
        logger.info(f"現在の時間は授業期間内ですか? {'はい' if is_within_class_time else 'いいえ'}")

        if not is_within_class_time:
            logger.info("現在の時間は授業期間外です。")
            # 授業開始までの秒数を取得
            print(psql.class_times.seconds_until_class_start(today.time()))
            print(today.time())
            seconds = psql.class_times.seconds_until_class_start(today.time())
            # 今日後で授業がある場合
            if seconds is not None:
                logger.info(f"授業が始まるまでスリープします。({seconds}秒)")
                sleep(seconds)
            # 今日後で授業がない場合
            else:
                # 深夜までの秒数を取得
                seconds = (datetime.datetime.combine(today, datetime.time.max) - today).total_seconds()
                logger.info(f"明日までスリープします。({seconds}秒)")
                sleep(seconds)
                continue
        else:
            logger.info("現在の時間は授業期間内です。")

        # iPhoneから位置情報を取得
        lat_lon = api.iphone.location()
        if lat_lon is None:
            logger.error("位置情報の取得に失敗しました。")
            continue

        logger.info(f"取得した位置情報: 緯度={lat_lon['latitude']}, 経度={lat_lon['longitude']}")

        # データベースに位置情報を挿入
        psql.gps_locations.insert(lat_lon['latitude'], lat_lon['longitude'])
        logger.info("位置情報データをデータベースに挿入しました。")

        # データベースからすべての位置情報を取得して表示
        logger.info("データベースからすべての位置情報を取得しました。")
        print(psql.gps_locations.fetch_all())

        # 60秒間スリープ
        logger.info("60秒間スリープします。")
        sleep(60)

if __name__ == '__main__':
    main()
