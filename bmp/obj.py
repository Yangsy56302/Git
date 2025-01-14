from typing import Any, NotRequired, Optional, TypeGuard, TypedDict
import math
import uuid
import bmp.base
import bmp.collect
import bmp.color
import bmp.loc
import bmp.ref

class SpaceObjectExtra(TypedDict):
    static_transform: bmp.loc.SpaceTransform
    dynamic_transform: bmp.loc.SpaceTransform

default_space_extra: SpaceObjectExtra = {
    "static_transform": bmp.loc.default_space_transform.copy(),
    "dynamic_transform": bmp.loc.default_space_transform.copy()
}

class LevelObjectIcon(TypedDict):
    name: str
    color: bmp.color.ColorHex

class LevelObjectExtra(TypedDict):
    icon: LevelObjectIcon

class PathExtra(TypedDict):
    unlocked: bool
    conditions: dict[str, int]

default_level_extra: LevelObjectExtra = {"icon": {"name": "empty", "color": 0xFFFFFF}}

class ObjectJson(TypedDict):
    type: str
    pos: bmp.loc.Coord[int]
    orient: bmp.loc.OrientStr
    space_id: NotRequired[bmp.ref.SpaceIDJson]
    space_extra: NotRequired[SpaceObjectExtra]
    level_id: NotRequired[bmp.ref.LevelIDJson]
    level_extra: NotRequired[LevelObjectExtra]
    path_extra: NotRequired[PathExtra]

PropertiesDict = dict[type["Text"], dict[int, int]]

class Properties(object):
    def __init__(self, prop: Optional[PropertiesDict] = None) -> None:
        self.__dict: PropertiesDict = prop if prop is not None else {}
    def __bool__(self) -> bool:
        return len(self.__dict) != 0
    def __repr__(self) -> str:
        string = ""
        string += "Properties()\n"
        string += "Enabled:\n"
        for prop, count in self.enabled_dict().items():
            string += f"\t{prop.__name__} * {count}\n"
        string += "Disabled:\n"
        for prop, count in self.disabled_dict().items():
            string += f"\t{prop.__name__} * {count}\n"
        return string
    @staticmethod
    def calc_count(negnum_dict: dict[int, int], negated_number: int = 0) -> int:
        if len(negnum_dict) == 0:
            return 0
        if len(negnum_dict) == 1:
            return int(list(negnum_dict.keys())[0] == negated_number)
        negnum_list = []
        for neg, num in negnum_dict.items():
            negnum_list.extend([neg] * num)
        negnum_list.sort(reverse=True)
        current_negnum = negnum_list[0]
        current_count = 0
        for n in negnum_list:
            if n < negated_number:
                break
            elif n == current_negnum:
                current_count += 1
            elif current_negnum - n == 1:
                current_count = min(0, -current_count) + 1
                current_negnum = n
            else:
                current_count = 1
                current_negnum = n
        return max(0, current_count) if current_negnum == negated_number else 0
    def overwrite(self, prop: type["Text"], negated: bool) -> None:
        self.__dict[prop] = {int(negated): 1}
    def update(self, prop: type["Text"], negated_level: int) -> None:
        self.__dict.setdefault(prop, {})
        self.__dict[prop].setdefault(negated_level, 0)
        self.__dict[prop][negated_level] += 1
    def remove(self, prop: type["Text"], *, negated_level: int) -> None:
        self.__dict.setdefault(prop, {})
        self.__dict[prop].setdefault(negated_level, 0)
        self.__dict[prop][negated_level] -= 1
    def exist(self, prop: type["Text"]) -> bool:
        return len(self.__dict.get(prop, {}).items()) != 0
    def get_raw(self, prop: type["Text"], *, negated_number: int = 0) -> int:
        if len(self.__dict.get(prop, {}).items()) == 0:
            return 0
        return self.__dict[prop].get(negated_number, 0)
    def get(self, prop: type["Text"], *, negated_number: int = 0) -> int:
        if len(self.__dict.get(prop, {}).items()) == 0:
            return 0
        return self.calc_count(self.__dict[prop], negated_number)
    def has(self, prop: type["Text"], *, negated_number: int = 0) -> bool:
        if len(self.__dict.get(prop, {}).items()) == 0:
            return False
        if self.calc_count(self.__dict[prop], negated_number) > 0:
            return True
        return False
    def clear(self) -> None:
        self.__dict.clear()
    def enabled(self, prop: type["Text"]) -> bool:
        if self.__dict.get(prop) is None:
            return False
        return self.calc_count(self.__dict[prop], 0) > 0
    def disabled(self, prop: type["Text"]) -> bool:
        if self.__dict.get(prop) is None:
            return False
        return self.calc_count(self.__dict[prop], 1) > 0
    def enabled_dict(self) -> dict[type["Text"], int]:
        return {k: v for k, v in {k: self.calc_count(v, 0) for k, v in self.__dict.items()}.items() if v != 0}
    def disabled_dict(self) -> dict[type["Text"], int]:
        return {k: v for k, v in {k: self.calc_count(v, 1) for k, v in self.__dict.items()}.items() if v != 0}

class OldObjectState(object):
    def __init__(
        self,
        *,
        pos: Optional[bmp.loc.Coord[int]] = None,
        direct: Optional[bmp.loc.Orient] = None,
        space: Optional[bmp.ref.SpaceID] = None,
        level: Optional[bmp.ref.LevelID] = None
    ) -> None:
        self.pos: Optional[bmp.loc.Coord[int]] = pos
        self.direct: Optional[bmp.loc.Orient] = direct
        self.space: Optional[bmp.ref.SpaceID] = space
        self.level: Optional[bmp.ref.LevelID] = level

special_operators: tuple[type["Operator"], ...]

class Object(object):
    ref_type: type["Object"]
    json_name: str
    sprite_name: str
    display_name: str
    sprite_color: bmp.color.PaletteIndex
    sprite_varients: tuple[int, ...] = (0x0, )
    def __init__(
        self,
        pos: bmp.loc.Coord[int],
        direct: bmp.loc.Orient = bmp.loc.Orient.S,
        *,
        space_id: Optional[bmp.ref.SpaceID] = None,
        level_id: Optional[bmp.ref.LevelID] = None
    ) -> None:
        self.uuid: uuid.UUID = uuid.uuid4()
        self.pos: bmp.loc.Coord[int] = pos
        self.orient: bmp.loc.Orient = direct
        self.direct_mapping: dict[bmp.loc.Orient, bmp.loc.Orient] = {d: d for d in bmp.loc.Orient}
        self.old_state: OldObjectState = OldObjectState()
        self.space_id: Optional[bmp.ref.SpaceID] = space_id
        self.level_id: Optional[bmp.ref.LevelID] = level_id
        self.properties: Properties = Properties()
        self.special_operator_properties: dict[type["Operator"], Properties] = {o: Properties() for o in special_operators}
        self.move_number: int = 0
        self.sprite_state: int = 0
    def __eq__(self, obj: "Object") -> bool:
        return self.uuid == obj.uuid
    def __hash__(self) -> int:
        return hash(self.uuid)
    def __repr__(self) -> str:
        string = f"object {self.json_name} at {self.pos} facing {self.orient}"
        return "<" + string + ">"
    @property
    def x(self) -> int:
        return self.pos[0]
    @x.setter
    def x(self, value: int) -> None:
        self.pos = (value, self.pos[1])
    @property
    def y(self) -> int:
        return self.pos[1]
    @y.setter
    def y(self, value: int) -> None:
        self.pos = (self.pos[0], value)
    def reset_uuid(self) -> None:
        self.uuid = uuid.uuid4()
    def set_direct_mapping(self, mapping: dict[bmp.loc.Orient, bmp.loc.Orient]) -> None:
        self.orient = mapping[self.direct_mapping[self.orient]]
        self.direct_mapping = mapping.copy()
    def set_sprite(self, **kwds) -> None:
        self.sprite_state = 0
    def to_json(self) -> ObjectJson:
        json_object: ObjectJson = {"type": self.json_name, "pos": self.pos, "orient": self.orient.name}
        if self.space_id is not None:
            json_object = {**json_object, "space_id": self.space_id.to_json()}
        if self.level_id is not None:
            json_object = {**json_object, "level_id": self.level_id.to_json()}
        return json_object

class NotRealObject(Object):
    pass

Object.ref_type = NotRealObject

class Static(Object):
    sprite_varients: tuple[int, ...] = (0x0, )
    def set_sprite(self, **kwds) -> None:
        self.sprite_state = 0

class Tiled(Object):
    sprite_varients: tuple[int, ...] = tuple(i for i in range(0x10))
    def set_sprite(self, connected: Optional[dict[bmp.loc.Orient, bool]] = None, **kwds) -> None:
        connected = {bmp.loc.Orient.W: False, bmp.loc.Orient.S: False, bmp.loc.Orient.A: False, bmp.loc.Orient.D: False} if connected is None else connected
        self.sprite_state = (connected[bmp.loc.Orient.D] * 0x1) | (connected[bmp.loc.Orient.W] * 0x2) | (connected[bmp.loc.Orient.A] * 0x4) | (connected[bmp.loc.Orient.S] * 0x8)

class Animated(Object):
    sprite_varients: tuple[int, ...] = tuple(i for i in range(0x4))
    def set_sprite(self, round_num: int = 0, **kwds) -> None:
        self.sprite_state = round_num % 0x4

class Directional(Object):
    sprite_varients: tuple[int, ...] = tuple(i * 0x8 for i in range(0x4))
    def set_sprite(self, **kwds) -> None:
        self.sprite_state = int(math.log2(int(self.orient.value))) * 0x8

class AnimatedDirectional(Object):
    sprite_varients: tuple[int, ...] = \
        tuple(i * 0x8 for i in range(0x4)) + \
        tuple(i * 0x8 + 0x1 for i in range(0x4)) + \
        tuple(i * 0x8 + 0x2 for i in range(0x4)) + \
        tuple(i * 0x8 + 0x3 for i in range(0x4))
    def set_sprite(self, round_num: int = 0, **kwds) -> None:
        self.sprite_state = int(math.log2(int(self.orient.value))) * 0x8 | round_num % 4

class Character(Object):
    sprite_varients: tuple[int, ...] = \
        tuple(i * 0x8 for i in range(0x4)) + \
        tuple(i * 0x8 + 0x1 for i in range(0x4)) + \
        tuple(i * 0x8 + 0x2 for i in range(0x4)) + \
        tuple(i * 0x8 + 0x3 for i in range(0x4))
    def set_sprite(self, **kwds) -> None:
        if self.move_number > 0:
            temp_state = (self.sprite_state & 0x3) + 1 if (self.sprite_state & 0x3) != 0x3 else 0x0
            self.sprite_state = int(math.log2(int(self.orient.value))) * 0x8 | temp_state
        else:
            self.sprite_state = int(math.log2(int(self.orient.value))) * 0x8 | (self.sprite_state & 0x3)

class Baba(Character):
    json_name = "baba"
    sprite_name = "baba"
    display_name = "Baba"
    sprite_color: bmp.color.PaletteIndex = (0, 3)

class Keke(Character):
    json_name = "keke"
    sprite_name = "keke"
    display_name = "Keke"
    sprite_color: bmp.color.PaletteIndex = (2, 2)

class Me(Character):
    json_name = "me"
    sprite_name = "me"
    display_name = "Me"
    sprite_color: bmp.color.PaletteIndex = (3, 1)

class Patrick(Directional):
    json_name = "patrick"
    sprite_name = "patrick"
    display_name = "Patrick"
    sprite_color: bmp.color.PaletteIndex = (4, 1)

class Skull(Directional):
    json_name = "skull"
    sprite_name = "skull"
    display_name = "Skull"
    sprite_color: bmp.color.PaletteIndex = (2, 1)

class Ghost(Directional):
    json_name = "ghost"
    sprite_name = "ghost"
    display_name = "Ghost"
    sprite_color: bmp.color.PaletteIndex = (4, 2)

class Wall(Tiled):
    json_name = "wall"
    sprite_name = "wall"
    display_name = "Wall"
    sprite_color: bmp.color.PaletteIndex = (1, 1)

class Hedge(Tiled):
    json_name = "hedge"
    sprite_name = "hedge"
    display_name = "Hedge"
    sprite_color: bmp.color.PaletteIndex = (5, 1)

class Ice(Tiled):
    json_name = "ice"
    sprite_name = "ice"
    display_name = "Ice"
    sprite_color: bmp.color.PaletteIndex = (1, 1)

class Tile(Static):
    json_name = "tile"
    sprite_name = "tile"
    display_name = "Tile"
    sprite_color: bmp.color.PaletteIndex = (0, 0)

class Grass(Tiled):
    json_name = "grass"
    sprite_name = "grass"
    display_name = "Grass"
    sprite_color: bmp.color.PaletteIndex = (5, 0)

class Water(Tiled):
    json_name = "water"
    sprite_name = "water"
    display_name = "Water"
    sprite_color: bmp.color.PaletteIndex = (1, 3)

class Lava(Tiled):
    json_name = "lava"
    sprite_name = "water"
    display_name = "Lava"
    sprite_color: bmp.color.PaletteIndex = (2, 3)

class Door(Static):
    json_name = "door"
    sprite_name = "door"
    display_name = "Door"
    sprite_color: bmp.color.PaletteIndex = (2, 2)

class Key(Static):
    json_name = "key"
    sprite_name = "key"
    display_name = "Key"
    sprite_color: bmp.color.PaletteIndex = (2, 4)

class Box(Static):
    json_name = "box"
    sprite_name = "box"
    display_name = "Box"
    sprite_color: bmp.color.PaletteIndex = (6, 1)

class Rock(Static):
    json_name = "rock"
    sprite_name = "rock"
    display_name = "Rock"
    sprite_color: bmp.color.PaletteIndex = (6, 2)

class Fruit(Static):
    json_name = "fruit"
    sprite_name = "fruit"
    display_name = "Fruit"
    sprite_color: bmp.color.PaletteIndex = (2, 2)

class Belt(AnimatedDirectional):
    json_name = "belt"
    sprite_name = "belt"
    display_name = "Belt"
    sprite_color: bmp.color.PaletteIndex = (1, 1)

class Sun(Static):
    json_name = "sun"
    sprite_name = "sun"
    display_name = "Sun"
    sprite_color: bmp.color.PaletteIndex = (2, 4)

class Moon(Static):
    json_name = "moon"
    sprite_name = "moon"
    display_name = "Moon"
    sprite_color: bmp.color.PaletteIndex = (2, 4)

class Star(Static):
    json_name = "star"
    sprite_name = "star"
    display_name = "Star"
    sprite_color: bmp.color.PaletteIndex = (2, 4)

class What(Static):
    json_name = "what"
    sprite_name = "what"
    display_name = "What"
    sprite_color: bmp.color.PaletteIndex = (0, 3)

class Love(Static):
    json_name = "love"
    sprite_name = "love"
    display_name = "Love"
    sprite_color: bmp.color.PaletteIndex = (4, 2)

class Flag(Static):
    json_name = "flag"
    sprite_name = "flag"
    display_name = "Flag"
    sprite_color: bmp.color.PaletteIndex = (2, 4)

class Line(Tiled):
    json_name = "line"
    sprite_name = "line"
    display_name = "Line"
    sprite_color: bmp.color.PaletteIndex = (0, 3)

class Dot(Static):
    json_name = "dot"
    sprite_name = "dot"
    display_name = "Dot"
    sprite_color: bmp.color.PaletteIndex = (0, 3)

class Orb(Static):
    json_name = "orb"
    sprite_name = "orb"
    display_name = "Orb"
    sprite_color: bmp.color.PaletteIndex = (4, 1)

class Cursor(Static):
    json_name = "cursor"
    sprite_name = "cursor"
    display_name = "Cursor"
    sprite_color: bmp.color.PaletteIndex = (4, 2)

class SpaceObject(Object):
    light_overlay: bmp.color.ColorHex = 0x000000
    dark_overlay: bmp.color.ColorHex = 0xFFFFFF
    def __init__(
        self,
        pos: bmp.loc.Coord[int],
        direct: bmp.loc.Orient = bmp.loc.Orient.S,
        *,
        space_id: bmp.ref.SpaceID,
        level_id: Optional[bmp.ref.LevelID] = None,
        space_extra: SpaceObjectExtra = default_space_extra
    ) -> None:
        self.space_id: bmp.ref.SpaceID
        super().__init__(pos, direct, space_id=space_id, level_id=level_id)
        self.space_extra: SpaceObjectExtra = space_extra.copy()
    def __repr__(self) -> str:
        string = super().__repr__()[1:-1]
        string += f" stand for space {self.space_id!r}"
        return "<" + string + ">"
    def to_json(self) -> ObjectJson:
        return {**super().to_json(), "space_extra": self.space_extra}

class Space(SpaceObject):
    dark_overlay: bmp.color.ColorHex = 0xC0C0C0
    json_name = "space"
    display_name = "Space"
    sprite_color: bmp.color.PaletteIndex = (1, 3)
        
class Clone(SpaceObject):
    light_overlay: bmp.color.ColorHex = 0x404040
    json_name = "clone"
    display_name = "Clone"
    sprite_color: bmp.color.PaletteIndex = (1, 4)

space_object_types: list[type[SpaceObject]] = [Space, Clone]
default_space_object_type: type[SpaceObject] = Space

class LevelObject(Object):
    def __init__(
        self,
        pos: bmp.loc.Coord[int],
        direct: bmp.loc.Orient = bmp.loc.Orient.S,
        *,
        space_id: Optional[bmp.ref.SpaceID] = None,
        level_id: bmp.ref.LevelID,
        level_extra: LevelObjectExtra = default_level_extra
    ) -> None:
        self.level_id: bmp.ref.LevelID
        super().__init__(pos, direct, space_id=space_id, level_id=level_id)
        self.level_extra: LevelObjectExtra = level_extra
    def __repr__(self) -> str:
        string = super().__repr__()[1:-1]
        string += f" stand for level {self.level_id!r}"
        return "<" + string + ">"
    def to_json(self) -> ObjectJson:
        return {**super().to_json(), "level_extra": self.level_extra}

class Level(LevelObject):
    json_name = "level"
    sprite_name = "level"
    display_name = "Level"
    sprite_color: bmp.color.PaletteIndex = (4, 1)

level_object_types: tuple[type[LevelObject], ...] = (Level, )
default_level_object_type: type[LevelObject] = Level

class Path(Tiled):
    json_name = "path"
    sprite_name = "line"
    display_name = "Path"
    sprite_color: bmp.color.PaletteIndex = (0, 2)
    def __init__(
        self,
        pos: bmp.loc.Coord[int],
        direct: bmp.loc.Orient = bmp.loc.Orient.S,
        *,
        space_id: Optional[bmp.ref.SpaceID] = None,
        level_id: Optional[bmp.ref.LevelID] = None,
        unlocked: bool = False,
        conditions: Optional[dict[type[bmp.collect.Collectible], int]] = None
    ) -> None:
        super().__init__(pos, direct, space_id=space_id, level_id=level_id)
        self.unlocked: bool = unlocked
        self.conditions: dict[type[bmp.collect.Collectible], int] = conditions if conditions is not None else {}
    def to_json(self) -> ObjectJson:
        return {**super().to_json(), "path_extra": {"unlocked": self.unlocked, "conditions": {k.json_name: v for k, v in self.conditions.items()}}}

class Game(Object):
    def __init__(
        self,
        pos: bmp.loc.Coord[int],
        direct: bmp.loc.Orient = bmp.loc.Orient.S,
        *,
        space_id: Optional[bmp.ref.SpaceID] = None,
        level_id: Optional[bmp.ref.LevelID] = None,
        ref_type: type[Object]
    ) -> None:
        super().__init__(pos, direct, space_id=space_id, level_id=level_id)
        self.ref_type = ref_type
    json_name = "game"
    display_name = "Game"
    sprite_color: bmp.color.PaletteIndex = (4, 2)

class Text(Object):
    pass

class Noun(Text):
    ref_type: type["Object"]

class GeneralNoun(Noun):
    ref_type: type["Object"]

class Prefix(Text):
    pass

class Infix(Text):
    sprite_color: bmp.color.PaletteIndex = (0, 3)

class Operator(Text):
    sprite_color: bmp.color.PaletteIndex = (0, 3)

class Property(Text):
    pass

class TextBaba(GeneralNoun):
    ref_type = Baba
    sprite_color: bmp.color.PaletteIndex = (4, 1)

class TextKeke(GeneralNoun):
    ref_type = Keke
    
class TextMe(GeneralNoun):
    ref_type = Me

class TextPatrick(GeneralNoun):
    ref_type = Patrick

class TextSkull(GeneralNoun):
    ref_type = Skull

class TextGhost(GeneralNoun):
    ref_type = Ghost

class TextWall(GeneralNoun):
    ref_type = Wall
    sprite_color: bmp.color.PaletteIndex = (0, 1)

class TextHedge(GeneralNoun):
    ref_type = Hedge

class TextIce(GeneralNoun):
    ref_type = Ice
    sprite_color: bmp.color.PaletteIndex = (1, 3)

class TextTile(GeneralNoun):
    ref_type = Tile
    sprite_color: bmp.color.PaletteIndex = (0, 1)

class TextGrass(GeneralNoun):
    ref_type = Grass

class TextWater(GeneralNoun):
    ref_type = Water

class TextLava(GeneralNoun):
    ref_type = Lava
    sprite_name = "text_lava"

class TextDoor(GeneralNoun):
    ref_type = Door

class TextKey(GeneralNoun):
    ref_type = Key

class TextBox(GeneralNoun):
    ref_type = Box

class TextRock(GeneralNoun):
    ref_type = Rock
    sprite_color: bmp.color.PaletteIndex = (6, 1)

class TextFruit(GeneralNoun):
    ref_type = Fruit

class TextBelt(GeneralNoun):
    ref_type = Belt
    sprite_color: bmp.color.PaletteIndex = (1, 3)

class TextSun(GeneralNoun):
    ref_type = Sun

class TextMoon(GeneralNoun):
    ref_type = Moon

class TextStar(GeneralNoun):
    ref_type = Star

class TextWhat(GeneralNoun):
    ref_type = What

class TextLove(GeneralNoun):
    ref_type = Love

class TextFlag(GeneralNoun):
    ref_type = Flag

class TextLine(GeneralNoun):
    ref_type = Line

class TextDot(GeneralNoun):
    ref_type = Dot

class TextCursor(GeneralNoun):
    ref_type = Cursor
    sprite_color: bmp.color.PaletteIndex = (2, 4)

class TextText(GeneralNoun):
    ref_type = Text
    json_name = "text_text"
    sprite_name = "text_text"
    display_name = "TEXT"
    sprite_color: bmp.color.PaletteIndex = (4, 1)

class TextLevelObject(GeneralNoun):
    ref_type = LevelObject

class TextLevel(GeneralNoun):
    ref_type = Level

class TextSpaceObject(GeneralNoun):
    ref_type = SpaceObject

class TextSpace(GeneralNoun):
    ref_type = Space
    sprite_name = "text_space"

class TextClone(GeneralNoun):
    ref_type = Clone
    sprite_name = "text_clone"

class TextPath(GeneralNoun):
    ref_type = Path
    sprite_name = "text_path"

class TextGame(GeneralNoun):
    ref_type = Game
    json_name = "text_game"
    sprite_name = "text_game"
    display_name = "GAME"

class TextOften(Prefix):
    json_name = "text_often"
    sprite_name = "text_often"
    display_name = "OFTEN"
    sprite_color: bmp.color.PaletteIndex = (5, 4)

class TextSeldom(Prefix):
    json_name = "text_seldom"
    sprite_name = "text_seldom"
    display_name = "SELDOM"
    sprite_color: bmp.color.PaletteIndex = (3, 2)

class TextMeta(Prefix):
    json_name = "text_meta"
    sprite_name = "text_meta"
    display_name = "META"
    sprite_color: bmp.color.PaletteIndex = (4, 1)

class TextText_(Text):
    json_name = "text_text_"
    sprite_name = "text_text_underline"
    display_name = "TEXT_"
    sprite_color: bmp.color.PaletteIndex = (4, 0)

class TextOn(Infix):
    json_name = "text_on"
    sprite_name = "text_on"
    display_name = "ON"

class TextNear(Infix):
    json_name = "text_near"
    sprite_name = "text_near"
    display_name = "NEAR"

class TextNextto(Infix):
    json_name = "text_nextto"
    sprite_name = "text_nextto"
    display_name = "NEXTTO"

class TextWithout(Infix):
    json_name = "text_without"
    sprite_name = "text_without"
    display_name = "WITHOUT"

class TextFeeling(Infix):
    json_name = "text_feeling"
    sprite_name = "text_feeling"
    display_name = "FEELING"

class TextIs(Operator):
    json_name = "text_is"
    sprite_name = "text_is"
    display_name = "IS"

class TextHas(Operator):
    json_name = "text_has"
    sprite_name = "text_has"
    display_name = "HAS"

class TextMake(Operator):
    json_name = "text_make"
    sprite_name = "text_make"
    display_name = "MAKE"

class TextWrite(Operator):
    json_name = "text_write"
    sprite_name = "text_write"
    display_name = "WRITE"

special_operators: tuple[type[Operator], ...] = (TextHas, TextMake, TextWrite)

class TextNot(Text):
    json_name = "text_not"
    sprite_name = "text_not"
    display_name = "NOT"
    sprite_color: bmp.color.PaletteIndex = (2, 2)

class TextAnd(Text):
    json_name = "text_and"
    sprite_name = "text_and"
    display_name = "AND"
    sprite_color: bmp.color.PaletteIndex = (0, 3)

class TextYou(Property):
    json_name = "text_you"
    sprite_name = "text_you"
    display_name = "YOU"
    sprite_color: bmp.color.PaletteIndex = (4, 1)

class TextMove(Property):
    json_name = "text_move"
    sprite_name = "text_move"
    display_name = "MOVE"
    sprite_color: bmp.color.PaletteIndex = (5, 4)

class TextStop(Property):
    json_name = "text_stop"
    sprite_name = "text_stop"
    display_name = "STOP"
    sprite_color: bmp.color.PaletteIndex = (5, 1)

class TextPush(Property):
    json_name = "text_push"
    sprite_name = "text_push"
    display_name = "PUSH"
    sprite_color: bmp.color.PaletteIndex = (6, 1)

class TextSink(Property):
    json_name = "text_sink"
    sprite_name = "text_sink"
    display_name = "SINK"
    sprite_color: bmp.color.PaletteIndex = (1, 3)

class TextFloat(Property):
    json_name = "text_float"
    sprite_name = "text_float"
    display_name = "FLOAT"
    sprite_color: bmp.color.PaletteIndex = (1, 4)

class TextOpen(Property):
    json_name = "text_open"
    sprite_name = "text_open"
    display_name = "OPEN"
    sprite_color: bmp.color.PaletteIndex = (2, 4)

class TextShut(Property):
    json_name = "text_shut"
    sprite_name = "text_shut"
    display_name = "SHUT"
    sprite_color: bmp.color.PaletteIndex = (2, 2)

class TextHot(Property):
    json_name = "text_hot"
    sprite_name = "text_hot"
    display_name = "HOT"
    sprite_color: bmp.color.PaletteIndex = (2, 3)

class TextMelt(Property):
    json_name = "text_melt"
    sprite_name = "text_melt"
    display_name = "MELT"
    sprite_color: bmp.color.PaletteIndex = (1, 3)

class TextWin(Property):
    json_name = "text_win"
    sprite_name = "text_win"
    display_name = "WIN"
    sprite_color: bmp.color.PaletteIndex = (2, 4)

class TextDefeat(Property):
    json_name = "text_defeat"
    sprite_name = "text_defeat"
    display_name = "DEFEAT"
    sprite_color: bmp.color.PaletteIndex = (2, 1)

class TextShift(Property):
    json_name = "text_shift"
    sprite_name = "text_shift"
    display_name = "SHIFT"
    sprite_color: bmp.color.PaletteIndex = (1, 3)

class TextTele(Property):
    json_name = "text_tele"
    sprite_name = "text_tele"
    display_name = "TELE"
    sprite_color: bmp.color.PaletteIndex = (1, 4)

class TransformProperty(Property):
    sprite_color: bmp.color.PaletteIndex = (1, 4)

class DirectionalProperty(TransformProperty):
    ref_direct: bmp.loc.Orient
    ref_transform: bmp.loc.SpaceTransform

class DirectFixProperty(DirectionalProperty):
    pass

class TextUp(DirectFixProperty):
    json_name = "text_up"
    sprite_name = "text_up"
    display_name = "UP"
    ref_direct = bmp.loc.Orient.W
    ref_transform = {"direct": ref_direct.name, "flip": False}

class TextDown(DirectFixProperty):
    json_name = "text_down"
    sprite_name = "text_down"
    display_name = "DOWN"
    ref_direct = bmp.loc.Orient.S
    ref_transform = {"direct": ref_direct.name, "flip": False}

class TextLeft(DirectFixProperty):
    json_name = "text_left"
    sprite_name = "text_left"
    display_name = "LEFT"
    ref_direct = bmp.loc.Orient.A
    ref_transform = {"direct": ref_direct.name, "flip": False}

class TextRight(DirectFixProperty):
    json_name = "text_right"
    sprite_name = "text_right"
    display_name = "RIGHT"
    ref_direct = bmp.loc.Orient.D
    ref_transform = {"direct": ref_direct.name, "flip": False}

direct_fix_properties: list[type[DirectFixProperty]] = [TextLeft, TextUp, TextRight, TextDown]

class DirectRotateProperty(DirectionalProperty):
    pass

class TextTurn(DirectRotateProperty):
    json_name = "text_turn"
    sprite_name = "text_turn"
    display_name = "TURN"
    ref_direct = bmp.loc.Orient.A
    ref_transform = {"direct": ref_direct.name, "flip": False}

class TextDeturn(DirectRotateProperty):
    json_name = "text_deturn"
    sprite_name = "text_deturn"
    display_name = "DETURN"
    ref_direct = bmp.loc.Orient.D
    ref_transform = {"direct": ref_direct.name, "flip": False}

direct_rotate_properties: list[type[DirectRotateProperty]] = [TextTurn, TextDeturn]

class DirectMappingProperty(TransformProperty):
    ref_mapping: dict[bmp.loc.Orient, bmp.loc.Orient]
    ref_transform: bmp.loc.SpaceTransform

class TextFlip(DirectMappingProperty):
    json_name = "text_flip"
    sprite_name = "text_flip"
    display_name = "FLIP"
    ref_mapping = {
        bmp.loc.Orient.W: bmp.loc.Orient.W,
        bmp.loc.Orient.S: bmp.loc.Orient.S,
        bmp.loc.Orient.A: bmp.loc.Orient.D,
        bmp.loc.Orient.D: bmp.loc.Orient.A,
    }
    ref_transform = {"direct": "S", "flip": True}

direct_mapping_properties: list[type[DirectMappingProperty]] = [TextFlip]

class TextEnter(Property):
    json_name = "text_enter"
    sprite_name = "text_enter"
    display_name = "ENTER"
    sprite_color: bmp.color.PaletteIndex = (5, 4)
    
class TextLeave(Property):
    json_name = "text_leave"
    sprite_name = "text_leave"
    display_name = "LEAVE"
    sprite_color: bmp.color.PaletteIndex = (2, 2)

class TextBonus(Property):
    json_name = "text_bonus"
    sprite_name = "text_bonus"
    display_name = "BONUS"
    sprite_color: bmp.color.PaletteIndex = (4, 1)

class TextHide(Property):
    json_name = "text_hide"
    sprite_name = "text_hide"
    display_name = "HIDE"
    sprite_color: bmp.color.PaletteIndex = (3, 2)

class TextWord(Property):
    json_name = "text_word"
    sprite_name = "text_word"
    display_name = "WORD"
    sprite_color: bmp.color.PaletteIndex = (0, 3)

class TextSelect(Property):
    json_name = "text_select"
    sprite_name = "text_select"
    display_name = "SELECT"
    sprite_color: bmp.color.PaletteIndex = (2, 4)

class TextTextPlus(Property):
    json_name = "text_text+"
    sprite_name = "text_text_plus"
    display_name = "TEXT+"
    sprite_color: bmp.color.PaletteIndex = (4, 1)

class TextTextMinus(Property):
    json_name = "text_text-"
    sprite_name = "text_text_minus"
    display_name = "TEXT-"
    sprite_color: bmp.color.PaletteIndex = (4, 2)

class TextEnd(Property):
    json_name = "text_end"
    sprite_name = "text_end"
    display_name = "END"
    sprite_color: bmp.color.PaletteIndex = (0, 3)

class TextDone(Property):
    json_name = "text_done"
    sprite_name = "text_done"
    display_name = "DONE"
    sprite_color: bmp.color.PaletteIndex = (0, 3)

class Metatext(GeneralNoun):
    ref_type: type[Text]
    meta_tier: int
    _base_ref_type: type[Text]

class SpecialNoun(Noun):
    ref_type: type[NotRealObject] = NotRealObject
    sprite_color = (0, 3)
    @classmethod
    def isreferenceof(cls, other: Object, **kwds) -> bool:
        raise NotImplementedError()

class FixedNoun(SpecialNoun):
    @classmethod
    def isreferenceof(cls, other: Object, **kwds) -> bool:
        return False

class RangedNoun(SpecialNoun):
    ref_type: tuple[type[Noun], ...]
    @classmethod
    def isreferenceof(cls, other: Object, **kwds) -> bool:
        return any(map(lambda n: isinstance(other, n) if not isinstance(n, SpecialNoun) else n.isreferenceof(other), cls.ref_type))

class TextEmpty(SpecialNoun):
    json_name = "text_empty"
    sprite_name = "text_empty"
    display_name = "EMPTY"

class TextAll(RangedNoun):
    json_name = "text_all"
    sprite_name = "text_all"
    display_name = "ALL"

class GroupNoun(RangedNoun):
    @classmethod
    def isreferenceof(cls, other: Object, **kwds) -> bool:
        return other.properties.enabled(cls)

class TextGroup(GroupNoun):
    json_name = "text_group"
    sprite_name = "text_group"
    display_name = "GROUP"
    sprite_color = (3, 2)

group_noun_types: tuple[type[GroupNoun], ...] = (TextGroup, )

class SpecificSpaceNoun(FixedNoun):
    delta_infinite_tier: int
    @classmethod
    def isreferenceof(cls, other: Object, **kwds) -> TypeGuard[SpaceObject]:
        if isinstance(other, SpaceObject):
            return True
        return False

class TextInfinity(SpecificSpaceNoun):
    json_name = "text_infinity"
    sprite_name = "text_infinity"
    display_name = "INFINITY"
    delta_infinite_tier = 1
    @classmethod
    def isreferenceof(cls, other: SpaceObject, **kwds) -> bool:
        if super().isreferenceof(other):
            if other.space_id.infinite_tier > 0:
                return True
        return False

class TextEpsilon(SpecificSpaceNoun):
    json_name = "text_epsilon"
    sprite_name = "text_epsilon"
    display_name = "EPSILON"
    delta_infinite_tier = -1
    @classmethod
    def isreferenceof(cls, other: SpaceObject, **kwds) -> bool:
        if super().isreferenceof(other):
            if other.space_id.infinite_tier < 0:
                return True
        return False

class TextParabox(RangedNoun):
    ref_type = (TextInfinity, TextEpsilon)
    json_name = "text_parabox"
    sprite_name = "text_parabox"
    display_name = "PARABOX"

SupportsReferenceType = GeneralNoun | RangedNoun
SupportsIsReferenceOf = FixedNoun | RangedNoun

noun_class_list: list[type[Noun]] = [
    TextBaba, TextKeke, TextMe, TextPatrick, TextSkull, TextGhost,
    TextWall, TextHedge, TextIce, TextTile, TextGrass, TextWater, TextLava,
    TextDoor, TextKey, TextBox, TextRock, TextFruit, TextBelt, TextSun, TextMoon, TextStar, TextWhat, TextLove, TextFlag,
    TextLine, TextDot, TextCursor,
    TextText, TextSpace, TextClone, TextLevel, TextPath, TextGame
]

for noun_class in noun_class_list:
    if not hasattr(noun_class, "json_name"):
        setattr(noun_class, "json_name", "text_" + noun_class.ref_type.json_name)
    if not hasattr(noun_class, "sprite_name"):
        setattr(noun_class, "sprite_name", "text_" + noun_class.ref_type.sprite_name)
    if not hasattr(noun_class, "display_name"):
        setattr(noun_class, "display_name", noun_class.ref_type.display_name.upper())
    if not hasattr(noun_class, "sprite_color"):
        setattr(noun_class, "sprite_color", noun_class.ref_type.sprite_color)

special_noun_class_list: list[type[SpecialNoun]] = []
special_noun_class_list.extend([TextAll, TextInfinity, TextEpsilon, TextParabox])

prop_class_list: list[type[Property]] = [
    TextYou, TextMove, TextStop, TextPush,
    TextSink, TextFloat, TextOpen, TextShut, TextHot, TextMelt,
    TextWin, TextDefeat, TextShift, TextTele,
    TextUp, TextDown, TextLeft, TextRight, TextTurn, TextDeturn, TextFlip,
    TextEnter, TextLeave, TextBonus, TextHide, TextWord, TextSelect, TextTextPlus, TextTextMinus, TextEnd, TextDone
]

text_class_list: list[type[Text]] = [
    TextText_, TextOften, TextSeldom, TextMeta,
    TextOn, TextNear, TextNextto, TextWithout, TextFeeling,
    TextIs, TextHas, TextMake, TextWrite,
    TextNot, TextAnd
]
text_class_list.extend(noun_class_list)
text_class_list.extend(special_noun_class_list)
text_class_list.extend(prop_class_list)

object_class_only: list[type[Object]] = [Text, Game]
object_used: list[type[Object]] = text_class_list + [t.ref_type for t in noun_class_list if t.ref_type not in object_class_only]

name_to_class: dict[str, type[Object]] = {t.json_name: t for t in object_used}
name_to_class["world"] = Space
name_to_class["text_world"] = TextSpace

class_to_noun_dict: dict[type[Object], type[Noun]] = {t.ref_type: t for t in noun_class_list if t.ref_type not in object_class_only}
class_to_noun_dict[Game] = TextGame
    
nouns_not_in_all: tuple[type[Noun], ...] = (TextAll, TextText, TextLevelObject, TextSpaceObject, TextGame)
types_not_in_all: tuple[type[Object], ...] = (Text, LevelObject, SpaceObject, Game)
nouns_in_not_all: tuple[type[Noun], ...] = (TextText, )
types_in_not_all: tuple[type[Object], ...] = (Text, )

metatext_class_dict: dict[int, list[type[Metatext]]] = {}
current_metatext_tier: int = bmp.base.options["metatext"]["tier"]

def generate_metatext(T: type[Text]) -> type[Metatext]:
    new_type_name = "Text" + T.__name__
    new_type_tier = new_type_name.count("Text") - (1 if new_type_name[-4:] != "Text" and new_type_name[-5:] != "Text_" else 2)
    new_type_base = T._base_ref_type if issubclass(T, Metatext) else T
    new_type_vars: dict[str, Any] = {
        "json_name": "text_" + T.json_name,
        "sprite_name": T.sprite_name,
        "ref_type": T,
        "_base_ref_type": new_type_base,
        "meta_tier": new_type_tier,
        "display_name": "TEXT_" + T.display_name,
        "sprite_color": T.sprite_color
    }
    new_type: type[Metatext] = type(new_type_name, (Metatext, ), new_type_vars)
    return new_type

def generate_metatext_at_tier(tier: int) -> list[type[Metatext]]:
    global class_to_noun_dict, object_used, name_to_class, noun_class_list, text_class_list
    if metatext_class_dict.get(tier) is not None:
        return metatext_class_dict[tier]
    if tier < 1:
        raise ValueError(str(tier))
    if tier == 1:
        new_metatext_class_list: list[type[Metatext]] = []
        for noun in text_class_list:
            new_metatext_class_list.append(generate_metatext(noun))
        metatext_class_dict[1] = new_metatext_class_list
        for new_type in new_metatext_class_list:
            object_used.append(new_type)
            name_to_class[new_type.json_name] = new_type
            if "world" in new_type.json_name:
                name_to_class[new_type.json_name.replace("world", "space")] = new_type
            noun_class_list.append(new_type)
            text_class_list.append(new_type)
            class_to_noun_dict[new_type.ref_type] = new_type
        return new_metatext_class_list
    old_metatext_class_list = generate_metatext_at_tier(tier - 1)
    new_metatext_class_list: list[type[Metatext]] = []
    for noun in old_metatext_class_list:
        new_metatext_class_list.append(generate_metatext(noun))
    metatext_class_dict[tier] = new_metatext_class_list
    for new_type in new_metatext_class_list:
        object_used.append(new_type)
        name_to_class[new_type.json_name] = new_type
        noun_class_list.append(new_type)
        text_class_list.append(new_type)
        class_to_noun_dict[new_type.ref_type] = new_type
    return new_metatext_class_list

if bmp.base.options["metatext"]["enabled"]:
    generate_metatext_at_tier(bmp.base.options["metatext"]["tier"])
    
def same_float_prop(obj_1: Object, obj_2: Object):
    return not (obj_1.properties.has(TextFloat) ^ obj_2.properties.has(TextFloat))

def get_noun_from_type(object_type: type[Object]) -> type[Noun]:
    global current_metatext_tier
    global class_to_noun_dict, object_used, name_to_class, noun_class_list, text_class_list
    return_value: Optional[type[Noun]] = class_to_noun_dict.get(object_type)
    if return_value is not None:
        return return_value
    for new_object_type, noun_type in class_to_noun_dict.items():
        if object_type == new_object_type:
            return noun_type
        elif object_type.__name__ == new_object_type.__name__:
            return noun_type
        elif issubclass(object_type, new_object_type) and not issubclass(noun_type, TextText):
            return_value = noun_type
    if return_value is None:
        current_metatext_tier += 1
        generate_metatext_at_tier(current_metatext_tier)
        return get_noun_from_type(object_type)
    return return_value

def json_to_object(json_object: ObjectJson, ver: Optional[str] = None) -> Object:
    global current_metatext_tier
    global class_to_noun_dict, object_used, name_to_class, noun_class_list, text_class_list
    space_id: Optional[bmp.ref.SpaceID] = None
    level_id: Optional[bmp.ref.LevelID] = None
    space_extra: Optional[SpaceObjectExtra] = None
    level_extra: Optional[LevelObjectExtra] = None
    org_space_extra: SpaceObjectExtra = default_space_extra
    org_level_extra: LevelObjectExtra = default_level_extra
    if bmp.base.compare_versions(ver if ver is not None else "0.0", "3.8") == -1:
        old_space_id = json_object.get("world")
        if old_space_id is not None:
            space_id = bmp.ref.SpaceID(old_space_id.get("name", ""), old_space_id.get("infinite_tier", 0))
        old_level_id = json_object.get("level")
        if old_level_id is not None:
            level_id = bmp.ref.LevelID(old_level_id.get("name", ""))
            org_level_extra = {"icon": old_level_id.get("icon", default_level_extra["icon"])}
    elif bmp.base.compare_versions(ver if ver is not None else "0.0", "3.91") == -1:
        space_id_json = json_object.get("world_id")
        if space_id_json is not None:
            space_id = bmp.ref.SpaceID(**space_id_json)
        level_id_json = json_object.get("level_id")
        if level_id_json is not None:
            level_id = bmp.ref.LevelID(**level_id_json)
        org_space_extra = json_object.get("world_extra", default_space_extra)
        org_level_extra = json_object.get("level_extra", default_level_extra)
    elif bmp.base.compare_versions(ver if ver is not None else "0.0", "4.001") == -1:
        space_id_json = json_object.get("space_id")
        if space_id_json is not None:
            space_id = bmp.ref.SpaceID(**space_id_json)
        level_id_json = json_object.get("level_id")
        if level_id_json is not None:
            level_id = bmp.ref.LevelID(**level_id_json)
        org_space_extra = json_object.get("space_extra", default_space_extra)
        org_level_extra = json_object.get("level_extra", default_level_extra)
    else:
        space_id_json = json_object.get("space_id")
        if space_id_json is not None:
            space_id = bmp.ref.SpaceID(**space_id_json)
        level_id_json = json_object.get("level_id")
        if level_id_json is not None:
            level_id = bmp.ref.LevelID(**level_id_json)
        org_space_extra = json_object.get("space_extra", default_space_extra)
        org_level_extra = json_object.get("level_extra", default_level_extra)
    space_extra = default_space_extra.copy()
    if org_space_extra is not None:
        space_extra.update(org_space_extra)
    level_extra = default_level_extra.copy()
    if org_level_extra is not None:
        level_extra.update(org_level_extra)
    object_type = name_to_class.get(json_object["type"])
    if bmp.base.compare_versions(ver if ver is not None else "0.0", "4.001") == -1:
        pos: bmp.loc.Coord[int] = (json_object["position"][0], json_object["position"][1]) # type: ignore
        if bmp.base.compare_versions(ver if ver is not None else "0.0", "3.91") == -1:
            direct = bmp.loc.Orient[json_object["orientation"]] # type: ignore
        else:
            direct = bmp.loc.Orient[json_object["direction"]] # type: ignore
    else:
        pos: bmp.loc.Coord[int] = (json_object["pos"][0], json_object["pos"][1])
        direct = bmp.loc.Orient[json_object["orient"]]
    if object_type is None:
        if json_object["type"].startswith("text_text_"):
            current_metatext_tier += 1
            generate_metatext_at_tier(current_metatext_tier)
            return json_to_object(json_object, ver)
        raise ValueError(json_object["type"])
    if issubclass(object_type, LevelObject):
        if level_id is not None:
            return object_type(
                pos=pos,
                direct=direct,
                space_id=space_id,
                level_id=level_id,
                level_extra=level_extra
            )
        raise ValueError(level_id)
    if issubclass(object_type, SpaceObject):
        if space_id is not None:
            return object_type(
                pos=pos,
                direct=direct,
                space_id=space_id,
                level_id=level_id,
                space_extra=space_extra
            )
        raise ValueError(space_id)
    if issubclass(object_type, Path):
        path_extra = json_object.get("path_extra")
        if path_extra is None:
            path_extra = {"unlocked": False, "conditions": {}}
        reversed_collectible_dict = {v: k for k, v in bmp.collect.collectible_dict.items()}
        conditions: dict[type[bmp.collect.Collectible], int] = {reversed_collectible_dict[k]: v for k, v in path_extra["conditions"].items()}
        return object_type(
            pos=pos,
            direct=direct,
            space_id=space_id,
            level_id=level_id,
            unlocked=path_extra["unlocked"],
            conditions=conditions
        )
    return object_type(
        pos=pos,
        direct=direct,
        space_id=space_id,
        level_id=level_id
    )