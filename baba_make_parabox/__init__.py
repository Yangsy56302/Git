import os
import json

print("Baba Make Parabox")
os.environ["PYGAME_HIDE_SUPPORT_PROMPT"] = "TRUE"

import pygame

import baba_make_parabox.basics as basics
import baba_make_parabox.spaces as spaces
import baba_make_parabox.objects as objects
import baba_make_parabox.rules as rules
import baba_make_parabox.levels as levels
import baba_make_parabox.displays as displays
import baba_make_parabox.worlds as worlds
import baba_make_parabox.edits as edits
import baba_make_parabox.games as games

versions = "1.7"

def main() -> None:
    if os.environ.get("PYINSTALLER") == "TRUE":
        pass # just do nothing
    elif not basics.arg_error:
        if basics.args.versions:
            print(f"Version: {versions}")
        if basics.args.test:
            games.test()
            pygame.quit()
            print("Thank you for testing Baba Make Parabox!")
            return
        elif basics.args.code:
            pass
        elif basics.args.input is not None:
            for filename in basics.args.input:
                filename: str
                filename = filename.lstrip()
                with open(os.path.join("worlds", filename + ".json"), "r", encoding="ascii") as file:
                    games.play(worlds.json_to_world(json.load(file)))
            pygame.quit()
            print("Thank you for playing Baba Make Parabox!")
            return
        elif basics.args.edit is not None:
            filename: str = basics.args.edit.lstrip()
            if os.path.isfile(os.path.join("worlds", filename + ".json")):
                with open(os.path.join("worlds", filename + ".json"), "r", encoding="ascii") as file:
                    world = worlds.json_to_world(json.load(file))
            else:
                level = levels.level("main", (16, 16), color=pygame.Color("#000000"))
                world = worlds.world(filename, [level])
            world = edits.level_editor(world)
            with open(os.path.join("worlds", filename + ".json"), "w", encoding="ascii") as file:
                json.dump(world.to_json(), file, indent=4)
            pygame.quit()
            print("Thank you for editing Baba Make Parabox!")
            return
    else:
        print("Oops, looks like you enter the wrong argument.")
        print("Now the game will set a test world instead.")
        games.test()
        pygame.quit()
        print("Thank you for testing Baba Make Parabox!")
        return

__all__ = ["basics", "spaces", "objects", "rules", "levels", "displays", "worlds", "edits", "main"]