from pyicloud import PyiCloudService
import psycopg2

import datetime
import os
import sys

from time import sleep


def main():
    user_name = os.environ.get('USER_NAME')
    password = os.environ.get('PASSWORD')

    api = PyiCloudService(user_name, password, cookie_directory="./.pyicloud", verify=True)

    # 2要素認証または2段階認証が必要かどうかを確認
    print(api.requires_2fa, api.requires_2sa)

    # 2要素認証が必要な場合
    if api.requires_2fa:
        print("Two-factor authentication required.")
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
                        print("CODE: ", code)
                        break
            except FileNotFoundError:
                print("File not found.")
                sys.exit(1)
            
            sleep(30)

        # 認証コードを検証
        result = api.validate_2fa_code(code)
        print(f"Code validation result: {result}")

        if not result:
            print("Failed to verify security code")
            sys.exit(1)

        # セッションが信頼されているかどうかを確認
        if not api.is_trusted_session:
            print("Session is not trusted. Requesting trust...")
            # セッションの信頼をリクエスト
            result = api.trust_session()
            print(f"Session trust result {result}")

            if not result:
                print("Failed to request trust. You will likely be prompted for the code again in the coming weeks")

    # 2段階認証が必要な場合
    elif api.requires_2sa:
        import click

        print("Two-step authentication required. Your trusted devices are:")

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

    for i, device in enumerate(api.devices):
        print(f"{i + 1}. {device}")

    today = datetime.datetime(2000, 1, 1)

    # データベースに接続する
    DATABASE_URL= os.getenv('DATABASE_URL')
    while True:
        try:
            conn = psycopg2.connect(DATABASE_URL)
            break
        except psycopg2.OperationalError:
            print('Retrying connection...')

    # カーソルを取得する
    cursor = conn.cursor()

    # holidaysテーブルからすべてのデータを取り出して表示する
    cursor.execute("SELECT * FROM holidays")
    holidays = cursor.fetchall()
    for holiday in holidays:
        print(holiday)

    # 現在のディレクトリを表示
    current_directory = os.getcwd()
    print(f"現在のディレクトリ: {current_directory}")

    # 現在のディレクトリのファイルとフォルダをすべて表示
    files_and_folders = os.listdir(current_directory)
    print("ファイルとフォルダ:")
    for item in files_and_folders:
        print(item)

    while True:
        # 日付が変わったなら
        if datetime.datetime.now() != today:
            today = datetime.datetime.now()

            # 今日が授業除外日でないか確認する
            # holidaysテーブルをクエリ
            query = """
            SELECT * FROM holidays
            WHERE start_date <= %s AND end_date >= %s
            AND (start_period IS NULL OR start_period <= %s)
            AND (end_period IS NULL OR end_period >= %s)
            """
            t = datetime.datetime.today().date()
            cursor.execute(query, (t, t, 1, 1))
            result = cursor.fetchone()

            # 結果を確認
            if result:
                print("今日のコマは休暇に含まれています。")
            else:
                print("今日のコマは休暇に含まれていません。")
            
            break

    lat_lon = api.devices[1].location()

    print(lat_lon)

if __name__ == '__main__':
    main()
