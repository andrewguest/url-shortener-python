build-image:
	docker build --tag url-shortener-python:latest .

start-container:
	docker run -d -p 8000:8000 url-shortener-python:latest