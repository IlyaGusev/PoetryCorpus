# -*- coding: utf-8 -*-
# Автор: Гусев Илья
# Описание: Шаблоноы ритма.


class Group:
    def __init__(self, exp, flag):
        self.exp = exp
        self.flag = flag
        self.extended = []

    def __str__(self):
        return self.exp + self.flag + ": " + str(self.extended)

    def __repr__(self):
        return self.__str__()


class Patterns:
    @staticmethod
    def compile_pattern(metre_pattern, l):
        group = Group(metre_pattern, "")
        Patterns.__process_inner(group, l)
        return list(set([st for st in group.extended if len(st) == l]))

    @staticmethod
    def __process_inner(group, l):
        children_groups = Patterns.__find_groups(group.exp)
        if len(children_groups) == 0:
            # Нижний уровень.
            if group.flag == "?":
                group.extended = [group.exp]
            elif group.flag == "*":
                group.extended = [group.exp * i for i in range(1, l // len(group.exp) + 1)]
            else:
                assert(group.flag == "")
                group.extended = [group.exp]
        else:
            for child in children_groups:
                Patterns.__process_inner(child, l)
            group.extended = Patterns.__next(children_groups, 0, "", l)

    @staticmethod
    def __find_groups(expression):
        groups = []
        counter = 0
        begin = -1
        for i in range(len(expression)):
            if expression[i] == "(":
                counter += 1
                if counter == 1:
                    begin = i + 1
            if expression[i] == ")":
                if counter == 1:
                    flag = ""
                    if i + 1 < len(expression) and (expression[i + 1] == "?" or expression[i + 1] == "*"):
                        flag = expression[i + 1]
                    groups.append(Group(expression[begin:i], flag))
                counter -= 1
            assert(counter >= 0)
        assert(counter == 0)
        return groups

    @staticmethod
    def __next(groups, index, pattern, l):
        if len(pattern) > l or index >= len(groups):
            if sum([int(groups[i].flag == "") for i in range(index, len(groups))]) == 0:
                return [pattern, ]
            return []
        result = []
        flag = groups[index].flag
        if flag == "*":
            # Продолжаем все варианты *
            for i in range(len(groups[index].extended)):
                result += Patterns.__next(groups, index, pattern + groups[index].extended[i], l)
            # Пропускаем *
            result += Patterns.__next(groups, index + 1, pattern, l)
        elif flag == "?":
            # Пропускаем ?
            result += Patterns.__next(groups, index + 1, pattern, l)
            # Продолжаем ?
            for st in groups[index].extended:
                result += Patterns.__next(groups, index + 1, pattern + st, l)
        else:
            for st in groups[index].extended:
                result += Patterns.__next(groups, index + 1, pattern + st, l)
        return result
