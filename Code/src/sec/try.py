import numpy as np
import matplotlib.pyplot as plt

# Константы
U1 = ...  # Задайте значение U1
k1 = ...  # Задайте значение k1
c = ...  # Задайте значение c
ρ0 = ...  # Задайте значение ρ0
g = ...  # Задайте значение g
M = ...  # Задайте значение M
R = ...  # Задайте значение R
T = ...  # Задайте значение T
m0 = ...  # Задайте значение m0
GM = ...  # Задайте значение GM
α0 = ...  # Задайте значение α0
γ1 = ...  # Задайте значение γ1
t1 = ...  # Задайте конечное время


# Определяем систему уравнений
def system(t, x):
    x1, x2, x3, x4 = x
    S = np.sqrt(x2 ** 2 + x4 ** 2)  # x5
    dx1_dt = x2
    dx2_dt = (U1 * k1 - 0.5 * c * ρ0 * np.exp(-g * M * x3 / (R * T)) * S * x2 ** 2 * np.cos(α0 - γ1 * t)) / (
                m0 - k1 * t)
    dx3_dt = x4
    dx4_dt = (U1 * k1 - 0.5 * c * ρ0 * np.exp(-g * M * x3 / (R * T)) * S * x4 ** 2 * np.sin(α0 - γ1 * t) +
              GM * (m0 - k1 * t) / (R + x3) ** 2) / (m0 - k1 * t)
    return np.array([dx1_dt, dx2_dt, dx3_dt, dx4_dt])


# Метод Рунге-Кутта 4-го порядка
def runge_kutta_4(f, y0, t0, t1, dt):
    t_values = np.arange(t0, t1, dt)
    y_values = np.zeros((len(t_values), len(y0)))
    y_values[0] = y0

    for i in range(1, len(t_values)):
        t = t_values[i - 1]
        y = y_values[i - 1]

        k1 = f(t, y)
        k2 = f(t + dt / 2, y + dt / 2 * k1)
        k3 = f(t + dt / 2, y + dt / 2 * k2)
        k4 = f(t + dt, y + dt * k3)

        y_values[i] = y + (dt / 6) * (k1 + 2 * k2 + 2 * k3 + k4)

    return t_values, y_values


# Начальные условия
y0 = np.array([x1_0, x2_0, x3_0, x4_0])  # Задайте начальные условия
t0 = 0.0
dt = 0.01

# Решаем систему
t_values, y_values = runge_kutta_4(system, y0, t0, t1, dt)

# Визуализация результатов
plt.figure(figsize=(10, 8))
plt.subplot(211)
plt.plot(t_values, y_values[:, 0], label='x1')
plt.plot(t_values, y_values[:, 1], label='x2')
plt.title('Решение системы дифференциальных уравнений')
plt.xlabel('Время (t)')
plt.ylabel('Значения')
plt.legend()

plt.subplot(212)
plt.plot(t_values, y_values[:, 2], label='x3')
plt.plot(t_values, y_values[:, 3], label='x4')
plt.xlabel('Время (t)')
plt.ylabel('Значения')
plt.legend()

plt.tight_layout()
plt.show()