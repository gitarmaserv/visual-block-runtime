# PROJECT MAP

## Структура проекта

```
visual-block-runtime/
├── backend/              # Python Runtime (FastAPI)
│   ├── main.py          # Точка входа
│   ├── api/             # HTTP API endpoints
│   ├── runtime/         # Логика выполнения графа
│   ├── plugins/         # Loader плагинов
│   ├── db/              # SQLite модуль
│   └── models/          # Pydantic модели
├── frontend/            # React + Vite + Electron
│   ├── src/
│   │   ├── components/ # React Flow компоненты
│   │   ├── hooks/      # Custom hooks
│   │   ├── services/   # API клиент
│   │   ├── store/      # State management
│   │   └── styles/     # CSS стили
│   ├── electron/       # Electron main process
│   └── package.json
├── plugins/            # Плагины (user-extensible)
│   └── <plugin_id>/
│       ├── plugin.py
│       ├── README.md
│       └── requirements.txt (опционально)
├── docs/               # Документация
│   ├── PROJECT_MAP.md
│   ├── SPEC.md
│   ├── PLUGIN_DEV_GUIDE.md
│   └── API.md
├── scripts/           # Утилиты
├── .kiloignore        # Игнор для Kilo/агентов
├── .gitignore         # Git ignore
├── .env.example       # Пример переменных окружения
└── README.md          # Главный README
```

## Базы данных

- **app.sqlite**: Настройки приложения, глобальные переменные
- **project.sqlite**: Данные проекта (граф, переменные, настройки нод)

## Ключевые принципы

1. UI и Python разделены
2. Коммуникация только через API (HTTP + WebSocket)
3. Плагины самодостаточны
4. Логирование в log.txt
