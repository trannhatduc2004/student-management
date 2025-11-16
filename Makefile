.PHONY: help install run init-db docker-build docker-up docker-down clean

help:
	@echo "Các lệnh có sẵn:"
	@echo "  make install     - Cài đặt dependencies"
	@echo "  make run         - Chạy ứng dụng local"
	@echo "  make init-db     - Khởi tạo database và dữ liệu mẫu"
	@echo "  make docker-build - Build Docker image"
	@echo "  make docker-up   - Chạy với Docker Compose"
	@echo "  make docker-down - Dừng Docker containers"
	@echo "  make clean       - Xóa cache và database local"

install:
	pip install -r requirements.txt

run:
	python app.py

init-db:
	python init_db.py

docker-build:
	docker build -t student-management .

docker-up:
	docker-compose up -d

docker-down:
	docker-compose down

clean:
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
	rm -f *.db *.sqlite *.sqlite3