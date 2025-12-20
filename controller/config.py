# CONTROLLER UDP 네트워크 설정
CONTROLLER_HOST = "192.168.0.2" # 호스트 주소
CONTROLLER_PORT = 5000          # 포트 번호
CONTROLLER_UDP_STREAM_OPTIONS = ( # UDP 스트림 옵션
    f"probesize=32"        # 분석 데이터 최소화
    f"&analyzeduration=0"  # 분석 시간 제거
    f"&low_delay=1"        # 저지연 모드
    f"&overrun_nonfatal=1" # 프레임 손실 무시
)

# G-WAGEN TCP 네트워크 설정
G_WAGEN_HOST = "192.168.0.3" # 호스트 주소
G_WAGEN_PORT = 5001          # 포트 번호
G_WAGEN_TCP_NETWORK_CONNECTION_TIMEOUT = 5.0 # 연결 타임아웃
G_WAGEN_TCP_NETWORK_RETRY_WAIT = 5.0         # 재시도 대기 시간
G_WAGEN_TCP_NETWORK_INTERVAL = 0.05          # 상태 전송 간격

# 창 이름
WINDOW_NAME = "G-WAGEN WINDOW"

# 스레드 종료 대기 시간
THREAD_JOIN_TIMEOUT = 5.0

# 조이스틱 매핑 설정
STEER_AXIS = 0                                           # 조향 축
BRAKE_AXIS = 2                                           # 브레이크 축
ACCEL_AXIS = 5                                           # 악셀 축
HEADLIGHT_BUTTONS = (1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0)    # 전조등 버튼
HAZARD_LIGHT_BUTTONS = (0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0) # 비상등 버튼
HORN_BUTTONS = (0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0)         # 클락션 버튼
GEAR_D_BUTTONS = (0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0)       # 주행 기어 버튼
GEAR_R_BUTTONS = (0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0)       # 후진 기어 버튼
GEAR_N_BUTTONS = (0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0)       # 중립 기어 버튼
GEAR_MAP = {
    GEAR_D_BUTTONS: "D",
    GEAR_R_BUTTONS: "R",
    GEAR_N_BUTTONS: "N"
}

# 배터리 잔량 표시 설정
BATTERY_IMAGE_PATH = "images/battery.png" # 배터리 이미지 경로
BATTERY_IMAGE_SIZE = (120, 120)           # 배터리 이미지 크기
BATTERY_SOC_BAR_WIDTH = 800               # 배터리 잔량 바 너비
BATTERY_SOC_BAR_HEIGHT = 40               # 배터리 잔량 바 높이
BATTERY_SOC_BAR_OFFSET_X = -60            # 배터리 잔량 바 X 오프셋
BATTERY_SOC_BAR_OFFSET_Y = -120           # 배터리 잔량 바 Y 오프셋