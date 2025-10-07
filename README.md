# Vroomly

### Локальный запуск проекта на Unix-системах (в Windows можно использовать WSL или Linux-терминалы)
Для бекендеров: запуск всех бекенд-сервисов, кроме самого бекенда,
он запускается вручную для отладки (см. backend/README.md для подробностей настройки)
```bash
make setup-for-backend
```
Для фронтендеров: запуск всех бекенд-сервисов
```bash
make setup-for-frontend
```

### Известные проблемы

В Windows не устанавливаются гит-хуки в контейнер бекенда:
Ошибка: `./backend/scripts/setup_docker_precommit.sh: /bin/sh^M: bad interpreter: No such file or directory`
Решение: для файла (а лучше для всего проекта) `./backend/scripts/setup_docker_precommit.sh` изменить отступы с CRLF на LF
