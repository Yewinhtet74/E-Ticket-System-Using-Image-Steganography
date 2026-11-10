-- ============================================================
-- airline_database setup for the YE Air Flask project
-- Rebuilt from the SQL queries in app.py / mycollection.py / ticket_center.py.
-- Planes match price_of_route.json; flights are SAMPLE data.
-- Safe: CREATE DATABASE fails if airline_database already exists,
-- so an existing (original) database is never overwritten.
-- ============================================================

CREATE DATABASE airline_database CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci;
USE airline_database;

CREATE TABLE plane (
  plane_no INT PRIMARY KEY,
  first_seat INT NOT NULL DEFAULT 0,
  business_seat INT NOT NULL DEFAULT 0,
  premium_seat INT NOT NULL DEFAULT 0,
  economy_seat INT NOT NULL DEFAULT 0
);

CREATE TABLE route (
  flight_no VARCHAR(10) PRIMARY KEY,
  departure CHAR(3) NOT NULL,
  arrival CHAR(3) NOT NULL,
  day TINYINT NOT NULL COMMENT '1=Mon ... 7=Sun',
  departure_time TIME NOT NULL,
  arrival_time TIME NOT NULL,
  flight_time TIME NOT NULL,
  plane_no INT NOT NULL,
  FOREIGN KEY (plane_no) REFERENCES plane(plane_no)
);

CREATE TABLE ticket (
  ticket_no INT PRIMARY KEY,
  secret_code VARCHAR(36) NOT NULL UNIQUE,
  passenger VARCHAR(100) NOT NULL,
  passport VARCHAR(30) NOT NULL,
  flight_no VARCHAR(10) NOT NULL,
  class VARCHAR(15) NOT NULL,
  date DATE NOT NULL,
  email VARCHAR(100),
  phone VARCHAR(30),
  check_in TIME NULL DEFAULT NULL
);

-- one row only; read by get_key() (must have exactly 2 columns)
CREATE TABLE aes (
  secret_key VARBINARY(16) NOT NULL,
  iv VARBINARY(16) NOT NULL
);

-- per-ticket AES key + IV used to verify uploaded e-tickets
CREATE TABLE aes2 (
  ticket_no INT PRIMARY KEY,
  secret_key VARBINARY(16) NOT NULL,
  iv VARBINARY(16) NOT NULL
);

-- column order matters: find_counter() reads counter_no as the 3rd column
CREATE TABLE checkincounter (
  flight_no VARCHAR(10) NOT NULL,
  date DATE NOT NULL,
  counter_no INT NOT NULL,
  passcode VARCHAR(8) NOT NULL,
  PRIMARY KEY (flight_no, date)
);

CREATE TABLE adminaccount (
  username VARCHAR(50) PRIMARY KEY,
  password VARCHAR(100) NOT NULL
);

-- ---------- data ----------
-- placeholder row: get_key() reads it, but every ticket gets its own random key (stored in aes2)
INSERT INTO aes (secret_key, iv) VALUES (X'00000000000000000000000000000000', X'00000000000000000000000000000000');

INSERT INTO adminaccount (username, password) VALUES ('admin', 'admin123');

INSERT INTO plane (plane_no, first_seat, business_seat, premium_seat, economy_seat) VALUES
  (1, 0, 0, 24, 150),
  (2, 0, 0, 24, 150),
  (3, 0, 20, 40, 0),
  (4, 0, 16, 30, 120),
  (5, 8, 0, 30, 150),
  (6, 8, 24, 0, 180),
  (7, 0, 20, 30, 140),
  (8, 0, 24, 48, 0),
  (9, 0, 20, 40, 0),
  (10, 0, 0, 30, 150),
  (13, 0, 30, 0, 250),
  (14, 0, 28, 40, 200);

-- RGN <-> BKK: Mon, Tue, Wed, Thu, Fri, Sat, Sun
-- RGN <-> SIN: Mon, Wed, Fri, Sun
-- RGN <-> KUL: Tue, Thu, Sat
-- RGN <-> SGN: Mon, Thu, Sat
-- RGN <-> CGK: Tue, Fri
-- RGN <-> MNL: Wed, Sat
-- RGN <-> ICN: Tue, Fri, Sun
-- RGN <-> HND: Mon, Thu, Sat
INSERT INTO route (flight_no, departure, arrival, day, departure_time, arrival_time, flight_time, plane_no) VALUES
  ('YE0101', 'RGN', 'BKK', 1, '08:00:00', '09:45:00', '01:15:00', 1),
  ('YE0102', 'BKK', 'RGN', 1, '11:00:00', '11:50:00', '01:20:00', 1),
  ('YE0103', 'RGN', 'BKK', 2, '08:00:00', '09:45:00', '01:15:00', 2),
  ('YE0104', 'BKK', 'RGN', 2, '11:00:00', '11:50:00', '01:20:00', 2),
  ('YE0105', 'RGN', 'BKK', 3, '08:00:00', '09:45:00', '01:15:00', 1),
  ('YE0106', 'BKK', 'RGN', 3, '11:00:00', '11:50:00', '01:20:00', 1),
  ('YE0107', 'RGN', 'BKK', 4, '08:00:00', '09:45:00', '01:15:00', 2),
  ('YE0108', 'BKK', 'RGN', 4, '11:00:00', '11:50:00', '01:20:00', 2),
  ('YE0109', 'RGN', 'BKK', 5, '08:00:00', '09:45:00', '01:15:00', 1),
  ('YE0110', 'BKK', 'RGN', 5, '11:00:00', '11:50:00', '01:20:00', 1),
  ('YE0111', 'RGN', 'BKK', 6, '08:00:00', '09:45:00', '01:15:00', 2),
  ('YE0112', 'BKK', 'RGN', 6, '11:00:00', '11:50:00', '01:20:00', 2),
  ('YE0113', 'RGN', 'BKK', 7, '08:00:00', '09:45:00', '01:15:00', 1),
  ('YE0114', 'BKK', 'RGN', 7, '11:00:00', '11:50:00', '01:20:00', 1),
  ('YE0201', 'RGN', 'SIN', 1, '10:30:00', '14:50:00', '02:50:00', 5),
  ('YE0202', 'SIN', 'RGN', 1, '16:00:00', '17:30:00', '03:00:00', 5),
  ('YE0203', 'RGN', 'SIN', 3, '10:30:00', '14:50:00', '02:50:00', 6),
  ('YE0204', 'SIN', 'RGN', 3, '16:00:00', '17:30:00', '03:00:00', 6),
  ('YE0205', 'RGN', 'SIN', 5, '10:30:00', '14:50:00', '02:50:00', 5),
  ('YE0206', 'SIN', 'RGN', 5, '16:00:00', '17:30:00', '03:00:00', 5),
  ('YE0207', 'RGN', 'SIN', 7, '10:30:00', '14:50:00', '02:50:00', 6),
  ('YE0208', 'SIN', 'RGN', 7, '16:00:00', '17:30:00', '03:00:00', 6),
  ('YE0301', 'RGN', 'KUL', 2, '09:15:00', '13:15:00', '02:30:00', 3),
  ('YE0302', 'KUL', 'RGN', 2, '14:30:00', '15:35:00', '02:35:00', 3),
  ('YE0303', 'RGN', 'KUL', 4, '09:15:00', '13:15:00', '02:30:00', 4),
  ('YE0304', 'KUL', 'RGN', 4, '14:30:00', '15:35:00', '02:35:00', 4),
  ('YE0305', 'RGN', 'KUL', 6, '09:15:00', '13:15:00', '02:30:00', 3),
  ('YE0306', 'KUL', 'RGN', 6, '14:30:00', '15:35:00', '02:35:00', 3),
  ('YE0401', 'RGN', 'SGN', 1, '13:00:00', '15:40:00', '02:10:00', 7),
  ('YE0402', 'SGN', 'RGN', 1, '17:00:00', '18:45:00', '02:15:00', 7),
  ('YE0403', 'RGN', 'SGN', 4, '13:00:00', '15:40:00', '02:10:00', 8),
  ('YE0404', 'SGN', 'RGN', 4, '17:00:00', '18:45:00', '02:15:00', 8),
  ('YE0405', 'RGN', 'SGN', 6, '13:00:00', '15:40:00', '02:10:00', 7),
  ('YE0406', 'SGN', 'RGN', 6, '17:00:00', '18:45:00', '02:15:00', 7),
  ('YE0501', 'RGN', 'CGK', 2, '07:30:00', '12:00:00', '04:00:00', 9),
  ('YE0502', 'CGK', 'RGN', 2, '13:30:00', '17:10:00', '04:10:00', 9),
  ('YE0503', 'RGN', 'CGK', 5, '07:30:00', '12:00:00', '04:00:00', 9),
  ('YE0504', 'CGK', 'RGN', 5, '13:30:00', '17:10:00', '04:10:00', 9),
  ('YE0601', 'RGN', 'MNL', 3, '11:00:00', '16:20:00', '03:50:00', 10),
  ('YE0602', 'MNL', 'RGN', 3, '17:30:00', '20:00:00', '04:00:00', 10),
  ('YE0603', 'RGN', 'MNL', 6, '11:00:00', '16:20:00', '03:50:00', 10),
  ('YE0604', 'MNL', 'RGN', 6, '17:30:00', '20:00:00', '04:00:00', 10),
  ('YE0701', 'RGN', 'ICN', 2, '23:30:00', '07:30:00', '05:30:00', 13),
  ('YE0702', 'ICN', 'RGN', 2, '18:00:00', '22:00:00', '06:30:00', 13),
  ('YE0703', 'RGN', 'ICN', 5, '23:30:00', '07:30:00', '05:30:00', 13),
  ('YE0704', 'ICN', 'RGN', 5, '18:00:00', '22:00:00', '06:30:00', 13),
  ('YE0705', 'RGN', 'ICN', 7, '23:30:00', '07:30:00', '05:30:00', 13),
  ('YE0706', 'ICN', 'RGN', 7, '18:00:00', '22:00:00', '06:30:00', 13),
  ('YE0801', 'RGN', 'HND', 1, '22:00:00', '07:00:00', '06:30:00', 14),
  ('YE0802', 'HND', 'RGN', 1, '11:00:00', '16:15:00', '07:45:00', 14),
  ('YE0803', 'RGN', 'HND', 4, '22:00:00', '07:00:00', '06:30:00', 14),
  ('YE0804', 'HND', 'RGN', 4, '11:00:00', '16:15:00', '07:45:00', 14),
  ('YE0805', 'RGN', 'HND', 6, '22:00:00', '07:00:00', '06:30:00', 14),
  ('YE0806', 'HND', 'RGN', 6, '11:00:00', '16:15:00', '07:45:00', 14);
