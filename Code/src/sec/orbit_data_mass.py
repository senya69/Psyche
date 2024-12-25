import krpc
import matplotlib.pyplot as plt
import time

# Подключение к серверу kRPC
conn = krpc.connect('orbit_data')

# Получение объекта космического корабля
vessel = conn.space_center.active_vessel

# Создание массивов для данных о времени и высоте
time_values = []
altitude_values = []
t = 0

# Получение высоты корабля на протяжении полета
with open('mass.txt', 'w') as f:
    while True:
        # Получение текущей высоты
        altitude = vessel.flight().surface_altitude
        f.write(f'{t}: {vessel.mass}\n')
        time_values.append(t)  # Запись текущего времени в массив
        altitude_values.append(vessel.mass)  # Запись текущей высоты в массив


        time.sleep(1)
        t += 1
        # Проверка условия завершения сбора данных
        if altitude > 250000:  # Остановка считывания данных при наборе высоты 160км
            break

# Построение графика скорости от времени
plt.plot(time_values, altitude_values)
plt.title('Изменение массы ракеты от времени (KSP)')
plt.xlabel('Время, секунды')
plt.ylabel('Масса, килограммы')
plt.show()