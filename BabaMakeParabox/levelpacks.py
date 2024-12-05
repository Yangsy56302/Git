import copy
from typing import Any, Optional, TypedDict
import uuid

from BabaMakeParabox import basics, colors, displays, objects, collects, refs, rules, levels, spaces, worlds

class ReturnInfo(TypedDict):
    win: bool
    end: bool
    transform: bool
    game_push: bool
    selected_level: Optional[refs.LevelID]
default_levelpack_info: ReturnInfo = {"win": False, "end": False, "transform": False, "game_push": False, "selected_level": None}

class LevelpackJson(TypedDict):
    ver: str
    name: str
    main_level: refs.LevelIDJson
    collectibles: list[collects.CollectibleJson]
    level_list: list[levels.LevelJson]
    rule_list: list[list[str]]

class Levelpack(object):
    def __init__(self, name: str, level_list: list[levels.Level], main_level_id: Optional[refs.LevelID] = None, collectibles: Optional[set[collects.Collectible]] = None, rule_list: Optional[list[rules.Rule]] = None) -> None:
        self.name: str = name
        self.level_list: list[levels.Level] = list(level_list)
        self.main_level_id: refs.LevelID = main_level_id if main_level_id is not None else self.level_list[0].level_id
        self.collectibles: set[collects.Collectible] = collectibles if collectibles is not None else set()
        self.rule_list: list[rules.Rule] = rule_list if rule_list is not None else rules.default_rule_list
        if rule_list is not None:
            for level in self.level_list:
                level.rule_list.extend(self.rule_list)
                level.rule_list = basics.remove_same_elements(level.rule_list)
    def get_level(self, level_id: refs.LevelID) -> Optional[levels.Level]:
        level = list(filter(lambda l: level_id == l.level_id, self.level_list))
        return level[0] if len(level) != 0 else None
    def get_exact_level(self, level_id: refs.LevelID) -> levels.Level:
        level = list(filter(lambda l: level_id == l.level_id, self.level_list))
        return level[0]
    def set_level(self, level: levels.Level) -> None:
        for i in range(len(self.level_list)):
            if level == self.level_list[i]:
                self.level_list[i] = level
                return
        self.level_list.append(level)
    def transform(self, active_level: levels.Level) -> None:
        for world in active_level.world_list:
            delete_object_list = []
            for old_obj in world.object_list:
                old_type = type(old_obj)
                new_types = []
                for noun, count in old_obj.properties.enabled_dict().items():
                    if issubclass(noun, objects.Noun):
                        new_types.extend([noun.ref_type] * count)
                not_new_types = []
                for noun, count in old_obj.properties.disabled_dict().items():
                    if issubclass(noun, objects.Noun):
                        not_new_types.extend([noun.ref_type] * count)
                transform_success = False
                old_type_is_old_type = False
                old_type_is_not_old_type = False
                for new_type in new_types:
                    if isinstance(old_obj, new_type):
                        old_type_is_old_type = True
                for not_new_type in not_new_types:
                    if isinstance(old_obj, not_new_type):
                        old_type_is_not_old_type = True
                if old_type_is_not_old_type:
                    transform_success = True
                if not old_type_is_old_type:
                    if objects.All in new_types:
                        new_types.remove(objects.All)
                        all_nouns = [t for t in active_level.all_list if t not in not_new_types]
                        new_types.extend([t.ref_type for t in all_nouns])
                    for new_text_type, new_text_count in old_obj.special_operator_properties[objects.TextWrite].enabled_dict().items():
                        for _ in range(new_text_count):
                            new_obj = new_text_type(old_obj.pos, old_obj.orient, world_id=old_obj.world_id, level_id=old_obj.level_id)
                            world.new_obj(new_obj)
                        transform_success = True
                    for new_type in new_types:
                        if issubclass(new_type, objects.Game):
                            if isinstance(old_obj, (objects.LevelPointer, objects.WorldPointer)):
                                world.new_obj(objects.Game(old_obj.pos, old_obj.orient, ref_type=objects.get_noun_from_type(old_type)))
                            else:
                                world.new_obj(objects.Game(old_obj.pos, old_obj.orient, ref_type=old_type))
                            transform_success = True
                        elif issubclass(new_type, objects.LevelPointer):
                            if isinstance(old_obj, new_type):
                                pass
                            elif isinstance(old_obj, objects.LevelPointer):
                                world.new_obj(new_type(old_obj.pos, old_obj.orient, level_id=old_obj.level_id, level_pointer_extra=old_obj.level_pointer_extra))
                                transform_success = True
                            elif isinstance(old_obj, objects.WorldPointer):
                                level_id: refs.LevelID = refs.LevelID(old_obj.world_id.name)
                                self.set_level(levels.Level(level_id, active_level.world_list, super_level_id=active_level.level_id,
                                                            main_world_id=old_obj.world_id, rule_list=active_level.rule_list))
                                level_pointer_extra: objects.LevelPointerExtra = {"icon": {"name": "world", "color": world.color}}
                                new_obj = new_type(old_obj.pos, old_obj.orient, level_id=level_id, level_pointer_extra=level_pointer_extra)
                                world.new_obj(new_obj)
                                transform_success = True
                            elif old_obj.level_id is not None:
                                world.new_obj(new_type(old_obj.pos, old_obj.orient, level_id=old_obj.level_id))
                                transform_success = True
                            else:
                                world_id: refs.WorldID = refs.WorldID(old_obj.uuid.hex)
                                world_color = colors.to_background_color(old_obj.sprite_color)
                                new_world = worlds.World(world_id, spaces.Coord(3, 3), world_color)
                                level_id: refs.LevelID = refs.LevelID(old_obj.uuid.hex)
                                self.set_level(levels.Level(level_id, [new_world], super_level_id=active_level.level_id, rule_list=active_level.rule_list))
                                new_world.new_obj(old_type(spaces.Coord(1, 1)))
                                level_pointer_extra: objects.LevelPointerExtra = {"icon": {"name": old_obj.sprite_name, "color": old_obj.sprite_color}}
                                new_obj = new_type(old_obj.pos, old_obj.orient, level_id=level_id)
                                world.new_obj(new_obj)
                                transform_success = True
                        elif issubclass(new_type, objects.WorldPointer):
                            if isinstance(old_obj, new_type):
                                pass
                            elif isinstance(old_obj, objects.WorldPointer):
                                world.new_obj(new_type(old_obj.pos, old_obj.orient, world_id=old_obj.world_id, world_pointer_extra=old_obj.world_pointer_extra))
                                transform_success = True
                            elif isinstance(old_obj, objects.LevelPointer):
                                new_level = self.get_exact_level(old_obj.level_id)
                                for temp_world in new_level.world_list:
                                    active_level.set_world(temp_world)
                                world.new_obj(new_type(old_obj.pos, old_obj.orient, world_id=new_level.main_world_id))
                                transform_success = True
                            elif old_obj.world_id is not None:
                                world.new_obj(new_type(old_obj.pos, old_obj.orient, world_id=old_obj.world_id))
                                transform_success = True
                            else:
                                world_id: refs.WorldID = refs.WorldID(old_obj.uuid.hex)
                                world_color = colors.to_background_color(old_obj.sprite_color)
                                new_world = worlds.World(world_id, spaces.Coord(3, 3), world_color)
                                new_world.new_obj(old_type(spaces.Coord(1, 1), old_obj.orient))
                                active_level.set_world(new_world)
                                world.new_obj(new_type(old_obj.pos, old_obj.orient, world_id=world_id))
                                transform_success = True
                        elif new_type == objects.Text:
                            if not isinstance(old_obj, objects.Text):
                                transform_success = True
                                new_obj = objects.get_noun_from_type(old_type)(old_obj.pos, old_obj.orient, world_id=old_obj.world_id, level_id=old_obj.level_id)
                                world.new_obj(new_obj)
                        else:
                            transform_success = True
                            new_obj = new_type(old_obj.pos, old_obj.orient, world_id=old_obj.world_id, level_id=old_obj.level_id)
                            world.new_obj(new_obj)
                if transform_success:
                    delete_object_list.append(old_obj)
            for delete_obj in delete_object_list: 
                world.del_obj(delete_obj)
    def world_transform(self, active_level: levels.Level) -> None:
        old_obj_list: dict[type[objects.WorldPointer], list[tuple[refs.WorldID, objects.WorldPointer]]]
        new_type_list: dict[type[objects.WorldPointer], list[type[objects.Object]]]
        for world_pointer_type in objects.world_pointers:
            for world in active_level.world_list:
                old_obj_list = {p: [] for p in objects.world_pointers}
                for other_world in active_level.world_list:
                    for old_obj in other_world.get_worlds():
                        if isinstance(old_obj, world_pointer_type) and world.world_id == old_obj.world_id:
                            old_obj_list[type(old_obj)].append((other_world.world_id, old_obj))
                new_type_list = {p: [] for p in objects.world_pointers}
                for prop_type, prop_count in world.properties[world_pointer_type].enabled_dict().items():
                    if not issubclass(prop_type, objects.Noun):
                        continue
                    if issubclass(prop_type, objects.TextAll):
                        new_type_list[world_pointer_type].extend(objects.in_not_all * prop_count)
                    else:
                        new_type_list[world_pointer_type].extend([prop_type.ref_type] * prop_count)
                for new_text_type, new_text_count in world.special_operator_properties[world_pointer_type][objects.TextWrite].enabled_dict().items():
                    new_type_list[world_pointer_type].extend([new_text_type] * new_text_count)
                for old_world_id, old_obj in old_obj_list[world_pointer_type]:
                    old_world = active_level.get_exact_world(old_world_id)
                    object_transform_success = True
                    for new_type in new_type_list[world_pointer_type]:
                        if issubclass(world_pointer_type, new_type):
                            object_transform_success = False
                            break
                        elif issubclass(new_type, objects.WorldPointer):
                            new_obj = new_type(old_obj.pos, old_obj.orient, world_id=old_obj.world_id, world_pointer_extra=old_obj.world_pointer_extra)
                        elif issubclass(new_type, objects.LevelPointer):
                            new_level_id = refs.LevelID(old_obj.world_id.name)
                            new_level_pointer_extra = objects.LevelPointerExtra(icon=objects.LevelPointerIcon(
                                name=objects.get_noun_from_type(world_pointer_type).json_name, color=active_level.get_exact_world(old_obj.world_id).color
                            ))
                            self.set_level(levels.Level(new_level_id, active_level.world_list, super_level_id=active_level.level_id, main_world_id=old_obj.world_id))
                            new_obj = new_type(old_obj.pos, old_obj.orient, level_id=new_level_id, level_pointer_extra=new_level_pointer_extra)
                        elif issubclass(new_type, objects.Game):
                            new_obj = objects.Game(old_obj.pos, old_obj.orient, ref_type=objects.get_noun_from_type(world_pointer_type))
                        elif issubclass(new_type, objects.Text):
                            new_obj = objects.get_noun_from_type(world_pointer_type)(old_obj.pos, old_obj.orient, world_id=old_obj.world_id)
                        else:
                            new_obj = new_type(old_obj.pos, old_obj.orient, world_id=old_obj.world_id)
                        old_world.new_obj(new_obj)
                    if object_transform_success and len(new_type_list[world_pointer_type]) != 0:
                        old_world.del_obj(old_obj)
    def level_transform(self, active_level: levels.Level) -> bool:
        old_obj_list: dict[type[objects.LevelPointer], list[tuple[refs.LevelID, refs.WorldID, objects.LevelPointer]]]
        new_type_list: dict[type[objects.LevelPointer], list[type[objects.Object]]]
        transform_success = False
        for level_pointer_type in objects.level_pointers:
            old_obj_list = {p: [] for p in objects.level_pointers}
            for level in self.level_list:
                for other_world in level.world_list:
                    for old_obj in other_world.get_levels():
                        if isinstance(old_obj, level_pointer_type) and active_level.level_id == old_obj.level_id:
                            old_obj_list[type(old_obj)].append((level.level_id, other_world.world_id, old_obj))
            new_type_list = {p: [] for p in objects.level_pointers}
            for prop_type, prop_count in active_level.properties[level_pointer_type].enabled_dict().items():
                if not issubclass(prop_type, objects.Noun):
                    continue
                if issubclass(prop_type, objects.TextAll):
                    new_type_list[level_pointer_type].extend(objects.in_not_all * prop_count)
                else:
                    new_type_list[level_pointer_type].extend([prop_type.ref_type] * prop_count)
            for new_text_type, new_text_count in active_level.special_operator_properties[level_pointer_type][objects.TextWrite].enabled_dict().items():
                new_type_list[level_pointer_type].extend([new_text_type] * new_text_count)
            for old_level_id, old_world_id, old_obj in old_obj_list[level_pointer_type]:
                old_level = self.get_exact_level(old_level_id)
                old_world = old_level.get_exact_world(old_world_id)
                object_transform_success = True
                for new_type in new_type_list[level_pointer_type]:
                    if issubclass(level_pointer_type, new_type):
                        object_transform_success = False
                        break
                    elif issubclass(new_type, objects.LevelPointer):
                        new_obj = new_type(old_obj.pos, old_obj.orient, level_id=old_obj.level_id, level_pointer_extra=old_obj.level_pointer_extra)
                    elif issubclass(new_type, objects.WorldPointer):
                        for new_world in active_level.world_list:
                            if old_level.get_world(new_world.world_id) is None:
                                old_level.set_world(new_world)
                        new_obj = new_type(old_obj.pos, old_obj.orient, world_id=active_level.main_world_id)
                    elif issubclass(new_type, objects.Game):
                        new_obj = objects.Game(old_obj.pos, old_obj.orient, ref_type=objects.get_noun_from_type(level_pointer_type))
                    elif issubclass(new_type, objects.Text):
                        new_obj = objects.get_noun_from_type(level_pointer_type)(old_obj.pos, old_obj.orient, level_id=active_level.level_id)
                    else:
                        new_obj = new_type(old_obj.pos, old_obj.orient, level_id=active_level.level_id)
                    old_world.new_obj(new_obj)
                if object_transform_success and len(new_type_list[level_pointer_type]) != 0:
                    old_world.del_obj(old_obj)
                    transform_success = True
        return transform_success
    def prepare(self, active_level: levels.Level) -> dict[uuid.UUID, objects.Properties]:
        clear_counts: int = 0
        for sub_level in self.level_list:
            if sub_level.super_level_id == active_level.level_id and sub_level.collected[collects.Spore]:
                clear_counts += 1
                self.collectibles.add(collects.Spore(sub_level.level_id))
        if active_level.map_info is not None and clear_counts >= active_level.map_info["minimum_clear_for_blossom"]:
            active_level.collected[collects.Blossom] = True
        old_prop_dict: dict[uuid.UUID, objects.Properties] = {}
        for world in active_level.world_list:
            for obj in world.object_list:
                old_prop_dict[obj.uuid] = copy.deepcopy(obj.properties)
                obj.move_number = 0
            for path in world.get_objs_from_type(objects.Path):
                unlocked = True
                for bonus_type, bonus_counts in path.conditions.items():
                    if len({c for c in self.collectibles if isinstance(c, bonus_type)}) < bonus_counts:
                        unlocked = False
                path.unlocked = unlocked
        active_level.update_rules(old_prop_dict)
        for world in active_level.world_list:
            for obj in world.object_list:
                obj.old_state = objects.OldObjectState()
        return old_prop_dict
    def turn(self, active_level: levels.Level, op: spaces.PlayerOperation) -> ReturnInfo:
        old_prop_dict: dict[uuid.UUID, objects.Properties] = self.prepare(active_level)
        active_level.sound_events = []
        active_level.created_levels = []
        game_push = False
        game_push |= active_level.you(op)
        game_push |= active_level.move()
        active_level.update_rules(old_prop_dict)
        game_push |= active_level.shift()
        active_level.update_rules(old_prop_dict)
        self.transform(active_level)
        self.world_transform(active_level)
        transform = self.level_transform(active_level)
        active_level.game()
        active_level.text_plus_and_text_minus()
        active_level.update_rules(old_prop_dict)
        active_level.tele()
        selected_level = active_level.select(op)
        active_level.update_rules(old_prop_dict)
        active_level.done()
        active_level.sink()
        active_level.hot_and_melt()
        active_level.defeat()
        active_level.open_and_shut()
        active_level.update_rules(old_prop_dict)
        active_level.make()
        active_level.update_rules(old_prop_dict)
        for new_level in active_level.created_levels:
            self.set_level(new_level)
        active_level.all_list_set()
        active_level.bonus()
        end = active_level.end()
        win = active_level.win()
        for world in active_level.world_list:
            for path in world.get_objs_from_type(objects.Path):
                unlocked = True
                for bonus_type, bonus_counts in path.conditions.items():
                    if len({c for c in self.collectibles if isinstance(c, bonus_type)}) < bonus_counts:
                        unlocked = False
                path.unlocked = unlocked
        if active_level.collected[collects.Bonus] and win:
            self.collectibles.add(collects.Bonus(active_level.level_id))
        return {"win": win, "end": end, "transform": transform,
                "game_push": game_push, "selected_level": selected_level}
    def to_json(self) -> LevelpackJson:
        json_object: LevelpackJson = {
            "ver": basics.versions,
            "name": self.name,
            "main_level": self.main_level_id.to_json(),
            "collectibles": list(map(collects.Collectible.to_json, self.collectibles)),
            "level_list": list(map(levels.Level.to_json, self.level_list)),
            "rule_list": []
        }
        for rule in self.rule_list:
            json_object["rule_list"].append([])
            for obj in rule:
                json_object["rule_list"][-1].append({v: k for k, v in objects.object_name.items()}[obj])
        return json_object

def json_to_levelpack(json_object: LevelpackJson) -> Levelpack:
    ver = json_object.get("ver")
    reversed_collectible_dict = {v: k for k, v in collects.collectible_dict.items()}
    collectibles: set[collects.Collectible] = set()
    level_list = []
    for level in json_object["level_list"]:
        level_list.append(levels.json_to_level(level, ver))
    rule_list: list[rules.Rule] = []
    for rule in json_object["rule_list"]:
        rule_list.append([])
        for object_type in rule:
            rule_list[-1].append(objects.object_name[object_type]) # type: ignore
    if basics.compare_versions(ver if ver is not None else "0.0", "3.8") == -1:
        main_level_id: refs.LevelID = refs.LevelID(json_object["main_level"]) # type: ignore
    else:
        main_level_id: refs.LevelID = refs.LevelID(**json_object["main_level"])
        for collectible in json_object["collectibles"]:
            collectibles.add(reversed_collectible_dict[collectible["type"]](source=refs.LevelID(collectible["source"]["name"])))
    return Levelpack(name=json_object["name"],
                     main_level_id=main_level_id,
                     level_list=level_list,
                     collectibles=collectibles,
                     rule_list=rule_list)