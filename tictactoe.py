# Игра в крестики нолики
import random
import sys
from attr import attrib, attrs
from math import inf as infinity


@attrs
class Player:
    # Базовый класс для всех игроков (AI и пользователя)
    # Содежит выигрышные координаты
    win_coord = ((0, 1, 2), (3, 4, 5), (6, 7, 8), (0, 3, 6), (1, 4, 7), (2, 5, 8), (0, 4, 8), (2, 4, 6))

    # Аттрибуты класса. Использую библиотеку attr, которая делает ненужным использование __init__. Mark - символ, за
    # который играем, level - уровень игрока (определяется в конкретном классе)
    mark = attrib()
    level = attrib(default=None)
    # alt_mark - символ оппонента. Если мы играем за крестик, у оппонента нолик
    alt_mark = attrib(default=('X' if mark == 'O' else 'O'))

    #
    def random_turn(self, field):
        """
        Случайный ход. Используется для легкого и среднего AI
        """
        while True:

            # Выбираем случайное число
            index = random.randrange(9)

            # Если на его месте не _, а уже стоит символ, повторяем
            if field[index] != '_':
                continue

            # Если нашли пустую клеточку, ставим туда наш символ
            field[index] = self.mark
            self.print_turn(field)
            return

    def print_turn(self, field):
        """
        Печает, чей сейчас ход
        """
        print(f'Making move level "{self.level}"')
        print_field(field)


@attrs
class User(Player):
    level = 'User'

    def turn(self, field):
        """
        Делает ход за игрока
        """

        # Бесконечный цкл, который запрашивает у игрока координаты, когда игрок вводит подходящие координаты, выходит из
        # цикла
        while True:

            # Игрок должен ввести две координаты, например 1 1. Первая цифра - номер строчки (считается снизу), вторая -
            # номер столбца
            coords = input('Enter the coordinates: ').split()

            # Если введено не 2 символа, возвращается к началу цикла
            if len(coords) != 2:
                print('Enter two numbers!')
                continue

            # Преобразуем строку в переменные, чтобы проверить, что они являются цифрами
            coord_1 = coords[0]
            coord_2 = coords[1]

            # Проверяем, являются ли введенные символами цифрами
            if not coord_1.isnumeric() or not coord_2.isnumeric():
                print('You should enter numbers!')
                continue

            # Преобразуем переменные в цифры
            coord_1, coord_2 = int(coord_1), int(coord_2)

            # Если цифры меньше 1 или больше 3, повторяем цикл
            if not (1 <= coord_1 <= 3) or not (1 <= coord_2 <= 3):
                print('Coordinates should be from 1 to 3!')
                continue

            # Из-за специфики, что мы считаем номера строк для координат снизу, мы преобразуем в их в "номарльное
            # представление". То есть 3 становится 1, 1 - тройкой.
            if coord_2 == 1:
                coord_2 = 3
            elif coord_2 == 3:
                coord_2 = 1

            # Наше поле представляет собой список, поэтому нужно преобразовать
            index = coord_1 - 1 + (coord_2 - 1) * 3

            # Если на месте координат есть другой символ, не пустая клетка, повторить цикл заново
            if field[index] != '_':
                print('This cell is occupied! Choose another one!')
                continue

            # Если все хорошо, ставим в координаты поля символ и выходим из цикла
            field[index] = self.mark
            print_field(field)
            return


@attrs
class EasyAI(Player):
    # Легкий AI, ходит только случайно
    level = 'easy'

    def turn(self, field):
        self.random_turn(field)


@attrs
class MediumAI(Player):
    # Средний AI, если видит, что может победить или что противник может победить, предотвращает
    level = 'medium'

    def turn(self, field):
        for i in self.win_coord:
            coords = [field[j] for j in i]

            # Проверяет, если на поле на следующем ходу кто-то может победить, ставить в эту клетку свой символ
            if (coords.count('X') == 2 or coords.count('O') == 2) and coords.count('_') == 1:
                index = coords.index('_')
                index = i[index]
                field[index] = self.mark
                self.print_turn(field)
                print_field(field)
                return

        # Если такой ситуации нет, делает случайный ход
        self.random_turn(field)
        return


@attrs
class HardAI(Player):
    # Класс тяжелого AI, использует алгоритм минимакс для хода

    level = 'hard'

    def minimax(self, field, player):
        """
        Исследует все возможные ходы и возвращает лучший. Если ход ведет к победе, ставит ходу +10, если к поражению -
        -10, если ничья - 0. В нашем случае player - self.mark. Так как мы используем классы и этот аттрибут означает,
        какой символ у игрока этого класса.
        """

        # Создаем копию поля, чтобы оригинальное не изменялось во время алгоритма
        new_field = field

        # Создаем список индексов пустых клеток
        empty_index = [num for num, i in enumerate(new_field) if i == '_']

        # Определяем переменную best, мы ее далее будем перезаписывать, если полученные очки больше значения infinity
        if player == self.mark:
            best = [-1, -infinity]
        else:
            best = [-1, +infinity]

        # Базовые случаи. Если побеждает текущий игрок, возвращаем 10, если побеждает противник
        # возвращаем -10, если ничья - тогда 0.
        if result(new_field) == f'{self.mark} wins':
            score = [-1, 10]
            return score
        elif result(new_field) == f'{self.alt_mark} wins':
            score = [-1, -10]
            return score
        elif result(new_field) == 'Draw':
            score = [-1, 0]
            return score

        # Проходим по всем пустым клеткам
        for num, i in enumerate(empty_index):

            # Ставим в каждую символ текущего икрока
            new_field[i] = player

            # Рекурсивно вызываем функцию для следующего хода
            if player == self.mark:
                score = self.minimax(new_field, player=self.alt_mark)
            else:
                score = self.minimax(new_field, player=self.mark)

            # Записываем в переменную score индекс хода
            score[0] = i

            # Обнуляем ячейку, в которую поставили символ
            new_field[i] = '_'

            # Если мы получили значение лучше, чем записано в best, мы заменяем значение.
            # Для игрока-компьютера, который вызывает алгоритм чем больше значение, тем лучше
            # Для антагониста наоборот (то есть если ходит противник, чем меньше мы получили очков, тем
            # лучше его ход. А нам нужно учитывать все ходы, даже худшие для нас)
            if player == self.mark:
                if score[1] > best[1]:
                    best = score
            else:
                if score[1] < best[1]:
                    best = score
        # Возвращаем best, где на первом месте индекс хода, на втором - набранные очки
        return best

    def turn(self, field):
        """
        Делаем ход, используя минимакс
        """

        self.field = field
        best_move = self.minimax(field, player=self.mark)
        field[best_move[0]] = self.mark
        self.print_turn(field)
        print_field(field)


def main_menu():
    while True:

        # Спрашиваем у игрока, что хотим сделать. Он должен ввести комманду типа start easy user. на первом месте стоит
        # действие, на втором игрок X, на третьем игрок O. Если введен user - играет человек, если easy, medium, hard -
        # соответсвующий уровень компьютера. Если выбран exit - программа прекращается
        options = ['start', 'easy', 'medium', 'hard', 'user', 'exit']
        user_options = input('Input command: > ').split()
        if user_options[0] == 'exit':
            sys.exit()

        # Проверяем, чтобы были введены нужные слова и создаем классы игроков
        if len(user_options) == 3 and all([(i in options) for i in user_options]):
            x_player = create_class(mark='X', level=user_options[1])
            o_player = create_class(mark='O', level=user_options[2])
            tictactoe(x_player, o_player)

        # Если что-то не так, печаем "Bad parameters"
        else:
            print('Bad parameters!')


def tictactoe(player_1, player_2):
    """
    Функция отвечает за сам процесс игры
    """

    # Сначала строим поле
    user_field = ['_' for _ in range(9)]

    # Печатаем поле
    print_field(user_field)

    # Делаем ходы, пока не будет определн результат игры
    while not result(user_field):
        player_1.turn(field=user_field)

        # Если после хода игрока партия завершается - выходим из цикла
        if result(user_field):
            break
        player_2.turn(field=user_field)

    # Печаетаем результат игры
    print(result(user_field))


def create_class(mark, level):
    """
    Отвечает за создание класса
    """
    if level == 'user':
        return User(mark)
    elif level == 'hard':
        return HardAI(mark)
    elif level == 'medium':
        return MediumAI(mark)
    elif level == 'easy':
        return EasyAI(mark)


def result(field):
    """
    Функция отвечает за проверку результата игры
    """

    # win_coord - координаты победных позиций
    win_coord = ((0, 1, 2), (3, 4, 5), (6, 7, 8), (0, 3, 6), (1, 4, 7), (2, 5, 8), (0, 4, 8), (2, 4, 6))
    for i in win_coord:

        # Если в клеточках победных координат стоят одинаковые символы и это не пустая клетка (_), возвращает символ
        # победителя
        if field[i[0]] == field[i[1]] == field[i[2]] and field[i[0]] != '_':
            return f'{field[i[0]]} wins'

    # Если не нашли победителя и на поле не осталось свободных клеток, возрщает Draw (ничья)
    if not ('_' in field):
        return 'Draw'
    return


def print_field(field):
    """
    Функция отвечает за вывод игрового поля
    """
    print('-' * 9)
    for i in range(0, 9, 3):
        print('| ', end='')
        for j in range(3):
            print(field[i + j], end=' ')
        print('|')
    print('-' * 9)


if __name__ == '__main__':
    main_menu()
