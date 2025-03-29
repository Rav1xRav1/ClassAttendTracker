import psycopg2
from psycopg2 import sql
from datetime import datetime, time

# holidaysテーブルのクラス
class HOLIDAYS:
    def __init__(self, cursor):
        self.cursor = cursor
    
    # 引数の日付が休暇が調べる
    def is_holiday_date(self, today):
        query = """
        SELECT * FROM holidays
        WHERE start_date <= %s AND end_date >= %s
        AND (start_period IS NULL OR start_period <= %s)
        AND (end_period IS NULL OR end_period >= %s)
        """
        self.cursor.execute(query, (today.date(), today.date(), 1, 1))
        return self.cursor.fetchone()
    
    # 引数の日付が休暇だった場合、休暇終了までの秒数を取得する
    def seconds_until_holiday_end(self, today):
        holiday = self.is_holiday_date(today)
        print(holiday)
        if holiday:
            end_date = holiday[2]
            end_period = holiday[4]
            if end_period is None:
                end_datetime = datetime.combine(end_date, datetime.max.time())
            else:
                end_datetime = datetime.combine(end_date, time(end_period))
            print(end_datetime, today)
            return (end_datetime - today).total_seconds()
        return None

# schedulesテーブルのクラス
class SCHEDULES:
    def __init__(self, cursor):
        self.cursor = cursor
    
    # 全ての情報を返す
    def fetch_all(self):
        query = """
        SELECT * FROM schedules
        """
        self.cursor.execute(query)
        return self.cursor.fetchall()

    # 現在時刻から現在何限目かを取得する関数
    def get_current_period(self, today_time):
        print(today_time)
        query = """
        SELECT period FROM class_times
        WHERE start_time <= %s AND end_time >= %s
        LIMIT 1
        """
        self.cursor.execute(query, (today_time, today_time))
        result = self.cursor.fetchone()
        return result[0] if result else None

    # 現在の曜日と時限数を使用して現在の授業を取得する関数
    def get_current_class(self, today):
        current_period = self.get_current_period(today.time())
        if current_period is None:
            return None
        
        query = """
        SELECT * FROM schedules
        WHERE weekday = %s AND period = %s
        LIMIT 1
        """
        day_of_week = today.weekday()  # 月曜日が0、日曜日が6
        self.cursor.execute(query, (day_of_week, current_period))
        return self.cursor.fetchone()

# class_timesテーブルのクラス
class CLASS_TIMES:
    def __init__(self, cursor):
        self.cursor = cursor
    
    # 全ての情報を返す
    def fetch_all(self):
        query = """
        SELECT * FROM class_times
        """
        self.cursor.execute(query)
        return self.cursor.fetchall()
    
    # 現在の時間以降で最も近い授業の時間を取得して現在時刻から何秒か返す
    def seconds_until_class_start(self, today):
        query = """
        SELECT start_time FROM class_times
        WHERE start_time >= %s
        ORDER BY start_time ASC
        LIMIT 1
        """
        self.cursor.execute(query, (today,))
        result = self.cursor.fetchone()
        if result:
            return (datetime.combine(datetime.today(), result[0]) - datetime.now()).total_seconds()
        return None

# 取得した位置情報を保存するテーブルを操作する
class GPS_LOCATIONS:
    def __init__(self, cursor, conn):
        self.cursor = cursor
        self.conn = conn  # conn属性を追加

    # 全データを取得して返す
    def fetch_all(self):
        query = """
        SELECT * FROM gps_locations
        """
        self.cursor.execute(query)
        return self.cursor.fetchall()

    # 位置情報を保存する関数
    def insert(self, lat, lon):
        query = """
        INSERT INTO gps_locations (latitude, longitude, timestamp)
        VALUES (%s, %s, %s)
        """
        self.cursor.execute(query, (lat, lon, datetime.now()))
        self.conn.commit()

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
        self.schedules = SCHEDULES(self.cursor)
        self.gps_locations = GPS_LOCATIONS(self.cursor, self.conn)  # connを渡す
        self.class_times = CLASS_TIMES(self.cursor)

    def close(self):
        self.cursor.close()
        self.conn.close()
