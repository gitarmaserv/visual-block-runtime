# Example Plugin

## Описание
Пример плагина для демонстрации структуры плагинов в Visual Block Runtime. Этот плагин принимает сообщение и количество повторений, формирует результат и возвращает его.

## Input/Output
- **Input**: Не требуется (`requires_input: false`)
- **Output**: Словарь с ключами `result` и `original_message`

## Параметры

| Key | Label | Type | Default | Help | Advanced |
|-----|-------|------|---------|------|----------|
| message | Message | string | Hello World | Message that will be logged and returned as output. | No |
| count | Count | int | 1 | Number of times to repeat the message. | No |
| fail_simulation | Simulate Failure | bool | false | If true, the plugin will return FAIL status. | Yes |

## Возвращаемые статусы

| Status | Code | Meaning |
|--------|------|---------|
| OK | SUCCESS | Успешное выполнение |
| FAIL | SIMULATED_FAILURE | Симуляция ошибки (когда `fail_simulation: true`) |

## Пример использования

1. Добавьте ноду `Example Plugin` на граф из категории "Utility"
2. В инспекторе ноды задайте параметры:
   - Message: "Hello"
   - Count: 3
3. Соедините ноды с помощью ребер (OK/Fail)
4. Запустите выполнение

## Логирование

Плагин пишет следующие события в лог:
- INFO: Начало выполнения с параметрами
- INFO: Успешное завершение
- WARN: Если запрошена симуляция ошибки
