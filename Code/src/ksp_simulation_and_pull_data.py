import krpc
import time
import csv
from math import sqrt
import numpy as np
import pathlib

# Подключаемся к игре
conn = krpc.connect(name="Автопилот Psyche")
vessel = conn.space_center.active_vessel

# Создаем файл для записи данных
PATH = str(pathlib.Path(__file__).parent.joinpath("ksp_flight_data.csv"))
with open(PATH, mode="w", newline="") as file:
    writer = csv.writer(file)
    writer.writerow(["Time", "Altitude", "Vertical Velocity", "Horizontal Velocity",
                     "Total Velocity", "Drag", "Displacement"])

    # Подготовка к запуску
    vessel.control.sas = True
    vessel.control.rcs = False
    vessel.control.throttle = 1.0


    # Начальная позиция для расчета смещения
    initial_position = vessel.position(vessel.orbit.body.reference_frame)
    # Длина вектора
    initial_position_vec_length = np.linalg.norm(initial_position)

    vessel.control.activate_next_stage()  # Запуск двигателей первой ступени -- 7
    print("Запуск через 3...")
    time.sleep(1)
    print("2...")
    time.sleep(1)
    print("1...")
    time.sleep(1)
    vessel.control.activate_next_stage()  # Освобождение от стартовых клемм -- 6

    # Счетчик времени
    start_time = conn.space_center.ut
    stage_main_engines = ["", "Merlin 1D (B5) x18 boosters", "Merlin 1D (B5) x9 core", "Merlin 1D (B5) Vacuum", "Ion Thruster"]

    print(f"Пуск!\nВремя старта: {start_time:.2f} с")

    # Основной цикл полета
    while True:
        # Настоящее время
        ut = conn.space_center.ut

        # Прошедшее время с начала
        elapsed_time = ut - start_time

        # Сбор данных
        altitude = vessel.flight().mean_altitude
        speed = vessel.flight(vessel.orbit.body.reference_frame).speed
        drag_x, drag_y, drag_z = vessel.flight().drag
        drag = sqrt(drag_x ** 2 + drag_y ** 2 + drag_z ** 2)

        # Текущее положение для расчета смещения
        current_position = vessel.position(vessel.orbit.body.reference_frame)

        # Расчет смещения
        current_position = current_position / np.linalg.norm(current_position) * initial_position_vec_length
        horizontal_displacement = np.linalg.norm(current_position - initial_position)

        # Получение скоростей
        vertical_speed = vessel.flight(vessel.orbit.body.reference_frame).vertical_speed
        horizontal_speed = vessel.flight(vessel.orbit.body.reference_frame).horizontal_speed

        # Записываем данные в файл
        writer.writerow([elapsed_time, altitude, vertical_speed, horizontal_speed, speed, drag, horizontal_displacement])

        # Наклон ракеты в зависимости от высоты
        vessel.auto_pilot.target_roll = 0
        vessel.auto_pilot.engage()
        if altitude == 70000:
            vessel.control.activate_next_stage()  # Отделяем бустеры -- 5, основной двигатель еще работает
            print("Отделение бустеров")
        if altitude < 150000:
            target_pitch = 90 * (1 - altitude / 150000)  # Чем выше высота, тем меньше наклон
            vessel.auto_pilot.target_pitch_and_heading(target_pitch, 90)
        else:
            vessel.auto_pilot.target_pitch_and_heading(0, 90)
            break

    vessel.control.throttle = 0.0
    time.sleep(3)
    vessel.control.activate_next_stage()  # Отделяем основной двигатель -- 4
    print("Отделение основного двигателя")
    time.sleep(5)
    vessel.control.activate_next_stage()  # Запускаем первый двигатель второй стадии -- 3
    vessel.control.throttle = 1.0
    print("Запуск двигателя в вакууме")
    time.sleep(20)
    vessel.control.activate_next_stage()  # Отделяем обтекатель -- 2
    print("Отделяем обтекатель")
    print("Конец")
