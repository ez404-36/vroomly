# Vroomly

### Локальное развертывание проекта на Unix-системах (в Windows можно использовать WSL или Linux-терминалы)
Для бекендеров: запуск всех бекенд-сервисов, кроме самого бекенда,
он запускается вручную для отладки (см. backend/README.md для подробностей настройки)
```bash
make setup-for-backend
```
Для фронтендеров: запуск всех бекенд-сервисов
```bash
make setup-for-frontend
```

После успешного поднятия всех сервисов необходимо наполнить БД первичными данными:
```bash
make seeds
```

### Известные проблемы

**Конфликт подсетей Docker и VPN (Amnezia, WireGuard и др.)**

Если при включённом VPN БД недоступна, это значит, что подсеть Docker пересекается с VPN-туннелем.

Решение: удалите старую сеть и пересоздайте с правильной подсетью:
```bash
docker compose down
docker network rm vroomly
make setup-for-backend
```

---

**Windows: не устанавливаются гит-хуки в контейнер бекенда:**

Ошибка: `./backend/scripts/setup_docker_precommit.sh: /bin/sh^M: bad interpreter: No such file or directory`
Решение: для файла `./backend/scripts/setup_docker_precommit.sh` изменить перенос строк с CRLF на LF
