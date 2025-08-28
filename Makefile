.PHONY: help db-setup migrate run clean

help: ## Show this help message
	@echo "Available commands:"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

db-setup: ## Create database if it doesn't exist
	@echo "Setting up database..."
	./setup_db.sh

migrate: ## Run Django migrations
	@echo "Running migrations..."
	. venv/bin/activate && python3 manage.py migrate

run: ## Start Django development server
	@echo "Starting Django server..."
	. venv/bin/activate && python3 manage.py runserver

setup: db-setup migrate ## Complete setup: create DB and run migrations
	@echo "Setup complete!"

clean: ## Remove Python cache files
	@echo "Cleaning Python cache..."
	find . -type f -name "*.pyc" -delete
	find . -type d -name "__pycache__" -delete

test-s3: ## Test S3 connection
	@echo "Testing S3 connection..."
	. venv/bin/activate && python test_s3.py

