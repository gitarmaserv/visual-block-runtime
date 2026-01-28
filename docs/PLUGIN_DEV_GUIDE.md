# PLUGIN_DEV_GUIDE.md

## Создание плагина

### 1. Структура плагина

```
plugins/<plugin_id>/
├── plugin.py        # ОБЯЗАТЕЛЬНО
├── README.md        # ОБЯЗАТЕЛЬНО
├── requirements.txt # Опционально
└── assets/          # Опционально
```

### 2. Пример плагина

**`plugins/example/plugin.py`:**

```python
def get_spec():
    return {
        "plugin_id": "example",
        "name": "Example Plugin",
        "version": "1.0.0",
        "description": "Пример плагина для демонстрации",
        "category": "Utility",
        "tags": ["example", "demo"],
        "requires_input": False,
        "produces_output": True,
        "params": [
            {
                "key": "message",
                "label": "Message",
                "type": "string",
                "default": "Hello World",
                "help": "Message to print to log",  # ОБЯЗАТЕЛЬНО
                "group": "Main",
                "advanced": False,
                "ui_visibility": "inspector",
                "node_order": 0,
                "node_compact": False
            }
        ]
    }

def run(ctx, params, in_data):
    ctx.log("INFO", f"Plugin executed with message: {params['message']}")
    
    return {
        "status": "OK",
        "code": "SUCCESS",
        "message": "Plugin executed successfully",
        "output": {"result": params['message']}
    }
```

### 3. Требования к README.md

**`plugins/example/README.md`:**

```markdown
# Example Plugin

## Описание
Пример плагина для демонстрации структуры.

## Input/Output
- **Input**: Не требуется
- **Output**: Словарь с ключом `result`

## Параметры

| Key | Label | Default | Help |
|-----|-------|---------|------|
| message | Message | Hello World | Message to print to log |

## Пример использования
Добавьте ноду на граф и запустите выполнение.
```

### 4. Требования к параметрам

**ОБЯЗАТЕЛЬНЫЕ поля ParamSpec:**
- `key` - уникальный идентификатор параметра
- `label` - читаемое название
- `type` - тип виджета (string, int, float, bool, select, text, file)
- `default` - значение по умолчанию
- `help` - **НЕ ПУСТОЙ** текст подсказки

**Опционально:**
- `group` - группа для группировки в инспекторе
- `advanced` - скрывать по умолчанию
- `ui_visibility` - `inspector` (по умолчанию), `node`, `hidden`
- `node_order` - порядок отображения на ноде
- `node_compact` - компактный режим на ноде

### 5. Типы параметров

| Type | Widget | Example |
|------|--------|---------|
| string | Input | "text" |
| int | Input (number) | 42 |
| float | Input (number) | 3.14 |
| bool | Checkbox | true |
| select | Dropdown | ["opt1", "opt2"] |
| text | Textarea | "long text" |
| file | File picker | "path/to/file" |
| password | Password input | "secret" |

### 6. Возвращаемые статусы

| Status | Meaning | Edge |
|--------|---------|------|
| OK | Успешное выполнение | OK edge |
| FAIL | Ошибка бизнес-логики | FAIL edge |
| ERROR | Критическая ошибка | Depends on `error_to_fail` |

### 7. Best Practices

1. **Всегда логируйте** ключевые шаги через `ctx.log`
2. **Валидируйте входные данные** в начале `run()`
3. **Обрабатывайте исключения** внутри `run()`
4. **Документируйте** каждый параметр в README.md
5. **Проверяйте** наличие required input перед использованием
