import krpc
import math
import time


def orbit(vessel, conn):
    turn_start_altitude = 250
    turn_end_altitude = 45000
    target_altitude = 250000
    t1 = time.time()  # Время, за которое уйдет все топливо из первой ступени
    t2 = time.time()  # Время, за которое уйдет все топливо из второй ступени
    t3 = time.time()  # Время, за которое уйдет все топливо из третьей ступени

    # Set up streams for telemetry
    ut = conn.add_stream(getattr, conn.space_center, 'ut')
    altitude = conn.add_stream(getattr, vessel.flight(), 'mean_altitude')
    apoapsis = conn.add_stream(getattr, vessel.orbit, 'apoapsis_altitude')

    stage_3_resources = vessel.resources_in_decouple_stage(stage=5, cumulative=False)
    srb_fuel3 = conn.add_stream(stage_3_resources.amount, 'SolidFuel')

    stage_2_resources = vessel.resources_in_decouple_stage(stage=4, cumulative=False)
    srb_fuel2 = conn.add_stream(stage_2_resources.amount, 'LiquidFuel')

    stage_1_resources = vessel.resources_in_decouple_stage(stage=1, cumulative=False)
    srb_fuel1 = conn.add_stream(stage_1_resources.amount, 'LiquidFuel')
    #
    # # Pre-launch setup
    # vessel.control.sas = False
    # vessel.control.rcs = False
    # vessel.control.throttle = 1.0

    print(f'Масса ракеты: {vessel.mass}')
    print(f'Масса топлива 3 ступени: {srb_fuel3()}')
    print(f'Масса топлива 2 ступени: {srb_fuel2()}')
    print(f'Масса топлива 1 ступени: {srb_fuel1()}')
    print(f'Масса 3 ступени без топлива: {sum([i.mass for i in vessel.parts.in_decouple_stage(stage=3)]) - srb_fuel3()}')
    print(f'Масса 2 ступени без топлива: {sum([i.mass for i in vessel.parts.in_decouple_stage(stage=2)]) - srb_fuel2()}')
    print(f'Масса 1 ступени без топлива: {sum([i.mass for i in vessel.parts.in_decouple_stage(stage=0)]) - srb_fuel1()}')

    vessel.control.activate_next_stage()
    # Countdown...
    # print('3...')
    time.sleep(1)
    # print('2...')
    time.sleep(1)
    # print('1...')
    time.sleep(1)
    # print('Запуск!')
    # print(f'Начальное кол-во твердого топлива: {srb_fuel3()}')
    # print(f'Начальное кол-во жидкого топлива: {srb_fuel2()}')

    # Activate the first stage
    vessel.control.activate_next_stage()
    vessel.auto_pilot.engage()
    vessel.auto_pilot.target_pitch_and_heading(90, 90)

    # Main ascent loop
    srbs_separated3, srbs_separated2 = False, False
    turn_angle, counter_for_stages = 0, 0
    while True:
        counter_for_stages += 1
        # Gravity turn
        if altitude() > turn_start_altitude and altitude() < turn_end_altitude:
            frac = ((altitude() - turn_start_altitude) /
                    (turn_end_altitude - turn_start_altitude))
            new_turn_angle = frac * 90
            if abs(new_turn_angle - turn_angle) > 0.5:
                turn_angle = new_turn_angle
                vessel.auto_pilot.target_pitch_and_heading(90 - turn_angle, 90)

        # Separate SRBs when finished
        if not srbs_separated3:
            if srb_fuel3() < 0.15:
                vessel.control.throttle = 0
                vessel.control.activate_next_stage()
                print(f'Время, за которое уйдет все топливо из 3 ступени: {time.time() - t3}')
                t2 = time.time()
                time.sleep(1)
                vessel.control.throttle = 1
                srbs_separated3 = True
                # print('Отсоединена 3-я ступень')

        if not srbs_separated2:
            if srb_fuel2() < 0.1:
                vessel.control.activate_next_stage()
                print(f'Время, за которое уйдет все топливо из 2 ступени: {time.time() - t2}')
                counter_for_stages = t2
                srbs_separated2 = True
                # print('Отсоединена 2-я ступень')

        # Decrease throttle when approaching target apoapsis
        if apoapsis() > target_altitude * 0.9:
            # print('Приближаемся к целевому апоапсису')
            break

    vessel.control.throttle = 0.25
    while apoapsis() < target_altitude:
        pass
    # print('Целевой апоапсис достигнут')
    vessel.control.throttle = 0.0

    # Wait until out of atmosphere
    # print('Выход из атмосферы')
    while altitude() < 70500:
        pass

    # Plan circularization burn (using vis-viva equation)
    # print('Планирование сжигания циркуляризации')
    mu = vessel.orbit.body.gravitational_parameter
    r = vessel.orbit.apoapsis
    a1 = vessel.orbit.semi_major_axis
    a2 = r
    v1 = math.sqrt(mu * ((2. / r) - (1. / a1)))
    v2 = math.sqrt(mu * ((2. / r) - (1. / a2)))
    delta_v = v2 - v1
    node = vessel.control.add_node(
        ut() + vessel.orbit.time_to_apoapsis, prograde=delta_v)

    # Calculate burn time (using rocket equation)
    F = vessel.available_thrust
    Isp = vessel.specific_impulse * 9.82
    m0 = vessel.mass
    m1 = m0 / math.exp(delta_v / Isp)
    flow_rate = F / Isp
    burn_time = (m0 - m1) / flow_rate

    # Orientate ship
    # print('Ориентация корабля для кругового сжигания')
    vessel.auto_pilot.reference_frame = node.reference_frame
    vessel.auto_pilot.target_direction = (0, 1, 0)
    vessel.auto_pilot.wait()

    # Wait until burn
    # print('Ожидание, пока сгорит циркуляризация')
    burn_ut = ut() + vessel.orbit.time_to_apoapsis - (burn_time / 2.)
    lead_time = 5
    conn.space_center.warp_to(burn_ut - lead_time)

    # Execute burn
    # print('Готов выполнить маневр')
    time_to_apoapsis = conn.add_stream(getattr, vessel.orbit, 'time_to_apoapsis')
    while time_to_apoapsis() - (burn_time / 2.) > 0:
        pass
    # print('Выполнение маневра')
    vessel.control.throttle = 1.0
    time.sleep(burn_time - 0.1)

    node.remove()
    vessel.control.throttle = 0

conn = krpc.connect(name="Psyche")
vessel = conn.space_center.active_vessel
space_center = conn.space_center

orbit(vessel, conn)