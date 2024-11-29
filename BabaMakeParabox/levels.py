import os
from typing import Any, NotRequired, Optional, TypedDict
import random
import copy
import uuid

from BabaMakeParabox import basics, colors, spaces, objects, rules, worlds, displays

import pygame

class LevelMainWorldJson(TypedDict):
    name: str
    infinite_tier: int

class LevelJson(TypedDict):
    name: str
    super_level: Optional[str]
    is_map: NotRequired[bool]
    main_world: LevelMainWorldJson
    world_list: list[worlds.WorldJson]

max_move_count: int = 16

class Level(object):
    def __init__(self, name: str, world_list: list[worlds.World], *, super_level: Optional[str] = None, main_world_name: Optional[str] = None, main_world_tier: Optional[int] = None, is_map: bool = False, rule_list: Optional[list[rules.Rule]] = None) -> None:
        self.name: str = name
        self.world_list: list[worlds.World] = list(world_list)
        self.super_level: Optional[str] = super_level
        self.main_world_name: str = main_world_name if main_world_name is not None else world_list[0].name
        self.main_world_tier: int = main_world_tier if main_world_tier is not None else world_list[0].infinite_tier
        self.rule_list: list[rules.Rule] = rule_list if rule_list is not None else rules.default_rule_list
        self.is_map: bool = is_map
        self.game_properties: objects.Properties = objects.Properties()
        self.properties: objects.Properties = objects.Properties()
        self.special_operator_properties: dict[type[objects.Operator], objects.Properties] = {o: objects.Properties() for o in objects.special_operators}
        self.created_levels: list["Level"] = []
        self.all_list: list[type[objects.Noun]] = []
        self.sound_events: list[str] = []
    def __eq__(self, level: "Level") -> bool:
        return self.name == level.name
    @property
    def main_world(self) -> worlds.World:
        return self.get_exact_world({"name": self.main_world_name, "infinite_tier": self.main_world_tier})
    @main_world.getter
    def main_world(self) -> worlds.World:
        return self.get_exact_world({"name": self.main_world_name, "infinite_tier": self.main_world_tier})
    def get_world(self, world_info: objects.WorldPointerExtraJson) -> Optional[worlds.World]:
        for world in self.world_list:
            if world.name == world_info["name"] and world.infinite_tier == world_info["infinite_tier"]:
                return world
        return None
    def get_world_or_default(self, world_info: objects.WorldPointerExtraJson, *, default: worlds.World) -> worlds.World:
        world = self.get_world(world_info)
        if world is None:
            return default
        return world
    def get_exact_world(self, world_info: objects.WorldPointerExtraJson) -> worlds.World:
        world = self.get_world(world_info)
        if world is None:
            raise KeyError(world_info)
        return world
    def set_world(self, world: worlds.World) -> None:
        for i in range(len(self.world_list)):
            if world.name == self.world_list[i].name:
                self.world_list[i] = world
                return
        self.world_list.append(world)
    def find_super_worlds(self, world_info: objects.WorldPointerExtraJson) -> list[tuple[worlds.World, objects.World]]:
        return_value: list[tuple[worlds.World, objects.World]] = []
        for super_world in self.world_list:
            for obj in super_world.get_worlds():
                if world_info == obj.world_info:
                    return_value.append((super_world, obj))
        return return_value
    def all_list_set(self) -> None:
        for world in self.world_list:
            for obj in world.object_list:
                noun_type = objects.get_noun_from_type(type(obj))
                in_not_in_all = False
                for not_all in objects.not_in_all:
                    if isinstance(obj, not_all):
                        in_not_in_all = True
                if noun_type not in self.all_list and not in_not_in_all:
                    self.all_list.append(noun_type)
    def meet_prefix_conditions(self, world: worlds.World, obj: objects.BmpObject, prefix_info_list: list[rules.PrefixInfo], is_meta: bool = False) -> bool:
        return_value = True
        for prefix_info in prefix_info_list:
            meet_prefix_condition = True
            if prefix_info.prefix_type == objects.TextMeta:
                meet_prefix_condition = is_meta
            elif prefix_info.prefix_type == objects.TextOften:
                meet_prefix_condition = random.choice((True, True, True, False))
            elif prefix_info.prefix_type == objects.TextSeldom:
                meet_prefix_condition = random.choice((True, False, False, False, False, False))
            return_value = return_value and (meet_prefix_condition if not prefix_info.negated else not meet_prefix_condition)
        return return_value
    def meet_infix_conditions(self, world: worlds.World, obj: objects.BmpObject, infix_info_list: list[rules.InfixInfo], old_feeling: Optional[objects.Properties] = None) -> bool:
        for infix_info in infix_info_list:
            meet_infix_condition = True
            if infix_info.infix_type in (objects.TextOn, objects.TextNear, objects.TextNextto):
                matched_objs: list[objects.BmpObject] = [obj]
                if infix_info.infix_type == objects.TextOn:
                    find_range = [(obj.x, obj.y)]
                elif infix_info.infix_type == objects.TextNear:
                    find_range = [(obj.x - 1, obj.y - 1), (obj.x, obj.y - 1), (obj.x + 1, obj.y - 1),
                                  (obj.x - 1, obj.y), (obj.x, obj.y), (obj.x + 1, obj.y),
                                  (obj.x - 1, obj.y + 1), (obj.x, obj.y + 1), (obj.x + 1, obj.y + 1)]
                elif infix_info.infix_type == objects.TextNextto:
                    find_range = [(obj.x, obj.y - 1), (obj.x - 1, obj.y), (obj.x + 1, obj.y), (obj.x, obj.y + 1)]
                for match_negated, match_type_text in infix_info[2]: # type: ignore
                    match_type_text: type[objects.Noun]
                    match_type = match_type_text.obj_type
                    if match_type == objects.All:
                        if match_negated:
                            match_objs: list[objects.BmpObject] = []
                            for new_match_type in [o for o in self.all_list if issubclass(o, objects.in_not_all)]:
                                for pos in find_range:
                                    match_objs.extend([o for o in world.get_objs_from_pos_and_type(pos, new_match_type) if o not in matched_objs])
                                if len(match_objs) == 0:
                                    meet_infix_condition = False
                                    break
                                matched_objs.append(match_objs[0])
                        else:
                            match_objs: list[objects.BmpObject] = []
                            for new_match_type in [o for o in self.all_list if not issubclass(o, objects.not_in_all)]:
                                for pos in find_range:
                                    match_objs.extend([o for o in world.get_objs_from_pos_and_type(pos, new_match_type) if o not in matched_objs])
                                if len(match_objs) == 0:
                                    meet_infix_condition = False
                                    break
                                matched_objs.append(match_objs[0])
                    else:
                        if match_negated:
                            match_objs: list[objects.BmpObject] = []
                            for new_match_type in [o for o in self.all_list if (not issubclass(o, objects.not_in_all)) and not issubclass(o, match_type)]:
                                for pos in find_range:
                                    match_objs.extend([o for o in world.get_objs_from_pos_and_type(pos, new_match_type) if o not in matched_objs])
                            if len(match_objs) == 0:
                                meet_infix_condition = False
                            else:
                                matched_objs.append(match_objs[0])
                        else:
                            match_objs: list[objects.BmpObject] = []
                            for pos in find_range:
                                match_objs.extend([o for o in world.get_objs_from_pos_and_type(pos, match_type) if o not in matched_objs])
                            if len(match_objs) == 0:
                                meet_infix_condition = False
                            else:
                                matched_objs.append(match_objs[0])
                    if not meet_infix_condition:
                        break
            elif infix_info.infix_type == objects.TextFeeling:
                if old_feeling is None:
                    meet_infix_condition = False
                else:
                    for infix_noun_info in infix_info.infix_noun_info_list:
                        if old_feeling.has(infix_noun_info.infix_noun_type) == infix_noun_info.negated:
                            meet_infix_condition = False
            elif infix_info.infix_type == objects.TextWithout:
                meet_infix_condition = True
                matched_objs: list[objects.BmpObject] = [obj]
                match_type_count: dict[tuple[bool, type[objects.Noun]], int] = {}
                for match_negated, match_type_text in infix_info[2]: # type: ignore
                    match_type_text: type[objects.Noun]
                    match_type_count.setdefault((match_negated, match_type_text), 0)
                    match_type_count[(match_negated, match_type_text)] += 1
                for (match_negated, match_type_text), match_count in match_type_count.items():
                    match_type_text: type[objects.Noun]
                    match_type = match_type_text.obj_type
                    if match_type == objects.All:
                        if match_negated:
                            match_objs: list[objects.BmpObject] = []
                            for new_match_type in [o for o in self.all_list if issubclass(o, objects.in_not_all)]:
                                match_objs.extend(world.get_objs_from_type(new_match_type))
                                if len(match_objs) >= match_count:
                                    meet_infix_condition = False
                                    break
                        else:
                            match_objs: list[objects.BmpObject] = []
                            for new_match_type in [o for o in self.all_list if not issubclass(o, objects.not_in_all)]:
                                match_objs.extend(world.get_objs_from_type(new_match_type))
                                if len(match_objs) >= match_count:
                                    meet_infix_condition = False
                                    break
                    else:
                        if match_negated:
                            match_objs: list[objects.BmpObject] = []
                            for new_match_type in [o for o in self.all_list if (not issubclass(o, objects.not_in_all)) and not issubclass(o, match_type)]:
                                match_objs.extend(world.get_objs_from_type(new_match_type))
                            if len(match_objs) >= match_count:
                                meet_infix_condition = False
                        else:
                            match_objs: list[objects.BmpObject] = world.get_objs_from_type(match_type)
                            if len(match_objs) >= match_count:
                                meet_infix_condition = False
                    if not meet_infix_condition:
                        break
            if meet_infix_condition == infix_info.negated:
                return False
        return True
    def recursion_rules(self, world: worlds.World, rule_list: Optional[list[rules.Rule]] = None, passed: Optional[list[worlds.World]] = None) -> None:
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
            sub_world = self.get_exact_world(sub_world_obj.world_info)
            self.recursion_rules(sub_world, rule_list, passed)
    def update_rules(self, old_prop_dict: dict[uuid.UUID, objects.Properties]) -> None:
        self.game_properties = objects.Properties()
        self.properties = objects.Properties()
        self.special_operator_properties = {o: objects.Properties() for o in objects.special_operators}
        for world in self.world_list:
            world.properties[objects.World] = objects.Properties()
            world.properties[objects.Clone] = objects.Properties()
            world.special_operator_properties[objects.World] = {o: objects.Properties() for o in objects.special_operators}
            world.special_operator_properties[objects.Clone] = {o: objects.Properties() for o in objects.special_operators}
            for obj in world.object_list:
                obj.properties = objects.Properties()
                obj.special_operator_properties = {o: objects.Properties() for o in objects.special_operators}
        for world in self.world_list:
            world.rule_list = world.get_rules()
        for world in self.world_list:
            self.recursion_rules(world)
        new_prop_list: list[tuple[objects.BmpObject, tuple[type[objects.Text], int]]] = []
        for world in self.world_list:
            for rule in world.rule_list + self.rule_list:
                for atom_rule in rules.to_atom_rules(rule):
                    for rule_info in rules.analysis_rule(atom_rule):
                        prefix_info_list = rule_info.prefix_info_list
                        noun_negated_tier = rule_info.noun_negated_tier
                        noun_type = rule_info.noun_type
                        infix_info_list = rule_info.infix_info_list
                        oper_type = rule_info.oper_type
                        prop_negated_tier = rule_info.prop_negated_tier
                        prop_type = rule_info.prop_type
                        if oper_type != objects.TextIs:
                            continue
                        if prop_type != objects.TextWord:
                            continue
                        obj_type = noun_type.obj_type
                        if obj_type == objects.All:
                            if noun_negated_tier % 2 == 1:
                                for obj in [o for o in world.object_list if isinstance(o, objects.in_not_all)]:
                                    if self.meet_infix_conditions(world, obj, infix_info_list, old_prop_dict.get(obj.uuid)) and self.meet_prefix_conditions(world, obj, prefix_info_list):
                                        new_prop_list.append((obj, (objects.TextWord, prop_negated_tier)))
                            else:
                                for obj in [o for o in world.object_list if not isinstance(o, objects.not_in_all)]:
                                    if self.meet_infix_conditions(world, obj, infix_info_list, old_prop_dict.get(obj.uuid)) and self.meet_prefix_conditions(world, obj, prefix_info_list):
                                        new_prop_list.append((obj, (objects.TextWord, prop_negated_tier)))
                        else:
                            if noun_negated_tier % 2 == 1:
                                for obj in [o for o in world.object_list if (not isinstance(o, objects.not_in_all)) and not isinstance(o, obj_type)]:
                                    if self.meet_infix_conditions(world, obj, infix_info_list, old_prop_dict.get(obj.uuid)) and self.meet_prefix_conditions(world, obj, prefix_info_list):
                                        new_prop_list.append((obj, (objects.TextWord, prop_negated_tier)))
                            else:
                                for obj in world.get_objs_from_type(obj_type):
                                    if self.meet_infix_conditions(world, obj, infix_info_list, old_prop_dict.get(obj.uuid)) and self.meet_prefix_conditions(world, obj, prefix_info_list):
                                        new_prop_list.append((obj, (objects.TextWord, prop_negated_tier)))
        for obj, prop in new_prop_list:
            prop_type, prop_negated_count = prop
            obj.properties.update(prop_type, prop_negated_count)
        for world in self.world_list:
            world.properties[objects.World] = objects.Properties()
            world.properties[objects.Clone] = objects.Properties()
            world.special_operator_properties[objects.World] = {o: objects.Properties() for o in objects.special_operators}
            world.special_operator_properties[objects.Clone] = {o: objects.Properties() for o in objects.special_operators}
            for obj in world.object_list:
                obj.properties = objects.Properties()
                obj.special_operator_properties = {o: objects.Properties() for o in objects.special_operators}
        for world in self.world_list:
            world.rule_list = world.get_rules()
        for world in self.world_list:
            self.recursion_rules(world)
        new_prop_list = []
        for world in self.world_list:
            for rule in world.rule_list + self.rule_list:
                for atom_rule in rules.to_atom_rules(rule):
                    for rule_info in rules.analysis_rule(atom_rule):
                        prefix_info_list = rule_info.prefix_info_list
                        noun_negated_tier = rule_info.noun_negated_tier
                        noun_type = rule_info.noun_type
                        infix_info_list = rule_info.infix_info_list
                        oper_type = rule_info.oper_type
                        prop_negated_tier = rule_info.prop_negated_tier
                        prop_type = rule_info.prop_type
                        obj_type = noun_type.obj_type
                        if obj_type == objects.All:
                            if noun_negated_tier % 2 == 1:
                                obj_list = [o for o in world.object_list if isinstance(o, objects.in_not_all)]
                            else:
                                obj_list = [o for o in world.object_list if not isinstance(o, objects.not_in_all)]
                            for obj in obj_list:
                                if self.meet_infix_conditions(world, obj, infix_info_list, old_prop_dict.get(obj.uuid)) and self.meet_prefix_conditions(world, obj, prefix_info_list):
                                    if oper_type == objects.TextIs:
                                        new_prop_list.append((obj, (prop_type, prop_negated_tier)))
                                    else:
                                        obj.special_operator_properties[oper_type].update(prop_type, prop_negated_tier)
                        elif obj_type == objects.Game and oper_type == objects.TextIs:
                            if noun_negated_tier % 2 == 0 and len(infix_info_list) == 0 and self.meet_prefix_conditions(world, objects.BmpObject((0, 0)), prefix_info_list, True):
                                self.game_properties.update(prop_type, prop_negated_tier)
                        elif obj_type == objects.Level:
                            if noun_negated_tier % 2 == 0 and len(infix_info_list) == 0 and self.meet_prefix_conditions(world, objects.BmpObject((0, 0)), prefix_info_list, True):
                                if oper_type == objects.TextIs:
                                    self.properties.update(prop_type, prop_negated_tier)
                                else:
                                    self.special_operator_properties[oper_type].update(prop_type, prop_negated_tier)
                        elif obj_type == objects.World:
                            if noun_negated_tier % 2 == 0 and len(infix_info_list) == 0 and self.meet_prefix_conditions(world, objects.BmpObject((0, 0)), prefix_info_list, True):
                                if oper_type == objects.TextIs:
                                    world.properties[objects.World].update(prop_type, prop_negated_tier)
                                else:
                                    world.special_operator_properties[objects.World][oper_type].update(prop_type, prop_negated_tier)
                        elif obj_type == objects.Clone:
                            if noun_negated_tier % 2 == 0 and len(infix_info_list) == 0 and self.meet_prefix_conditions(world, objects.BmpObject((0, 0)), prefix_info_list, True):
                                if oper_type == objects.TextIs:
                                    world.properties[objects.Clone].update(prop_type, prop_negated_tier)
                                else:
                                    world.special_operator_properties[objects.Clone][oper_type].update(prop_type, prop_negated_tier)
                        if noun_negated_tier % 2 == 1:
                            obj_list = [o for o in world.object_list if (not isinstance(o, objects.not_in_all)) and not isinstance(o, obj_type)]
                        else:
                            obj_list = world.get_objs_from_type(obj_type)
                        for obj in obj_list:
                            if self.meet_infix_conditions(world, obj, infix_info_list, old_prop_dict.get(obj.uuid)) and self.meet_prefix_conditions(world, obj, prefix_info_list):
                                if oper_type == objects.TextIs:
                                    new_prop_list.append((obj, (prop_type, prop_negated_tier)))
                                else:
                                    obj.special_operator_properties[oper_type].update(prop_type, prop_negated_tier)
        for obj, prop in new_prop_list:
            prop_type, prop_negated_count = prop
            obj.properties.update(prop_type, prop_negated_count)
    def move_obj_between_worlds(self, old_world: worlds.World, obj: objects.BmpObject, new_world: worlds.World, pos: spaces.Coord) -> None:
        if obj in old_world.object_list:
            old_world.del_obj(obj)
        obj = copy.deepcopy(obj)
        obj.reset_uuid()
        obj.pos = pos
        new_world.new_obj(obj)
    def move_obj_in_world(self, world: worlds.World, obj: objects.BmpObject, pos: spaces.Coord) -> None:
        if obj in world.object_list:
            world.del_obj(obj)
        obj = copy.deepcopy(obj)
        obj.reset_uuid()
        obj.pos = pos
        world.new_obj(obj)
    def destroy_obj(self, world: worlds.World, obj: objects.BmpObject) -> None:
        world.del_obj(obj)
        for new_noun_type, new_noun_count in obj.special_operator_properties[objects.TextHas].enabled_dict().items(): # type: ignore
            new_noun_type: objects.Noun
            if new_noun_type == objects.TextGame:
                if isinstance(obj, (objects.LevelPointer, objects.WorldPointer)):
                    for _ in range(new_noun_count):
                        world.new_obj(objects.Game(obj.pos, obj.orient, obj_type=objects.get_noun_from_type(type(obj))))
                else:
                    for _ in range(new_noun_count):
                        world.new_obj(objects.Game(obj.pos, obj.orient, obj_type=type(obj)))
            elif new_noun_type == objects.TextLevel:
                if obj.level_info is not None:
                    for _ in range(new_noun_count):
                        world.new_obj(objects.Level(obj.pos, obj.orient, world_info=obj.world_info, level_info=obj.level_info))
                else:
                    world_color = colors.to_background_color(displays.sprite_colors[obj.sprite_name])
                    new_world = worlds.World(obj.uuid.hex, (3, 3), 0, world_color)
                    obj.pos = (1, 1)
                    obj.reset_uuid()
                    new_world.new_obj(obj)
                    self.created_levels.append(Level(obj.uuid.hex, [new_world], super_level=self.name, rule_list=self.rule_list))
                    level_info: objects.LevelPointerExtraJson = {"name": obj.uuid.hex, "icon": {"name": obj.sprite_name, "color": displays.sprite_colors[obj.sprite_name]}}
                    for _ in range(new_noun_count):
                        world.new_obj(objects.Level(obj.pos, obj.orient, level_info=level_info))
            elif new_noun_type == objects.TextWorld:
                if obj.world_info is not None:
                    for _ in range(new_noun_count):
                        world.new_obj(objects.World(obj.pos, obj.orient, world_info=obj.world_info, level_info=obj.level_info))
                else:
                    world_color = colors.to_background_color(displays.sprite_colors[obj.sprite_name])
                    new_world = worlds.World(obj.uuid.hex, (3, 3), 0, world_color)
                    obj.pos = (1, 1)
                    obj.reset_uuid()
                    new_world.new_obj(obj)
                    self.set_world(new_world)
                    world_info: objects.WorldPointerExtraJson = {"name": obj.uuid.hex, "infinite_tier": 0}
                    for _ in range(new_noun_count):
                        world.new_obj(objects.World(obj.pos, obj.orient, world_info=world_info))
            elif new_noun_type == objects.TextClone:
                if obj.world_info is not None:
                    for _ in range(new_noun_count):
                        world.new_obj(objects.Clone(obj.pos, obj.orient, world_info=obj.world_info, level_info=obj.level_info))
                else:
                    world_color = colors.to_background_color(displays.sprite_colors[obj.sprite_name])
                    new_world = worlds.World(obj.uuid.hex, (3, 3), 0, world_color)
                    obj.pos = (1, 1)
                    obj.reset_uuid()
                    new_world.new_obj(obj)
                    self.set_world(new_world)
                    world_info: objects.WorldPointerExtraJson = {"name": obj.uuid.hex, "infinite_tier": 0}
                    for _ in range(new_noun_count):
                        world.new_obj(objects.Clone(obj.pos, obj.orient, world_info=world_info))
            elif new_noun_type == objects.TextText:
                new_obj_type = objects.get_noun_from_type(type(obj))
                for _ in range(new_noun_count):
                    world.new_obj(new_obj_type(obj.pos, obj.orient, world_info=obj.world_info, level_info=obj.level_info))
            else:
                new_obj_type = new_noun_type.obj_type
                for _ in range(new_noun_count):
                    world.new_obj(new_obj_type(obj.pos, obj.orient, world_info=obj.world_info, level_info=obj.level_info))
    def get_move_list(self, world: worlds.World, obj: objects.BmpObject, orient: spaces.Orient, pos: Optional[spaces.Coord] = None, pushed: Optional[list[objects.BmpObject]] = None, passed: Optional[list[worlds.World]] = None, transnum: Optional[float] = None, depth: int = 0) -> Optional[list[tuple[objects.BmpObject, worlds.World, spaces.Coord, spaces.Orient]]]:
        if depth > 128:
            return None
        depth += 1
        pushed = pushed[:] if pushed is not None else []
        if obj in pushed:
            return None
        passed = passed[:] if passed is not None else []
        pos = pos if pos is not None else obj.pos
        new_pos = spaces.pos_facing(pos, orient)
        exit_world = False
        exit_list = []
        if world.out_of_range(new_pos) and not obj.properties.disabled(objects.TextLeave):
            exit_world = True
            # infinite exit
            if world in passed:
                super_world_list = self.find_super_worlds({"name": world.name, "infinite_tier": world.infinite_tier + 1})
                for super_world, world_obj in super_world_list:
                    if isinstance(world_obj, objects.World) and not super_world.properties[objects.World].disabled(objects.TextLeave):
                        continue
                    if isinstance(world_obj, objects.Clone) and not super_world.properties[objects.Clone].disabled(objects.TextLeave):
                        continue
                    new_transnum = super_world.transnum_to_bigger_transnum(transnum, world_obj.pos, orient) if transnum is not None else world.pos_to_transnum(obj.pos, orient)
                    new_move_list = self.get_move_list(super_world, obj, orient, world_obj.pos, pushed, passed, new_transnum, depth)
                    if new_move_list is None:
                        exit_world = False
                    else:
                        exit_list.extend(new_move_list)
                if len(super_world_list) == 0:
                    exit_world = False
            # exit
            else:
                inf_super_world_list = self.find_super_worlds({"name": world.name, "infinite_tier": world.infinite_tier})
                for inf_super_world, world_obj in inf_super_world_list:
                    if isinstance(world_obj, objects.World) and not inf_super_world.properties[objects.World].disabled(objects.TextLeave):
                        continue
                    if isinstance(world_obj, objects.Clone) and not inf_super_world.properties[objects.Clone].disabled(objects.TextLeave):
                        continue
                    new_transnum = inf_super_world.transnum_to_bigger_transnum(transnum, world_obj.pos, orient) if transnum is not None else world.pos_to_transnum(obj.pos, orient)
                    passed.append(world)
                    new_move_list = self.get_move_list(inf_super_world, obj, orient, world_obj.pos, pushed, passed, new_transnum, depth)
                    if new_move_list is None:
                        exit_world = False
                    else:
                        exit_list.extend(new_move_list)
                if len(inf_super_world_list) == 0:
                    exit_world = False
        # push
        push_objects = [o for o in world.get_objs_from_pos(new_pos) if o.properties.has(objects.TextPush)]
        objects_that_cant_push: list[objects.BmpObject] = []
        push = False
        push_list = []
        if len(push_objects) != 0 and not world.out_of_range(new_pos):
            push = True
            for push_object in push_objects:
                pushed.append(obj)
                new_move_list = self.get_move_list(world, push_object, orient, pushed=pushed, depth=depth)
                pushed.pop()
                if new_move_list is None:
                    objects_that_cant_push.append(push_object)
                    push = False
                    break
                else:
                    push_list.extend(new_move_list)
            push_list.append((obj, world, new_pos, orient))
        # stop wall & shut door
        not_stop_list = []
        simple = False
        if not world.out_of_range(new_pos):
            stop_objects = [o for o in world.get_objs_from_pos(new_pos) if o.properties.has(objects.TextStop) and not o.properties.has(objects.TextPush)]
            stop_objects.extend(objects_that_cant_push)
            if len(stop_objects) != 0:
                if obj.properties.has(objects.TextOpen):
                    simple = True
                    for stop_object in stop_objects:
                        if not stop_object.properties.has(objects.TextShut):
                            simple = False
                elif obj.properties.has(objects.TextShut):
                    simple = True
                    for stop_object in stop_objects:
                        if not stop_object.properties.has(objects.TextOpen):
                            simple = False
            else:
                simple = True
        if simple:
            not_stop_list.append((obj, world, new_pos, orient))
        # squeeze
        squeeze = False
        squeeze_list = []
        if isinstance(obj, objects.WorldPointer) and obj.properties.has(objects.TextPush) and not world.out_of_range(new_pos):
            sub_world = self.get_world(obj.world_info)
            if sub_world is None:
                pass
            elif isinstance(obj, objects.World) and not sub_world.properties[objects.World].disabled(objects.TextEnter):
                pass
            elif isinstance(obj, objects.Clone) and not sub_world.properties[objects.Clone].disabled(objects.TextEnter):
                pass
            else:
                new_push_objects = list(filter(lambda o: objects.Properties.has(o.properties, objects.TextPush), world.get_objs_from_pos(new_pos)))
                if len(new_push_objects) != 0:
                    squeeze = True
                    temp_stop_object = objects.TextStop(spaces.pos_facing(pos, spaces.swap_orientation(orient)))
                    temp_stop_object.properties.update(objects.TextStop, 0)
                    world.new_obj(temp_stop_object)
                    for new_push_object in new_push_objects:
                        if new_push_object.properties.disabled(objects.TextEnter):
                            squeeze = False
                            break
                        input_pos = sub_world.default_input_position(orient)
                        pushed.append(obj)
                        test_move_list = self.get_move_list(sub_world, new_push_object, spaces.swap_orientation(orient), input_pos, pushed=pushed, depth=depth)
                        pushed.pop()
                        if test_move_list is None:
                            squeeze = False
                            break
                        squeeze_list.extend(test_move_list)
                    if squeeze:
                        squeeze_list.append((obj, world, new_pos, orient))
                    world.del_obj(temp_stop_object)
        enter_world = False
        enter_list = []
        worlds_that_cant_push = [o for o in objects_that_cant_push if isinstance(o, objects.WorldPointer)]
        if len(worlds_that_cant_push) != 0 and (not world.out_of_range(new_pos)) and not obj.properties.disabled(objects.TextEnter):
            enter_world = True
            enter_atleast_one_world = False
            for world_obj in worlds_that_cant_push:
                sub_world = self.get_world(world_obj.world_info)
                if sub_world is None:
                    enter_world = False
                    break
                elif isinstance(world_obj, objects.World) and not sub_world.properties[objects.World].disabled(objects.TextEnter):
                    pass
                elif isinstance(world_obj, objects.Clone) and not sub_world.properties[objects.Clone].disabled(objects.TextEnter):
                    pass
                else:
                    new_move_list = None
                    # infinite enter
                    if sub_world in passed:
                        inf_sub_world = self.get_world({"name": sub_world.name, "infinite_tier": sub_world.infinite_tier - 1})
                        if inf_sub_world is None:
                            enter_world = False
                            break
                        elif isinstance(world_obj, objects.World) and not inf_sub_world.properties[objects.World].disabled(objects.TextEnter):
                            pass
                        elif isinstance(world_obj, objects.Clone) and not inf_sub_world.properties[objects.Clone].disabled(objects.TextEnter):
                            pass
                        else:
                            new_transnum = 0.5
                            input_pos = inf_sub_world.default_input_position(spaces.swap_orientation(orient))
                            passed.append(world)
                            new_move_list = self.get_move_list(inf_sub_world, obj, orient, input_pos, pushed, passed, new_transnum, depth)
                    # enter
                    else:
                        new_transnum = world.transnum_to_smaller_transnum(transnum, world_obj.pos, spaces.swap_orientation(orient)) if transnum is not None else 0.5
                        input_pos = sub_world.transnum_to_pos(transnum, spaces.swap_orientation(orient)) if transnum is not None else sub_world.default_input_position(spaces.swap_orientation(orient))
                        passed.append(world)
                        new_move_list = self.get_move_list(sub_world, obj, orient, input_pos, pushed, passed, new_transnum, depth)
                    if new_move_list is not None:
                        enter_list.extend(new_move_list)
                        enter_atleast_one_world = True
                    else:
                        enter_world = False
                        break
            enter_world &= enter_atleast_one_world
        if exit_world:
            return basics.remove_same_elements(exit_list)
        elif push:
            return basics.remove_same_elements(push_list)
        elif enter_world:
            return basics.remove_same_elements(enter_list)
        elif squeeze:
            return basics.remove_same_elements(squeeze_list)
        elif simple:
            return basics.remove_same_elements(not_stop_list)
        else:
            return None
    def move_objs_from_move_list(self, move_list: list[tuple[objects.BmpObject, worlds.World, spaces.Coord, spaces.Orient]]) -> None:
        move_list = basics.remove_same_elements(move_list)
        for move_obj, new_world, new_pos, new_orient in move_list:
            move_obj.move_number += 1
            for world in self.world_list:
                if move_obj in world.object_list:
                    old_world = world
            if old_world == new_world:
                self.move_obj_in_world(old_world, move_obj, new_pos)
            else:
                self.move_obj_between_worlds(old_world, move_obj, new_world, new_pos)
            move_obj.orient = new_orient
        if len(move_list) != 0 and "move" not in self.sound_events:
            self.sound_events.append("move")
    def you(self, orient: spaces.PlayerOperation) -> bool:
        if orient == spaces.NullOrient.O:
            return False
        pushing_game = False
        finished = False
        for i in range(max_move_count):
            if finished:
                return pushing_game
            move_list = []
            finished = True
            for world in self.world_list:
                you_objs = [o for o in world.object_list if i < o.properties.get(objects.TextYou)]
                if len(you_objs) != 0:
                    finished = False
                for obj in you_objs:
                    obj.orient = orient
                    new_move_list = self.get_move_list(world, obj, obj.orient)
                    if new_move_list is not None:
                        move_list.extend(new_move_list)
                    else:
                        pushing_game = True
            move_list = basics.remove_same_elements(move_list)
            self.move_objs_from_move_list(move_list)
        return pushing_game
    def select(self, orient: spaces.PlayerOperation) -> Optional[str]:
        if orient == spaces.NullOrient.O:
            level_objs: list[objects.LevelPointer] = []
            for world in self.world_list:
                select_objs = [o for o in world.object_list if o.properties.has(objects.TextSelect)]
                for obj in select_objs:
                        level_objs.extend(world.get_levels_from_pos(obj.pos))
            if len(level_objs) != 0:
                self.sound_events.append("level")
                return random.choice(level_objs).level_info["name"]
        else:
            for world in self.world_list:
                select_objs = [o for o in world.object_list if o.properties.has(objects.TextSelect)]
                for obj in select_objs:
                    new_pos = spaces.pos_facing(obj.pos, orient)
                    if not world.out_of_range(new_pos):
                        self.move_obj_in_world(world, obj, new_pos)
            return None
    def move(self) -> bool:
        pushing_game = False
        for world in self.world_list:
            global_move_count = world.properties[objects.World].get(objects.TextMove) + self.properties.get(objects.TextMove)
            for i in range(global_move_count):
                move_list = []
                for obj in world.object_list:
                    if not obj.properties.has(objects.TextFloat):
                        new_move_list = self.get_move_list(world, obj, spaces.Orient.S)
                        if new_move_list is not None:
                            move_list.extend(new_move_list)
                        else:
                            pushing_game = True
                move_list = basics.remove_same_elements(move_list)
                self.move_objs_from_move_list(move_list)
        finished = False
        for i in range(max_move_count):
            if finished:
                return pushing_game
            move_list = []
            finished = True
            for world in self.world_list:
                move_objs = [o for o in world.object_list if i < o.properties.get(objects.TextMove)]
                if len(move_objs) != 0:
                    finished = False
                for obj in move_objs:
                    new_move_list = self.get_move_list(world, obj, obj.orient)
                    if new_move_list is not None:
                        move_list = new_move_list
                    else:
                        obj.orient = spaces.swap_orientation(obj.orient)
                        new_move_list = self.get_move_list(world, obj, obj.orient)
                        if new_move_list is not None:
                            move_list = new_move_list
                        else:
                            pushing_game = True
            move_list = basics.remove_same_elements(move_list)
            self.move_objs_from_move_list(move_list)
        return pushing_game
    def shift(self) -> bool:
        pushing_game = False
        for world in self.world_list:
            global_shift_count = world.properties[objects.World].get(objects.TextShift) + self.properties.get(objects.TextShift)
            for i in range(global_shift_count):
                move_list = []
                for obj in world.object_list:
                    if not obj.properties.has(objects.TextFloat):
                        new_move_list = self.get_move_list(world, obj, spaces.Orient.S)
                        if new_move_list is not None:
                            move_list.extend(new_move_list)
                        else:
                            pushing_game = True
                move_list = basics.remove_same_elements(move_list)
                self.move_objs_from_move_list(move_list)
        finished = False
        for i in range(max_move_count):
            if finished:
                return pushing_game
            move_list = []
            finished = True
            for world in self.world_list:
                shifter_objs = [o for o in world.object_list if i < o.properties.get(objects.TextShift)]
                for shifter_obj in shifter_objs:
                    shifted_objs = [o for o in world.get_objs_from_pos(shifter_obj.pos) if obj != shifter_obj and objects.same_float_prop(obj, shifter_obj)]
                    for obj in shifted_objs:
                        new_move_list = self.get_move_list(world, obj, shifter_obj.orient)
                        if new_move_list is not None:
                            move_list.extend(new_move_list)
                            finished = False
                        else:
                            pushing_game = True
            move_list = basics.remove_same_elements(move_list)
            self.move_objs_from_move_list(move_list)
        return pushing_game
    def tele(self) -> None:
        if self.properties.has(objects.TextTele):
            pass
        for world in self.world_list:
            if world.properties[objects.World].has(objects.TextTele):
                pass
        tele_list: list[tuple[worlds.World, objects.BmpObject, worlds.World, spaces.Coord]] = []
        object_list: list[tuple[worlds.World, objects.BmpObject]] = []
        for world in self.world_list:
            object_list.extend([(world, o) for o in world.object_list])
        tele_objs = [t for t in object_list if t[1].properties.has(objects.TextTele)]
        tele_obj_types: dict[type[objects.BmpObject], list[tuple[worlds.World, objects.BmpObject]]] = {}
        for obj_type in [n.obj_type for n in objects.noun_class_list]:
            for tele_obj in tele_objs:
                if isinstance(tele_obj[1], obj_type):
                    tele_obj_types[obj_type] = tele_obj_types.get(obj_type, []) + [tele_obj]
        for new_tele_objs in tele_obj_types.values():
            if len(new_tele_objs) <= 1:
                continue
            for tele_world, tele_obj in new_tele_objs:
                other_tele_objs = new_tele_objs[:]
                other_tele_objs.remove((tele_world, tele_obj))
                for obj in world.get_objs_from_pos(tele_obj.pos):
                    if obj == tele_obj:
                        continue
                    if objects.same_float_prop(obj, tele_obj):
                        other_tele_world, other_tele_obj = random.choice(other_tele_objs)
                        tele_list.append((world, obj, other_tele_world, other_tele_obj.pos))
        for old_world, obj, new_world, pos in tele_list:
            self.move_obj_between_worlds(old_world, obj, new_world, pos)
        if len(tele_list) != 0:
            self.sound_events.append("tele")
    def sink(self) -> None:
        success = False
        for world in self.world_list:
            delete_list = []
            sink_objs = [o for o in world.object_list if o.properties.has(objects.TextSink)]
            if world.properties[objects.World].has(objects.TextSink) or self.properties.has(objects.TextSink):
                for obj in world.object_list:
                    if not obj.properties.has(objects.TextFloat):
                        delete_list.append(obj)
            for sink_obj in sink_objs:
                for obj in world.get_objs_from_pos(sink_obj.pos):
                    if obj == sink_obj:
                        continue
                    if obj.pos == sink_obj.pos:
                        if objects.same_float_prop(obj, sink_obj):
                            if obj not in delete_list and sink_obj not in delete_list:
                                delete_list.append(obj)
                                delete_list.append(sink_obj)
                                break
            for obj in delete_list:
                self.destroy_obj(world, obj)
            if len(delete_list) != 0:
                success = True
        if success:
            self.sound_events.append("sink")
    def hot_and_melt(self) -> None:
        success = False
        for world in self.world_list:
            delete_list = []
            melt_objs = [o for o in world.object_list if o.properties.has(objects.TextMelt)]
            hot_objs = [o for o in world.object_list if o.properties.has(objects.TextHot)]
            if len(hot_objs) != 0 and (world.properties[objects.World].has(objects.TextMelt) or self.properties.has(objects.TextMelt)):
                for melt_obj in melt_objs:
                    if not melt_obj.properties.has(objects.TextFloat):
                        delete_list.extend(world.object_list)
                continue
            if len(melt_objs) != 0 and (world.properties[objects.World].has(objects.TextHot) or self.properties.has(objects.TextHot)):
                for melt_obj in melt_objs:
                    if not melt_obj.properties.has(objects.TextFloat):
                        delete_list.append(melt_obj)
                continue
            for hot_obj in hot_objs:
                for melt_obj in melt_objs:
                    if hot_obj.pos == melt_obj.pos:
                        if objects.same_float_prop(hot_obj, melt_obj):
                            if melt_obj not in delete_list:
                                delete_list.append(melt_obj)
            for obj in delete_list:
                self.destroy_obj(world, obj)
            if len(delete_list) != 0:
                success = True
        if success:
            self.sound_events.append("melt")
    def defeat(self) -> None:
        success = False
        for world in self.world_list:
            delete_list = []
            you_objs = [o for o in world.object_list if o.properties.has(objects.TextYou)]
            defeat_objs = [o for o in world.object_list if o.properties.has(objects.TextDefeat)]
            if len(defeat_objs) != 0 and (world.properties[objects.World].has(objects.TextYou) or self.properties.has(objects.TextYou)):
                delete_list.extend(world.object_list)
                continue
            for you_obj in you_objs:
                if world.properties[objects.World].has(objects.TextDefeat) or self.properties.has(objects.TextDefeat):
                    if you_obj not in delete_list:
                        delete_list.append(you_obj)
                        continue
                for defeat_obj in defeat_objs:
                    if you_obj.pos == defeat_obj.pos:
                        if objects.same_float_prop(defeat_obj, you_obj):
                            if you_obj not in delete_list:
                                delete_list.append(you_obj)
            for obj in delete_list:
                self.destroy_obj(world, obj)
            if len(delete_list) != 0:
                success = True
        if success:
            self.sound_events.append("defeat")
    def open_and_shut(self) -> None:
        success = False
        for world in self.world_list:
            delete_list = []
            shut_objs = [o for o in world.object_list if o.properties.has(objects.TextShut)]
            open_objs = [o for o in world.object_list if o.properties.has(objects.TextOpen)]
            if len(open_objs) != 0 and (world.properties[objects.World].has(objects.TextShut) or self.properties.has(objects.TextShut)):
                delete_list.extend(world.object_list)
                continue
            if len(shut_objs) != 0 and (world.properties[objects.World].has(objects.TextOpen) or self.properties.has(objects.TextOpen)):
                delete_list.extend(world.object_list)
                continue
            for open_obj in open_objs:
                for shut_obj in shut_objs:
                    if shut_obj.pos == open_obj.pos:
                        if shut_obj not in delete_list and open_obj not in delete_list:
                            delete_list.append(shut_obj)
                            if shut_obj != open_obj:
                                delete_list.append(open_obj)
                            break
            for obj in delete_list:
                self.destroy_obj(world, obj)
            if len(delete_list) != 0:
                success = True
        if success:
            self.sound_events.append("open")
    def make(self) -> None:
        for world in self.world_list:
            for obj in world.object_list:
                for make_noun_type, make_noun_count in obj.special_operator_properties[objects.TextMake].enabled_dict().items(): # type: ignore
                    make_noun_type: type[objects.Noun]
                    if make_noun_type == objects.TextGame:
                        if isinstance(obj, (objects.LevelPointer, objects.WorldPointer)):
                            for _ in range(make_noun_count):
                                world.new_obj(objects.Game(obj.pos, obj.orient, obj_type=objects.get_noun_from_type(type(obj))))
                        else:
                            for _ in range(make_noun_count):
                                world.new_obj(objects.Game(obj.pos, obj.orient, obj_type=type(obj)))
                    elif make_noun_type == objects.TextLevel:
                        if len(world.get_objs_from_pos_and_type(obj.pos, objects.Level)) != 0:
                            pass
                        elif obj.level_info is not None:
                            for _ in range(make_noun_count):
                                world.new_obj(objects.Level(obj.pos, obj.orient, world_info=obj.world_info, level_info=obj.level_info))
                        else:
                            world_color = colors.to_background_color(displays.sprite_colors[obj.sprite_name])
                            new_world = worlds.World(obj.uuid.hex, (3, 3), 0, world_color)
                            new_obj = copy.deepcopy(obj)
                            new_obj.pos = (1, 1)
                            new_obj.reset_uuid()
                            new_world.new_obj(new_obj)
                            self.created_levels.append(Level(obj.uuid.hex, [new_world], super_level=self.name, rule_list=self.rule_list))
                            level_info: objects.LevelPointerExtraJson = {"name": obj.uuid.hex, "icon": {"name": obj.sprite_name, "color": displays.sprite_colors[obj.sprite_name]}}
                            for _ in range(make_noun_count):
                                world.new_obj(objects.Level(obj.pos, obj.orient, world_info=obj.world_info, level_info=level_info))
                    elif make_noun_type == objects.TextWorld:
                        if len(world.get_objs_from_pos_and_type(obj.pos, objects.World)) != 0:
                            pass
                        if obj.world_info is not None:
                            for _ in range(make_noun_count):
                                world.new_obj(objects.World(obj.pos, obj.orient, world_info=obj.world_info, level_info=obj.level_info))
                        else:
                            world_color = colors.to_background_color(displays.sprite_colors[obj.sprite_name])
                            new_world = worlds.World(obj.uuid.hex, (3, 3), 0, world_color)
                            new_obj = copy.deepcopy(obj)
                            new_obj.pos = (1, 1)
                            new_obj.reset_uuid()
                            new_world.new_obj(new_obj)
                            self.set_world(new_world)
                            world_info: objects.WorldPointerExtraJson = {"name": obj.uuid.hex, "infinite_tier": 0}
                            for _ in range(make_noun_count):
                                world.new_obj(objects.World(obj.pos, obj.orient, world_info=world_info, level_info=obj.level_info))
                    elif make_noun_type == objects.TextClone:
                        if len(world.get_objs_from_pos_and_type(obj.pos, objects.Clone)) != 0:
                            pass
                        if obj.world_info is not None:
                            for _ in range(make_noun_count):
                                world.new_obj(objects.Clone(obj.pos, obj.orient, world_info=obj.world_info, level_info=obj.level_info))
                        else:
                            world_color = colors.to_background_color(displays.sprite_colors[obj.sprite_name])
                            new_world = worlds.World(obj.uuid.hex, (3, 3), 0, world_color)
                            new_obj = copy.deepcopy(obj)
                            new_obj.pos = (1, 1)
                            new_obj.reset_uuid()
                            new_world.new_obj(new_obj)
                            self.set_world(new_world)
                            world_info: objects.WorldPointerExtraJson = {"name": obj.uuid.hex, "infinite_tier": 0}
                            for _ in range(make_noun_count):
                                world.new_obj(objects.Clone(obj.pos, obj.orient, world_info=world_info, level_info=obj.level_info))
                    elif make_noun_type == objects.TextText:
                        make_obj_type = objects.get_noun_from_type(type(obj))
                        if len(world.get_objs_from_pos_and_type(obj.pos, make_obj_type)) != 0:
                            pass
                        for _ in range(make_noun_count):
                            world.new_obj(make_obj_type(obj.pos, obj.orient, world_info=obj.world_info, level_info=obj.level_info))
                    else:
                        make_obj_type = make_noun_type.obj_type
                        if len(world.get_objs_from_pos_and_type(obj.pos, make_obj_type)) != 0:
                            pass
                        for _ in range(make_noun_count):
                            world.new_obj(make_obj_type(obj.pos, obj.orient, world_info=obj.world_info, level_info=obj.level_info))
    def text_plus_and_text_minus(self) -> None:
        for world in self.world_list:
            delete_list = []
            text_plus_objs = [o for o in world.object_list if o.properties.has(objects.TextTextPlus)]
            text_minus_objs = [o for o in world.object_list if o.properties.has(objects.TextTextMinus)]
            for text_plus_obj in text_plus_objs:
                if text_plus_obj in text_minus_objs:
                    continue
                new_type = objects.get_noun_from_type(type(text_plus_obj))
                if new_type != objects.TextText:
                    delete_list.append(text_plus_obj)
                    world.new_obj(new_type(text_plus_obj.pos, text_plus_obj.orient, world_info=text_plus_obj.world_info, level_info=text_plus_obj.level_info))
            for text_minus_obj in text_minus_objs:
                if text_minus_obj in text_plus_objs:
                    continue
                if not isinstance(text_minus_obj, objects.Noun):
                    continue
                new_type = text_minus_obj.obj_type
                if new_type == objects.Text:
                    continue
                delete_list.append(text_minus_obj)
                if issubclass(new_type, objects.Game):
                    world.new_obj(objects.Game(text_minus_obj.pos, text_minus_obj.orient, obj_type=objects.TextGame))
                elif issubclass(new_type, objects.LevelPointer):
                    if text_minus_obj.level_info is not None:
                        world.new_obj(objects.Level(text_minus_obj.pos, text_minus_obj.orient, world_info=text_minus_obj.world_info, level_info=text_minus_obj.level_info))
                    else:
                        world_color = colors.to_background_color(displays.sprite_colors[text_minus_obj.sprite_name])
                        new_world = worlds.World(text_minus_obj.uuid.hex, (3, 3), 0, world_color)
                        self.created_levels.append(Level(text_minus_obj.uuid.hex, [new_world], super_level=self.name, rule_list=self.rule_list))
                        new_world.new_obj(type(text_minus_obj)((1, 1), text_minus_obj.orient))
                        level_info: objects.LevelPointerExtraJson = {"name": text_minus_obj.uuid.hex, "icon": {"name": text_minus_obj.sprite_name, "color": displays.sprite_colors[text_minus_obj.sprite_name]}}
                        new_obj = objects.Level(text_minus_obj.pos, text_minus_obj.orient, level_info=level_info)
                        world.new_obj(new_obj)
                elif issubclass(new_type, objects.WorldPointer):
                    if text_minus_obj.world_info is not None:
                        world.new_obj(new_type(text_minus_obj.pos, text_minus_obj.orient, world_info=text_minus_obj.world_info, level_info=text_minus_obj.level_info))
                    else:
                        world_color = colors.to_background_color(displays.sprite_colors[text_minus_obj.sprite_name])
                        new_world = worlds.World(text_minus_obj.uuid.hex, (3, 3), 0, world_color)
                        new_world.new_obj(type(text_minus_obj)((1, 1), text_minus_obj.orient))
                        self.set_world(new_world)
                        world_info: objects.WorldPointerExtraJson = {"name": text_minus_obj.uuid.hex, "infinite_tier": 0}
                        new_obj = new_type(text_minus_obj.pos, text_minus_obj.orient, world_info=world_info)
                        world.new_obj(new_obj)
                else:
                    world.new_obj(new_type(text_minus_obj.pos, text_minus_obj.orient, world_info=text_minus_obj.world_info, level_info=text_minus_obj.level_info))
            for obj in delete_list:
                self.destroy_obj(world, obj)
    def game(self) -> None:
        for world in self.world_list:
            for game_obj in world.get_objs_from_type(objects.Game):
                if basics.current_os == basics.windows:
                    if os.path.exists("submp.exe"):
                        os.system(f"start submp.exe {game_obj.obj_type.json_name}")
                    elif os.path.exists("submp.py"):
                        os.system(f"start /b python submp.py {game_obj.obj_type.json_name}")
                elif basics.current_os == basics.linux:
                    os.system(f"python ./submp.py {game_obj.obj_type.json_name} &")
    def win(self) -> bool:
        for world in self.world_list:
            you_objs = [o for o in world.object_list if o.properties.has(objects.TextYou)]
            win_objs = [o for o in world.object_list if o.properties.has(objects.TextWin)]
            for you_obj in you_objs:
                if world.properties[objects.World].has(objects.TextWin) or self.properties.has(objects.TextWin):
                    if not you_obj.properties.has(objects.TextFloat):
                        self.sound_events.append("win")
                        return True
                for win_obj in win_objs:
                    if you_obj.pos == win_obj.pos:
                        if objects.same_float_prop(you_obj, win_obj):
                            self.sound_events.append("win")
                            return True
        return False
    def end(self) -> bool:
        for world in self.world_list:
            you_objs = [o for o in world.object_list if o.properties.has(objects.TextYou)]
            end_objs = [o for o in world.object_list if o.properties.has(objects.TextEnd)]
            for you_obj in you_objs:
                if world.properties[objects.World].has(objects.TextEnd) or self.properties.has(objects.TextEnd):
                    if not you_obj.properties.has(objects.TextFloat):
                        self.sound_events.append("end")
                        return True
                for end_obj in end_objs:
                    if you_obj.pos == end_obj.pos:
                        if objects.same_float_prop(you_obj, end_obj):
                            self.sound_events.append("end")
                            return True
        return False
    def done(self) -> None:
        success = False
        for world in self.world_list:
            delete_list = []
            if world.properties[objects.World].has(objects.TextDone) or self.properties.has(objects.TextDone):
                delete_list.extend(world.object_list)
            for obj in world.object_list:
                if obj.properties.has(objects.TextDone):
                    delete_list.append(obj)
            for obj in delete_list:
                world.del_obj(obj)
            if len(delete_list) != 0:
                success = True
        if success:
            self.sound_events.append("done")
    def have_you(self) -> bool:
        for world in self.world_list:
            for obj in world.object_list:
                if obj.properties.has(objects.TextYou):
                    return True
        return False
    def show_world(self, world: worlds.World, frame: int, layer: int = 0, cursor: Optional[spaces.Coord] = None) -> pygame.Surface:
        if layer >= basics.options["world_display_recursion_depth"]:
            return displays.sprites.get("world", 0, frame).copy()
        pixel_sprite_size = displays.sprite_size * displays.pixel_size
        world_surface_size = (world.width * pixel_sprite_size, world.height * pixel_sprite_size)
        world_surface = pygame.Surface(world_surface_size, pygame.SRCALPHA)
        obj_surface_list: list[tuple[spaces.Coord, pygame.Surface, objects.BmpObject]] = []
        for i in range(len(world.object_list)):
            obj = world.object_list[i]
            if isinstance(obj, objects.World):
                obj_world = self.get_world(obj.world_info)
                if obj_world is not None:
                    obj_surface = self.show_world(obj_world, frame, layer + 1)
                    obj_surface = displays.set_surface_color_dark(obj_surface, 0xC0C0C0)
                else:
                    obj_surface = displays.sprites.get("level", 0, frame).copy()
                obj_surface_pos = (obj.x * pixel_sprite_size, obj.y * pixel_sprite_size)
                obj_surface_list.append((obj_surface_pos, obj_surface, obj))
            elif isinstance(obj, objects.Clone):
                obj_world = self.get_world(obj.world_info)
                if obj_world is not None:
                    obj_surface = self.show_world(obj_world, frame, layer + 1)
                    obj_surface = displays.set_surface_color_light(obj_surface, 0x404040)
                else:
                    obj_surface = displays.sprites.get("clone", 0, frame).copy()
                obj_surface_pos = (obj.x * pixel_sprite_size, obj.y * pixel_sprite_size)
                obj_surface_list.append((obj_surface_pos, obj_surface, obj))
            elif isinstance(obj, objects.Level):
                obj_surface = displays.set_surface_color_dark(displays.sprites.get(obj.sprite_name, obj.sprite_state, frame).copy(), obj.level_info["icon"]["color"])
                icon_surface = displays.set_surface_color_light(displays.sprites.get(obj.level_info["icon"]["name"], 0, frame).copy(), 0xFFFFFF)
                icon_surface_pos = ((obj_surface.get_width() - icon_surface.get_width()) // 2,
                                    (obj_surface.get_height() - icon_surface.get_height()) // 2)
                obj_surface.blit(icon_surface, icon_surface_pos)
                obj_surface_pos = (obj.x * pixel_sprite_size, obj.y * pixel_sprite_size)
                obj_surface_list.append((obj_surface_pos, obj_surface, obj))
            elif isinstance(obj, objects.Metatext):
                obj_surface = displays.sprites.get(obj.sprite_name, 0, frame).copy()
                obj_surface = pygame.transform.scale(obj_surface, (displays.sprite_size * len(str(obj.meta_tier)), displays.sprite_size * len(str(obj.meta_tier))))
                tier_surface = pygame.Surface((displays.sprite_size * len(str(obj.meta_tier)), displays.sprite_size), pygame.SRCALPHA)
                tier_surface.fill("#00000000")
                for digit, char in enumerate(str(obj.meta_tier)):
                    tier_surface.blit(displays.sprites.get("text_" + char, 0, frame), (displays.sprite_size * digit, 0))
                tier_surface = displays.set_alpha(tier_surface, 0x80)
                tier_surface_pos = ((obj_surface.get_width() - tier_surface.get_width()) // 2,
                                    (obj_surface.get_height() - tier_surface.get_height()) // 2)
                obj_surface.blit(tier_surface, tier_surface_pos)
                obj_surface_pos = (obj.x * pixel_sprite_size, obj.y * pixel_sprite_size)
                obj_surface_list.append((obj_surface_pos, obj_surface, obj))
            elif isinstance(obj, objects.Cursor):
                obj_surface = displays.sprites.get(obj.sprite_name, obj.sprite_state, frame).copy()
                obj_surface_pos = (obj.x * pixel_sprite_size - (obj_surface.get_width() - displays.sprite_size) * displays.pixel_size // 2,
                                   obj.y * pixel_sprite_size - (obj_surface.get_height() - displays.sprite_size) * displays.pixel_size // 2)
                obj_surface_list.append((obj_surface_pos, obj_surface, obj))
            else:
                obj_surface = displays.sprites.get(obj.sprite_name, obj.sprite_state, frame).copy()
                obj_surface_pos = (obj.x * pixel_sprite_size, obj.y * pixel_sprite_size)
                obj_surface_list.append((obj_surface_pos, obj_surface, obj))
        sorted_obj_surface_list = map(lambda o: list(map(lambda t: isinstance(o[-1], t), displays.order)).index(True), obj_surface_list)
        sorted_obj_surface_list = map(lambda t: t[1], sorted(zip(sorted_obj_surface_list, obj_surface_list), key=lambda t: t[0], reverse=True))
        for pos, surface, obj in sorted_obj_surface_list:
            if isinstance(obj, objects.Cursor):
                world_surface.blit(pygame.transform.scale(surface, (displays.pixel_size * surface.get_width(), displays.pixel_size * surface.get_height())), pos)
            else:
                world_surface.blit(pygame.transform.scale(surface, (pixel_sprite_size, pixel_sprite_size)), pos)
        if cursor is not None:
            surface = displays.sprites.get("cursor", 0, frame).copy()
            pos = (cursor[0] * pixel_sprite_size - (surface.get_width() - displays.sprite_size) * displays.pixel_size // 2,
                   cursor[1] * pixel_sprite_size - (surface.get_height() - displays.sprite_size) * displays.pixel_size // 2)
            world_surface.blit(pygame.transform.scale(surface, (displays.pixel_size * surface.get_width(), displays.pixel_size * surface.get_height())), pos)
        world_background = pygame.Surface(world_surface.get_size(), pygame.SRCALPHA)
        world_background.fill(pygame.Color(*colors.hex_to_rgb(world.color)))
        world_background.blit(world_surface, (0, 0))
        world_surface = world_background
        if world.infinite_tier > 0:
            infinite_surface = displays.sprites.get("text_infinite", 0, frame)
            multi_infinite_surface = pygame.Surface((infinite_surface.get_width(), infinite_surface.get_height() * world.infinite_tier), pygame.SRCALPHA)
            multi_infinite_surface.fill("#00000000")
            for i in range(world.infinite_tier):
                multi_infinite_surface.blit(infinite_surface, (0, i * infinite_surface.get_height()))
            multi_infinite_surface = pygame.transform.scale_by(multi_infinite_surface, world.height * displays.pixel_size / world.infinite_tier)
            multi_infinite_surface = displays.set_alpha(multi_infinite_surface, 0x80)
            world_surface.blit(multi_infinite_surface, ((world_surface.get_width() - multi_infinite_surface.get_width()) // 2, 0))
        elif world.infinite_tier < 0:
            epsilon_surface = displays.sprites.get("text_epsilon", 0, frame)
            multi_epsilon_surface = pygame.Surface((epsilon_surface.get_width(), epsilon_surface.get_height() * -world.infinite_tier), pygame.SRCALPHA)
            multi_epsilon_surface.fill("#00000000")
            for i in range(-world.infinite_tier):
                multi_epsilon_surface.blit(epsilon_surface, (0, i * epsilon_surface.get_height()))
            multi_epsilon_surface = pygame.transform.scale_by(multi_epsilon_surface, world.height * displays.pixel_size / -world.infinite_tier)
            multi_epsilon_surface = displays.set_alpha(multi_epsilon_surface, 0x80)
            world_surface.blit(multi_epsilon_surface, ((world_surface.get_width() - multi_epsilon_surface.get_width()) // 2, 0))
        return world_surface
    def to_json(self) -> LevelJson:
        json_object: LevelJson = {"name": self.name, "world_list": [], "super_level": self.super_level, "is_map": self.is_map, "main_world": {"name": self.main_world_name, "infinite_tier": self.main_world_tier}}
        for world in self.world_list:
            json_object["world_list"].append(world.to_json())
        return json_object

def json_to_level(json_object: LevelJson, ver: Optional[str] = None) -> Level:
    world_list = []
    for world in json_object["world_list"]:
        world_list.append(worlds.json_to_world(world, ver))
    return Level(name=json_object["name"],
                 world_list=world_list,
                 super_level=json_object["super_level"],
                 main_world_name=json_object["main_world"]["name"],
                 main_world_tier=json_object["main_world"]["infinite_tier"],
                 is_map=json_object.get("is_map", False))