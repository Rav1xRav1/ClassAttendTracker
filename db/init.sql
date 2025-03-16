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

-- 授業がない日を保存するテーブル
CREATE TABLE holidays (
    id SERIAL PRIMARY KEY,
    start_date DATE NOT NULL, -- 休暇の開始日
    end_date DATE NOT NULL, -- 休暇の終了日
    start_period INT CHECK (start_period BETWEEN 1 AND 7), -- 休暇の開始コマ（オプション）
    end_period INT CHECK (end_period BETWEEN 1 AND 7), -- 休暇の終了コマ（オプション）
    description VARCHAR(255) -- 祝日や休暇の説明
);

-- 授業が振替になる日を保存するテーブル
CREATE TABLE rescheduled_classes (
    id SERIAL PRIMARY KEY,
    original_date DATE NOT NULL, -- 元の授業日
    new_date DATE NOT NULL, -- 振替後の授業日
    original_period INT NOT NULL CHECK (original_period BETWEEN 1 AND 7), -- 元の授業コマ
    new_period INT NOT NULL CHECK (new_period BETWEEN 1 AND 7), -- 振替後の授業コマ
    schedule_id INT REFERENCES schedules(id) ON DELETE CASCADE -- 振替対象の授業
);

-- 授業の時間を管理するテーブル
CREATE TABLE class_times (
    id SERIAL PRIMARY KEY,
    period INT NOT NULL CHECK (period BETWEEN 1 AND 7), -- 1限目から7限目まで
    start_time TIME NOT NULL, -- 授業開始時間
    end_time TIME NOT NULL -- 授業終了時間
);

-- 位置情報を保存するテーブル
CREATE TABLE location_data (
    id SERIAL PRIMARY KEY,
    latitude DOUBLE PRECISION NOT NULL, -- 緯度
    longitude DOUBLE PRECISION NOT NULL, -- 経度
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP -- 位置情報の取得時間
);

