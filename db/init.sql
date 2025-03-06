-- 建物情報テーブル（授業の場所）
CREATE TABLE locations (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL, -- 建物名
    latitude DOUBLE PRECISION NOT NULL, -- 緯度
    longitude DOUBLE PRECISION NOT NULL -- 経度
);

-- 授業スケジュールテーブル
CREATE TABLE schedules (
    id SERIAL PRIMARY KEY,
    weekday INT NOT NULL CHECK (weekday BETWEEN 0 AND 6), -- 0:日曜, 1:月曜, ..., 6:土曜
    period INT NOT NULL CHECK (period BETWEEN 1 AND 7), -- 1限目から7限目まで
    location_id INT REFERENCES locations(id) ON DELETE CASCADE, -- 授業が行われる建物
    class_name VARCHAR(255) NOT NULL -- 授業名
);

-- 出席管理テーブル（特定の1人の出席情報を記録）
CREATE TABLE attendance (
    id SERIAL PRIMARY KEY,
    schedule_id INT REFERENCES schedules(id) ON DELETE CASCADE,
    status VARCHAR(20) CHECK (status IN ('present', 'absent', 'late')), -- 出席ステータス
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- データ挿入用の別ファイルを読み込む
-- \i /docker-entrypoint-initdb.d/insert_data.sql;
