# Baba Make Parabox

![Game icon](BabaMakeParabox.png)

**Baba Make Parabox** is a fan-made sokoban-like metagame by **Yangsy56302**.
The original games are [**Baba Is You**](https://hempuli.com/baba/) and [**Patrick's Parabox**](https://www.patricksparabox.com/),
made separately by **Arvi Hempuli** and **Patrick Traynor**.

## How to run

Note: batch files in `python` folder only works when python files exists,
and batch files in `exe` folder only works when execution files exists.

If you want to run the source code, download These Things:
- **Python** **_(latest)_**: [Link](https://www.python.org/downloads/)
- **PIP**: Should install with Python
- **Pygame**: Run `pip install -U pygame` in Terminal or something similar to Terminal
- **PyInstaller** **_(optional, if you need .exe)_**: Run `pip install -U pyinstaller` in Terminal too

Run `test.bat` to start a official game test.

Run `input.bat` to play a world from json file in the `worlds*`* folder.

Run `edit.bat` to edit and save a world from json file in the `worlds` folder, or create one.

You can run `help.bat` for more information with how to run the game in terminal.

If you need to make an .exe file, run `py_2_exe.bat`.

### How to control

- WSAD: You move.
- Space: You wait for something.
- Z: Undo, max 100 times.
- R: Restart.
- Minus / Equals: Select level for camera to focus.

### How to win

Simply put something that is **YOU** to something that is **WIN**.

And remember:

1. Sometimes the rules itself can be changed;
2. Sometimes some of the rules can not be changed;
3. Sometimes you need to get inside of the sublevel;
4. Sometimes you need to create a paradox.

## How to make a custom world

**Important: the levels that placed are pointed to the levels that camera looks at.**
**If you want to put levels inside other levels, please considering cut / paste.**

### How to control

- WSAD: Move cursor.
- IKJL: Change orientation.
- Q / E: Select object.
- Tab: Switch object / noun.
- Enter: Place object on cursor.
- Backspace: Destroy all objects on cursor.
- Minus / Equals: Select level.
- P: New level (information from terminal inputs).
- O: Delete current level (confirm in terminal).
- R: Change global rules (information from terminal inputs).
- Z: Undo, max 100 times.
- X: Cut all objects on cursor.
- C: Copy all objects on cursor.
- V: Paste all objects on cursor.
- Close Pygame Window: Save and quit.

## List of Versions

| Number |    Time    | Informations |
|--------|------------|--------------|
| 1.0    | 2024.07.05 | Initialized. |
| 1.1    | 2024.07.06 | Keke is Move; Undo and Restart; Baba make Levels |
| 1.11   | 2024.07.06 | Level is Previous and Next |
| 1.2    | 2024.07.06 | Flag is Win; Game is EXE |
| 1.3    | 2024.07.06 | Baba is Keke; World is Input and Output |
| 1.31   | 2024.07.07 | Terminal is More; Text is not Hide; Level is Red |
| 1.4    | 2024.07.07 | Baba make Worlds |
| 1.41   | 2024.07.07 | Level is Best and Swap |
| 1.42   | 2024.07.08 | Code is Better |
| 1.5    | 2024.07.08 | Baba is Float; Me is Sink; Rock is Defeat |
| 1.6    | 2024.07.08 | Door is Shut; Key is Open |
| 1.7    | 2024.07.09 | All has Color; Lava is Hot; Ice is Melt |
| 1.8    | 2024.07.10 | Game has Icon; Baba is Word; Keke is Shift; Rock is Tele |
| 1.81   | 2024.07.10 | Argv is Better |

## Bug Reports and Advices

Send your message to yangsy56302@163.com!

## Support

Not open for now.