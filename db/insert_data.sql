-- 初期データを挿入
-- 建物情報
INSERT INTO locations (name, latitude, longitude) VALUES 
('Building A', 35.6895, 139.6917),
('Building B', 35.6896, 139.6920);

-- 授業スケジュール情報
INSERT INTO schedules (weekday, period, location_id, class_name) VALUES 
(1, 2, 1, 'Mathematics'),
(1, 3, 2, 'Physics'),
(2, 1, 1, 'Chemistry');
