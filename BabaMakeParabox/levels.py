from typing import Any, Optional
import random

from BabaMakeParabox import basics, spaces, objects, rules, worlds, displays

import pygame

class level(object):
    class_name: str = "level"
    def __init__(self, name: str, world_list: list[worlds.world], super_level: Optional[str] = None, main_world_name: Optional[str] = None, main_world_tier: Optional[int] = None, rule_list: Optional[list[rules.Rule]] = None) -> None:
        self.name: str = name
        self.world_list: list[worlds.world] = list(world_list)
        self.super_level: Optional[str] = super_level
        self.main_world_name: str = main_world_name if main_world_name is not None else world_list[0].name
        self.main_world_tier: int = main_world_tier if main_world_tier is not None else world_list[0].inf_tier
        self.rule_list: list[rules.Rule] = rule_list if rule_list is not None else rules.default_rule_list
        self.game_properties: list[type[objects.Object]] = []
        self.all_list: list[type[objects.Object]] = []
        self.sound_events: list[str] = []
    def __eq__(self, level: "level") -> bool:
        return self.name == level.name
    def __str__(self) -> str:
        return self.class_name
    def __repr__(self) -> str:
        return self.class_name
    def find_rules(self, *match_rule: Optional[type[objects.Text]]) -> list[rules.Rule]:
        found_rules = []
        for rule in self.rule_list:
            if len(rule) != len(match_rule):
                continue
            not_match = False
            for i in range(len(rule)):
                text_type = match_rule[i]
                if text_type is not None:
                    if not issubclass(rule[i], text_type):
                        not_match = True
                        break
            if not_match:
                continue
            found_rules.append(rule)
        return found_rules
    def get_world(self, name: str, inf_tier: int) -> Optional[worlds.world]:
        world = list(filter(lambda l: l.name == name and l.inf_tier == inf_tier, self.world_list))
        return world[0] if len(world) != 0 else None
    def get_exist_world(self, name: str, inf_tier: int) -> worlds.world:
        world = list(filter(lambda l: l.name == name and l.inf_tier == inf_tier, self.world_list))
        return world[0]
    def set_world(self, world: worlds.world) -> None:
        for i in range(len(self.world_list)):
            if world.name == self.world_list[i].name:
                self.world_list[i] = world
                return
        self.world_list.append(world)
    def find_super_world(self, name: str, inf_tier: int) -> Optional[tuple[worlds.world, objects.Object]]:
        for super_world in self.world_list:
            for obj in super_world.get_worlds():
                if name == obj.name and inf_tier == obj.inf_tier:
                    return (super_world, obj)
        return None
    def all_list_set(self) -> None:
        for world in self.world_list:
            for obj in world.object_list:
                in_all = any(map(lambda t: isinstance(obj, t), objects.not_in_all))
                noun_type = objects.nouns_objs_dicts.get_noun(type(obj))
                if noun_type is not None and noun_type not in self.all_list and not in_all:
                    self.all_list.append(noun_type)
    def cancel_rules(self, rule_list: list[rules.Rule]) -> list[rules.Rule]:
        rule_tier_dict: dict[int, list[rules.Rule]] = {}
        for rule in rule_list:
            for noun_negated, noun_type, prop_negated_count, prop_type in rules.analysis_rule(rule):
                rule_tier_dict.setdefault(prop_negated_count, [])
                rule_tier_dict[prop_negated_count].append(rule)
        passed: list[tuple[bool, type[objects.Object], type[objects.Object]]] = []
        new_passed: list[tuple[bool, type[objects.Object], type[objects.Object]]] = []
        new_rule_list: list[rules.Rule] = []
        for rule_tier, rule_list in sorted(list(rule_tier_dict.items()), key=lambda p: p[0], reverse=True):
            for rule in rule_list:
                for noun_negated, noun_type, prop_negated_count, prop_type in rules.analysis_rule(rule):
                    if (noun_negated, noun_type, prop_type) not in passed:
                        new_rule_list.append(rule)
                        new_passed.append((noun_negated, noun_type, prop_type))
            passed.extend(new_passed)
        return new_rule_list
    def recursion_rules(self, world: worlds.world, rule_list: Optional[list[rules.Rule]] = None, passed: Optional[list[worlds.world]] = None) -> None:
        passed = passed if passed is not None else []
        if world in passed:
            return
        passed.append(world)
        rule_list = rule_list if rule_list is not None else []
        world.rule_list.extend(rule_list)
        rule_list = world.rule_list
        sub_world_objs = world.get_worlds()
        if len(sub_world_objs) == 0:
            return
        for sub_world_obj in sub_world_objs:
            sub_world = self.get_exist_world(sub_world_obj.name, sub_world_obj.inf_tier)
            self.recursion_rules(sub_world, rule_list, passed)
    def recursion_strict_rules(self, world: worlds.world, rule_list: Optional[list[rules.Rule]] = None, passed: Optional[list[worlds.world]] = None) -> None:
        passed = passed if passed is not None else []
        if world in passed:
            return
        passed.append(world)
        rule_list = rule_list if rule_list is not None else []
        world.strict_rule_list.extend(rule_list)
        rule_list = world.strict_rule_list
        sub_world_objs = world.get_worlds()
        if len(sub_world_objs) == 0:
            return
        for sub_world_obj in sub_world_objs:
            sub_world = self.get_exist_world(sub_world_obj.name, sub_world_obj.inf_tier)
            self.recursion_rules(sub_world, rule_list, passed)
    def update_strict_rules(self) -> None:
        self.game_properties = []
        for world in self.world_list:
            for obj in world.object_list:
                obj.clear_prop()
            world.strict_rule_list = rules.to_atom_rules(world.get_rules())
        for world in self.world_list:
            self.recursion_strict_rules(world)
            world.strict_rule_list.extend([r for r in self.rule_list if r[-1] is objects.WORD])
            world.strict_rule_list = basics.remove_same_elements(world.strict_rule_list)
            world.strict_rule_list = self.cancel_rules(world.strict_rule_list)
            world.strict_rule_list = basics.remove_same_elements(world.strict_rule_list)
        for world in self.world_list:
            for word_rule in basics.remove_same_elements(world.strict_rule_list):
                for noun_negated, noun_type, prop_negated_count, prop_type in rules.analysis_rule(word_rule):
                    if prop_type != objects.WORD:
                        continue
                    obj_type = objects.nouns_objs_dicts.get_obj(noun_type)
                    if obj_type is None:
                        if noun_type == objects.ALL:
                            if noun_negated:
                                for obj in [o for o in world.object_list if isinstance(o, objects.in_not_all)]:
                                    obj.new_prop(objects.WORD, prop_negated_count % 2 == 1)
                            else:
                                for obj in [o for o in world.object_list if not isinstance(o, objects.not_in_all)]:
                                    obj.new_prop(objects.WORD, prop_negated_count % 2 == 1)
                    else:
                        if noun_negated:
                            for obj in [o for o in world.object_list if (not isinstance(o, objects.Special)) and not isinstance(o, obj_type)]:
                                obj.new_prop(objects.WORD, prop_negated_count % 2 == 1)
                        else:
                            for obj in [o for o in world.object_list if isinstance(o, obj_type)]:
                                obj.new_prop(objects.WORD, prop_negated_count % 2 == 1)
        for world in self.world_list:
            world.strict_rule_list = rules.to_atom_rules(world.get_rules())
            for obj in world.object_list:
                obj.clear_prop()
        for world in self.world_list:
            world.strict_rule_list = basics.remove_same_elements(world.strict_rule_list)
            world.strict_rule_list = self.cancel_rules(world.strict_rule_list)
            world.strict_rule_list = basics.remove_same_elements(world.strict_rule_list)
    def update_rules(self) -> None:
        self.update_strict_rules()
        for world in self.world_list:
            for obj in world.object_list:
                obj.clear_prop()
            world.rule_list = rules.to_atom_rules(world.get_rules())
        for world in self.world_list:
            self.recursion_rules(world)
            world.rule_list.extend([r for r in self.rule_list if r[-1] is objects.WORD])
            world.rule_list = basics.remove_same_elements(world.rule_list)
            world.rule_list = self.cancel_rules(world.rule_list)
            world.rule_list = basics.remove_same_elements(world.rule_list)
        for world in self.world_list:
            for word_rule in basics.remove_same_elements(world.rule_list):
                for noun_negated, noun_type, prop_negated_count, prop_type in rules.analysis_rule(word_rule):
                    if prop_type != objects.WORD:
                        continue
                    obj_type = objects.nouns_objs_dicts.get_obj(noun_type)
                    if obj_type is None:
                        if noun_type == objects.ALL:
                            if noun_negated:
                                for obj in [o for o in world.object_list if isinstance(o, objects.in_not_all)]:
                                    obj.new_prop(objects.WORD, prop_negated_count % 2 == 1)
                            else:
                                for obj in [o for o in world.object_list if not isinstance(o, objects.not_in_all)]:
                                    obj.new_prop(objects.WORD, prop_negated_count % 2 == 1)
                    else:
                        if obj_type == objects.Game:
                            if not noun_negated:
                                self.game_properties.append(objects.WORD)
                        if noun_negated:
                            for obj in [o for o in world.object_list if (not isinstance(o, objects.Special)) and not isinstance(o, obj_type)]:
                                obj.new_prop(objects.WORD, prop_negated_count % 2 == 1)
                        else:
                            for obj in [o for o in world.object_list if isinstance(o, obj_type)]:
                                obj.new_prop(objects.WORD, prop_negated_count % 2 == 1)
        for world in self.world_list:
            world.rule_list = rules.to_atom_rules(world.get_rules())
            for obj in world.object_list:
                obj.clear_prop()
        for world in self.world_list:
            self.recursion_rules(world)
            world.rule_list.extend(self.rule_list)
            world.rule_list = basics.remove_same_elements(world.rule_list)
            world.rule_list = self.cancel_rules(world.rule_list)
            world.rule_list = basics.remove_same_elements(world.rule_list)
        for world in self.world_list:
            for prop_rule in world.rule_list:
                for noun_negated, noun_type, prop_negated_count, prop_type in rules.analysis_rule(prop_rule):
                    obj_type = objects.nouns_objs_dicts.get_obj(noun_type)
                    if obj_type is None:
                        if noun_type == objects.ALL:
                            if noun_negated:
                                for obj in [o for o in world.object_list if isinstance(o, objects.in_not_all)]:
                                    obj.new_prop(prop_type, prop_negated_count % 2 == 1)
                            else:
                                for obj in [o for o in world.object_list if not isinstance(o, objects.not_in_all)]:
                                    obj.new_prop(prop_type, prop_negated_count % 2 == 1)
                    else:
                        if obj_type == objects.Game:
                            if not noun_negated:
                                self.game_properties.append(prop_type)
                        if noun_negated:
                            for obj in [o for o in world.object_list if (not isinstance(o, objects.Special)) and not isinstance(o, obj_type)]:
                                obj.new_prop(prop_type, prop_negated_count % 2 == 1)
                        else:
                            for obj in [o for o in world.object_list if isinstance(o, obj_type)]:
                                obj.new_prop(prop_type, prop_negated_count % 2 == 1)
    def move_obj_between_worlds(self, old_world: worlds.world, obj: objects.Object, new_world: worlds.world, new_pos: spaces.Coord) -> None:
        old_world.object_pos_index[old_world.pos_to_index(obj.pos)].remove(obj)
        old_world.object_list.remove(obj)
        obj.pos = new_pos
        new_world.object_list.append(obj)
        new_world.object_pos_index[new_world.pos_to_index(obj.pos)].append(obj)
    def move_obj_in_world(self, world: worlds.world, obj: objects.Object, pos: spaces.Coord) -> None:
        world.object_pos_index[world.pos_to_index(obj.pos)].remove(obj)
        obj.pos = pos
        world.object_pos_index[world.pos_to_index(obj.pos)].append(obj)
    def same_float_prop(self, obj_1: objects.Object, obj_2: objects.Object):
        return not (obj_1.has_prop(objects.FLOAT) ^ obj_2.has_prop(objects.FLOAT))
    def get_move_list(self, cause: type[objects.Property], world: worlds.world, obj: objects.Object, facing: spaces.Orient, pos: Optional[spaces.Coord] = None, pushed: Optional[list[objects.Object]] = None, passed: Optional[list[worlds.world]] = None, transnum: Optional[float] = None, depth: int = 0) -> Optional[list[tuple[objects.Object, worlds.world, spaces.Coord, spaces.Orient]]]:
        if depth > 128:
            return None
        depth += 1
        pushed = pushed[:] if pushed is not None else []
        if obj in pushed:
            return None
        passed = passed[:] if passed is not None else []
        pos = pos if pos is not None else obj.pos
        new_pos = spaces.pos_facing(pos, facing)
        simple_push = True
        exit_world = False
        exit_list = []
        if world.out_of_range(new_pos):
            exit_world = True
            simple_push = False
            # infinite exit
            if world in passed:
                return_value = self.find_super_world(world.name, world.inf_tier + 1)
                if return_value is None:
                    exit_world = False
                else:
                    super_world, world_obj = return_value
                    new_transnum = super_world.transnum_to_bigger_transnum(transnum, world_obj.pos, facing) if transnum is not None else world.pos_to_transnum(obj.pos, facing)
                    new_move_list = self.get_move_list(cause, super_world, obj, facing, world_obj.pos, pushed, passed, new_transnum, depth)
                    if new_move_list is None:
                        exit_world = False
                    else:
                        exit_list.extend(new_move_list)
            # exit
            else:
                return_value = self.find_super_world(world.name, world.inf_tier)
                if return_value is None:
                    exit_world = False
                else:
                    super_world, world_obj = return_value
                    new_transnum = super_world.transnum_to_bigger_transnum(transnum, world_obj.pos, facing) if transnum is not None else world.pos_to_transnum(obj.pos, facing)
                    passed.append(world)
                    new_move_list = self.get_move_list(cause, super_world, obj, facing, world_obj.pos, pushed, passed, new_transnum, depth)
                    if new_move_list is None:
                        exit_world = False
                    else:
                        exit_list.extend(new_move_list)
        # stop wall & shut door
        stop_objects = list(filter(lambda o: objects.Object.has_prop(o, objects.STOP) and not objects.Object.has_prop(o, objects.PUSH), world.get_objs_from_pos(new_pos)))
        move_list = []
        can_move = True
        if len(stop_objects) != 0 and not world.out_of_range(new_pos):
            simple_push = False
            if obj.has_prop(objects.OPEN):
                for stop_object in stop_objects:
                    if stop_object.has_prop(objects.SHUT):
                        return [(obj, world, new_pos, facing)]
            for stop_object in stop_objects:
                obj_can_move = False
                if issubclass(cause, objects.YOU) and stop_object.has_prop(objects.YOU):
                    if obj.has_prop(objects.YOU) and not obj.has_prop(objects.STOP):
                        obj_can_move = True
                    else:
                        pushed.append(obj)
                        new_move_list = self.get_move_list(cause, world, stop_object, facing, pushed=pushed, depth=depth)
                        pushed.pop()
                        if new_move_list is not None:
                            obj_can_move = True
                            move_list.extend(new_move_list)
                if not obj_can_move:
                    can_move = False
        # push
        push_objects = list(filter(lambda o: objects.Object.has_prop(o, objects.PUSH), world.get_objs_from_pos(new_pos)))
        you_objects = list(filter(lambda o: objects.Object.has_prop(o, objects.YOU), world.get_objs_from_pos(new_pos)))
        if not issubclass(cause, objects.YOU):
            push_objects.extend(you_objects)
        worlds_that_cant_push: list[objects.WorldPointer] = []
        push = False
        push_list = []
        if len(push_objects) != 0 and not world.out_of_range(new_pos):
            push = True
            simple_push = False
            for push_object in push_objects:
                pushed.append(obj)
                new_move_list = self.get_move_list(cause, world, push_object, facing, pushed=pushed, depth=depth)
                pushed.pop()
                if new_move_list is None:
                    if isinstance(push_object, objects.WorldPointer):
                        worlds_that_cant_push.append(push_object)
                    push = False
                    break
                else:
                    push_list.extend(new_move_list)
            push_list.append((obj, world, new_pos, facing))
        # squeeze
        squeeze = False
        squeeze_list = []
        if isinstance(obj, objects.WorldPointer) and obj.has_prop(objects.PUSH) and not world.out_of_range(new_pos):
            sub_world = self.get_world(obj.name, obj.inf_tier)
            if sub_world is not None:
                new_push_objects = list(filter(lambda o: objects.Object.has_prop(o, objects.PUSH), world.get_objs_from_pos(new_pos)))
                if len(new_push_objects) != 0:
                    squeeze = True
                    simple_push = False
                    temp_stop_object = objects.STOP(spaces.pos_facing(pos, spaces.swap_orientation(facing)))
                    temp_stop_object.new_prop(objects.STOP)
                    world.new_obj(temp_stop_object)
                    for new_push_object in new_push_objects:
                        input_pos = sub_world.default_input_position(facing)
                        pushed.append(obj)
                        test_move_list = self.get_move_list(cause, sub_world, new_push_object, spaces.swap_orientation(facing), input_pos, pushed=pushed, depth=depth)
                        pushed.pop()
                        if test_move_list is None:
                            squeeze = False
                            break
                        else:
                            squeeze_list.extend(test_move_list)
                    if squeeze:
                        squeeze_list.append((obj, world, new_pos, facing))
                    world.del_obj(temp_stop_object)
        enter_world = False
        enter_list = []
        if len(worlds_that_cant_push) != 0 and not world.out_of_range(new_pos):
            enter_world = True
            simple_push = False
            for world_object in worlds_that_cant_push:
                sub_world = self.get_world(world_object.name, world_object.inf_tier)
                if sub_world is None:
                    enter_world = False
                    break
                else:
                    new_move_list = None
                    # infinite enter
                    if sub_world in passed:
                        sub_sub_world = self.get_world(sub_world.name, sub_world.inf_tier - 1)
                        if sub_sub_world is not None:
                            new_transnum = 0.5
                            input_pos = sub_sub_world.default_input_position(spaces.swap_orientation(facing))
                            passed.append(world)
                            new_move_list = self.get_move_list(cause, sub_sub_world, obj, facing, input_pos, pushed, passed, new_transnum, depth)
                        else:
                            enter_world = False
                            break
                    # enter
                    else:
                        new_transnum = world.transnum_to_smaller_transnum(transnum, world_object.pos, spaces.swap_orientation(facing)) if transnum is not None else 0.5
                        input_pos = sub_world.transnum_to_pos(transnum, spaces.swap_orientation(facing)) if transnum is not None else sub_world.default_input_position(spaces.swap_orientation(facing))
                        passed.append(world)
                        new_move_list = self.get_move_list(cause, sub_world, obj, facing, input_pos, pushed, passed, new_transnum, depth)
                    if new_move_list is not None:
                        enter_list.extend(new_move_list)
                    else:
                        enter_world = False
                        break
        if exit_world:
            move_list = exit_list
        elif push:
            move_list = push_list
        elif enter_world:
            move_list = enter_list
        elif squeeze:
            move_list = squeeze_list
        if not can_move:
            return None
        if exit_world or push or enter_world or squeeze:
            return basics.remove_same_elements(move_list)
        if simple_push:
            return [(obj, world, new_pos, facing)] 
    def move_objs_from_move_list(self, move_list: list[tuple[objects.Object, worlds.world, spaces.Coord, spaces.Orient]]) -> None:
        move_list = basics.remove_same_elements(move_list)
        for move_obj, new_world, new_pos, new_facing in move_list:
            move_obj.moved = True
            for world in self.world_list:
                if move_obj in world.object_list:
                    old_world = world
            if old_world == new_world:
                self.move_obj_in_world(old_world, move_obj, new_pos)
            else:
                self.move_obj_between_worlds(old_world, move_obj, new_world, new_pos)
        if len(move_list) != 0 and "move" not in self.sound_events:
            self.sound_events.append("move")
    def you(self, facing: spaces.PlayerOperation) -> bool:
        if facing == spaces.O:
            return False
        move_list = []
        pushing_game = False
        for world in self.world_list:
            you_objs = filter(lambda o: objects.Object.has_prop(o, objects.YOU), world.object_list)
            for obj in you_objs:
                obj.facing = facing # type: ignore
                new_move_list = self.get_move_list(objects.YOU, world, obj, obj.facing) # type: ignore
                if new_move_list is not None:
                    move_list.extend(new_move_list)
                else:
                    pushing_game = True
        move_list = basics.remove_same_elements(move_list)
        self.move_objs_from_move_list(move_list)
        return pushing_game
    def select(self, facing: spaces.PlayerOperation) -> Optional[str]:
        if facing == spaces.O:
            for world in self.world_list:
                select_objs = filter(lambda o: objects.Object.has_prop(o, objects.SELECT), world.object_list)
                levels: list[objects.Level] = []
                for obj in select_objs:
                    levels.extend(world.get_levels_from_pos(obj.pos))
                    if len(levels) != 0:
                        self.sound_events.append("level")
                        return levels[0].name
        else:
            for world in self.world_list:
                select_objs = filter(lambda o: objects.Object.has_prop(o, objects.SELECT), world.object_list)
                for obj in select_objs:
                    new_pos = spaces.pos_facing(obj.pos, facing) # type: ignore
                    if not world.out_of_range(new_pos):
                        self.move_obj_in_world(world, obj, new_pos)
            return None
    def move(self) -> bool:
        pushing_game = False
        for world in self.world_list:
            move_objs = filter(lambda o: objects.Object.has_prop(o, objects.MOVE), world.object_list)
            for obj in move_objs:
                move_list = []
                new_move_list = self.get_move_list(objects.MOVE, world, obj, obj.facing)
                if new_move_list is not None:
                    move_list = new_move_list
                else:
                    obj.facing = spaces.swap_orientation(obj.facing)
                    new_move_list = self.get_move_list(objects.MOVE, world, obj, obj.facing)
                    if new_move_list is not None:
                        move_list = new_move_list
                    else:
                        pushing_game = True
                move_list = basics.remove_same_elements(move_list)
                self.move_objs_from_move_list(move_list)
        return pushing_game
    def shift(self) -> bool:
        move_list = []
        pushing_game = False
        for world in self.world_list:
            shift_objs = filter(lambda o: objects.Object.has_prop(o, objects.SHIFT), world.object_list)
            for shift_obj in shift_objs:
                for obj in world.get_objs_from_pos(shift_obj.pos):
                    if obj == shift_obj:
                        continue
                    if self.same_float_prop(obj, shift_obj):
                        new_move_list = self.get_move_list(objects.SHIFT, world, obj, shift_obj.facing)
                        if new_move_list is not None:
                            move_list.extend(new_move_list)
                        else:
                            pushing_game = True
        move_list = basics.remove_same_elements(move_list)
        self.move_objs_from_move_list(move_list)
        return pushing_game
    def tele(self) -> None:
        tele_list: list[tuple[worlds.world, objects.Object, spaces.Coord]] = []
        object_list = []
        for world in self.world_list:
            object_list.extend(world.object_list)
        tele_objs = filter(lambda o: objects.Object.has_prop(o, objects.TELE), object_list)
        tele_obj_types: dict[type[objects.Object], list[objects.Object]] = {}
        for obj_type in objects.nouns_objs_dicts.pairs.values():
            for tele_obj in tele_objs:
                if isinstance(tele_obj, obj_type):
                    tele_obj_types[obj_type] = tele_obj_types.get(obj_type, []) + [tele_obj]
        for tele_objs in tele_obj_types.values():
            if len(tele_objs) <= 1:
                continue
            for tele_obj in tele_objs:
                other_tele_objs = tele_objs[:]
                other_tele_objs.remove(tele_obj)
                for obj in world.get_objs_from_pos(tele_obj.pos):
                    if obj == tele_obj:
                        continue
                    if self.same_float_prop(obj, tele_obj):
                        other_tele_obj = random.choice(other_tele_objs)
                        tele_list.append((world, obj, other_tele_obj.pos))
        for world, obj, pos in tele_list:
            self.move_obj_in_world(world, obj, pos)
        if len(tele_list) != 0:
            self.sound_events.append("tele")
    def sink(self) -> None:
        delete_list = []
        for world in self.world_list:
            sink_objs = filter(lambda o: objects.Object.has_prop(o, objects.SINK), world.object_list)
            for sink_obj in sink_objs:
                for obj in world.get_objs_from_pos(sink_obj.pos):
                    if obj == sink_obj:
                        continue
                    if self.same_float_prop(obj, sink_obj):
                        if obj not in delete_list and sink_obj not in delete_list:
                            delete_list.append(obj)
                            delete_list.append(sink_obj)
                            break
        for obj in delete_list:
            world.del_obj(obj)
        if len(delete_list) != 0:
            self.sound_events.append("sink")
    def hot_and_melt(self) -> None:
        delete_list = []
        for world in self.world_list:
            hot_objs = filter(lambda o: objects.Object.has_prop(o, objects.DEFEAT), world.object_list)
            for hot_obj in hot_objs:
                melt_objs = filter(lambda o: objects.Object.has_prop(o, objects.YOU), world.get_objs_from_pos(hot_obj.pos))
                for melt_obj in melt_objs:
                    if self.same_float_prop(hot_obj, melt_obj):
                        if melt_obj not in delete_list:
                            delete_list.append(melt_obj)
        for obj in delete_list:
            world.del_obj(obj)
        if len(delete_list) != 0:
            self.sound_events.append("melt")
    def defeat(self) -> None:
        delete_list = []
        for world in self.world_list:
            defeat_objs = filter(lambda o: objects.Object.has_prop(o, objects.DEFEAT), world.object_list)
            for defeat_obj in defeat_objs:
                you_objs = filter(lambda o: objects.Object.has_prop(o, objects.YOU), world.get_objs_from_pos(defeat_obj.pos))
                for you_obj in you_objs:
                    if self.same_float_prop(defeat_obj, you_obj):
                        if you_obj not in delete_list:
                            delete_list.append(you_obj)
        for obj in delete_list:
            world.del_obj(obj)
        if len(delete_list) != 0:
            self.sound_events.append("defeat")
    def open_and_shut(self) -> None:
        delete_list = []
        for world in self.world_list:
            shut_objs = filter(lambda o: objects.Object.has_prop(o, objects.SHUT), world.object_list)
            for shut_obj in shut_objs:
                open_objs = filter(lambda o: objects.Object.has_prop(o, objects.OPEN), world.get_objs_from_pos(shut_obj.pos))
                for open_obj in open_objs:
                    if shut_obj not in delete_list and open_obj not in delete_list:
                        delete_list.append(shut_obj)
                        delete_list.append(open_obj)
                        break
        for obj in delete_list:
            world.del_obj(obj)
        if len(delete_list) != 0:
            self.sound_events.append("open")
    def transform(self) -> tuple[list["level"], list[objects.Object], list[objects.Object]]:
        new_levels: list[level] = []
        level_transform_to: list[objects.Object] = []
        new_window_objects: list[objects.Object] = []
        for world in self.world_list:
            delete_object_list = []
            for old_obj in world.object_list: # type: ignore
                old_obj: objects.Object # type: ignore
                old_type = type(old_obj)
                new_nouns = [t for t in old_obj.properties if issubclass(t, objects.Noun)]
                new_types = [t for t in map(objects.nouns_objs_dicts.get_obj, new_nouns) if t is not None]
                not_new_types: list[type[objects.Object]] = []
                for maybe_not_new_noun in [t for t in old_obj.negate_properties if issubclass(t, objects.Noun)]:
                    maybe_not_new_type = objects.nouns_objs_dicts.get_obj(maybe_not_new_noun)
                    if maybe_not_new_type is not None:
                        not_new_types.append(maybe_not_new_type)
                transform_success = False
                old_type_is_old_type = False
                for old_property in old_obj.properties:
                    if issubclass(old_property, objects.Noun):
                        if issubclass(old_property, objects.nouns_objs_dicts.get_exist_noun(old_type)):
                            old_type_is_old_type = True
                if not old_type_is_old_type:
                    if objects.ALL in new_nouns:
                        all_nouns = [t for t in self.all_list if t not in not_new_types]
                        new_types.extend([t for t in map(objects.nouns_objs_dicts.get_obj, all_nouns) if t is not None]) # type: ignore
                    for new_type in new_types:
                        pass_other_transform = False
                        for not_new_type in not_new_types:
                            if issubclass(new_type, not_new_type):
                                if issubclass(old_type, not_new_type):
                                    transform_success = True
                                else:
                                    pass_other_transform = True
                        if pass_other_transform:
                            pass
                        elif issubclass(new_type, objects.Game):
                            if issubclass(old_type, objects.Level):
                                new_obj = objects.Sprite(old_obj.pos, objects.Level.sprite_name, facing=old_obj.facing)
                                new_window_objects.append(new_obj)
                            elif issubclass(old_type, objects.World):
                                new_obj = objects.Sprite(old_obj.pos, objects.World.sprite_name, facing=old_obj.facing)
                                new_window_objects.append(new_obj)
                            elif issubclass(old_type, objects.Clone):
                                new_obj = objects.Sprite(old_obj.pos, objects.Clone.sprite_name, facing=old_obj.facing)
                                new_window_objects.append(new_obj)
                            else:
                                new_window_objects.append(old_obj)
                            transform_success = True
                        elif issubclass(new_type, objects.Level):
                            if issubclass(old_type, objects.Level):
                                pass
                            elif issubclass(old_type, objects.WorldPointer):
                                old_obj: objects.WorldPointer # type: ignore
                                new_levels.append(level(old_obj.name, self.world_list, self.name, old_obj.name, old_obj.inf_tier, self.rule_list))
                                new_obj = objects.Level(old_obj.pos, old_obj.name, facing=old_obj.facing)
                                world.new_obj(new_obj)
                                transform_success = True
                            else:
                                new_world = worlds.world(old_obj.uuid.hex, (1, 1), 0, 0x000000)
                                new_levels.append(level(old_obj.uuid.hex, [new_world], self.name, rule_list=self.rule_list))
                                new_world.new_obj(old_type((0, 0)))
                                new_obj = objects.Level(old_obj.pos, old_obj.uuid.hex, facing=old_obj.facing)
                                world.new_obj(new_obj)
                                transform_success = True
                        elif issubclass(new_type, objects.World):
                            if issubclass(old_type, objects.World):
                                pass
                            elif issubclass(old_type, objects.Level):
                                old_obj: objects.Level # type: ignore
                                info = {"from": {"type": objects.Level, "name": old_obj.name}, "to": {"type": new_type}}
                                world.new_obj(objects.Transform(old_obj.pos, info, old_obj.facing))
                                transform_success = True
                            elif issubclass(old_type, objects.Clone):
                                old_obj: objects.Clone # type: ignore
                                world.new_obj(objects.World(old_obj.pos, old_obj.name, old_obj.inf_tier, old_obj.facing))
                                transform_success = True
                            else:
                                new_world = worlds.world(old_obj.uuid.hex, (1, 1), 0, 0x000000)
                                new_world.new_obj(old_type((0, 0), old_obj.facing)) # type: ignore
                                self.set_world(new_world)
                                world.new_obj(objects.World(old_obj.pos, old_obj.uuid.hex, 0, old_obj.facing))
                                transform_success = True
                        elif issubclass(new_type, objects.Clone):
                            if issubclass(old_type, objects.Clone):
                                pass
                            elif issubclass(old_type, objects.Level):
                                old_obj: objects.Level # type: ignore
                                info = {"from": {"type": objects.Level, "name": old_obj.name}, "to": {"type": new_type}}
                                world.new_obj(objects.Transform(old_obj.pos, info, old_obj.facing))
                                transform_success = True
                            elif issubclass(old_type, objects.World):
                                old_obj: objects.World # type: ignore
                                world.new_obj(objects.Clone(old_obj.pos, old_obj.name, old_obj.inf_tier, old_obj.facing))
                                transform_success = True
                            else:
                                new_world = worlds.world(old_obj.uuid.hex, (1, 1), 0, 0x000000)
                                new_world.new_obj(old_type((0, 0), old_obj.facing)) # type: ignore
                                self.set_world(new_world)
                                world.new_obj(objects.Clone(old_obj.pos, old_obj.uuid.hex, 0, old_obj.facing))
                                transform_success = True
                        elif issubclass(new_type, objects.Text) and not issubclass(old_type, objects.Text):
                            transform_success = True
                            new_obj = objects.nouns_objs_dicts.get_exist_noun(old_type)(old_obj.pos, old_obj.facing)
                            world.new_obj(new_obj)
                        else:
                            transform_success = True
                            new_obj = new_type(old_obj.pos, old_obj.facing)
                            world.new_obj(new_obj)
                if transform_success:
                    delete_object_list.append(old_obj)
            for delete_obj in delete_object_list:
                world.del_obj(delete_obj)
        for world in self.world_list:
            world_transform_to: list[objects.Object] = []
            clone_transform_to: list[objects.Object] = []
            old_type_is_old_type_list: list[type[objects.Object]] = []
            old_type_is_not_old_type_list: list[type[objects.Object]] = []
            for rule in world.strict_rule_list:
                for old_negated, old_type, new_negated_count, new_type in rules.analysis_rule(rule):
                    new_negated = new_negated_count % 2 == 1
                    special_not_new_types: dict[type[objects.Object], list[type[objects.Object]]] = {}
                    if issubclass(old_type, (objects.Level, objects.World, objects.Clone)):
                        if new_negated and not old_negated:
                            special_not_new_types[old_type] = special_not_new_types.get(old_type, []) + [new_type]
                            if issubclass(new_type, old_type):
                                old_type_is_not_old_type_list.append(old_type)
                        elif (not new_negated) and (not old_negated) and issubclass(new_type, old_type):
                            old_type_is_old_type_list.append(old_type)
            special_new_types: dict[type[objects.Object], list[type[objects.Object]]] = {}
            special_new_types[objects.Level] = []
            special_new_types[objects.World] = []
            special_new_types[objects.Clone] = []
            for rule in world.strict_rule_list:
                for old_negated, old_type, new_negated_count, new_type in rules.analysis_rule(rule):
                    if issubclass(old_type, (objects.Level, objects.World, objects.Clone)):
                        if old_type in old_type_is_old_type_list:
                            continue
                        if issubclass(new_type, objects.Noun):
                            if issubclass(new_type, objects.ALL):
                                special_new_types[old_type].extend([t for t in self.all_list if t not in special_not_new_types])
                            elif new_type not in special_not_new_types:
                                special_new_types[old_type].append(new_type)
            for old_type in (objects.Level, objects.World, objects.Clone):
                if old_type in old_type_is_not_old_type_list:
                    if issubclass(old_type, objects.Level):
                        level_transform_to.append(objects.Empty((0, 0)))
                    elif issubclass(old_type, objects.World):
                        world_transform_to.append(objects.Empty((0, 0)))
                    elif issubclass(old_type, objects.Clone):
                        clone_transform_to.append(objects.Empty((0, 0)))
                for new_type in special_new_types[old_type]:
                    if issubclass(old_type, objects.Level):
                        if issubclass(new_type, objects.Level):
                            continue
                        elif issubclass(new_type, objects.World):
                            info = {"from": {"type": objects.Level, "name": self.name}, "to": {"type": objects.World}}
                            level_transform_to.append(objects.Transform((0, 0), info))
                        elif issubclass(new_type, objects.Clone):
                            info = {"from": {"type": objects.Level, "name": self.name}, "to": {"type": objects.Clone}}
                            level_transform_to.append(objects.Transform((0, 0), info))
                        elif issubclass(new_type, objects.Game):
                            level_transform_to.append(objects.Empty((0, 0)))
                            new_obj = objects.Sprite((0, 0), objects.Level.sprite_name)
                            new_window_objects.append(new_obj)
                        elif issubclass(new_type, objects.Text):
                            level_transform_to.append(objects.LEVEL((0, 0)))
                        else:
                            level_transform_to.append(new_type((0, 0)))
                    elif issubclass(old_type, objects.World):
                        if issubclass(new_type, objects.World):
                            continue
                        elif issubclass(new_type, objects.Level):
                            new_levels.append(level(world.name, self.world_list, self.name, world.name, world.inf_tier, self.rule_list))
                            world_transform_to.append(objects.Level((0, 0), world.name))
                        elif issubclass(new_type, objects.Clone):
                            world_transform_to.append(objects.Clone((0, 0), world.name, world.inf_tier))
                        elif issubclass(new_type, objects.Game):
                            level_transform_to.append(objects.Empty((0, 0)))
                            new_obj = objects.Sprite((0, 0), objects.World.sprite_name)
                            new_window_objects.append(new_obj)
                        elif issubclass(new_type, objects.Text):
                            world_transform_to.append(objects.WORLD((0, 0)))
                        else:
                            world_transform_to.append(new_type((0, 0))) # type: ignore
                    elif issubclass(old_type, objects.Clone):
                        if issubclass(new_type, objects.Clone):
                            continue
                        elif issubclass(new_type, objects.Level):
                            new_levels.append(level(world.name, self.world_list, self.name, world.name, world.inf_tier, self.rule_list))
                            clone_transform_to.append(objects.Level((0, 0), world.name))
                        elif issubclass(new_type, objects.World):
                            clone_transform_to.append(objects.World((0, 0), world.name, world.inf_tier))
                        elif issubclass(new_type, objects.Game):
                            level_transform_to.append(objects.Empty((0, 0)))
                            new_obj = objects.Sprite((0, 0), objects.Clone.sprite_name)
                            new_window_objects.append(new_obj)
                        elif issubclass(new_type, objects.Text):
                            clone_transform_to.append(objects.CLONE((0, 0)))
                        else:
                            clone_transform_to.append(new_type((0, 0))) # type: ignore
            delete_special_object_list: list[objects.Object] = []
            for super_world in self.world_list:
                if len(world_transform_to) != 0:
                    for world_obj in filter(lambda o: o.name == world.name and o.inf_tier == world.inf_tier, super_world.get_worlds()):
                        delete_special_object_list.append(world_obj)
                        for transform_obj in world_transform_to:
                            transform_obj.pos = world_obj.pos
                            transform_obj.facing = world_obj.facing
                            super_world.new_obj(transform_obj)
                if len(clone_transform_to) != 0:
                    for clone_obj in filter(lambda o: o.name == world.name and o.inf_tier == world.inf_tier, super_world.get_clones()):
                        delete_special_object_list.append(clone_obj)
                        for transform_obj in clone_transform_to:
                            transform_obj.pos = clone_obj.pos
                            transform_obj.facing = clone_obj.facing
                            super_world.new_obj(transform_obj)
            for obj in delete_special_object_list:
                super_world.del_obj(obj)
        return (new_levels, level_transform_to, new_window_objects)
    def win(self) -> bool:
        for world in self.world_list:
            you_objs = filter(lambda o: objects.Object.has_prop(o, objects.YOU), world.object_list)
            win_objs = filter(lambda o: objects.Object.has_prop(o, objects.WIN), world.object_list)
            float_objs = filter(lambda o: objects.Object.has_prop(o, objects.FLOAT), world.object_list)
            for you_obj in you_objs:
                for win_obj in win_objs:
                    if you_obj.pos == win_obj.pos:
                        if not ((you_obj in float_objs) ^ (win_obj in float_objs)):
                            self.sound_events.append("win")
                            return True
        return False
    def end(self) -> bool:
        for world in self.world_list:
            you_objs = filter(lambda o: objects.Object.has_prop(o, objects.YOU), world.object_list)
            end_objs = filter(lambda o: objects.Object.has_prop(o, objects.END), world.object_list)
            float_objs = filter(lambda o: objects.Object.has_prop(o, objects.FLOAT), world.object_list)
            for you_obj in you_objs:
                for end_obj in end_objs:
                    if you_obj.pos == end_obj.pos:
                        if not ((you_obj in float_objs) ^ (end_obj in float_objs)):
                            self.sound_events.append("end")
                            return True
        return False
    def done(self) -> None:
        delete_list = []
        for world in self.world_list:
            for obj in world.object_list:
                if obj.has_prop(objects.DONE):
                    delete_list.append(obj)
        for obj in delete_list:
            world.del_obj(obj)
        if len(delete_list) != 0:
            self.sound_events.append("done")
    def round(self, op: spaces.PlayerOperation) -> dict[str, Any]:
        self.sound_events = []
        for world in self.world_list:
            for obj in world.object_list:
                obj.moved = False
        self.update_rules()
        pushing_game = self.you(op)
        pushing_game |= self.move()
        self.update_rules()
        self.shift()
        self.update_rules()
        new_levels, transform_to, new_window_objects = self.transform()
        self.update_rules()
        self.tele()
        selected_level = self.select(op)
        self.update_rules()
        self.done()
        self.sink()
        self.hot_and_melt()
        self.defeat()
        self.open_and_shut()
        self.update_rules()
        self.all_list_set()
        win = self.win()
        end = self.end()
        return {"win": win, "end": end,
                "selected_level": selected_level,
                "new_levels": new_levels,
                "transform_to": transform_to,
                "pushing_game": pushing_game,
                "new_window_objects": new_window_objects}
    def have_you(self) -> bool:
        for world in self.world_list:
            for obj in world.object_list:
                if obj.has_prop(objects.YOU):
                    return True
        return False
    def show_world(self, world: worlds.world, frame: int, layer: int = 0, cursor: Optional[spaces.Coord] = None) -> pygame.Surface:
        if layer >= basics.options["world_display_recursion_depth"]:
            return displays.sprites.get("world", 0, frame).copy()
        pixel_sprite_size = displays.sprite_size * displays.pixel_size
        world_surface_size = (world.width * pixel_sprite_size, world.height * pixel_sprite_size)
        world_surface = pygame.Surface(world_surface_size, pygame.SRCALPHA)
        obj_surface_list: list[tuple[spaces.Coord, pygame.Surface, objects.Object]] = []
        for i in range(len(world.object_list)):
            obj = world.object_list[i]
            if isinstance(obj, objects.World):
                obj_world = self.get_world(obj.name, obj.inf_tier)
                if obj_world is not None:
                    obj_surface = self.show_world(obj_world, frame, layer + 1)
                    obj_surface = displays.set_color_dark(obj_surface, 0xCCCCCC)
                else:
                    obj_surface = displays.sprites.get("level", 0, frame).copy()
                surface_pos = (obj.x * pixel_sprite_size, obj.y * pixel_sprite_size)
                obj_surface_list.append((surface_pos, obj_surface, obj))
            elif isinstance(obj, objects.Clone):
                obj_world = self.get_world(obj.name, obj.inf_tier)
                if obj_world is not None:
                    obj_surface = self.show_world(obj_world, frame, layer + 1)
                    obj_surface = displays.set_color_light(obj_surface, 0x444444)
                else:
                    obj_surface = displays.sprites.get("clone", 0, frame).copy()
                surface_pos = (obj.x * pixel_sprite_size, obj.y * pixel_sprite_size)
                obj_surface_list.append((surface_pos, obj_surface, obj))
            elif isinstance(obj, objects.Level):
                obj_surface = displays.set_color_dark(displays.sprites.get(obj.sprite_name, obj.sprite_state, frame).copy(), obj.icon_color)
                icon_surface = displays.set_color_light(displays.sprites.get(obj.icon_name, 0, frame).copy(), 0xFFFFFF)
                icon_surface_pos = ((obj_surface.get_width() - icon_surface.get_width()) * displays.pixel_size // 2,
                                    (obj_surface.get_height() - icon_surface.get_width()) * displays.pixel_size // 2)
                obj_surface.blit(icon_surface, icon_surface_pos)
                surface_pos = (obj.x * pixel_sprite_size - (obj_surface.get_width() - displays.sprite_size) * displays.pixel_size // 2,
                               obj.y * pixel_sprite_size - (obj_surface.get_height() - displays.sprite_size) * displays.pixel_size // 2)
                obj_surface_list.append((surface_pos, obj_surface, obj))
            else:
                obj_surface = displays.sprites.get(obj.sprite_name, obj.sprite_state, frame).copy()
                surface_pos = (obj.x * pixel_sprite_size - (obj_surface.get_width() - displays.sprite_size) * displays.pixel_size // 2,
                               obj.y * pixel_sprite_size - (obj_surface.get_height() - displays.sprite_size) * displays.pixel_size // 2)
                obj_surface_list.append((surface_pos, obj_surface, obj))
        sorted_obj_surface_list = map(lambda o: list(map(lambda t: isinstance(o[-1], t), displays.order)).index(True), obj_surface_list)
        sorted_obj_surface_list = map(lambda t: t[1], sorted(zip(sorted_obj_surface_list, obj_surface_list), key=lambda t: t[0], reverse=True))
        for pos, surface, obj in sorted_obj_surface_list:
            if isinstance(obj, objects.WorldPointer):
                world_surface.blit(pygame.transform.scale(surface, (pixel_sprite_size, pixel_sprite_size)), pos)
            else:
                world_surface.blit(pygame.transform.scale(surface, (displays.pixel_size * surface.get_width(), displays.pixel_size * surface.get_height())), pos)
        if cursor is not None:
            surface = displays.sprites.get("cursor", 0, frame).copy()
            pos = (cursor[0] * pixel_sprite_size - (surface.get_width() - displays.sprite_size) * displays.pixel_size // 2,
                   cursor[1] * pixel_sprite_size - (surface.get_height() - displays.sprite_size) * displays.pixel_size // 2)
            world_surface.blit(pygame.transform.scale(surface, (displays.pixel_size * surface.get_width(), displays.pixel_size * surface.get_height())), pos)
        world_background = pygame.Surface(world_surface.get_size(), pygame.SRCALPHA)
        world_background.fill(pygame.Color(world.color))
        world_background.blit(world_surface, (0, 0))
        world_surface = world_background
        if world.inf_tier > 0:
            infinite_surface = displays.sprites.get("text_infinite", 0, frame)
            multi_infinite_surface = pygame.Surface((infinite_surface.get_width(), infinite_surface.get_height() * world.inf_tier), pygame.SRCALPHA)
            multi_infinite_surface.fill("#00000000")
            for i in range(world.inf_tier):
                multi_infinite_surface.blit(infinite_surface, (0, i * infinite_surface.get_height()))
            multi_infinite_surface = pygame.transform.scale_by(multi_infinite_surface, world.height * displays.pixel_size / world.inf_tier)
            multi_infinite_surface = displays.set_alpha(multi_infinite_surface, 0x44)
            world_surface.blit(multi_infinite_surface, ((world_surface.get_width() - multi_infinite_surface.get_width()) // 2, 0))
        elif world.inf_tier < 0:
            epsilon_surface = displays.sprites.get("text_epsilon", 0, frame)
            multi_epsilon_surface = pygame.Surface((epsilon_surface.get_width(), epsilon_surface.get_height() * -world.inf_tier), pygame.SRCALPHA)
            multi_epsilon_surface.fill("#00000000")
            for i in range(-world.inf_tier):
                multi_epsilon_surface.blit(epsilon_surface, (0, i * epsilon_surface.get_height()))
            multi_epsilon_surface = pygame.transform.scale_by(multi_epsilon_surface, world.height * displays.pixel_size / -world.inf_tier)
            multi_epsilon_surface = displays.set_alpha(multi_epsilon_surface, 0x44)
            world_surface.blit(multi_epsilon_surface, ((world_surface.get_width() - multi_epsilon_surface.get_width()) // 2, 0))
        return world_surface
    def to_json(self) -> dict[str, Any]:
        json_object = {"name": self.name, "world_list": [], "super_level": self.super_level, "main_world": {"name": self.main_world_name, "infinite_tier": self.main_world_tier}}
        for world in self.world_list:
            json_object["world_list"].append(world.to_json())
        return json_object

def json_to_level(json_object: dict[str, Any]) -> level: # oh hell no * 3
    world_list = []
    for world in json_object["world_list"]: # type: ignore
        world_list.append(worlds.json_to_world(world)) # type: ignore
    return level(name=json_object["name"], # type: ignore
                 world_list=world_list,
                 super_level=json_object["super_level"], # type: ignore
                 main_world_name=json_object["main_world"]["name"], # type: ignore
                 main_world_tier=json_object["main_world"]["infinite_tier"]) # type: ignore