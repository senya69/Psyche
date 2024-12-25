import matplotlib.pyplot as plt
import math


class Rocket:
    _total_mass = 50436
    _mass_1_stage = 6686
    _dry_mass_1_stage = 4206
    _mass_2_stage = 11630
    _dry_mass_2_stage = 1794
    _mass_3_stage = 32120
    _dry_mass_3_stage = 6284

    _isp3 = 135
    _isp2 = 266
    _isp1 = 191

    _g0 = 9.80665

    _theta_0 = 90
    _tau = 900
    _mediane_diff = []

    _Vex = 2570
    _Pex = 10**5
    _C = 1004.68506
    _T0 = 288.16
    _M_earth = 0.02896968
    _R0 = 8.314462618
    _R = 6378000

    _burning_time_3_stage = 46
    _burning_time_2_stage = 99
    _burning_time_1_stage = 51

    _total_time = 381

    _time_arr = list(range(_total_time))

    _fuel_consumption_3_stage = (_mass_3_stage - _dry_mass_3_stage) / _burning_time_3_stage
    _fuel_consumption_2_stage = (_mass_2_stage - _dry_mass_2_stage) / _burning_time_2_stage
    _fuel_consumption_1_stage = (_mass_1_stage - _dry_mass_1_stage) / _burning_time_1_stage

    # Инициализируем массивы для хранения значений
    _mass_total_arr = [0] * _total_time
    _mass_1_stage_arr = [0] * _total_time
    _mass_2_stage_arr = [0] * _total_time
    _mass_3_stage_arr = [0] * _total_time
    _velocity_arr = [0] * _total_time
    _diff_arr = [0] * _total_time
    _height_arr = list(range(0, 150000, 100))
    _impulse_3_stage_arr = [0] * 1500
    _impulse_2_stage_arr = [0] * 1500
    _impulse_1_stage_arr = [0] * 1500

    with open('velocity.txt', 'r') as f:
        data = f.readlines()
        _new_data = []
        for i in data:
            i = i[:-1:]
            _new_data.append(float(i))

    with open('mass.txt', 'r') as f:
        data = f.readlines()
        _new_data_mass = []
        for i in data:
            i = i[:-1:]
            _new_data_mass.append(float(i))

    def __init__(self):
        self.total_mass = Rocket._total_mass
        self.mass_1_stage = Rocket._mass_1_stage
        self.dry_mass_1_stage = Rocket._dry_mass_1_stage
        self.mass_2_stage = Rocket._mass_2_stage
        self.dry_mass_2_stage = Rocket._dry_mass_2_stage
        self.mass_3_stage = Rocket._mass_3_stage
        self.dry_mass_3_stage = Rocket._dry_mass_3_stage

    def mass_change(self):
        # Работа 3-й ступени
        for i in range(46):
            self.total_mass -= Rocket._fuel_consumption_3_stage
            self.mass_3_stage -= Rocket._fuel_consumption_3_stage
            Rocket._mass_total_arr[i] = self.total_mass
            Rocket._mass_1_stage_arr[i] = self.mass_1_stage
            Rocket._mass_2_stage_arr[i] = self.mass_2_stage
            Rocket._mass_3_stage_arr[i] = self.mass_3_stage

        # Переход к 2-й ступени
        self.total_mass -= Rocket._dry_mass_3_stage
        for i in range(46, 145):
            self.total_mass -= Rocket._fuel_consumption_2_stage
            self.mass_2_stage -= Rocket._fuel_consumption_2_stage
            Rocket._mass_total_arr[i] = self.total_mass
            Rocket._mass_1_stage_arr[i] = self.mass_1_stage
            Rocket._mass_2_stage_arr[i] = self.mass_2_stage
            Rocket._mass_3_stage_arr[i] = self.mass_3_stage

        # Летит без работы двигателей
        for i in range(145, 169):
            Rocket._mass_total_arr[i] = self.total_mass
            Rocket._mass_1_stage_arr[i] = self.mass_1_stage
            Rocket._mass_2_stage_arr[i] = self.mass_2_stage
            Rocket._mass_3_stage_arr[i] = self.mass_3_stage

        # Работа 1-й ступени
        self.total_mass -= Rocket._dry_mass_2_stage
        for i in range(169, 220):
            self.total_mass -= Rocket._fuel_consumption_1_stage
            self.mass_1_stage -= Rocket._fuel_consumption_1_stage
            Rocket._mass_total_arr[i] = self.total_mass
            Rocket._mass_1_stage_arr[i] = self.mass_1_stage
            Rocket._mass_2_stage_arr[i] = self.mass_2_stage
            Rocket._mass_3_stage_arr[i] = self.mass_3_stage

        for i in range(220, 381):
            Rocket._mass_total_arr[i] = self.total_mass
            Rocket._mass_1_stage_arr[i] = self.mass_1_stage
            Rocket._mass_2_stage_arr[i] = self.mass_2_stage
            Rocket._mass_3_stage_arr[i] = self.mass_3_stage

        # plt.figure()
        # plt.title('Изменение массы ракеты от времени (Мат модель)')
        # plt.xlabel('Время, секунды')
        # plt.ylabel('Масса, килограммы')
        # plt.plot(Rocket._time_arr, Rocket._mass_total_arr, label='Общая масса (Мат модель)')
        # plt.plot(Rocket._time_arr[:len(Rocket._new_data_mass)], Rocket._new_data_mass, label='Общая масса (КСП)')
        # plt.legend()
        # plt.grid()
        # plt.show()

    def angle(self, time):
        return math.radians(Rocket._theta_0 * math.exp(-time / Rocket._tau))

    def f_t(self, time, h):
        # Параметры сопротивления
        c_d = 0.47  # Коэффициент сопротивления (для цилиндрической формы ракеты)
        s_p = 0.5  # Площадь поперечного сечения ракеты в м²
        rho_0 = 1.225  # Плотность воздуха на уровне моря (кг/м³)
        _h = 8500  # Масштаб высоты для плотности воздуха (м)
        if isinstance(h, complex):
            h = h.real
        h = max(0, h)
        # Плотность воздуха на высоте h
        rho = rho_0 * math.exp(-h / _h)

        # Работа 3-й ступени
        if time < 46:
            v_ex = Rocket._isp3 * Rocket._g0  # Исходная скорость выброса для 3-й ступени
            p_d = Rocket._Pex * pow((1 - (Rocket._g0 * h) / (Rocket._C * Rocket._T0)),
                                    (Rocket._C * Rocket._M_earth / Rocket._R0))
            f_t = v_ex * Rocket._fuel_consumption_3_stage + 0.042 * (Rocket._Pex - p_d)

            # Сила лобового сопротивления
            f_d = 0.5 * c_d * rho * s_p * (Rocket._velocity_arr[int(time)] ** 2)  # Скорость уже зависит от времени
            f_t -= f_d  # Уменьшаем тягу на силу сопротивления
            return f_t

        # Работа 2-й ступени
        elif 46 <= time < 153:
            v_ex = Rocket._isp2 * Rocket._g0  # Исходная скорость выброса для 2-й ступени
            p_d = Rocket._Pex * pow((1 - (Rocket._g0 * h) / (Rocket._C * Rocket._T0)),
                                    (Rocket._C * Rocket._M_earth / Rocket._R0)
                                    )
            f_t = v_ex * Rocket._fuel_consumption_2_stage + 0.042 * (Rocket._Pex - p_d)

            # Сила лобового сопротивления
            f_d = 0.5 * c_d * rho * s_p * (Rocket._velocity_arr[int(time)] ** 2)  # Скорость зависит от времени
            f_t -= f_d  # Уменьшаем тягу на силу сопротивления
            return f_t

        # Работа 1-й ступени
        elif 153 <= time < 175:
            v_ex = Rocket._isp1 * Rocket._g0  # Исходная скорость выброса для 1-й ступени
            p_d = Rocket._Pex * pow((1 - (Rocket._g0 * h) / (Rocket._C * Rocket._T0)),
                                    (Rocket._C * Rocket._M_earth / Rocket._R0)
                                    )
            f_t = v_ex * Rocket._fuel_consumption_1_stage + 0.042 * (Rocket._Pex - p_d)

            # Сила лобового сопротивления
            f_d = 0.5 * c_d * rho * s_p * (Rocket._velocity_arr[int(time)] ** 2)
            f_t -= f_d  # Уменьшаем тягу на силу сопротивления
            return f_t

        # После работы двигателей, когда силы тяги исчезают
        else:
            return 0

    def velocity_change(self):
        self.mass_change()  # Обновление массы ракеты
        h = 0  # Начальная высота
        v_y = 0  # Начальная скорость
        dt = 1  # Шаг по времени в секундах
        list_h = [h]  # Список для хранения высоты
        list_v_y = [v_y]  # Список для хранения скорости
        list_prev_f_t = []  # Список для хранения тяги на предыдущем шаге

        for t in range(0, 291, dt):
            if t < 175:  # Работа двигателя
                mass = Rocket._mass_total_arr[t]  # Масса ракеты
                phi = self.angle(t)  # Угол наклона
                f_t = self.f_t(t, h)  # Тяга на текущем шаге
                list_prev_f_t.append(f_t)  # Добавляем тягу в список

                # Расчет ускорения с учетом тяги и силы тяжести
                a_y = (f_t * math.sin(phi) - mass * Rocket._g0) / mass

                # Применяем метод Эйлера для численного интегрирования
                v_y += a_y * dt  # Обновляем скорость
                h += v_y * dt  # Обновляем высоту (интегрируем скорость)

            elif t < 197:  # Ракета продолжает двигаться без работы двигателя
                v_y = v_y  # Скорость не меняется
                h += v_y * dt  # Интегрируем по высоте

            elif t < 290:  # Примерное уменьшение скорости на 1.564 метра в секунду
                v_y -= 1.5643453  # Скорость уменьшается с фиксированным значением
                h += v_y * dt  # Интегрируем по высоте

            # Добавляем текущие значения в списки
            list_h.append(h)
            list_v_y.append(v_y)
            if 3 < t < 290:
                if isinstance(list_v_y[t], complex):
                    list_v_y[t] = list_v_y[t].real
                Rocket._diff_arr[t] = abs(1 - list_v_y[t] / Rocket._new_data[t]) * 100
                Rocket._mediane_diff.append(Rocket._diff_arr[t])

        # Выводим среднее отклонение во время полета
        print(f'{sum(Rocket._mediane_diff) / len(Rocket._mediane_diff):.3f}%')
        # Построение графика
        plt.title('Изменение скорости ракеты от времени (Метод Эйлера)')
        plt.xlabel('Время, секунды')
        plt.ylabel('Скорость, метры в секунду')
        plt.plot(Rocket._time_arr[:len(Rocket._new_data)], Rocket._new_data, label='Скорость ракеты (КСП)')
        plt.plot(list_v_y, label='Скорость ракеты (Метод Эйлера)')
        plt.legend()
        plt.grid()
        plt.show()

        #  Выводим график разницы между данными скорости
        plt.title('Разница между скоростями в модели и в симуляции')
        plt.xlabel('Время, секунды')
        plt.ylabel('Разница в данных, проценты')
        plt.plot(Rocket._diff_arr, label='Разница в процентах')
        plt.plot()
        plt.legend()
        plt.grid()
        plt.show()

    def imp3_change(self):
        for i in range(len(Rocket._height_arr)):
            now_h = Rocket._height_arr[i]
            p_a = Rocket._Pex * pow(1 - (Rocket._g0 * now_h) / (Rocket._C * Rocket._T0),
                                    (Rocket._C * Rocket._M_earth / Rocket._R0)
                                    )
            f_t = Rocket._fuel_consumption_3_stage * Rocket._Vex + (Rocket._Pex - p_a) * 4.9807
            imp3 = f_t / (Rocket._fuel_consumption_3_stage * Rocket._g0)
            Rocket._impulse_3_stage_arr[i] = imp3

        fig, specific_impulse = plt.subplots()
        specific_impulse.set_title('Изменение удельного импульса 3 ступени')
        specific_impulse.set_xlabel('Удельный импульс, секунды')
        specific_impulse.set_ylabel('Высота, метры')
        specific_impulse.plot(Rocket._impulse_3_stage_arr[:250], Rocket._height_arr[:250])
        specific_impulse.grid()
        plt.show()


rocket = Rocket()
rocket.velocity_change()
rocket.imp3_change()