# trung-nguyen-legend-management
#bước 1:
git clone https://github.com/hzhzhz5/trung-nguyen-legend-management.git

cd trung-nguyen-legend-management

#bước 2: Tạo môi trường ảo bằng code trong cmd

python -m venv venv

venv\Scripts\activate

#bước 3: Tải thư viện

pip install -r requirements.txt

#bước 4: tạo file .env

SECRET_KEY=coffee_chain_secret_key_2026
DB_HOST=127.0.0.1
DB_PORT=3306
DB_NAME=trung_nguyen_legend_db
DB_USER=root
DB_PASSWORD=

#bước 5: chạy xampp tạo database

CREATE DATABASE trung_nguyen_legend_db

CHARACTER SET utf8mb4

COLLATE utf8mb4_unicode_ci;

#bước 6: chạy migration

flask --app run.py db upgrade

#bước 7: seed dữ liệu 

python seed_data.py

#sẽ có 3 tài khoản
#admin / admin123
#manager / manager123
#staff / staff123


#bước 8: Chạy Project

python run.py

#truy cập web

http://127.0.0.1:5000
