import psycopg2
from psycopg2 import sql
from datetime import datetime, time


class CLASS_LOCATIONS:
    def __init__(self, cursor):
        self.cursor = cursor

    # 全ての情報を返す
    def fetch_all(self):
        query = """
        SELECT * FROM class_locations
        """
        self.cursor.execute(query)
        return self.cursor.fetchall()
    
    def get_class_location(self, location_id):
        query = """
        SELECT latitude, longitude FROM class_locations WHERE id = %s
        """
        self.cursor.execute(query, (location_id,))
        result = self.cursor.fetchone()
        return result if result else None


class SCHEDULES:
    def __init__(self, cursor):
        self.cursor = cursor

    # 全ての内容を返す関数
    def fetch_all(self):
        query = """
        SELECT * FROM schedules
        """
        self.cursor.execute(query)
        return self.cursor.fetchall()

    #  引数の曜日の授業を取得する関数
    def get_classes_by_weekday(self, weekday):
        query = """
        SELECT * FROM schedules WHERE weekday = %s
        """
        self.cursor.execute(query, (weekday,))
        return self.cursor.fetchall()


class GPS_LOCATIONS:
    def __init__(self, cursor):
        self.cursor = cursor

    # 全ての情報を返す
    def fetch_all(self):
        query = """
        SELECT * FROM gps_locations
        """
        self.cursor.execute(query)
        return self.cursor.fetchall()

    # 引数に指定された時間帯の位置情報を返す関数
    def get_location_by_time(self, start_time, end_time):
        query = """
        SELECT * FROM gps_locations WHERE timestamp BETWEEN %s AND %s
        """
        self.cursor.execute(query, (start_time, end_time))
        return self.cursor.fetchall()
    

class CLASS_TIMES:
    def __init__(self, cursor):
        self.cursor = cursor

    # periodを受け取って授業の時間帯を取得する関数
    def get_class_time(self, period):
        query = """
        SELECT start_time, end_time FROM class_times WHERE period = %s
        """
        self.cursor.execute(query, (period,))
        result = self.cursor.fetchone()
        return result if result else None


class ATTENDANCE:
    def __init__(self, cursor):
        self.cursor = cursor

    # 出席情報を挿入する関数
    def insert_attendance(self, schedule_id, status, timestamp):
        query = """
        INSERT INTO attendance (schedule_id, status, timestamp) VALUES (%s, %s, %s)
        """
        self.cursor.execute(query, (schedule_id, status, timestamp))


class PSQL:
    def __init__(self, DATABASE_URL, *tables):
        while True:
            try:
                self.conn = psycopg2.connect(DATABASE_URL)
                break
            except psycopg2.OperationalError:
                print('Retrying connection...')
        self.cursor = self.conn.cursor()
        
        self.class_locations = CLASS_LOCATIONS(self.cursor)
        self.schedules = SCHEDULES(self.cursor)
        self.gps_locations = GPS_LOCATIONS(self.cursor)
        self.class_times = CLASS_TIMES(self.cursor)
        self.attendance = ATTENDANCE(self.cursor)

    def close(self):
        self.cursor.close()
        self.conn.close()
