import curses
import sys
from interface_tui import InterfaceTUI
import art


def handle_option_Sair(details_win):
    curses.endwin()
    sys.exit()


def main(screen):
    screen.keypad(True)
    curses.cbreak()
    curses.echo()
    curses.curs_set(0)  # Ocultar cursor
    curses.start_color()
    curses.init_color(8, 100, 100, 100)
    # curses.init_pair(1, 8, 8)
    curses.init_pair(1, curses.COLOR_WHITE, 8)

    # ▶️ - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -

    h, w = screen.getmaxyx()
    fasoft_art = art.text2art("FASOFT")
    fasoft_lines = fasoft_art.split('\n')
    info_win_height = len(fasoft_lines) + 6 + 2 + 2  # 6 para as demais linhas, 2 para as bordas superior e inferior
    menu_win_height = h - info_win_height
    info_win = curses.newwin(info_win_height, int(w * 0.3), 0, 0)
    menu_win = curses.newwin(menu_win_height, int(w * 0.3), info_win_height, 0)
    details_win = curses.newwin(h, int(w * 0.7 + 1), 0, int(w * 0.3))
    info_win.bkgd(' ', curses.color_pair(1))
    menu_win.bkgd(' ', curses.color_pair(1))
    details_win.bkgd(' ', curses.color_pair(1))
    screen.attron(curses.color_pair(1))
    screen.erase()
    screen.refresh()
    info_win.refresh()
    menu_win.refresh()
    details_win.refresh()

    # ▶️ - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -

    InterfaceTUI.draw_info_window(info_win)
    InterfaceTUI.draw_details_window(details_win, ["    LISTA DE TAREFAS", "ADICIONAR TAREFAS", "APAGAR TAREFAS", "SAIR"], 0)

    menu_items = ["LISTA DE TAREFAS", "ADICIONAR TAREFAS", "APAGAR TAREFAS", "SAIR"]

    menu_preview_actions = {
        "LISTA DE TAREFAS": lambda win: InterfaceTUI.draw_details_window(details_win, ["    Preview de LISTA DE TAREFAS"], 0),
        "ADICIONAR TAREFAS": lambda win: InterfaceTUI.draw_details_window(details_win, ["    Preview de ADICIONAR TAREFAS"], 0),
        "APAGAR TAREFAS": lambda win: InterfaceTUI.draw_details_window(details_win, ["    Preview de APAGAR TAREFAS"], 0),
        "SAIR": lambda win: InterfaceTUI.draw_details_window(details_win, ["    Preview de SAIR"], 0)
    }

    menu_select_actions = {
        "LISTA DE TAREFAS": InterfaceTUI.list_tasks,
        "ADICIONAR TAREFAS": lambda win: InterfaceTUI.handle_add_task(win, details_win),
        "APAGAR TAREFAS": InterfaceTUI.delete_tasks,
        "SAIR": handle_option_Sair
    }

    current_idx = 0

    while True:
        InterfaceTUI.draw_info_window(info_win)
        InterfaceTUI.draw_menu_window(menu_win, menu_items, current_idx)

        key = screen.getch()

        if key == curses.KEY_UP and current_idx > 0:
            current_idx -= 1
            preview_action = menu_preview_actions[menu_items[current_idx]]
            preview_action(details_win)
        elif key == curses.KEY_DOWN and current_idx < len(menu_items) - 1:
            current_idx += 1
            preview_action = menu_preview_actions[menu_items[current_idx]]
            preview_action(details_win)
        elif key == ord('q'):
            break

        if key == 10:  # Se a tecla ENTER for pressionada
            select_action = menu_select_actions[menu_items[current_idx]]
            select_action(details_win)

        # Atualização do display
        curses.doupdate()


curses.wrapper(main)
