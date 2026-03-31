# -*- coding: utf-8 -*-
"""Remove fuzzy flags and set correct en/it msgstr for known mismatched entries."""
from __future__ import annotations

import polib

# msgid -> (en_msgstr, it_msgstr)
FIXES: dict[str, tuple[str, str]] = {
    "## Решение": ("## Solution", "## Soluzione"),
    "### Запуск": ("### Run", "### Avvio"),
    "## Синтаксис": ("## Syntax", "## Sintassi"),
    "### Сохранение": ("### Saving", "### Salvataggio"),
    "### Срез с шагом": ("### Slice with step", "### Fetta con passo"),
    "## Скачивание Python": ("## Downloading Python", "## Download di Python"),
    "### Как создать файл": ("### How to create a file", "### Come creare un file"),
    "### Что такое .venv?": ("### What is .venv?", "### Cos'è .venv?"),
    "**Пример правильно:**": ("**Correct example:**", "**Esempio corretto:**"),
    "## Установка (Windows)": ("## Installation (Windows)", "## Installazione (Windows)"),
    "### Что такое синтаксис?": ("### What is syntax?", "### Cos'è la sintassi?"),
    "### Что такое .gitignore?": ("### What is .gitignore?", "### Cos'è .gitignore?"),
    "### Динамическая типизация": ("### Dynamic typing", "### Tipizzazione dinamica"),
    "## Первый запуск (терминал)": ("## First run (terminal)", "## Primo avvio (terminale)"),
    "Напиши в файле одну строку:": (
        "Write one line in the file:",
        "Scrivi nel file una sola riga:",
    ),
    "2. Создай переменную `total = 0`.": (
        "2. Create a variable `total = 0`.",
        "2. Crea la variabile `total = 0`.",
    ),
    "## print() — как увидеть результат": (
        "## print() — seeing the result",
        "## print() — come vedere il risultato",
    ),
    "## Что такое IDE и зачем она нужна": (
        "## What is an IDE and why you need one",
        "## Cos'è un IDE e a cosa serve",
    ),
    "## Создание файла и первая программа": (
        "## Creating a file and a first program",
        "## Creazione del file e primo programma",
    ),
    "## Виртуальное окружение (.venv) и .gitignore": (
        "## Virtual environment (.venv) and .gitignore",
        "## Ambiente virtuale (.venv) e .gitignore",
    ),
    "3. Проверь отступы у `print` — должны ли они быть?": (
        "3. Check the indentation of `print` — should it be indented?",
        "3. Controlla l'indentazione di `print` — deve esserci?",
    ),
    "1. Создай словарь `menu` с парами «название — цена».": (
        "1. Create a `menu` dictionary with «name — price» pairs.",
        "1. Crea il dizionario `menu` con coppie «nome — prezzo».",
    ),
    "2. Посмотри на синтаксис `if` — чего не хватает после условия?": (
        "2. Look at the `if` syntax — what's missing after the condition?",
        "2. Guarda la sintassi di `if` — cosa manca dopo la condizione?",
    ),
    "2. Проверь отступы: какие строки должны выполняться внутри цикла?": (
        "2. Check indentation: which lines should run inside the loop?",
        "2. Controlla l'indentazione: quali righe devono essere dentro il ciclo?",
    ),
    "Строки `print` — внутри блока `if`, поэтому обе сдвинуты на 4 пробела.": (
        "The `print` lines are inside the `if` block, so both are indented by 4 spaces.",
        "Le righe `print` sono dentro il blocco `if`, quindi entrambe sono indentate di 4 spazi.",
    ),
    (
        "Ошибка 1: двоеточие после `for i in numbers:` и после `for num in numbers:`."
    ): (
        "Error 1: colon after `for i in numbers:` and after `for num in numbers:`.",
        "Errore 1: due punti dopo `for i in numbers:` e dopo `for num in numbers:`.",
    ),
    (
        "Ошибка 2: отступ у `print(i * 2)` и у `total = total + num` — они внутри "
        "цикла."
    ): (
        "Error 2: indentation of `print(i * 2)` and of `total = total + num` — "
        "they are inside the loop.",
        "Errore 2: indentazione di `print(i * 2)` e di `total = total + num` — "
        "sono dentro il ciclo.",
    ),
    (
        "1. `input()` всегда возвращает строку. Можно ли сравнивать строку с числом "
        "18? Что нужно сделать?"
    ): (
        "1. `input()` always returns a string. Can you compare a string with the "
        "number 18? What do you need to do?",
        "1. `input()` restituisce sempre una stringa. Si può confrontare una stringa "
        "con il numero 18? Cosa serve fare?",
    ),
    (
        "Создай словарь с тремя парами: день недели — план (например, «Понедельник»: "
        "«учёба»). Выведи план на один из дней. Добавь четвёртую пару и выведи её."
    ): (
        "Create a dictionary with three pairs: weekday — plan (e.g. «Monday»: "
        "«study»). Print the plan for one day. Add a fourth pair and print it.",
        "Crea un dizionario con tre coppie: giorno della settimana — piano (es. "
        "«Lunedì»: «studio»). Stampa il piano per un giorno. Aggiungi una quarta "
        "coppia e stampala.",
    ),
    (
        "Цикл `while` выполняется, пока условие истинно. Важно менять переменную "
        "внутри цикла, иначе условие никогда не станет ложным и цикл будет "
        "бесконечным."
    ): (
        "The `while` loop runs while the condition is true. You must change the "
        "variable inside the loop; otherwise the condition never becomes false and "
        "the loop is infinite.",
        "Il ciclo `while` viene eseguito finché la condizione è vera. È importante "
        "cambiare la variabile nel ciclo, altrimenti la condizione non diventa mai "
        "falsa e il ciclo è infinito.",
    ),
    (
        "`for` — когда заранее известно, по чему идём (список, диапазон). `while` — "
        "когда повторять нужно до какого-то события (например, пока пользователь не "
        "введёт «выход»)."
    ): (
        "`for` — when you know in advance what you iterate over (list, range). "
        "`while` — when you need to repeat until something happens (e.g. until the "
        "user enters «exit»).",
        "`for` — quando sai in anticipo su cosa iterare (lista, range). `while` — "
        "quando serve ripetere fino a un evento (es. finché l'utente non inserisce "
        "«esci»).",
    ),
    (
        "Создай три переменные: своё имя, возраст и любимый город. Выведи их по "
        "очереди через `print()`. Попробуй также сложить два числа (например, 10 и "
        "20) и вывести результат."
    ): (
        "Create three variables: your name, age, and favorite city. Print them one "
        "by one with `print()`. Also try adding two numbers (e.g. 10 and 20) and "
        "print the result.",
        "Crea tre variabili: il tuo nome, età e città preferita. Stampale in "
        "sequenza con `print()`. Prova anche a sommare due numeri (es. 10 e 20) e "
        "stampa il risultato.",
    ),
    (
        "Создай файл `hello.py`, выведи своё имя и город. Запусти программу и "
        "убедись, что всё работает. Если используешь IDE — попробуй запустить "
        "программу кнопкой Run или через меню."
    ): (
        "Create `hello.py`, print your name and city. Run the program and verify it "
        "works. If you use an IDE — try Run or the menu.",
        "Crea il file `hello.py`, stampa nome e città. Esegui il programma e "
        "verifica che funzioni. Se usi un IDE — prova Esegui o dal menu.",
    ),
    (
        "Создай список из нескольких чисел (например, 3–5 штук). Выведи их с "
        "нумерацией через `enumerate` (1. ..., 2. ..., 3. ...). Или посчитай сумму "
        "всех чисел в цикле и выведи результат."
    ): (
        "Create a list of several numbers (e.g. 3–5). Print them with numbering "
        "via `enumerate` (1. ..., 2. ..., 3. ...). Or sum all numbers in a loop "
        "and print the result.",
        "Crea una lista di numeri (es. 3–5). Stampali con numerazione tramite "
        "`enumerate` (1. ..., 2. ..., 3. ...). Oppure somma tutti i numeri in un "
        "ciclo e stampa il risultato.",
    ),
    (
        "Сохрани файл (Ctrl+S). В терминале перейди в папку с файлом: `cd "
        "путь_к_папке`. Выполни: `python hello.py` (или `python3 hello.py` на "
        "Mac/Linux). Поздравляю — твоя первая программа работает."
    ): (
        "Save the file (Ctrl+S). In the terminal go to the folder with the file: "
        "`cd path_to_folder`. Run: `python hello.py` (or `python3 hello.py` on "
        "Mac/Linux). Congrats — your first program works.",
        "Salva il file (Ctrl+S). Nel terminale vai alla cartella del file: "
        "`cd percorso_cartella`. Esegui: `python hello.py` (o `python3 hello.py` su "
        "Mac/Linux). Congratulazioni — il tuo primo programma funziona.",
    ),
    (
        "Собери в одну программу всё изученное: словари, циклы, условия, input и "
        "print. Мини-проект: калькулятор счёта для кафе. Меню: капучино 2.50 €, "
        "корнетто 1.50 €, сок 2.00 €. Скидка 10% для заказов от 10 евро."
    ): (
        "Put everything you've learned into one program: dictionaries, loops, "
        "conditions, input and print. Mini-project: cafe bill calculator. Menu: "
        "cappuccino 2.50 €, cornetto 1.50 €, juice 2.00 €. 10% discount for orders "
        "from 10 euros.",
        "Metti in un solo programma tutto ciò che hai imparato: dizionari, cicli, "
        "condizioni, input e print. Mini-progetto: calcolatore del conto per un "
        "bar. Menu: cappuccino 2,50 €, cornetto 1,50 €, succo 2,00 €. Sconto 10% "
        "per ordini da 10 euro.",
    ),
    (
        "Открой терминал: в Windows — «Командная строка» или PowerShell, в Mac/Linux "
        "— Terminal. Введи `python` или `python3`. Увидишь приглашение `>>>` — "
        "значит, Python готов к работе. Можно вводить команды прямо в терминале. "
        "Чтобы выйти, напиши `exit()`."
    ): (
        "Open the terminal: on Windows — Command Prompt or PowerShell, on Mac/Linux "
        "— Terminal. Enter `python` or `python3`. You'll see `>>>` — Python is "
        "ready. You can type commands in the terminal. To exit, type `exit()`.",
        "Apri il terminale: su Windows — Prompt dei comandi o PowerShell, su "
        "Mac/Linux — Terminale. Digita `python` o `python3`. Vedrai `>>>` — Python "
        "è pronto. Puoi digitare comandi nel terminale. Per uscire, scrivi "
        "`exit()`.",
    ),
    "Скачать сертификат": ("Download certificate", "Scarica certificato"),
    "Регистрация →": ("Sign up →", "Registrazione →"),
}


def fix_po(path: str, lang: str) -> int:
    po = polib.pofile(path)
    key = "en" if lang == "en" else "it"
    n = 0
    for entry in po:
        if not entry.fuzzy:
            continue
        if entry.msgid not in FIXES:
            continue
        new_str = FIXES[entry.msgid][0 if key == "en" else 1]
        entry.msgstr = new_str
        entry.fuzzy = False
        entry.previous_msgid = None
        entry.previous_msgid_plural = None
        entry.previous_msgctxt = None
        n += 1
    po.save(path)
    return n


def main() -> None:
    root = __import__("pathlib").Path(__file__).resolve().parent.parent
    en = fix_po(str(root / "locale" / "en" / "LC_MESSAGES" / "django.po"), "en")
    it = fix_po(str(root / "locale" / "it" / "LC_MESSAGES" / "django.po"), "it")
    print(f"Fixed {en} fuzzy entries (en), {it} fuzzy entries (it)")


if __name__ == "__main__":
    main()
