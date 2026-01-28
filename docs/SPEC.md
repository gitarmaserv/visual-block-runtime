# SPEC.md - Контракты и спецификации

## 1. Контракт Plugin Spec

Каждый плагин должен экспортировать объект с методами:

```python
def get_spec() -> dict:
    """
    Возвращает спецификацию плагина.
    """
    return {
        "plugin_id": "unique_id",
        "name": "Human readable name",
        "version": "1.0.0",
        "description": "What this plugin does",
        "category": "Category name",  # ОБЯЗАТЕЛЬНО
        "tags": ["tag1", "tag2"],
        "requires_input": False,
        "produces_output": False,
        "params": [
            {
                "key": "param_key",
                "label": "Parameter Label",
                "type": "string",  # string, int, float, bool, select, text, file, etc.
                "default": "default_value",
                "help": "Help text for tooltip",  # ОБЯЗАТЕЛЬНО
                "group": "Group name",
                "advanced": False,
                "ui_visibility": "inspector",  # inspector, node, hidden
                "node_order": 0,
                "node_compact": False,
            }
        ]
    }

def run(ctx, params: dict, in_data: any) -> dict:
    """
    Выполняет логику плагина.
    
    Args:
        ctx: Контекст выполнения (логгер, run_id, node_uid)
        params: Словарь параметров из ParamSpec
        in_data: Данные из input переменной (или None)
    
    Returns:
        dict: Результат выполнения
    """
    return {
        "status": "OK",  # OK, FAIL, ERROR
        "code": "SUCCESS",  # Код результата (обязателен для FAIL/ERROR)
        "message": "Human readable message",
        "details": {"key": "value"},  # Опционально
        "output": None  # Любой формат, если produces_output=True
    }
```

## 2. Контракт Edge Branch

Каждый Edge в графе обязан иметь поле:

```javascript
{
  id: "e1-2",
  source: "node1",
  target: "node2",
  data: {
    branch: "ok" | "fail"  // ОБЯЗАТЕЛЬНО
  }
}
```

**Ограничения:**
- Максимум 1 OK-edge на ноду
- Максимум 1 FAIL-edge на ноду

## 3. Контракт переменных

### Ref формат
- Project: `proj:<var_id>`
- Global: `glob:<var_id>`

### Структура
```python
# Определение переменной
{
    "var_id": 1,
    "base_name": "my_data",
    "title": "1Value_my_data",  # Системный формат
    "description": "Description"
}

# Значение (хранится отдельно)
{
    "var_id": 1,
    "value_json": '{"key": "value"}',
    "updated_at": "2026-01-01 00:00:00"
}
```

## 4. Контракт логов (log.txt)

**Формат строки:**
```
YYYY-MM-DD HH:MM:SS.mmm | run=<run_id> | node=<node_uid> | title="<node_title>" | lvl=<LEVEL> | msg=<message>
```

**Пример:**
```
2026-01-28 12:00:00.123 | run=run_001 | node=node_1 | title="Start" | lvl=INFO | msg="Execution started"
```

**Уровни:** INFO, DEBUG, WARN, ERROR

**Правила:**
- msg всегда однострочный (экранировать \n как \\n)
- node_uid и node_title всегда присутствуют

## 5. Контракт Runtime Context (ctx)

```python
class RuntimeContext:
    def __init__(self, run_id: str, node_uid: str, node_title: str):
        self.run_id = run_id
        self.node_uid = node_uid
        self.node_title = node_title
    
    def log(self, level: str, message: str, details: dict = None):
        """Записать в лог."""
        pass
    
    @property
    def project_dir(self) -> str:
        """Директория проекта."""
        pass
    
    @property
    def artifacts_dir(self) -> str:
        """Директория для артефактов."""
        pass
```

## 6. Контракт узла графа (React Flow Node)

```javascript
{
  id: "node_1",
  type: "custom-node",
  position: { x: 100, y: 200 },
  data: {
    plugin_id: "example_plugin",
    node_title: "My Node",
    breakpoint: false,
    error_to_fail: false,
    input_var_ref: "proj:1",  // или null
    output_var_ref: "proj:2", // или null
    params: {
      param_key: "value"
    },
    visual: {
      // Настраиваемые визуальные параметры
      color: "#ff0000",
      compact: false
    }
  }
}
```

## 7. Статусы выполнения узла

- `Idle` - не выполнялся
- `Running` - выполняется
- `OK` - успешно завершен
- `FAIL` - завершен с ошибкой (ветка FAIL)
- `ERROR` - критическая ошибка
- `Paused` - остановлен на breakpoint
- `InvalidConfig` - неверная конфигурация
