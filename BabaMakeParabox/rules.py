from BabaMakeParabox import objects

Rule = list[type[objects.Text]]

basic_rule_types = [[objects.Noun, objects.IS, objects.Property],
                    [objects.Noun, objects.IS, objects.Noun]]

def to_atom_rules(rule_list: list[Rule]) -> list[Rule]:
    return_value: list[Rule] = []
    for rule in rule_list:
        raw_and_indexes = list(map(lambda t: issubclass(t, objects.AND), rule))
        and_indexes = []
        for i in range(len(raw_and_indexes)):
            if raw_and_indexes[i] == True:
                and_indexes.append(i)
        oper_index = list(map(lambda t: issubclass(t, objects.Operator), rule)).index(True)
        noun_list: list[list[type[objects.Text]]] = [[]]
        prop_list: list[list[type[objects.Text]]] = [[]]
        first_stage = True
        for i in range(len(rule)):
            if first_stage:
                if i == oper_index:
                    first_stage = False
                elif i in and_indexes:
                    noun_list.append([])
                else:
                    noun_list[-1].append(rule[i])
            else:
                if i in and_indexes:
                    prop_list.append([])
                else:
                    prop_list[-1].append(rule[i])
        oper = [rule[oper_index]]
        for noun in noun_list:
            for prop in prop_list:
                return_value.append(noun + oper + prop)
    return return_value

def analysis_rule(atom_rule: Rule) -> list[tuple[bool, type[objects.Noun], int, type[objects.Text]]]:
    return_value = []
    noun_index = list(map(lambda t: issubclass(t, objects.Noun), atom_rule)).index(True)
    noun_type: type[objects.Noun] = atom_rule[noun_index] # type: ignore
    noun_negated = atom_rule[:noun_index].count(objects.NOT) % 2 == 1
    prop_index = list(map(lambda t: issubclass(t, (objects.Noun, objects.Property)), atom_rule[noun_index + 2:])).index(True)
    prop_type: type[objects.Text] = atom_rule[prop_index + noun_index + 2] # type: ignore
    prop_negated_count = atom_rule[noun_index:].count(objects.NOT)
    return_value.append((noun_negated, noun_type, prop_negated_count, prop_type))
    return return_value

default_rule_list: list[Rule] = []
default_rule_list.append([objects.CURSOR, objects.IS, objects.SELECT])
default_rule_list.append([objects.TEXT, objects.IS, objects.PUSH])
default_rule_list.append([objects.WORLD, objects.IS, objects.PUSH])
default_rule_list.append([objects.CLONE, objects.IS, objects.PUSH])
default_rule_list.append([objects.LEVEL, objects.IS, objects.STOP])

advanced_rule_list: list[Rule] = []
advanced_rule_list.append([objects.BABA, objects.IS, objects.YOU])
advanced_rule_list.append([objects.WALL, objects.IS, objects.STOP])
advanced_rule_list.append([objects.ROCK, objects.IS, objects.PUSH])
advanced_rule_list.append([objects.FLAG, objects.IS, objects.WIN])
advanced_rule_list.extend(default_rule_list)