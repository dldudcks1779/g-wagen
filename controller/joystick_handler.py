import pygame
import config

# pygame 및 조이스틱 객체 초기화
def init_joystick():
    try:
        pygame.init()
        pygame.joystick.init()
        if pygame.joystick.get_count() == 0:
            raise RuntimeError("ERROR: 연결된 조이스틱 없음")
        joystick = pygame.joystick.Joystick(0)
        joystick.init()
        return joystick
    except pygame.error as error:
        raise RuntimeError(f"ERROR: pygame 또는 조이스틱 객체 초기화 실패 - {error}") from error

# 조이스틱 상태 반환
def get_joystick_status(joystick):
    pygame.event.pump()
    axes = [joystick.get_axis(i) for i in range(joystick.get_numaxes())]
    buttons = tuple([joystick.get_button(i) for i in range(joystick.get_numbuttons())][:11])
    steer = float(axes[config.STEER_AXIS]) if len(axes) > config.STEER_AXIS else 0.0
    steering_value = round(steer if abs(steer) > 0.1 else 0.0, 4)
    steering_direction = "LEFT" if steering_value < 0 else ("RIGHT" if steering_value > 0 else "CENTER")
    gear = config.GEAR_MAP.get(buttons, "")
    brake = axes[config.BRAKE_AXIS] if len(axes) > config.BRAKE_AXIS else -1.0
    brake_percent = round(max(0.0, min(1.0, (brake + 1.0) / 2.0)) * 100, 2)
    accel = axes[config.ACCEL_AXIS] if len(axes) > config.ACCEL_AXIS else -1.0
    accel_percent = round(max(0.0, min(1.0, (accel + 1.0) / 2.0)) * 100, 2)
    headlight = (buttons == config.HEADLIGHT_BUTTONS)
    hazard_light = (buttons == config.HAZARD_LIGHT_BUTTONS)
    horn = (buttons == config.HORN_BUTTONS)
    return {
        "steering_value": steering_value,
        "steering_direction": steering_direction,
        "gear": gear,
        "brake_percent": brake_percent,
        "accel_percent": accel_percent,
        "headlight": headlight,
        "hazard_light": hazard_light,
        "horn": horn
    }
