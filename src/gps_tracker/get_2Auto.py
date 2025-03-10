import sys
import os
from time import sleep

from pyicloud import PyiCloudService
from pyicloud.exceptions import PyiCloudFailedLoginException

# 環境変数からユーザー名とパスワードを取得
user_name = os.environ.get('USER_NAME')
password = os.environ.get('PASSWORD')

# PyiCloudServiceのインスタンスを作成
try:
    api = PyiCloudService(user_name, password, cookie_directory="./.pyicloud", verify=True)
except PyiCloudFailedLoginException:
    print("Failed to log in to iCloud. Please check your credentials.")
    sys.exit(1)

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
