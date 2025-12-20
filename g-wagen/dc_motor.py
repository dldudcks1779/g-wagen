import RPi.GPIO as GPIO
import config

# DC 모터 PWM 객체
pwm_drive = None
pwm_reverse = None
pwm_left_steering = None
pwm_right_steering = None

# DC 모터 초기화
def setup_dc_motors(state: dict):
    global pwm_drive, pwm_reverse, pwm_left_steering, pwm_right_steering
    for pin in (config.DRIVE_DC_MOTOR_PIN, config.REVERSE_DC_MOTOR_PIN, config.LEFT_DC_MOTOR_PIN, config.RIGHT_DC_MOTOR_PIN):
        GPIO.setup(pin, GPIO.OUT, initial=GPIO.LOW)
    pwm_drive = GPIO.PWM(config.DRIVE_DC_MOTOR_PIN, 500)
    pwm_reverse = GPIO.PWM(config.REVERSE_DC_MOTOR_PIN, 500)
    pwm_left_steering = GPIO.PWM(config.LEFT_DC_MOTOR_PIN, 500)
    pwm_right_steering = GPIO.PWM(config.RIGHT_DC_MOTOR_PIN, 500)
    for pwm in (pwm_drive, pwm_reverse, pwm_left_steering, pwm_right_steering):
        pwm.start(0)
    state["gear"] = "N"

# 전진 (D)
def drive(accel_percent: float):
    pwm_reverse.ChangeDutyCycle(0)
    pwm_drive.ChangeDutyCycle(accel_percent)

# 후진 (R)
def reverse(accel_percent: float):
    pwm_drive.ChangeDutyCycle(0)
    pwm_reverse.ChangeDutyCycle(accel_percent)

# 중립 (N)
def neutral():
    pwm_drive.ChangeDutyCycle(0)
    pwm_reverse.ChangeDutyCycle(0)

# 기어 제어
def control_gear(gear: str, brake_percent: float, accel_percent: float, state: dict):
    if brake_percent > 50 and gear in ("D", "R", "N"):
        state["gear"] = gear
    current_gear = state.get("gear", "N")
    if current_gear == "D":
        drive(accel_percent)
    elif current_gear == "R":
        reverse(accel_percent)
    else:
        neutral()

# 좌회전
def left_steering(steering_percent: float):
    pwm_right_steering.ChangeDutyCycle(0)
    pwm_left_steering.ChangeDutyCycle(steering_percent)

# 우회전
def right_steering(steering_percent: float):
    pwm_left_steering.ChangeDutyCycle(0)
    pwm_right_steering.ChangeDutyCycle(steering_percent)

# 조향 중앙
def center_steering():
    pwm_left_steering.ChangeDutyCycle(0)
    pwm_right_steering.ChangeDutyCycle(0)

# 조향 제어
def control_steering(steering_value: float, steering_direction: str):
    if steering_direction == "LEFT":
        left_steering(abs(steering_value) * 100)
    elif steering_direction == "RIGHT":
        right_steering(abs(steering_value) * 100)
    else:
        center_steering()

# DC 모터 제어
def control_dc_motors(command: dict, state: dict):
    steering_value = command.get("steering_value", 0.0)
    steering_direction = command.get("steering_direction", "CENTER")
    gear = command.get("gear", "N")
    brake_percent = float(command.get("brake_percent", 0.0))
    accel_percent = float(command.get("accel_percent", 0.0))
    control_gear(gear, brake_percent, accel_percent, state)
    control_steering(steering_value, steering_direction)

# DC 모터 정리
def cleanup_dc_motors():
    for pwm in (pwm_drive, pwm_reverse, pwm_left_steering, pwm_right_steering):
        if pwm:
            pwm.stop()