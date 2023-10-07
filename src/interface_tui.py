import curses
import art
import sys
import json
import uuid
import time
from cassandra.cluster import Cluster
from cassandra import util

# ▶️ - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
FIELDS = ["Título", "Data", "Descrição"]
BUTTONS = ["[ 💾 SALVAR  ]", "[ 🚫 CANCELAR  ]"]

TITLE_SIZE = 30
DATE_SIZE = 10
DESCRIPTION_SIZE = 60


# Criando a conexão
cluster = Cluster(['127.0.0.1'])
session = cluster.connect()

# Criando o keyspace (se não existir)
session.execute("""
    CREATE KEYSPACE IF NOT EXISTS tasks_manager
    WITH REPLICATION = {'class': 'SimpleStrategy', 'replication_factor': 1}
""")

# Usando o keyspace criado
session.set_keyspace('tasks_manager')

# Criando a tabela (se não existir)
session.execute("""
    CREATE TABLE IF NOT EXISTS tasks (
        id UUID PRIMARY KEY,
        title TEXT,
        date TEXT,
        description TEXT,
        done BOOLEAN
    )
""")


class InterfaceTUI:

    # ▶️ - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -

    @staticmethod
    def add_window_title(win, title):
        h, w = win.getmaxyx()
        # start_x = (w - len(title)) // 2
        start_x = 2
        win.addstr(0, start_x, title)

    # ▶️ - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -

    @staticmethod
    def draw_info_window(win):

        win.erase()
        win.keypad(1)
        win.box()
        InterfaceTUI.add_window_title(win, "🔸 --- GERENCIAMENTO DE TAREFAS --- 🔸 ")

        # Gerando e centralizando o texto ASCII Art
        fasoft_art = art.text2art("FASOFT", font='small')
        fasoft_lines = fasoft_art.split('\n')
        for idx, line in enumerate(fasoft_lines):
            start_x = (win.getmaxyx()[1] - len(line)) // 2
            win.addstr(1 + idx, start_x, line)

        # Continuando com as demais informações
        y_offset = len(fasoft_lines) + 1
        win.addstr(y_offset, 1, " FACULDADE DE ENG. DE SOFTWARE")
        win.addstr(y_offset + 2, 1, " 😇 PROFESSOR: Wilian Garcia de Assunção")
        win.addstr(y_offset + 3, 1, " 🤓 ALUNO: Alison Alain de Oliveira")
        win.addstr(y_offset + 5, 1, " 🔸 MATÉRIA: BD NÃO RELACIONAIS")
        win.addstr(y_offset + 6, 1, " 🔑 VERSÃO: 0.01 - CASSANDRA")
        win.refresh()

    # ▶️ - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -

    @staticmethod
    def draw_menu_window(win, menu_items, current_idx):
        win.keypad(1)
        win.clear()
        h, w = win.getmaxyx()

        for idx, item in enumerate(menu_items):
            if idx == current_idx:
                # Completa o item do menu com espaços até a largura da coluna
                padded_item = " 🔸 " + item.ljust(w - 4)  # -2 para levar em conta as bordas
                win.addstr(idx + 2, 1, padded_item, curses.A_CHARTEXT)
            else:
                win.addstr(idx + 2, 1, "    " + item)

        win.box()
        InterfaceTUI.add_window_title(win, "🔸 MENU 🔸")
        win.refresh()

    # ▶️ - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -

    @staticmethod
    def handle_option_Sair(details_win):
        curses.endwin()
        sys.exit()

    # ▶️ - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -

    @staticmethod
    def draw_details_window(win, menu_items, current_idx):
        win.erase()
        win.keypad(1)
        win.box()
        InterfaceTUI.add_window_title(win, "🔸 INFORMAÇÃO SOBRE O MENU 🔸 ")
        win.addstr(2, 6, "Detalhes da opção selecionada:")
        win.addstr(4, 2, menu_items[current_idx])
        win.refresh()

    # ▶️ - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -

    @staticmethod
    def handle_add_task(win, details_win):
        TAB_SPACES = 10
        win.erase()
        win.keypad(1)
        win.box()
        InterfaceTUI.add_window_title(win, "🔸 TELA DE CADASTRO - NOVA TÁREFA 🔸 ")
        curses.cbreak()
        win.keypad(1)
        curses.echo()

        current_field_idx = 0
        field_values = [""] * len(FIELDS)
        is_editing = False

        while True:
            # Atualizado para que cada campo esteja em uma linha separada
            # field_positions = [(i + 1, 1) for i in range(len(FIELDS))]
            field_positions = [(1, 1), (3, 1), (5, 1)]

            for idx, field in enumerate(FIELDS):
                prompt = f"{field.ljust(TAB_SPACES)}:"
                y, x = field_positions[idx]
                if idx == current_field_idx and not is_editing:
                    win.addstr(y + 1, x, " 🔸 " + prompt + field_values[idx].ljust(50), curses.A_BOLD)
                else:
                    win.addstr(y + 1, x, "    " + prompt + field_values[idx].ljust(50))

            # Posição dos botões ajustada de acordo com o número de campos
            button_line = len(FIELDS) + 6

            if current_field_idx == len(FIELDS):  # botão 'Salvar' selecionado
                win.addstr(button_line, 5, "[ 💾 SALVAR  ]", curses.A_REVERSE)
                win.addstr(button_line, 30, "[ 🚫 CANCELAR  ]")
            elif current_field_idx == len(FIELDS) + 1:  # botão 'Cancelar' selecionado
                win.addstr(button_line, 5, "[ 💾 SALVAR  ]")
                win.addstr(button_line, 30, "[ 🚫 CANCELAR  ]", curses.A_REVERSE)
            else:
                win.addstr(button_line, 5, "[ 💾 SALVAR  ]")
                win.addstr(button_line, 30, "[ 🚫 CANCELAR  ]")

            key = win.getch()

            if key == curses.KEY_UP or key == curses.KEY_LEFT:
                is_editing = False
                current_field_idx = (current_field_idx - 1) % (len(FIELDS) + 2)
            elif key == curses.KEY_DOWN or key == curses.KEY_RIGHT:
                is_editing = False
                current_field_idx = (current_field_idx + 1) % (len(FIELDS) + 2)
            elif key == 10:  # Enter
                if current_field_idx < len(FIELDS):
                    if not is_editing:
                        if not is_editing:
                            is_editing = True
                            y, x = field_positions[current_field_idx]
                            # Abaixo, a correção na posição x para levar em conta o tamanho da string prompt.
                            field_values[current_field_idx] = win.getstr(y + 1, x + TAB_SPACES + 6).decode('utf-8').ljust(50)
                            is_editing = False

                elif current_field_idx == len(FIELDS):  # botão 'Salvar'
                    data = dict(zip(FIELDS, field_values))
                    data['Concluído'] = False  # Adicionando o campo 'Concluído' e definindo como False

                    # 📎 ▶️ Cassabdra: O método util.uuid_from_time(time.time()) gera um UUID a partir do tempo atual
                    key = util.uuid_from_time(time.time())
                    session.execute(
                        """
                        INSERT INTO tasks (id, title, date, description, done)
                        VALUES (%s, %s, %s, %s, %s)
                        """,
                        (key, data['Título'], data['Data'], data['Descrição'], False)
                    )

                    InterfaceTUI.draw_details_window(details_win, [" ✅ SUCESSO!"], 0)
                    return True
                elif current_field_idx == len(FIELDS) + 1:  # botão 'Cancelar'
                    InterfaceTUI.draw_details_window(details_win, [" 🚫 CANCELADO!"], 0)
                    return False

    # ▶️ - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -

    @staticmethod
    def list_tasks(win):
        win.erase()
        win.keypad(1)
        win.box()
        InterfaceTUI.add_window_title(win, " 🔸 LISTA DE TAREFAS  🔸 ")

        # 📎 ▶️ Cassandra: O método session.execute() executa uma query no Cassandra
        rows = session.execute('SELECT id, title, date, description, done FROM tasks')
        tasks = [(row.id, {'Título': row.title, 'Data': row.date, 'Descrição': row.description, 'Concluído': row.done}) for row in rows]

        current_idx = 0
        while True:
            win.erase()
            win.box()
            InterfaceTUI.add_window_title(win, " 🔸 LISTA DE TAREFAS  🔸 ")

            for idx, (_, task) in enumerate(tasks):
                status = "[ 🔸 ]" if task["Concluído"] else "[    ]"
                # display_text = f"{status} {task['Título'] + ' - ' + task['Data']+ ' - ' + task['Descrição']}"
                title = task['Título'][:TITLE_SIZE].ljust(TITLE_SIZE)
                date = task['Data'][:DATE_SIZE].ljust(DATE_SIZE)
                description = task['Descrição'][:DESCRIPTION_SIZE].ljust(DESCRIPTION_SIZE)

                display_text = f"{status} {title} | {date} | {description}"
                if idx == current_idx:
                    win.addstr(idx + 2, 3, display_text, curses.A_BOLD)
                else:
                    win.addstr(idx + 2, 3, display_text)

            # Opção para sair da tela
            if len(tasks) == current_idx:
                win.addstr(len(tasks) + 3, 3, "[  SAIR   ]", curses.A_REVERSE)
            else:
                win.addstr(len(tasks) + 3, 3, "[  SAIR   ]")

            key = win.getch()

            if key == curses.KEY_UP and current_idx > 0:
                current_idx -= 1
            elif key == curses.KEY_DOWN and current_idx < len(tasks):
                current_idx += 1
            elif key == 10:  # ENTER
                if current_idx < len(tasks):
                    # Atualizar status de conclusão da tarefa selecionada
                    task_key, task = tasks[current_idx]
                    task["Concluído"] = not task["Concluído"]

                    # 📎 ▶️ Cassandra: O método session.execute() executa uma query no Cassandra
                    try:
                        session.execute(
                            """
                            UPDATE tasks SET done = %s WHERE id = %s
                            """,
                            (task["Concluído"], task_key)
                        )
                    except Exception as e:
                        print(e)
                        time.sleep(5)

                else:
                    # Sair da tela de lista
                    InterfaceTUI.draw_details_window(win, [" ♻️  RETORNANDO..."], 0)
                    return

    # ▶️ - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -

    @staticmethod
    def delete_tasks(win):
        win.erase()
        win.keypad(1)
        win.box()
        InterfaceTUI.add_window_title(win, " 🔸 DELETAR TAREFAS  🔸 ")

        # 📎 ▶️ redis_client: O método redis_client.keys('*') busca a lista de Chaves do Redis
        rows = session.execute('SELECT id, title, date, description, done FROM tasks')
        tasks = [(row.id, {'Título': row.title, 'Data': row.date, 'Descrição': row.description, 'Concluído': row.done}) for row in rows]

        current_idx = 0

        while True:
            win.erase()
            win.box()
            InterfaceTUI.add_window_title(win, " 🔸 DELETAR TAREFAS  🔸 ")

            for idx, (_, task) in enumerate(tasks):
                status = "[ 🔸 ]" if task.get("Concluído", False) else "[    ]"
                display_text = f"{status} {task['Título']}"
                if idx == current_idx:
                    win.addstr(idx + 2, 3, display_text, curses.A_BOLD)
                else:
                    win.addstr(idx + 2, 3, display_text)

            # Adiciona o botão "Voltar" abaixo da lista de tarefas
            if current_idx == len(tasks):
                win.addstr(len(tasks) + 3, 3, "[  VOLTAR   ]", curses.A_REVERSE)
            else:
                win.addstr(len(tasks) + 3, 3, "[  VOLTAR   ]")

            key = win.getch()

            if key == curses.KEY_UP and current_idx > 0:
                current_idx -= 1
            elif key == curses.KEY_DOWN and current_idx < len(tasks):  # Alterado para permitir a seleção do botão "Voltar"
                current_idx += 1
            elif key == 10:  # Enter
                if current_idx == len(tasks):  # Se o botão "Voltar" estiver selecionado
                    InterfaceTUI.draw_details_window(win, ["RETORNANDO..."], 0)
                    return
                else:  # Tela de confirmação para deletar
                    win.erase()
                    win.box()
                    InterfaceTUI.add_window_title(win, " 🔸 CONFIRMAÇÃO  🔸 ")
                    message = f"Tem certeza de que deseja deletar '{tasks[current_idx][1]['Título']}'?"
                    win.addstr(win.getmaxyx()[0] // 2, (win.getmaxyx()[1] - len(message)) // 2, message)

                    choices = ["[ SIM ]", "[ NÃO ]"]
                    choice_idx = 0

                    while True:
                        for idx, choice in enumerate(choices):
                            if idx == choice_idx:
                                win.addstr(win.getmaxyx()[0] // 2 + 1 + idx, win.getmaxyx()[1] // 2 - 4, choice, curses.A_REVERSE)
                            else:
                                win.addstr(win.getmaxyx()[0] // 2 + 1 + idx, win.getmaxyx()[1] // 2 - 4, choice)

                        confirm_key = win.getch()

                        if confirm_key == curses.KEY_UP and choice_idx > 0:
                            choice_idx -= 1
                        elif confirm_key == curses.KEY_DOWN and choice_idx < len(choices) - 1:
                            choice_idx += 1
                        elif confirm_key == 10:  # Enter
                            if choice_idx == 0:  # SIM
                                task_key, task = tasks[current_idx]
                                # 📎 ▶️ Cassandra: O método session.execute() executa uma query no Cassandra
                                session.execute(
                                    """
                                    DELETE FROM tasks WHERE id = %s
                                    """,
                                    (task_key,)
                                )

                                tasks.pop(current_idx)
                                if current_idx >= len(tasks):
                                    current_idx = len(tasks) - 1
                            break

            win.refresh()
