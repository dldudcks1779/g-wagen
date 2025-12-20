# G-WAGEN TCP 서버 설정
HOST = "0.0.0.0" # 호스트 주소
PORT = 5001      # 포트 번호

# GPIO 핀 번호 (BCM)
HEADLIGHT_LED_PIN = 13         # 전조등 LED
HAZARD_LIGHT_FRONT_LED_PIN = 6 # 비상등 앞 LED
HAZARD_LIGHT_BACK_LED_PIN = 12 # 비상등 뒤 LED
BRAKE_LIGHT_LED_PIN = 5        # 브레이크등 LED
DRIVE_DC_MOTOR_PIN = 20        # 전진 DC 모터 
REVERSE_DC_MOTOR_PIN = 26      # 후진 DC 모터
LEFT_DC_MOTOR_PIN = 16         # 좌회전 DC 모터
RIGHT_DC_MOTOR_PIN = 19        # 우회전 DC 모터
LEFT_SERVO_MOTOR_PIN = 14      # 왼쪽 서보 모터
RIGHT_SERVO_MOTOR_PIN = 15     # 오른쪽 서보 모터
HONK_SPEAKER_PIN = 4           # 경적 스피커

# 서보 모터 설정
SERVO_MOTOR_MIN_ANGLE = 0.0               # 최소 각도
SERVO_MOTOR_MAX_ANGLE = 180.0             # 최대 각도
SERVO_MOTOR_PULSE_WIDTH_MIN = 500         # 펄스 폭 최솟값 (μs)
SERVO_MOTOR_PULSE_WIDTH_MAX = 2500        # 펄스 폭 최댓값 (μs)
SERVO_MOTOR_LEFT_BASE_ANGLE = 85          # 왼쪽 기준 각도
SERVO_MOTOR_RIGHT_BASE_ANGLE = 30         # 오른쪽 기준 각도
SERVO_MOTOR_MAX_TRAVEL_DEGREE = 10.0      # 최대 이동 각도
SERVO_MOTOR_DEADBAND_PERCENT = 1.0        # 입력 신호 무시 구간 (%)
SERVO_MOTOR_DEADBAND_DEGREE = 1.0         # 목표 각도 도달 시 허용 오차 (°)
SERVO_MOTOR_FREQUENCY = 50                # 주파수 (Hz)
SERVO_MOTOR_MAX_DEGREE_PER_SECOND = 180.0 # 최대 회전 속도 (°/s)

# I2C 통신 설정 (MAX17043 배터리 잔량 측정 IC)
MAX17043_I2C_ADDRESS = 0x36  # MAX17043 칩의 I2C 장치 주소
MAX17043_SOC_REGISTER = 0x04 # 칩 내부의 배터리 잔량(SoC) 값이 저장된 레지스터 주소

# 배터리 체크 주기 (초)
BATTERY_CHECK_INTERVAL_SECONDS = 5.0