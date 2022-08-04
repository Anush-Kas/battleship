import os
from random import choice, randrange
from Colors import Colors

class Cell:
    """
    #### Создаем Класс "клетка".
    Здесь мы задаем визуальное отображение клеток и их цвет.
    По визуальному отображению мы проверяем какого типа клетка.
    По этой причине нельзя обозначать одним символом два разных типа.
    Иначе в логике возникнет путаница.
    """

    damaged_ship = Colors.set_color("▣", Colors.LIGHT_RED)  #: Поврежденный корабль
    destroyed_ship = Colors.set_color("✘", Colors.LIGHT_RED)  #: Уничтоженный корабль
    empty_cell = Colors.set_color(" ", Colors.PURPLE)  #: Пустая клетка
    miss_cell = Colors.set_color("•", Colors.LIGHT_GRAY)  #: Промах
    ship_cell = Colors.set_color("■", Colors.LIGHT_BLUE)  #: Корабль


class FieldPart:
    """#### Части поля игры"""
    main = "map"  #: Карта кораблей
    radar = "radar"  #: Радар
    weight = "weight"  #: Вес клетки карты


class Field:
    """
    #### Поле игры, состоит из трех частей:
    + **Карта:** где расставлены корабли игрока.
    + **Радар:** на котором игрок отмечает свои ходы и результаты.
    + **Вес клетки:** поле с весом клеток, используется для ходов ИИ.
    """

    def __init__(self, size):
        self.size = size
        self.map = [[Cell.empty_cell for _ in range(size)] for _ in range(size)]
        self.radar = [[Cell.empty_cell for _ in range(size)] for _ in range(size)]
        self.weight = [[1 for _ in range(size)] for _ in range(size)]

    def get_field_part(self, element):
        if element == FieldPart.main:
            return self.map
        if element == FieldPart.radar:
            return self.radar
        if element == FieldPart.weight:
            return self.weight

    def draw_field(self, element):
        """
        #### Рисуем поле.
        Здесь отрисовка делится на две части, т.к. отрисовка весов клеток идёт по другому
        """
        field = self.get_field_part(element)
        weights = self.get_max_weight_cells()

        if element == FieldPart.weight:
            for x in range(self.size):
                for y in range(self.size):
                    if (x, y) in weights:
                        print(Colors.GREEN, end="")
                    if field[x][y] < self.size:
                        print(" ", end="")
                    if field[x][y] == 0:
                        print(str("" + ". " + ""), end="")
                    else:
                        print(str("" + str(field[x][y]) + " "), end="")
                    print(Colors.END, end="")
                print()
        else:
            """
            Всё что было выше - рисование веса для отладки,
            его можно не использовать в конечной игре.
            Само поле рисуется вот так:
            """
            for x in range(-1, self.size):
                for y in range(-1, self.size):
                    if x == -1 and y == -1:
                        print("  ", end="")
                        continue
                    if x == -1 and y >= 0:
                        print(y + 1, end=" ")
                        continue
                    if x >= 0 and y == -1:
                        print(Game.letters[x], end="")
                        continue
                    print(" " + str(field[x][y]), end="")
                print("")
        print("")

    def check_ship_fits(self, ship, element) -> bool:
        """
        Функция проверяет, помещается ли корабль позицию поля.
        Будем использовать при расстановке кораблей,
        а так же при вычислении веса клеток возвращает `False` если не помещается
        и `True` если корабль помещается
        """
        field = self.get_field_part(element)

        if (
            ship.x + ship.height - 1 >= self.size
            or ship.x < 0
            or ship.y + ship.width - 1 >= self.size
            or ship.y < 0
        ):
            return False

        x = ship.x
        y = ship.y
        width = ship.width
        height = ship.height

        for p_x in range(x, x + height):
            for p_y in range(y, y + width):
                if str(field[p_x][p_y]) == Cell.miss_cell:
                    return False

        for p_x in range(x - 1, x + height + 1):
            for p_y in range(y - 1, y + width + 1):
                if p_x < 0 or p_x >= len(field) or p_y < 0 or p_y >= len(field):
                    continue
                if str(field[p_x][p_y]) in (Cell.ship_cell, Cell.destroyed_ship):
                    return False

        return True

    def mark_destroyed_ship(self, ship, element):
        """
        Когда корабль уничтожен необходимо пометить все клетки вокруг него
        сыгранными, а все клетки корабля - уничтоженными.
        Так и делаем, только в два подхода.
        """
        field = self.get_field_part(element)

        x, y = ship.x, ship.y
        width, height = ship.width, ship.height

        for p_x in range(x - 1, x + height + 1):
            for p_y in range(y - 1, y + width + 1):
                if p_x < 0 or p_x >= len(field) or p_y < 0 or p_y >= len(field):
                    continue
                field[p_x][p_y] = Cell.miss_cell

        for p_x in range(x, x + height):
            for p_y in range(y, y + width):
                field[p_x][p_y] = Cell.destroyed_ship

    def add_ship_to_field(self, ship, element):
        """
        #### Добавление корабля:
        Пробегаемся от позиции `(х, у)` корабля по его высоте и ширине
        и помечаем на поле эти клетки.
        Параметр `element` - сюда мы передаем к какой части поля мы обращаемся:

        + **Основная**,
        + **Радар**,
        + **Вес клетки**.
        """
        field = self.get_field_part(element)

        x, y = ship.x, ship.y
        width, height = ship.width, ship.height

        for p_x in range(x, x + height):
            for p_y in range(y, y + width):
                """
                Заметьте в клетку мы записываем ссылку на корабль.
                Таким образом обращаясь к клетке мы всегда можем
                получить текущее `HP` корабля.
                """
                field[p_x][p_y] = ship

    def get_max_weight_cells(self):
        """
        Функция возвращает список координат с самым большим коэффициентом шанса попадания
        """
        weights = {}
        max_weight = 0

        """
        Просто пробегаем по всем клеткам и заносим их в словарь с ключом,
        который является значением в клетке заодно запоминаем максимальное
        значение. Далее просто берём из словаря список координат с этим
        максимальным значением `weights[max_weight]`
        """
        for x in range(self.size):
            for y in range(self.size):
                if self.weight[x][y] > max_weight:
                    max_weight = self.weight[x][y]
                weights.setdefault(self.weight[x][y], []).append((x, y))

        return weights[max_weight]

    def recalculate_weight_map(self, available_ships):
        """
        #### Пересчет веса клеток

        Для начала мы выставляем всем клеткам `1`.
        Нам необязательно знать какой вес был у клетки в предыдущий раз:
        эффект веса не накапливается от хода к ходу.
        """
        self.weight = [[1 for _ in range(self.size)] for _ in range(self.size)]

        """
        Пробегаем по всем полю.
        Если находим раненый корабль - ставим клеткам выше ниже и по бокам
        коэффициенты умноженные на `50` т.к. логично, что корабль имеет
        продолжение в одну из сторон. По диагоналям от раненой клетки
        ничего не может быть - туда вписываем нули
        """
        for x in range(self.size):
            for y in range(self.size):
                if self.radar[x][y] == Cell.damaged_ship:
                    self.weight[x][y] = 0

                    if x - 1 >= 0:
                        if y - 1 >= 0:
                            self.weight[x - 1][y - 1] = 0
                        self.weight[x - 1][y] *= 50
                        if y + 1 < self.size:
                            self.weight[x - 1][y + 1] = 0

                    if y - 1 >= 0:
                        self.weight[x][y - 1] *= 50
                    if y + 1 < self.size:
                        self.weight[x][y + 1] *= 50

                    if x + 1 < self.size:
                        if y - 1 >= 0:
                            self.weight[x + 1][y - 1] = 0
                        self.weight[x + 1][y] *= 50
                        if y + 1 < self.size:
                            self.weight[x + 1][y + 1] = 0
        """
        Перебираем все корабли оставшиеся у противника.
        Это открытая информация исходя из правил игры.
        Проходим по каждой клетке поля. Если там уничтоженный корабль,
        подбитый корабль или клетка с промахом - ставим туда коэффициент `0`.
        Больше делать нечего - переходим следующей клетке.
        Иначе прикидываем может ли этот корабль начинаться с этой клетки в
        какую-либо сторону и если он помещается прибавляем коэффициент `1`.
        """
        for ship_size in available_ships:
            ship = Ship(ship_size, 1, 1, 0)
            #: вот тут бегаем по всем клеткам поля
            for x in range(self.size):
                for y in range(self.size):
                    if (
                        self.radar[x][y]
                        in (Cell.destroyed_ship, Cell.damaged_ship, Cell.miss_cell)
                        or self.weight[x][y] == 0
                    ):
                        self.weight[x][y] = 0
                        continue
                    #: вот здесь ворочаем корабль и проверяем помещается ли он
                    for rotation in range(0, 4):
                        ship.set_position(x, y, rotation)
                        if self.check_ship_fits(ship, FieldPart.radar):
                            self.weight[x][y] += 1


class Ship:
    """#### Корабли"""

    def __init__(self, size, x, y, rotation):
        self.size = size
        self.hp = size
        self.x = x
        self.y = y
        self.rotation = rotation
        self.set_rotation(rotation)

    def __str__(self):
        return Cell.ship_cell

    def set_position(self, x, y, r):
        """Позиция корябля"""
        self.x = x
        self.y = y
        self.set_rotation(r)

    def set_rotation(self, r):
        """Положение корабля `вертикально`, `горизонтально`"""
        self.rotation = r

        if self.rotation == 0:
            self.width = self.size
            self.height = 1
        elif self.rotation == 1:
            self.width = 1
            self.height = self.size
        elif self.rotation == 2:
            self.y = self.y - self.size + 1
            self.width = self.size
            self.height = 1
        elif self.rotation == 3:
            self.x = self.x - self.size + 1
            self.width = 1
            self.height = self.size


class Player:
    """#### Создаем игроков игры"""

    def __init__(self, name, is_ai, skill, auto_ship):
        self.name = name
        self.is_ai = is_ai
        self.auto_ship_setup = auto_ship
        self.skill = skill
        self.message = []
        self.ships = []
        self.enemy_ships = []
        self.field = None

    def get_input(self, input_type):
        """
        #### Ход игрока.

        Это либо расстановка кораблей `(input_type == "ship_setup")`
        Либо совершения выстрела `(input_type == "shot")`
        """
        if input_type == "ship_setup":
            if self.is_ai or self.auto_ship_setup:
                user_input = (
                    str(choice(Game.letters))
                    + str(randrange(0, self.field.size))
                    + choice(["H", "V"])
                )
            else:
                user_input = input().upper().replace(" ", "")

            if len(user_input) < 3:
                return 0, 0, 0

            x, y, r = user_input[0], user_input[1:-1], user_input[-1]

            if (
                x not in Game.letters
                or not y.isdigit()
                or int(y) not in range(1, Game.field_size + 1)
                or r not in ("H", "V")
            ):
                self.message.append("Приказ непонятен, ошибка формата данных")
                return 0, 0, 0

            return Game.letters.index(x), int(y) - 1, 0 if r == "H" else 1

        if input_type == "shot":
            if self.is_ai:
                if self.skill == 1:
                    x, y = choice(self.field.get_max_weight_cells())
                if self.skill == 0:
                    x, y = randrange(0, self.field.size), randrange(0, self.field.size)
            else:
                user_input = input().upper().replace(" ", "")
                x, y = user_input[0].upper(), user_input[1:]
                if (
                    x not in Game.letters
                    or not y.isdigit()
                    or int(y) not in range(1, Game.field_size + 1)
                ):
                    self.message.append("Приказ непонятен, ошибка формата данных")
                    return 500, 0
                x = Game.letters.index(x)
                y = int(y) - 1
            return x, y

    def make_shot(self, target_player):
        """При совершении выстрела мы будем запрашивать ввод данных с типом `shot`."""
        sx, sy = self.get_input("shot")

        if sx + sy == 500 or self.field.radar[sx][sy] != Cell.empty_cell:
            return "retry"

        #: Результат выстрела это, то что целевой игрок ответит на наш ход
        #: **промазал**, **попал** или **убил** (в случае - убил, возвращается весь корабль).
        shot_res = target_player.receive_shot((sx, sy))

        if shot_res == "miss":
            self.field.radar[sx][sy] = Cell.miss_cell

        if shot_res == "get":
            self.field.radar[sx][sy] = Cell.damaged_ship

        if type(shot_res) == Ship:
            destroyed_ship = shot_res
            self.field.mark_destroyed_ship(destroyed_ship, FieldPart.radar)
            self.enemy_ships.remove(destroyed_ship.size)
            shot_res = "kill"

        """После совершения выстрела пересчитаем карту весов"""
        self.field.recalculate_weight_map(self.enemy_ships)

        return shot_res

    def receive_shot(self, shot):
        """
        Здесь игрок будет принимать выстрел как и в жизни игрок должен
        отвечать (возвращать) результат выстрела **попал** `(return "get")`
        **промахнулся** `(return "miss")` или убил корабль (тогда возвращаем весь корабль)
        так проще т.к. сразу знаем и координаты корабля и его длину
        """
        sx, sy = shot

        if type(self.field.map[sx][sy]) == Ship:
            ship = self.field.map[sx][sy]
            ship.hp -= 1

            if ship.hp <= 0:
                self.field.mark_destroyed_ship(ship, FieldPart.main)
                self.ships.remove(ship)
                return ship

            self.field.map[sx][sy] = Cell.damaged_ship
            return "get"

        else:
            self.field.map[sx][sy] = Cell.miss_cell
            return "miss"


class Game:
    """Здесь пишем поведение нашей игры"""

    letters = ("A", "B", "C", "D", "E", "F", "G", "H", "I", "J")  #: Буквенное обозначение поля игры.
    ships_rules = [1, 1, 1, 1, 2, 2, 2, 3, 3, 4]  #: Правила расстановки количества кораблей.
    field_size = len(letters)  #: Размер поля игры, равен длинне `letters`.

    def __init__(self):
        self.players = []
        self.current_player = None
        self.next_player = None

        self.status = "prepare"

    def start_game(self):
        """При старте игры назначаем текущего и следующего игрока"""
        self.current_player = self.players[0]
        self.next_player = self.players[1]

    def status_check(self):
        """Функция переключения статусов"""

        """
        Переключаем с `prepare` на `in game` если в игру добавлено два игрока.
        Далее стартуем игру.
        """
        if self.status == "prepare" and len(self.players) >= 2:
            self.status = "in game"
            self.start_game()
            return True

        """
        Переключаем в статус `game over`, если у следующего игрока осталось `0` кораблей.
        """
        if self.status == "in game" and len(self.next_player.ships) == 0:
            self.status = "game over"
            return True

    def add_player(self, player):
        """При добавлении игрока создаем для него поле"""
        player.field = Field(Game.field_size)
        player.enemy_ships = list(Game.ships_rules)

        """Расставляем корабли"""
        self.ships_setup(player)

        """
        Высчитываем вес для клеток поля
        (это нужно только для ИИ, но в целом при расширении возможностей
        игры можно будет например на основе этого давать подсказки игроку).
        """
        player.field.recalculate_weight_map(player.enemy_ships)
        self.players.append(player)

    def ships_setup(self, player):
        """делаем расстановку кораблей по правилам заданным в классе `Game`"""

        for ship_size in Game.ships_rules:
            """
            Задаем колличество попыток при построении кораблей случайным образом
            нужно для того, чтобы не попасть в бесконечный цикл,
            когда для последнего корабля остаётся очень мало места.
            """
            retry_count = 30

            """
            Создаем предварительно корабль - болванку нужного размера
            дальше будет видно, что мы присваиваем ему координаты,
            которые ввел пользователь.
            """
            ship = Ship(ship_size, 0, 0, 0)

            while True:
                Game.clear_screen()
                if player.auto_ship_setup is not True:
                    player.field.draw_field(FieldPart.main)
                    player.message.append(
                        "Куда поставить {} корабль: ".format(ship_size)
                    )
                    for _ in player.message:
                        print(_)
                else:
                    print("{}. Расставляем корабли...".format(player.name))

                player.message.clear()

                x, y, r = player.get_input("ship_setup")

                """
                Если пользователь ввёл какую-то ерунду -
                функция возвратит нули, значит без вопросов делаем `continue`
                фактически просто просим еще раз ввести координаты
                """
                if x + y + r == 0:
                    continue

                ship.set_position(x, y, r)

                """
                Если корабль помещается на заданной позиции - отлично.
                Добавляем игроку на поле корабль, также добавляем корабль
                в список кораблей игрока, и переходим к следующему кораблю.
                """
                if player.field.check_ship_fits(ship, FieldPart.main):
                    player.field.add_ship_to_field(ship, FieldPart.main)
                    player.ships.append(ship)
                    break

                """
                Сюда мы добираемся только, если корабль не поместился.
                Пишем, позиция неправильная и отнимаем попытку на расстановку
                """
                player.message.append("Неправильная позиция!")
                retry_count -= 1
                if retry_count < 0:
                    """
                    После заданного количества неудачных попыток -
                    обнуляем карту игрока убираем у него все корабли
                    и начинаем расстановку по новой
                    """
                    player.field.map = [
                        [Cell.empty_cell for _ in range(Game.field_size)]
                        for _ in range(Game.field_size)
                    ]
                    player.ships = []
                    self.ships_setup(player)
                    return True

    def draw(self):
        """Здесь рисуем наше поле:"""
        if not self.current_player.is_ai:
            self.current_player.field.draw_field(FieldPart.main)
            self.current_player.field.draw_field(FieldPart.radar)

            """Если интересно знать вес клеток можно раскомментировать строку:"""
            # self.current_player.field.draw_field(FieldPart.weight)

        for line in self.current_player.message:
            print(line)

    def switch_players(self):
        """Игроки меняются вот так вот просто."""
        self.current_player, self.next_player = self.next_player, self.current_player

    @staticmethod
    def clear_screen():
        """Функция очистки экрана"""
        os.system("cls" if os.name == "nt" else "clear")


def main():
    """Запускаем Игру"""

    """Здесь делаем список из двух игроков и задаем им основные параметры"""
    players = []
    players.append(Player(name="Игрок", is_ai=False, auto_ship=True, skill=1))
    players.append(Player(name="Компьютер", is_ai=True, auto_ship=True, skill=1))

    """Создаем саму игру и погнали в бесконечном цикле"""
    game = Game()

    while True:
        """
        Каждое начало хода проверяем статус и дальше уже действуем исходя из статуса игры
        """
        game.status_check()

        if game.status == "prepare":
            game.add_player(players.pop(0))

        if game.status == "in game":
            """
            В основной части игры мы очищаем экран,
            добавляем сообщение для текущего игрока и отрисовываем игру
            """
            Game.clear_screen()
            game.current_player.message.append("Ждём приказа: ")
            game.draw()

            """
            Очищаем список сообщений для игрока.
            В следующий ход он уже получит новый список сообщений
            """
            game.current_player.message.clear()

            """На основе выстрела текущего игрока ждём результата выстрела"""
            shot_result = game.current_player.make_shot(game.next_player)

            """
            В зависимости от результата выдаем сообщения и текущему игроку и следующему.
            Ну а если промазал - передаем ход следующему игроку.
            """
            if shot_result == "miss":
                game.next_player.message.append(
                    "На этот раз {}, промахнулся! ".format(game.current_player.name)
                )
                game.next_player.message.append(
                    "Ваш ход {}!".format(game.next_player.name)
                )
                game.switch_players()
                continue
            elif shot_result == "retry":
                game.current_player.message.append("Попробуйте еще раз!")
                continue
            elif shot_result == "get":
                game.current_player.message.append("Отличный выстрел, продолжайте!")
                game.next_player.message.append("Наш корабль попал под обстрел!")
                continue
            elif shot_result == "kill":
                game.current_player.message.append("Корабль противника уничтожен!")
                game.next_player.message.append(
                    "Плохие новости, наш корабль был уничтожен :("
                )
                continue

        if game.status == "game over":
            Game.clear_screen()
            game.next_player.field.draw_field(FieldPart.main)
            game.current_player.field.draw_field(FieldPart.main)
            print("Это был последний корабль {}".format(game.next_player.name))
            print("{} выиграл матч! Поздравления!".format(game.current_player.name))
            break

    print("Спасибо за игру!")
    input("")


if __name__ == "__main__":
    main()

