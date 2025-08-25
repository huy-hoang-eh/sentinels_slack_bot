.PHONY: dev

# Auto-restart the bot when Python files change
dev:
	watchexec --restart --clear \
	  --watch src \
	  --watch main.py \
	  --exts py -- \
	  uv run main.py


