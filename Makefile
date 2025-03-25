uv-dev:
	uv run fastapi dev main.py

uv-granian:
	uv run granian --interface asgi main:app --host "0.0.0.0" --port 8000 --log-config logging_conf.json --reload

build-image:
	docker build --tag url-shortener-python:latest .

start-container:
	docker run -d -p 8000:8000 url-shortener-python:latest