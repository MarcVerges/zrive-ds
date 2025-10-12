setup:
	uv sync

lint:
	black src tests

test:
	flake8 src tests
	pytest tests

run:
	@if [ -z "$(m)" ]; then \
		echo "❌ Error: debes indicar el módulo a ejecutar:"; \
		echo "   make run m=module_1.module_1_main"; \
	else \
		python -m src.$(m); \
	fi