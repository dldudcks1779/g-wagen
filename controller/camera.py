import cv2
import config

# VideoCapture 객체 생성 및 스트림 열기
def create_video_capture():
    try:
        cap = cv2.VideoCapture(f"udp://{config.CONTROLLER_HOST}:{config.CONTROLLER_PORT}?{config.CONTROLLER_UDP_STREAM_OPTIONS}", cv2.CAP_FFMPEG)
    except Exception as exception:
        raise RuntimeError(f"ERROR: VideoCapture 객체 생성 실패 - {exception}") from exception
    if not cap.isOpened():
        cap.release()
        raise RuntimeError(f"ERROR: 스트림 열기 실패")
    return cap

# 전체 화면 창 설정
def setup_fullscreen_window(window_name):
    cv2.namedWindow(window_name, cv2.WINDOW_NORMAL)
    cv2.setWindowProperty(window_name, cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)