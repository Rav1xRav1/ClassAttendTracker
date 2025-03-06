import psycopg2
import os

# 環境変数からデータベース接続情報を取得
DATABASE_URL = os.getenv('DATABASE_URL', 'postgresql://user:password@db:5432/class_attendance')

def get_db_connection():
    # PostgreSQL に接続
    while True:
        try:
            conn = psycopg2.connect(DATABASE_URL)
            break
        except psycopg2.OperationalError:
            print('Retrying connection...')
    return conn

def fetch_locations():
    # データベース接続を取得
    conn = get_db_connection()
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

# メイン関数
if __name__ == '__main__':
    fetch_locations()
