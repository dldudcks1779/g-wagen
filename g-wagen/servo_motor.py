import pigpio
import asyncio
import math
import config

# 서보 모터 pigpio 객체
pi = None

# 펄스 폭 변환
def angle_to_pulse_width(angle: float):
    clamped_angle = max(config.SERVO_MOTOR_MIN_ANGLE, min(config.SERVO_MOTOR_MAX_ANGLE, angle))
    ratio = (clamped_angle - config.SERVO_MOTOR_MIN_ANGLE) / (config.SERVO_MOTOR_MAX_ANGLE - config.SERVO_MOTOR_MIN_ANGLE)
    return int(config.SERVO_MOTOR_PULSE_WIDTH_MIN + (config.SERVO_MOTOR_PULSE_WIDTH_MAX - config.SERVO_MOTOR_PULSE_WIDTH_MIN) * ratio)

# 서보 모터 초기화
def setup_servo_motors(state: dict):
    global pi
    pi = pigpio.pi()
    if not pi.connected:
        raise RuntimeError("ERROR: pigpio 데몬 연결 실패")
    state["brake"] = {
        "current_left": config.SERVO_MOTOR_LEFT_BASE_ANGLE,
        "current_right": config.SERVO_MOTOR_RIGHT_BASE_ANGLE,
        "target_left": config.SERVO_MOTOR_LEFT_BASE_ANGLE,
        "target_right": config.SERVO_MOTOR_RIGHT_BASE_ANGLE
    }
    pi.set_servo_pulsewidth(config.LEFT_SERVO_MOTOR_PIN, angle_to_pulse_width(state["brake"]["current_left"]))
    pi.set_servo_pulsewidth(config.RIGHT_SERVO_MOTOR_PIN, angle_to_pulse_width(state["brake"]["current_right"]))

# 서보 모터 제어
def control_servo_motors(command: dict, state: dict):
    brake_percent = float(command.get("brake_percent", 0.0))
    brake_percent = max(0.0, min(100.0, brake_percent)) if abs(brake_percent) >= config.SERVO_MOTOR_DEADBAND_PERCENT else 0.0
    delta = config.SERVO_MOTOR_DEADBAND_DEGREE * (brake_percent / 100.0)
    state["brake"]["target_left"] = max(0, min(180, config.SERVO_MOTOR_LEFT_BASE_ANGLE + max(0, min(config.SERVO_MOTOR_MAX_TRAVEL_DEGREE, delta)) * 10))
    state["brake"]["target_right"] = max(0, min(180, config.SERVO_MOTOR_RIGHT_BASE_ANGLE + max(-config.SERVO_MOTOR_MAX_TRAVEL_DEGREE, min(0, -delta)) * 10))

# 브레이크 업데이트
def update_brake(state_brake: dict, current: str, target: str, degree: float, pin: int):
    difference = state_brake[target] - state_brake[current]
    if abs(difference) > config.SERVO_MOTOR_DEADBAND_DEGREE:
        state_brake[current] += math.copysign(min(abs(difference), degree), difference)
        pi.set_servo_pulsewidth(pin, angle_to_pulse_width(state_brake[current]))

# 브레이크 업데이트 비동기 루프
async def update_brake_loop(state: dict):
    degree = config.SERVO_MOTOR_MAX_DEGREE_PER_SECOND / config.SERVO_MOTOR_FREQUENCY
    while True:
        update_brake(state["brake"], "current_left", "target_left", degree, config.LEFT_SERVO_MOTOR_PIN)
        update_brake(state["brake"], "current_right", "target_right", degree, config.RIGHT_SERVO_MOTOR_PIN)
        await asyncio.sleep(1.0 / config.SERVO_MOTOR_FREQUENCY)

# 서보 모터 정리
def cleanup_servo_motors():
    if pi and pi.connected:
        for pin in (config.LEFT_SERVO_MOTOR_PIN, config.RIGHT_SERVO_MOTOR_PIN):
            pi.set_servo_pulsewidth(pin, 0)
        pi.stop()
