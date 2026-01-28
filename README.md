# Visual Block Runtime

Desktop-приложение для визуального создания и выполнения графов из блоков (нод).

## Архитектура

- **Frontend**: React + Vite + Electron
- **Backend**: Python 3.12 + FastAPI
- **Плагины**: Python модули в папке `plugins/`

## Быстрый старт

### 1. Установка зависимостей

**Backend:**
```bash
cd backend
pip install -r requirements.txt
```

**Frontend:**
```bash
cd frontend
npm install
```

### 2. Запуск

**Terminal 1 - Backend:**
```bash
cd backend
python main.py
```

**Terminal 2 - Frontend:**
```bash
cd frontend
npm run dev
```

**Terminal 3 - Electron (опционально):**
```bash
cd frontend
npm run electron
```

### 3. Использование

1. Создайте новый проект через UI или вручную:
   ```bash
   mkdir MyProject.botui
   cd MyProject.botui
   touch project.sqlite log.txt
   mkdir artifacts
   ```

2. Откройте проект в приложении

3. Добавьте ноды из палитры слева

4. Соедините ноды ребрами (OK/Fail ветки)

5. Настройте параметры нод в инспекторе справа

6. Запустите выполнение

## Структура проекта

```
visual-block-runtime/
├── backend/              # Python Runtime
│   ├── main.py          # FastAPI приложение
│   ├── api/             # HTTP API endpoints
│   ├── db/              # SQLite модуль
│   ├── plugins/         # Loader плагинов
│   └── runtime/         # Логика выполнения
├── frontend/            # React + Vite + Electron
│   ├── src/
│   │   ├── components/  # UI компоненты
│   │   ├── store.js     # Zustand state management
│   │   └── styles/      # CSS стили
│   └── electron/        # Electron main process
├── plugins/             # Плагины
│   └── example_plugin/
├── docs/                # Документация
└── scripts/             # Утилиты
```

## Документация

- [PROJECT_MAP.md](docs/PROJECT_MAP.md) - Структура проекта
- [SPEC.md](docs/SPEC.md) - Контракты и спецификации
- [PLUGIN_DEV_GUIDE.md](docs/PLUGIN_DEV_GUIDE.md) - Как создавать плагины
- [API.md](docs/API.md) - API контракт

## Создание плагинов

См. [PLUGIN_DEV_GUIDE.md](docs/PLUGIN_DEV_GUIDE.md)

## API

Backend слушает `http://127.0.0.1:8000`

## Лицензия

MIT
