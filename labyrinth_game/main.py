#!/usr/bin/env python3

from labyrinth_game import player_actions, utils
from labyrinth_game.constants import COMMANDS


def process_command(game_state: dict, command_line: str) -> None:
    """Разбор и выполнение команды пользователя."""
    if not command_line:
        return

    raw = command_line.strip()
    cmd_parts = raw.split()
    command = cmd_parts[0].lower()
    args = cmd_parts[1:]

    # короткие направления без "go"
    directions = {"north", "south", "east", "west", "n", "s", "e", "w"}

    if command in {"quit", "exit"}:
        game_state["game_over"] = True
        print("Выход из игры.")
        return

    if command == "help":
        utils.show_help(COMMANDS)
        return

    if command == "look":
        utils.describe_current_room(game_state)
        return

    if command == "inventory":
        player_actions.show_inventory(game_state)
        return

    if command == "go":
        if not args:
            print("Укажите направление: north/south/east/west.")
            return
        direction = args[0].lower()
        player_actions.move_player(game_state, direction)
        return

    if command in directions:
        # n/s/e/w приводим к полным названиям
        mapping = {"n": "north", "s": "south", "e": "east", "w": "west"}
        direction = mapping.get(command, command)
        player_actions.move_player(game_state, direction)
        return

    if command == "take":
        if not args:
            print("Укажите предмет, который хотите взять.")
            return
        item_name = " ".join(args)
        player_actions.take_item(game_state, item_name)
        return

    if command == "use":
        if not args:
            print("Укажите предмет, который хотите использовать.")
            return
        item_name = " ".join(args)
        player_actions.use_item(game_state, item_name)
        return

    if command == "solve":
        # В сокровищнице solve означает попытку открыть сундук
        if game_state["current_room"] == "treasure_room":
            utils.attempt_open_treasure(game_state)
        else:
            utils.solve_puzzle(game_state)
        return

    print('Неизвестная команда. Введите "help" для списка команд.')


def main() -> None:
    """Точка входа в игру."""
    print("Добро пожаловать в Лабиринт сокровищ!")

    game_state = {
        "player_inventory": [],
        "current_room": "entrance",
        "game_over": False,
        "steps_taken": 0,
    }

    # стартовое описание комнаты
    utils.describe_current_room(game_state)

    while not game_state["game_over"]:
        command_line = player_actions.get_input("> ")
        # на случай Ctrl+C/EOF в get_input вернётся "quit"
        if command_line.strip().lower() in {"quit", "exit"}:
            game_state["game_over"] = True
            print("Выход из игры.")
            break

        process_command(game_state, command_line)


if __name__ == "__main__":
    main()
