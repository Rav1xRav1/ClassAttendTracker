import psycopg2
from psycopg2 import sql
from datetime import datetime, time


class CLASS_LOCATIONS:
    def __init__(self, cursor):
        self.cursor = cursor

    # 全ての情報を返す
    def fetch_all(self):
        query = """
        SELECT * FROM locations
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
    
    # 引数に与えられた曜日の授業を返す関数
    def get_class_by_weekday(self, weekday):
        query = """
        SELECT * FROM schedules WHERE weekday = %s
        """
        self.cursor.execute(query, (weekday,))
        return self.cursor.fetchall()


class SCHEDULES:
    def __init__(self, cursor):
        self.cursor = cursor

    #  引数の曜日の授業を取得する関数
    def get_classes_by_weekday(self, weekday):
        query = """
        SELECT * FROM schedules WHERE weekday = %s
        """
        self.cursor.execute(query, (weekday,))
        return self.cursor.fetchall()


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

    def close(self):
        self.cursor.close()
        self.conn.close()
