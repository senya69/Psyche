import krpc
import matplotlib.pyplot as plt
import time

# Подключение к серверу kRPC
conn = krpc.connect('cheker')

# Получение объекта космического корабля
vessel = conn.space_center.active_vessel

# Создание массивов для данных о времени и скорости
time_values = []
speed_values = []

# Получение скорости корабля на протяжении полета
with open('velocity.txt', 'w') as f:
    while True:
        # time = conn.space_center.ut  # Получение данных о текущем времени
        speed = vessel.flight(vessel.orbit.body.reference_frame).speed  # Получение текущей скорости
        time_values.append(time.time())  # Запись текущего времени в массив
        speed_values.append(speed)  # Запись текущей скорости в массив
        time.sleep(1)
        f.write(f'{time}: {speed}\n')
        print(f'{time}: {speed}\n')
        # Проверка условия завершения сбора данных
        altitude = vessel.flight().surface_altitude
        if altitude > 250000:  # Остановка считывания данных при наборе высоты 250км
            break

# Построение графика скорости от времени
plt.plot(time_values, speed_values)
plt.title('Изменение скорости ракеты от времени (KSP)')
plt.xlabel('Время, cекунды')
plt.ylabel('Скорость, метры в секунду')
plt.show()