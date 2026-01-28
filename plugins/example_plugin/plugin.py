"""Example Plugin for Visual Block Runtime."""


def get_spec():
    """Возвращает спецификацию плагина."""
    return {
        "plugin_id": "example_plugin",
        "name": "Example Plugin",
        "version": "1.0.0",
        "description": "Пример плагина для демонстрации структуры плагинов.",
        "category": "Utility",
        "tags": ["example", "demo", "test"],
        "requires_input": False,
        "produces_output": True,
        "params": [
            {
                "key": "message",
                "label": "Message",
                "type": "string",
                "default": "Hello World",
                "help": "Message that will be logged and returned as output.",
                "group": "Main",
                "advanced": False,
                "ui_visibility": "inspector",
                "node_order": 0,
                "node_compact": False,
            },
            {
                "key": "count",
                "label": "Count",
                "type": "int",
                "default": 1,
                "help": "Number of times to repeat the message.",
                "group": "Main",
                "advanced": False,
                "ui_visibility": "inspector",
                "node_order": 1,
                "node_compact": False,
            },
            {
                "key": "fail_simulation",
                "label": "Simulate Failure",
                "type": "bool",
                "default": False,
                "help": "If true, the plugin will return FAIL status.",
                "group": "Debug",
                "advanced": True,
                "ui_visibility": "inspector",
                "node_order": 2,
                "node_compact": False,
            },
        ]
    }


def run(ctx, params, in_data):
    """
    Выполняет логику плагина.
    
    Args:
        ctx: Контекст выполнения (логгер, run_id, node_uid)
        params: Словарь параметров
        in_data: Данные из input переменной (или None)
    
    Returns:
        dict: Результат выполнения
    """
    message = params.get("message", "Hello World")
    count = params.get("count", 1)
    should_fail = params.get("fail_simulation", False)
    
    ctx.log("INFO", f"Example plugin started with message='{message}', count={count}")
    
    if should_fail:
        ctx.log("WARN", "Simulating failure as requested")
        return {
            "status": "FAIL",
            "code": "SIMULATED_FAILURE",
            "message": "Failure was simulated by user setting",
            "details": {"message": message, "count": count},
            "output": None
        }
    
    # Формируем вывод
    result_message = " ".join([message] * count)
    
    ctx.log("INFO", f"Example plugin finished successfully")
    
    return {
        "status": "OK",
        "code": "SUCCESS",
        "message": f"Plugin executed: '{result_message}'",
        "details": {"message": message, "count": count},
        "output": {"result": result_message, "original_message": message}
    }
