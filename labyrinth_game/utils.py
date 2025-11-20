import math

from labyrinth_game.constants import (
    COMMANDS,
    EVENT_CHANCE_MODULO,
    PUZZLE_ALIASES,
    RANDOM_EVENT_TYPES,
    ROOMS,
    TRAP_DAMAGE_MODULO,
    TRAP_DEATH_THRESHOLD,
)


def describe_current_room(game_state: dict) -> None:
    """Вывести описание текущей комнаты, предметы, выходы и наличие загадки."""
    room_id = game_state["current_room"]
    room = ROOMS[room_id]

    print(f"\n== {room_id.upper()} ==")
    print(room["description"])

    items = room.get("items", [])
    if items:
        print("Заметные предметы:", ", ".join(items))

    exits = room.get("exits", {})
    if exits:
        print("Выходы:", ", ".join(exits.keys()))

    if room.get("puzzle") is not None:
        print('Кажется, здесь есть загадка (используйте команду "solve").')


def show_help(commands: dict | None = None) -> None:
    """Вывести список доступных команд."""
    if commands is None:
        commands = COMMANDS

    print("\nДоступные команды:")
    for cmd, desc in commands.items():
        # 16 символов под команду, затем описание
        print(f"  {cmd:<16} - {desc}")


def pseudo_random(seed: int, modulo: int) -> int:
    """Простая детерминированная псевдослучайная функция в диапазоне [0, modulo)."""
    if modulo <= 0:
        raise ValueError("modulo должен быть положительным целым числом")

    x = math.sin(seed * 12.9898) * 43758.5453
    fractional = x - math.floor(x)
    return int(fractional * modulo)


def trigger_trap(game_state: dict) -> None:
    """Срабатывание ловушки: потеря предмета или шанс смерти."""
    print("\nЛовушка активирована! Пол под ногами начинает дрожать...")

    inventory = game_state["player_inventory"]
    if inventory:
        index = pseudo_random(game_state["steps_taken"], len(inventory))
        lost_item = inventory.pop(index)
        print(f"Вы теряете предмет: {lost_item}.")
        return

    # Инвентарь пуст — шанс погибнуть
    roll = pseudo_random(game_state["steps_taken"], TRAP_DAMAGE_MODULO)
    if roll < TRAP_DEATH_THRESHOLD:
        print("Плита уходит из-под ног, вы падаете в пропасть. Игра окончена.")
        game_state["game_over"] = True
    else:
        print("Вы чудом удержались на краю и выбираетесь обратно.")


def random_event(game_state: dict) -> None:
    """Мелкие случайные события, происходящие при перемещении."""
    seed = game_state["steps_taken"]
    if pseudo_random(seed, EVENT_CHANCE_MODULO) != 0:
        return

    event_type = pseudo_random(seed + 1, RANDOM_EVENT_TYPES)
    room_id = game_state["current_room"]
    room = ROOMS[room_id]
    inventory = game_state["player_inventory"]

    if event_type == 0:
        print("\nВы замечаете на полу монетку.")
        room.setdefault("items", []).append("coin")
    elif event_type == 1:
        print("\nГде-то в темноте слышен подозрительный шорох.")
        if "sword" in inventory:
            print("Вы сжимаете меч, и существо отступает во тьму.")
    else:
        if room_id == "trap_room" and "torch" not in inventory:
            print("\nСлышен щелчок механизма — что-то явно не так...")
            trigger_trap(game_state)


def _is_answer_correct(user_answer: str, correct: str) -> bool:
    """Проверка ответа с учётом дополнительных вариантов."""
    normalized = user_answer.strip().lower()
    correct_norm = str(correct).strip().lower()
    candidates = {correct_norm}

    aliases = PUZZLE_ALIASES.get(correct_norm, [])
    candidates.update(alias.lower() for alias in aliases)

    return normalized in candidates


def solve_puzzle(game_state: dict) -> None:
    """Решение загадки в текущей комнате."""
    from labyrinth_game.player_actions import get_input  # отложенный импорт

    room_id = game_state["current_room"]
    room = ROOMS[room_id]
    puzzle = room.get("puzzle")

    if puzzle is None:
        print("Загадок здесь нет.")
        return

    question, correct_answer = puzzle
    print(question)
    answer = get_input("Ваш ответ: ")

    if _is_answer_correct(answer, correct_answer):
        print("Верно! Загадка решена.")
        room["puzzle"] = None  # больше нельзя решать

        inventory = game_state["player_inventory"]
        # Награда зависит от комнаты
        if room_id == "hall":
            if "treasure_key" not in inventory:
                inventory.append("treasure_key")
                print("Вы чувствуете, как в руке появляется ключ от сокровищ.")
        elif room_id == "library":
            print("Свитки шепчут вам забытые знания, но материальной награды нет.")
        elif room_id == "trap_room":
            # В ловушечной комнате удачное решение — уже награда
            print("Механизм ловушки останавливается, можно спокойно идти дальше.")
        else:
            print("Но в этот раз никакой явной награды не видно.")
    else:
        print("Неверно. Попробуйте снова.")
        if room_id == "trap_room":
            # В комнате-ловушке ошибка активирует ловушку
            trigger_trap(game_state)


def attempt_open_treasure(game_state: dict) -> None:
    """Попытаться открыть сундук с сокровищем в treasure_room."""
    from labyrinth_game.player_actions import get_input  # отложенный импорт

    room_id = game_state["current_room"]
    if room_id != "treasure_room":
        print("Здесь нет сундука с сокровищами.")
        return

    room = ROOMS[room_id]
    inventory = game_state["player_inventory"]

    if "treasure_key" in inventory:
        print("Вы применяете ключ, и замок щёлкает. Сундук открыт!")
        if "treasure_chest" in room["items"]:
            room["items"].remove("treasure_chest")
        print("В сундуке сокровище! Вы победили!")
        game_state["game_over"] = True
        return

    print(
        "Сундук заперт. Кажется, его можно открыть специальным кодом. "
        "Ввести код? (да/нет)"
    )
    choice = get_input("> ").strip().lower()
    if choice not in {"да", "yes", "y"}:
        print("Вы отступаете от сундука.")
        return

    puzzle = room.get("puzzle")
    if puzzle is None:
        print("Кода здесь нет, механизмы заржавели.")
        return

    question, correct_answer = puzzle
    print(question)
    code = get_input("Код: ")

    if _is_answer_correct(code, correct_answer):
        print("Код верный. Замок отпирается, крышка поддаётся.")
        if "treasure_chest" in room["items"]:
            room["items"].remove("treasure_chest")
        print("В сундуке сокровище! Вы победили!")
        game_state["game_over"] = True
    else:
        print("Код неверный. Сундук остаётся заперт.")
