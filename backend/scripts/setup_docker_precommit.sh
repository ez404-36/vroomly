#!/bin/sh
# Настройка pre-commit хука для работы внутри Docker-контейнера
# Использование: ./setup_docker_precommit.sh <container_name>

set -e

if [ -z "$1" ]; then
    echo "Usage: $0 <container_name>"
    exit 1
fi

CONTAINER_NAME="$1"
HOOK_FILE=".git/hooks/pre-commit"

if [ ! -f "$HOOK_FILE" ]; then
    echo "Error: pre-commit hook not found. Run 'pre-commit install' first."
    exit 1
fi

# Сохраняем оригинальный хук на всякий случай
cp "$HOOK_FILE" "${HOOK_FILE}.orig"

# Перезаписываем хук
cat > "$HOOK_FILE" <<EOL
#!/bin/sh
# Auto-generated Docker pre-commit hook
CONTAINER_NAME="$CONTAINER_NAME"

if [ "\$(docker ps -q -f name=\$CONTAINER_NAME)" ]; then
    docker exec -i \$CONTAINER_NAME sh -c "cd /app; pre-commit run --hook-stage pre-commit"
    EXIT_CODE=\$?
    if [ \$EXIT_CODE -ne 0 ]; then
        echo "Pre-commit hooks failed inside container \$CONTAINER_NAME"
        exit \$EXIT_CODE
    fi
else
    echo "Container \$CONTAINER_NAME is not running. Skipping pre-commit hooks."
fi

exit 0
EOL

chmod +x "$HOOK_FILE"
echo "Docker pre-commit hook installed for container '$CONTAINER_NAME'."
