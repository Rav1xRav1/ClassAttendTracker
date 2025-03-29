import psycopg2
import os

from psql import PSQL

from datetime import datetime


# メイン関数
def main():
    # 環境変数からデータベース接続情報を取得
    DATABASE_URL = os.getenv('DATABASE_URL', 'postgresql://user:password@db:5432/class_attendance')

    # データベース接続を取得
    while True:
        try:
            conn = psycopg2.connect(DATABASE_URL)
            break
        except psycopg2.OperationalError:
            print('Retrying connection...')
    cursor = conn.cursor()

    # print("TEST :",cursor)

    # テーブル一覧を取得
    cursor.execute("SELECT tablename FROM pg_tables WHERE schemaname = 'public';")

    # 結果を表示
    tables = cursor.fetchall()
    for table in tables:
        print(table[0])
    
    # locations テーブルからデータを取得
    cursor.execute('SELECT id, name, latitude, longitude FROM locations')
    locations = cursor.fetchall()
    
    # データを表示
    for location in locations:
        print(f'Location ID: {location[0]}, Name: {location[1]}, Latitude: {location[2]}, Longitude: {location[3]}')
    
    # クローズ
    cursor.close()
    conn.close()

    # 本日の曜日を1~6で取得
    today_weekday = datetime.now().weekday() + 1

    # 授業の中心座標と円の半径を取得
    # データベース接続のインスタンスを作成
    psql = PSQL(os.getenv('DATABASE_URL'))
    # 本日の授業のリストを取得
    today_class = psql.class_locations.get_class_location(today_weekday)


if __name__ == '__main__':
    main()
