# EntranceTest-Python
+ Cách deploy source code ở local PC
  + Lệnh để tải thư viện và khởi chạy ứng dụng: 
   - pip install Django==4.0.4
   - pip install djangorestframework
   - pip install djangorestframework_simplejwt
  + Thực thi lệnh để chạy server:
   - python manage.py runserver
+ Port để test ứng dụng:
  - http://127.0.0.1:8000/signin/
+ Cách kết nối database ở local PC
  - Thay đổi tập tin settings.py ở đường dẫn TodoWebDjangoWJTMySQL/TodoWebDjangoWJTMySQL/settings.py:
	DATABASES = {
    		'default': {
        		'ENGINE': 'django.db.backends.mysql',
        		'NAME': 'DB_Name', 
        		'HOST': '127.0.0.1',
        		'PORT': '3306',
        		'USER': 'user',
        		'PASSWORD': 'password',
    		}
Phần NAME thì thây thế là tên database đã tạo trên mysql
Phần PORT lấy từ MySQL Workbench
Phần USER và PASSWORD, thì dựa trên người dùng mỗi máy local

+ Cách khởi tạo database (tạo database, các table - và các dữ liệu mẫu nếu cần - dùng để chạy
project): có thể chọn cách export file .sql hoặc migration file của Django
	Cập nhật Settings:
		python manage.py makemigrations
		python manage.py migrate
