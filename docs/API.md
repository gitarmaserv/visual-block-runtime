# API.md - HTTP API контракт

## Базовый URL
```
http://127.0.0.1:8000/api
```

## WebSocket
```
ws://127.0.0.1:8000/ws/events
```

---

## Плагины

### GET /plugins
Получить список доступных плагинов.

**Response:**
```json
{
  "plugins": [
    {
      "plugin_id": "example",
      "name": "Example Plugin",
      "version": "1.0.0",
      "category": "Utility",
      "tags": ["demo"],
      "spec": { ... }  // Полный spec из get_spec()
    }
  ]
}
```

---

## Проекты

### POST /projects/create
Создать новый проект.

**Request:**
```json
{
  "name": "MyProject",
  "path": "/path/to/projects/MyProject.botui"
}
```

**Response:**
```json
{
  "success": true,
  "project_id": "MyProject"
}
```

### POST /projects/open
Открыть проект.

**Request:**
```json
{
  "path": "/path/to/MyProject.botui"
}
```

### POST /projects/save
Явное сохранение проекта.

### GET /projects/state
Текущее состояние проекта.

**Response:**
```json
{
  "path": "/path/to/MyProject.botui",
  "name": "MyProject",
  "is_modified": false
}
```

---

## Граф

### GET /graph/load
Загрузить граф.

**Response:**
```json
{
  "graph_json": {
    "nodes": [...],
    "edges": [...],
    "viewport": {...}
  }
}
```

### POST /graph/save
Сохранить граф.

**Request:**
```json
{
  "graph_json": { ... }
}
```

### POST /graph/validate
Валидировать граф перед запуском.

**Response:**
```json
{
  "valid": true,
  "errors": []
}
```

**Пример ошибок:**
```json
{
  "valid": false,
  "errors": [
    {
      "node_uid": "node_1",
      "error": "INPUT.NOT_SELECTED",
      "message": "Input variable not selected"
    }
  ]
}
```

---

## Ноды

### GET /nodes/settings
Настройки нод.

**Response:**
```json
{
  "settings": {
    "node_1": {
      "plugin_id": "example",
      "node_title": "My Node",
      "params": {},
      "input_var_ref": null,
      "output_var_ref": null,
      "error_to_fail": false,
      "breakpoint": false,
      "visual": {}
    }
  }
}
```

### POST /nodes/settings/update
Обновить настройки ноды.

**Request:**
```json
{
  "node_uid": "node_1",
  "settings": {
    "node_title": "New Title",
    "breakpoint": true
  }
}
```

---

## Переменные

### GET /vars/project
Список project переменных.

**Response:**
```json
{
  "variables": [
    {
      "var_id": 1,
      "base_name": "data",
      "title": "1Value_data",
      "description": "My data",
      "value_preview": {...}
    }
  ]
}
```

### POST /vars/project/create
Создать project переменную.

**Request:**
```json
{
  "base_name": "result",
  "description": "Result of operation"
}
```

**Response:**
```json
{
  "var_id": 2,
  "title": "2Value_result",
  "ref": "proj:2"
}
```

### GET /vars/get
Получить значение переменной.

**Query:** `?ref=proj:1`

**Response:**
```json
{
  "value": {...}
}
```

### POST /vars/set
Установить значение переменной.

**Request:**
```json
{
  "ref": "proj:1",
  "value": {...}
}
```

---

## Настройки приложения

### GET /app/settings
Получить настройки.

**Response:**
```json
{
  "settings": {
    "ui.theme": "dark",
    "ui.log.max_lines": 1000
  }
}
```

### POST /app/settings/set
Установить настройку.

**Request:**
```json
{
  "key": "ui.theme",
  "value": "dark"
}
```

---

## Выполнение

### POST /run/start_from_beginning
Запуск с начальной ноды.

**Request:**
```json
{
  "run_id": "run_001"
}
```

### POST /run/start_from_selected
Запуск с выбранной ноды.

**Request:**
```json
{
  "node_uid": "node_2",
  "run_id": "run_001"
}
```

### POST /run/stop_soft
Мягкая остановка (после завершения текущей ноды).

### POST /run/stop_hard
Жёсткая остановка (немедленно).

### POST /run/resume
Продолжить после паузы.

### GET /run/status
Статус выполнения.

**Response:**
```json
{
  "state": "Running",  // Idle, Running, Paused
  "run_id": "run_001",
  "active_node_uid": "node_3",
  "active_node_title": "Processing..."
}
```

---

## Логи

### GET /log/tail
Получить последние N строк лога.

**Query:** `?lines=100&level=INFO`

**Response:**
```json
{
  "lines": [
    "2026-01-28 12:00:00.123 | run=run_001 | ..."
  ]
}
```

---

## WebSocket Events

### ws://127.0.0.1:8000/ws/events

**run_state:**
```json
{
  "type": "run_state",
  "state": "Running",
  "run_id": "run_001",
  "active_node_uid": "node_3",
  "active_node_title": "Processing"
}
```

**log_line:**
```json
{
  "type": "log_line",
  "line": "2026-01-28 12:00:00.123 | run=run_001 | node=node_3 | ..."
}
```

**node_status:**
```json
{
  "type": "node_status",
  "node_uid": "node_1",
  "status": "OK"
}
```

**validation_errors:**
```json
{
  "type": "validation_errors",
  "errors": [...]
}
```
