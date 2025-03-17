from pyicloud import PyiCloudService
import psycopg2

import datetime
import os
import sys

from time import sleep

from psql import PSQL
import logging


def main():
    # ログの設定
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
    logger = logging.getLogger(__name__)
    
    # 環境変数からユーザー名とパスワードを取得
    user_name = os.environ.get('USER_NAME')
    password = os.environ.get('PASSWORD')

    # PyiCloudServiceのインスタンスを作成
    api = PyiCloudService(user_name, password, cookie_directory="./.pyicloud", verify=True)

    # 2要素認証または2段階認証が必要かどうかを確認
    # print(api.requires_2fa, api.requires_2sa)

    # 2要素認証が必要な場合
    if api.requires_2fa:
        logger.info("Two-factor authentication required.")
        # ユーザーに認証コードの入力を求める
        # code = input("Enter the code you received of one of your approved devices: ")

        # 設定ファイルから認証コードを取得
        while True:
            try:
                with open('.2fa_code', 'r') as f:
                    code = f.readline()
                    if code == "":
                        print("Code is empty.")
                    else:
                        logger.info(f"CODE: {code}")
                        break
            except FileNotFoundError:
                logger.error("File not found.")
                sys.exit(1)
            
            sleep(30)

        # 認証コードを検証
        result = api.validate_2fa_code(code)
        logger.info(f"Code validation result: {result}")

        if not result:
            logger.error("Failed to verify security code")
            sys.exit(1)

        # セッションが信頼されているかどうかを確認
        if not api.is_trusted_session:
            logger.info("Session is not trusted. Requesting trust...")
            # セッションの信頼をリクエスト
            result = api.trust_session()
            logger.info(f"Session trust result {result}")

            if not result:
                logger.error("Failed to request trust. You will likely be prompted for the code again in the coming weeks")

    # 2段階認証が必要な場合
    elif api.requires_2sa:
        import click

        logger.info("Two-step authentication required. Your trusted devices are:")

        # 信頼されたデバイスのリストを取得
        devices = api.trusted_devices
        for i, device in enumerate(devices):
            phoneNumber = device.get('phoneNumber')
            print(f"  {i}: {device.get('deviceName', f'SMS to {phoneNumber}')}")

        # 使用するデバイスをユーザーに選択させる
        device = click.prompt('Which device would you like to use?', default=0)
        device = devices[device]
        # 認証コードを送信
        if not api.send_verification_code(device):
            print("Failed to send verification code")
            sys.exit(1)

        # ユーザーに認証コードの入力を求める
        code = click.prompt('Please enter validation code')
        # 認証コードを検証
        if not api.validate_verification_code(device, code):
            print("Failed to verify verification code")
            sys.exit(1)

    # for i, device in enumerate(api.devices):
    #     print(f"{i + 1}. {device}")

    # データベース接続のインスタンスを作成
    psql = PSQL(os.getenv('DATABASE_URL'))

    today = datetime.datetime.min

    # holidaysテーブルからすべてのデータを取り出して表示する
    # holidays = psql.holidays.fetch_all()
    # for holiday in holidays:
    #     print(holiday)

    while True:
        today = datetime.datetime.today()

        # 今日が授業除外日でないか確認する
        is_holiday = psql.holidays.is_holiday_date(datetime.datetime.today())

        # 結果を確認
        if is_holiday:
            logger.info("現在時刻は除外時刻です。")
            # 休暇終了までの秒数を取得
            seconds = psql.holidays.seconds_until_holiday_end(datetime.datetime.today())
            logger.info(f"除外時間終了までスリープします。({seconds}秒)")
            # for _ in range(86400): sleep(seconds / 86400)
            # continue
        
        logger.info("今日のコマは休暇に含まれていません。")

        # 現在時刻が授業時間に含まれているか確認
        is_within_class_time = psql.schedules.get_current_period(today.time())
        # 現在時刻が授業時間に含まれていない場合
        if not is_within_class_time:
            logger.info("現在時刻は授業時間外です。")
            # 授業開始までの秒数を取得
            seconds = psql.schedules.seconds_until_class_start(today.time())
            # 本日これ以降授業があるなら
            if seconds is not None:
                logger.info(f"授業開始までスリープします。({seconds}秒)")
                sleep(seconds)
            # 本日これ以降授業がないなら
            else:
                # 次の日の午前0時までの秒数を取得
                seconds = (datetime.datetime.combine(today, datetime.time.max) - today).total_seconds()
                logger.info(f"明日までスリープします。({seconds}秒)")
                # sleep(seconds)
                # continue
        # 現在時刻が授業時間内なら
        else:
            pass

        # iPhoneの位置情報を取得
        lat_lon = api.iphone.location()
        if lat_lon is None:
            logger.error("Failed to get location.")
            continue

        logger.info(lat_lon)

        # 位置情報をデータベースに挿入
        psql.gps_locations.insert(lat_lon['latitude'], lat_lon['longitude'])

        # データベースからすべての位置情報を取得して表示
        print(psql.gps_locations.fetch_all())

        # 1分間スリープ
        sleep(60)

if __name__ == '__main__':
    main()
