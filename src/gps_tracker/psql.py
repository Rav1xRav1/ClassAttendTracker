import psycopg2
from psycopg2 import sql
from datetime import datetime

class HOLIDAYS:
    def __init__(self, cursor):
        self.cursor = cursor

    def fetch_all(self):
        query = "SELECT * FROM holidays"
        self.cursor.execute(query)
        return self.cursor.fetchall()
    
    # 引数の日付が休暇が調べる
    def is_holiday_date(self, date):
        query = """
        SELECT * FROM holidays
        WHERE start_date <= %s AND end_date >= %s
        AND (start_period IS NULL OR start_period <= %s)
        AND (end_period IS NULL OR end_period >= %s)
        """
        self.cursor.execute(query, (date, date, 1, 1))
        return self.cursor.fetchone()
    
    # 引数の日付が休暇だった場合、休暇終了までの秒数を取得する
    def seconds_until_holiday_end(self, date):
        holiday = self.is_holiday_date(date)
        print(holiday)
        if holiday:
            end_date = holiday[2]  # タプルのインデックスを使用
            end_datetime = datetime.combine(end_date, datetime.min.time())
            current_datetime = datetime.combine(date, datetime.min.time())
            return (end_datetime - current_datetime).total_seconds()
        return None

class PSQL:
    def __init__(self, DATABASE_URL, *tables):
        while True:
            try:
                self.conn = psycopg2.connect(DATABASE_URL)
                break
            except psycopg2.OperationalError:
                print('Retrying connection...')
        self.cursor = self.conn.cursor()
        
        self.holidays = HOLIDAYS(self.cursor)

    def close(self):
        self.cursor.close()
        self.connection.close()
