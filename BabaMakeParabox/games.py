from typing import Any, Optional
import random
import copy
import os
import multiprocessing

from BabaMakeParabox import basics, languages, sounds, spaces, objects, displays, levels, levelpacks, subgames

import pygame

def play(levelpack: levelpacks.levelpack) -> None:
    print(languages.current_language["game.levelpack.rule_list"]) 
    for rule in levelpack.rule_list:
        str_list = []
        for obj_type in rule:
            str_list.append(obj_type.class_name)
        print(" ".join(str_list))
    for level in levelpack.level_list:
        level.update_rules()
        for world in level.world_list:
            world.set_sprite_states(0)
    levelpack_backup = copy.deepcopy(levelpack)
    multiprocessing.set_start_method("spawn")
    subgame_pipes = []
    window = pygame.display.set_mode((720, 720), pygame.RESIZABLE)
    display_offset = [0.0, 0.0]
    display_offset_speed = [0.0, 0.0]
    pygame.display.set_caption(f"Baba Make Parabox Version {basics.versions}")
    pygame.display.set_icon(pygame.image.load("BabaMakeParabox.png"))
    displays.sprites.update()
    pygame.key.set_repeat()
    pygame.key.stop_text_input()
    clock = pygame.time.Clock()
    keybinds = {"W": pygame.K_w,
                "A": pygame.K_a,
                "S": pygame.K_s,
                "D": pygame.K_d,
                "Z": pygame.K_z,
                "R": pygame.K_r,
                "TAB": pygame.K_TAB,
                "ESCAPE": pygame.K_ESCAPE,
                "-": pygame.K_MINUS,
                "=": pygame.K_EQUALS,
                " ": pygame.K_SPACE,
                "F1": pygame.K_F1}
    keys = {v: False for v in keybinds.values()}
    cooldowns = {v: 0 for v in keybinds.values()}
    window.fill("#000000")
    current_level_name = levelpack.main_level
    current_level = levelpack.get_exist_level(current_level_name)
    current_world_index: int = current_level.world_list.index(current_level.get_exist_world(current_level.main_world_name, current_level.main_world_tier))
    default_level_info = {"win": False, "end": False, "selected_level": None, "new_levels": [], "transform_to": [], "pushing_game": False, "new_window_objects": []}
    level_info = default_level_info.copy()
    level_info_backup = default_level_info.copy()
    history = [{"world_index": current_world_index, "level_name": current_level_name, "level_info": default_level_info, "levelpack": copy.deepcopy(levelpack)}]
    level_changed = False
    world_changed = False
    round_num = 0
    frame = 1
    wiggle = 1
    freeze_time = -1
    milliseconds = 1000 // basics.options["fps"]
    real_fps = basics.options["fps"]
    if basics.options["bgm"]["enabled"]:
        pygame.mixer.music.load(os.path.join("midi", basics.options["bgm"]["name"]))
        pygame.mixer.music.set_volume(0.75)
        pygame.mixer.music.play(-1)
    game_running = True
    while game_running:
        frame += 1
        if frame >= basics.options["fpw"]:
            frame = 0
            wiggle = wiggle % 3 + 1
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                game_running = False
            if event.type == pygame.KEYDOWN and event.key in keybinds.values():
                keys[event.key] = True
            elif event.type == pygame.KEYUP and event.key in keybinds.values():
                keys[event.key] = False
        refresh = False
        if freeze_time == -1:
            if keys[keybinds["W"]] and cooldowns[keybinds["W"]] == 0:
                history.append({"world_index": current_world_index, "level_name": current_level_name, "level_info": level_info, "levelpack": copy.deepcopy(levelpack)})
                round_num += 1
                level_info = current_level.round(spaces.W)
                if objects.YOU in current_level.game_properties:
                    display_offset[1] -= window.get_height() / current_level.world_list[current_world_index].width
                if objects.PUSH in current_level.game_properties and level_info["pushing_game"]:
                    display_offset[1] -= window.get_height() / current_level.world_list[current_world_index].width
                refresh = True
            elif keys[keybinds["S"]] and cooldowns[keybinds["S"]] == 0:
                history.append({"world_index": current_world_index, "level_name": current_level_name, "level_info": level_info, "levelpack": copy.deepcopy(levelpack)})
                round_num += 1
                level_info = current_level.round(spaces.S)
                if objects.YOU in current_level.game_properties:
                    display_offset[1] += window.get_height() / current_level.world_list[current_world_index].width
                if objects.PUSH in current_level.game_properties and level_info["pushing_game"]:
                    display_offset[1] += window.get_height() / current_level.world_list[current_world_index].width
                refresh = True
            elif keys[keybinds["A"]] and cooldowns[keybinds["A"]] == 0:
                history.append({"world_index": current_world_index, "level_name": current_level_name, "level_info": level_info, "levelpack": copy.deepcopy(levelpack)})
                round_num += 1
                level_info = current_level.round(spaces.A)
                if objects.YOU in current_level.game_properties:
                    display_offset[0] -= window.get_width() / current_level.world_list[current_world_index].height
                if objects.PUSH in current_level.game_properties and level_info["pushing_game"]:
                    display_offset[0] -= window.get_width() / current_level.world_list[current_world_index].height
                refresh = True
            elif keys[keybinds["D"]] and cooldowns[keybinds["D"]] == 0:
                history.append({"world_index": current_world_index, "level_name": current_level_name, "level_info": level_info, "levelpack": copy.deepcopy(levelpack)})
                round_num += 1
                level_info = current_level.round(spaces.D)
                if objects.YOU in current_level.game_properties:
                    display_offset[0] += window.get_width() / current_level.world_list[current_world_index].height
                if objects.PUSH in current_level.game_properties and level_info["pushing_game"]:
                    display_offset[0] += window.get_width() / current_level.world_list[current_world_index].height
                refresh = True
            elif keys[keybinds[" "]] and cooldowns[keybinds[" "]] == 0:
                history.append({"world_index": current_world_index, "level_name": current_level_name, "level_info": level_info, "levelpack": copy.deepcopy(levelpack)})
                round_num += 1
                level_info = current_level.round(spaces.O)
                refresh = True
            elif keys[keybinds["ESCAPE"]] and cooldowns[keybinds["ESCAPE"]] == 0:
                history.append({"world_index": current_world_index, "level_name": current_level_name, "level_info": level_info, "levelpack": copy.deepcopy(levelpack)})
                current_level_name = current_level.super_level if current_level.super_level is not None else levelpack.main_level
                current_level = levelpack.get_exist_level(current_level_name)
                current_world_index = current_level.world_list.index(current_level.get_exist_world(current_level.main_world_name, current_level.main_world_tier))
                level_changed = True
                world_changed = True
                refresh = True
            elif keys[keybinds["Z"]] and cooldowns[keybinds["Z"]] == 0:
                if len(history) > 1:
                    data = copy.deepcopy(history.pop())
                    current_world_index = data["world_index"]
                    current_level_name = data["level_name"]
                    level_info = data["level_info"]
                    levelpack = data["levelpack"]
                    current_level = levelpack.get_exist_level(current_level_name)
                    round_num -= 1
                    refresh = True
                elif len(history) == 1:
                    data = copy.deepcopy(history[0])
                    current_world_index = data["world_index"]
                    current_level_name = data["level_name"]
                    level_info = data["level_info"]
                    levelpack = data["levelpack"]
                    current_level = levelpack.get_exist_level(current_level_name)
                    round_num = 0
                    refresh = True
            elif keys[keybinds["R"]] and cooldowns[keybinds["R"]] == 0:
                print(languages.current_language["game.levelpack.restart"])
                sounds.play("restart")
                levelpack = copy.deepcopy(levelpack_backup)
                current_level_name = levelpack.main_level
                current_level = levelpack.get_exist_level(current_level_name)
                current_world_index = current_level.world_list.index(current_level.get_exist_world(current_level.main_world_name, current_level.main_world_tier))
                history = [{"world_index": current_world_index, "level_name": current_level_name, "level_info": default_level_info, "levelpack": copy.deepcopy(levelpack)}]
                level_info = default_level_info.copy()
                display_offset = [0.0, 0.0]
                display_offset_speed = [0.0, 0.0]
                refresh = True
                level_changed = True
                world_changed = True
            elif keys[keybinds["TAB"]] and cooldowns[keybinds["TAB"]] == 0:
                print(languages.current_language["game.levelpack.rule_list"])
                for rule in levelpack.rule_list:
                    str_list = []
                    for obj_type in rule:
                        str_list.append(obj_type.class_name)
                    print(" ".join(str_list))
                print(languages.current_language["game.world.rule_list"])
                for rule in current_level.world_list[current_world_index].rule_list:
                    str_list = []
                    for obj_type in rule:
                        str_list.append(obj_type.class_name)
                    print(" ".join(str_list))
            elif keys[keybinds["-"]] and cooldowns[keybinds["-"]] == 0:
                current_world_index -= 1
                world_changed = True
            elif keys[keybinds["="]] and cooldowns[keybinds["="]] == 0:
                current_world_index += 1
                world_changed = True
            if objects.SHIFT in current_level.game_properties:
                display_offset[0] += window.get_width() / basics.options["fps"]
            if objects.MOVE in current_level.game_properties:
                display_offset[1] += window.get_height() / (4 * basics.options["fps"])
            if objects.SINK in current_level.game_properties:
                display_offset_speed[1] += window.get_height() / (16 * basics.options["fps"])
            elif objects.FLOAT in current_level.game_properties:
                display_offset_speed[1] -= window.get_height() / (64 * basics.options["fps"])
            else:
                display_offset_speed[0] = display_offset_speed[0] / 2
                display_offset_speed[1] = display_offset_speed[1] / 2
        else:
            freeze_time -= 1
        for key, value in keys.items():
            if value and cooldowns[key] == 0:
                cooldowns[key] = basics.options["input_cooldown"]
        if refresh:
            if objects.STOP in current_level.game_properties:
                basics.options["fps"] = 1
                basics.options["fpw"] = 1
                basics.options["input_cooldown"] = 1
            if objects.WIN in current_level.game_properties:
                sounds.play("win")
                game_running = False
            if objects.SHUT in current_level.game_properties:
                sounds.play("defeat")
                game_running = False
            if objects.END in current_level.game_properties:
                sounds.play("end")
                game_running = False
            if objects.DONE in current_level.game_properties:
                sounds.play("done")
                game_running = False
            if objects.OPEN in current_level.game_properties:
                if os.path.exists("BabaMakeParabox.exe"):
                    os.system("start BabaMakeParabox.exe")
                elif os.path.exists("BabaMakeParabox.py"):
                    os.system("start python BabaMakeParabox.py")
            if objects.HOT in current_level.game_properties and objects.MELT in current_level.game_properties:
                sounds.play("melt")
                game_running = False
            if objects.YOU in current_level.game_properties and objects.DEFEAT in current_level.game_properties:
                sounds.play("defeat")
                game_running = False
            if objects.TELE in current_level.game_properties:
                sounds.play("tele")
                display_offset = [float(random.randrange(window.get_width())), float(random.randrange(window.get_height()))]
            for event in current_level.sound_events:
                sounds.play(event)
            for new_level in level_info["new_levels"]:
                levelpack.set_level(new_level)
            for obj in level_info["new_window_objects"]:
                pipe = multiprocessing.Pipe(False)
                subgame_pipes.append(pipe[1])
                kwargs = {"wps": basics.options["fps"] / basics.options["fpw"], "obj": obj}
                process = multiprocessing.Process(target=subgames.new_window, args=(pipe[0], ), kwargs=kwargs)
                process.start()
            transform_success = False
            if len(level_info["transform_to"]) != 0:
                for level in levelpack.level_list:
                    for world in level.world_list:
                        for level_obj in world.get_levels():
                            if current_level.name == level_obj.name:
                                transform_success = True
                                for obj in level_info["transform_to"]:
                                    obj: objects.Object
                                    obj.pos = level_obj.pos
                                    obj.facing = level_obj.facing
                                    world.new_obj(obj)
                                world.del_obj(level_obj)
            for level in levelpack.level_list:
                for world in level.world_list:
                    transform_objs = world.get_objs_from_type(objects.Transform)
                    for transform_obj in transform_objs:
                        if issubclass(transform_obj.from_type, objects.Level):
                            from_level = levelpack.get_exist_level(transform_obj.from_name)
                            if issubclass(transform_obj.to_type, objects.WorldPointer):
                                for new_world in from_level.world_list:
                                    level.set_world(new_world)
                                new_obj = transform_obj.to_type(transform_obj.pos, from_level.main_world_name, from_level.main_world_tier, transform_obj.facing)
                                world.del_obj(transform_obj)
                                world.new_obj(new_obj)
                        elif issubclass(transform_obj.from_type, objects.WorldPointer):
                            from_world = level.get_exist_world(transform_obj.from_name, transform_obj.from_inf_tier)
                            if issubclass(transform_obj.to_type, objects.Level):
                                new_level = levels.level(from_world.name, level.world_list, level.name, transform_obj.from_name, transform_obj.from_inf_tier, level.rule_list)
                                levelpack.set_level(new_level)
                                new_obj = objects.Level(transform_obj.pos, from_world.name, icon_color=from_world.color, facing=transform_obj.facing)
                                world.del_obj(transform_obj)
                                world.new_obj(new_obj)
            for level in levelpack.level_list:
                for world in level.world_list:
                    world.repeated_world_to_clone()
            levelpack.set_level(current_level)
            if level_info["win"]:
                print(languages.current_language["game.level.win"])
                if freeze_time == -1:
                    level_info_backup = copy.deepcopy(level_info)
                    freeze_time = basics.options["fps"]
            elif level_info["end"]:
                print(languages.current_language["game.levelpack.end"])
                if freeze_time == -1:
                    level_info_backup = copy.deepcopy(level_info)
                    freeze_time = basics.options["fps"]
            elif transform_success and len(level_info["transform_to"]) != 0:
                print(languages.current_language["game.level.transform"])
                if freeze_time == -1:
                    level_info_backup = copy.deepcopy(level_info)
                    freeze_time = basics.options["fps"]
            elif level_info["selected_level"] is not None:
                print(languages.current_language["game.level.enter"])
                if freeze_time == -1:
                    level_info_backup = copy.deepcopy(level_info)
                    freeze_time = basics.options["fps"]
            for level in levelpack.level_list:
                for world in current_level.world_list:
                    world.object_list = list(filter(lambda o: not isinstance(o, objects.Empty), world.object_list))
                    world.set_sprite_states(round_num)
            level_info = default_level_info.copy()
        if freeze_time == 0:
            level_changed = True
            world_changed = True
            if level_info_backup["win"]:
                level = copy.deepcopy(levelpack_backup.get_level(current_level.name))
                if level is not None:
                    levelpack.set_level(level)
                super_level_name = current_level.super_level
                super_level = levelpack.get_level(super_level_name if super_level_name is not None else levelpack.main_level)
                current_level_name = super_level.name if super_level is not None else levelpack.main_level
                current_level = levelpack.get_exist_level(current_level_name)
            elif level_info_backup["end"]:
                game_running = False
            elif len(level_info_backup["transform_to"]) != 0:
                super_level_name = current_level.super_level
                super_level = levelpack.get_level(super_level_name if super_level_name is not None else levelpack.main_level)
                current_level_name = super_level.name if super_level is not None else levelpack.main_level
                current_level = levelpack.get_exist_level(current_level_name)
            elif level_info_backup["selected_level"] is not None:
                current_level_name = level_info_backup["selected_level"]
                current_level = levelpack.get_exist_level(current_level_name)
                current_world_index = current_level.world_list.index(current_level.get_exist_world(current_level.main_world_name, current_level.main_world_tier))
                round_num = 0
        current_world_index = current_world_index % len(current_level.world_list) if current_world_index >= 0 else len(current_level.world_list) - 1
        if level_changed:
            print(languages.current_language["game.level.current.name"], current_level.name, sep="")
            level_changed = False
        if world_changed:
            print(languages.current_language["game.world.current.name"], current_level.world_list[current_world_index].name, sep="")
            print(languages.current_language["game.world.current.inf_tier"], current_level.world_list[current_world_index].inf_tier, sep="")
            world_changed = False
        pygame.mixer.music.set_volume(0.75 if current_level.have_you() else 0.25)
        window.fill("#000000")
        displays.set_pixel_size(window.get_size())
        window.blit(pygame.transform.scale(current_level.show_world(current_level.world_list[current_world_index], wiggle), (window.get_width(), window.get_height())), (0, 0))
        real_fps = min(1000 / milliseconds, (real_fps * (basics.options["fps"] - 1) + 1000 / milliseconds) / basics.options["fps"])
        if keys[keybinds["F1"]]:
            real_fps_string = str(int(real_fps))
            for i in range(len(real_fps_string)):
                window.blit(displays.sprites.get(f"text_{real_fps_string[i]}", 0, wiggle), (i * displays.sprite_size, 0))
        for obj_type in [o for o in map(objects.nouns_objs_dicts.get_obj, [t for t in current_level.game_properties if issubclass(t, objects.Noun)]) if o is not None]:
            window.blit(pygame.transform.scale(displays.sprites.get(obj_type.sprite_name, 0, wiggle), window.get_size()), (0, 0))
        if abs(display_offset_speed[0]) > window.get_width() / basics.options["fps"] * 4:
            symbol = 1 if display_offset_speed[0] > 0 else -1
            display_offset_speed[0] = window.get_width() / basics.options["fps"] * symbol * 4
        if abs(display_offset_speed[1]) > window.get_height() / basics.options["fps"] * 4:
            symbol = 1 if display_offset_speed[1] > 0 else -1
            display_offset_speed[1] = window.get_height() / basics.options["fps"] * symbol * 4
        display_offset[0] += display_offset_speed[0]
        display_offset[1] += display_offset_speed[1]
        display_offset[0] %= float(window.get_width())
        display_offset[1] %= float(window.get_height())
        if display_offset[0] != 0.0 or display_offset[1] != 0.0:
            window_surface = pygame.display.get_surface().copy()
            window.blit(window_surface, [int(display_offset[0]), int(display_offset[1])])
            window.blit(window_surface, [int(display_offset[0] - window.get_width()), int(display_offset[1])])
            window.blit(window_surface, [int(display_offset[0]), int(display_offset[1] - window.get_height())])
            window.blit(window_surface, [int(display_offset[0] - window.get_width()), int(display_offset[1] - window.get_height())])
        pygame.display.flip()
        for key in cooldowns:
            if cooldowns[key] > 0:
                cooldowns[key] -= 1
        milliseconds = clock.tick(basics.options["fps"])
    for pipe in subgame_pipes:
        pipe.send(True)