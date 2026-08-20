# Makefile — one command each
build:
	docker build -t refapp:local .

test:
	pytest -q

run:
	GREETING="Reference App" PORT=8000 python -m refapp.app
