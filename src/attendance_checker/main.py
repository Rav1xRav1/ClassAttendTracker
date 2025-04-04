from geopy.distance import geodesic
import psycopg2
import os
from psql import PSQL
from datetime import datetime, timedelta
from time import sleep
import logging

# ログ設定
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("attendance_checker.log"),
        logging.StreamHandler()
    ]
)

# メイン関数
def main():
    while True:
        # 本日の曜日を1~6で取得 (月曜日=1, 日曜日=7)
        today_weekday = datetime.now().weekday() + 1
        logging.info(f"本日の曜日: {today_weekday}")

        # データベース接続のインスタンスを作成
        psql = PSQL(os.getenv('DATABASE_URL'))
        logging.info("データベース接続を確立しました")

        # 本日の曜日に基づいて授業スケジュールを取得
        today_class = psql.schedules.get_classes_by_weekday(today_weekday)
        logging.info(f"本日の授業数: {len(today_class)}")

        # 本日の授業リストからそれぞれの授業の教室座標を取得
        for class_location in today_class:
            # 授業の情報を取得
            id_ = class_location[0]
            semester = class_location[1]
            weekday = class_location[2]
            period = class_location[3]
            location_id = class_location[4]
            class_name = class_location[5]
            logging.info(f"授業情報: ID={id_}, Name={class_name}, Period={period}")

            # 教室の座標を取得 (緯度と経度)
            latitude, longitude = psql.class_locations.get_class_location(location_id)
            logging.info(f"教室座標: Latitude={latitude}, Longitude={longitude}")

            # 授業の時間帯を取得 (開始時間と終了時間)
            start_time, end_time = psql.class_times.get_class_times_by_period(period)
            logging.info(f"授業時間帯: Start={start_time}, End={end_time}")

            # 授業時間帯に記録されたGPS座標を取得
            coordinate_lst = psql.gps_locations.get_location_by_time(start_time, end_time)
            logging.info(f"取得したGPS座標数: {len(coordinate_lst)}")

            # 授業中に範囲内にいるかどうかを確認
            is_within_area = []
            for coordinate in coordinate_lst:
                gps_latitude = coordinate[1]
                gps_longitude = coordinate[2]

                # 教室の座標との距離を計算し、範囲内かどうかを判定 (50メートル以内)
                if 50 > geodesic((latitude, longitude), (gps_latitude, gps_longitude)).meters:
                    is_within_area.append(True)
                else:
                    is_within_area.append(False)

            # 授業中の位置情報が6割以上範囲内なら出席、それ以外は欠席とする
            if len(is_within_area) > 0 and (is_within_area.count(True) / len(is_within_area)) > 0.6:
                psql.attendance.insert_attendance(id_, 'present', start_time)
                logging.info(f"出席登録: ID={id_}, Status=present")
            else:
                psql.attendance.insert_attendance(id_, 'absent', start_time)
                logging.info(f"欠席登録: ID={id_}, Status=absent")

            # 明日の19時までスリープする
            sleep_time = (datetime.now().replace(hour=19, minute=0, second=0, microsecond=0) + timedelta(days=1) - datetime.now()).total_seconds()
            logging.info(f"スリープ時間: {sleep_time}秒")
            for _ in range(86400): sleep(sleep_time / 86400)


if __name__ == '__main__':
    logging.info("プログラムを開始します")
    main()
