from labyrinth_game import utils
from labyrinth_game.constants import ROOMS


def show_inventory(game_state: dict) -> None:
    """Показать содержимое инвентаря."""
    items = game_state["player_inventory"]
    if not items:
        print("Ваш инвентарь пуст.")
    else:
        print("Инвентарь:", ", ".join(items))


def get_input(prompt: str = "> ") -> str:
    """Безопасное чтение ввода пользователя."""
    try:
        return input(prompt).strip()
    except (KeyboardInterrupt, EOFError):
        print("\nВыход из игры.")
        return "quit"


def move_player(game_state: dict, direction: str) -> None:
    """Перемещение игрока в указанном направлении."""
    direction = direction.lower()
    room_id = game_state["current_room"]
    room = ROOMS[room_id]
    exits = room.get("exits", {})

    if direction not in exits:
        print("Нельзя пойти в этом направлении.")
        return

    new_room_id = exits[direction]
    inventory = game_state["player_inventory"]

    # Дополнительная проверка прохода в treasure_room
    if new_room_id == "treasure_room" and "rusty_key" not in inventory:
        print("Дверь заперта. Нужен старый ключ, чтобы пройти дальше.")
        return

    if new_room_id == "treasure_room" and "rusty_key" in inventory:
        print("Вы используете найденный ключ, чтобы открыть путь в комнату сокровищ.")

    game_state["current_room"] = new_room_id
    game_state["steps_taken"] += 1

    utils.describe_current_room(game_state)
    utils.random_event(game_state)


def take_item(game_state: dict, item_name: str) -> None:
    """Взять предмет из текущей комнаты."""
    item_name = item_name.strip()
    if not item_name:
        print("Что именно вы хотите взять?")
        return

    if item_name == "treasure_chest":
        print("Вы не можете поднять сундук, он слишком тяжёлый.")
        return

    room_id = game_state["current_room"]
    room = ROOMS[room_id]
    items = room.get("items", [])

    if item_name in items:
        items.remove(item_name)
        game_state["player_inventory"].append(item_name)
        print(f"Вы подняли: {item_name}")
    else:
        print("Такого предмета здесь нет.")


def use_item(game_state: dict, item_name: str) -> None:
    """Использовать предмет из инвентаря."""
    item_name = item_name.strip()
    inventory = game_state["player_inventory"]

    if item_name not in inventory:
        print("У вас нет такого предмета.")
        return

    if item_name == "torch":
        print("Вы зажигаете факел. Вокруг становится заметно светлее.")
    elif item_name == "sword":
        print("Вы крепче сжимаете меч и чувствуете себя увереннее.")
    elif item_name == "bronze_box":
        if "rusty_key" not in inventory:
            print("Вы открываете бронзовую шкатулку и находите старый ключ.")
            inventory.append("rusty_key")
        else:
            print("Шкатулка пуста.")
    else:
        print("Вы не знаете, как использовать этот предмет.")
