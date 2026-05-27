.PHONY: run help clean

help:
	@echo "clitype - Terminal Typing Test"
	@echo ""
	@echo "Available commands:"
	@echo "  make run    - Run the typing test application"
	@echo "  make clean  - Remove Python cache files"
	@echo "  make help   - Show this help message"

run:
	python3 clitype.py

clean:
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete 2>/dev/null || true
	@echo "Cleaned up Python cache files"
