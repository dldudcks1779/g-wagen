import cv2
import json
import pygame
import socket
import threading
import config
import camera
import joystick_handler

# 전역 변수 초기화
battery_soc = 0                                                             # 배터리 잔량
battery_image = cv2.imread(config.BATTERY_IMAGE_PATH, cv2.IMREAD_UNCHANGED) # 배터리 이미지
battery_mask = None                                                         # 배터리 마스크

# 배터리 이미지 크기 조정
if battery_image is not None:
    battery_image = cv2.resize(battery_image, (120, 120))
    battery_mask = battery_image[:, :, :3] > 0

# 리소스 (카메라, 소켓, 조이스틱, pygame) 정리
def cleanup_resources(cap=None, connection=None, joystick=None):
    if cap:
        try:
            cap.release()
        except Exception as exception:
            print(f"ERROR: 카메라 해제 실패 - {exception}")
    cv2.destroyAllWindows()
    if connection:
        try:
            connection.close()
        except Exception as exception:
            print(f"ERROR: 소켓 종료 실패 - {exception}")
    if joystick:
        try:
            joystick.quit()
        except Exception as exception:
            print(f"ERROR: 조이스틱 정리 실패 - {exception}")
    try:
        pygame.quit()
    except Exception as exception:
        print(f"ERROR: pygame 정리 실패 - {exception}")
        
# TCP 연결 처리
def handle_connection(event):
    while True:
        try:
            connection = socket.create_connection((config.G_WAGEN_HOST, config.G_WAGEN_PORT), timeout=config.G_WAGEN_TCP_NETWORK_CONNECTION_TIMEOUT)
            connection.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
            print(f"연결 성공 ({config.G_WAGEN_HOST}:{config.G_WAGEN_PORT})")
            return connection
        except socket.gaierror as error:
            raise RuntimeError(f"ERROR: 호스트 확인 실패 ({config.G_WAGEN_HOST}) - {error}") from error
        except (socket.timeout, ConnectionRefusedError) as error:
            print(f"ERROR: 연결 실패 ({config.G_WAGEN_HOST}:{config.G_WAGEN_PORT}) - {error}")
            print(f"{config.G_WAGEN_TCP_NETWORK_RETRY_WAIT} 초 후 재시도...")
            if event.wait(config.G_WAGEN_TCP_NETWORK_RETRY_WAIT):
                raise RuntimeError("프로그램 종료 요청")

# 배터리 잔량 수신
def receive_battery_soc(connection, event):
    global battery_soc
    buffer = ""
    while not event.is_set():
        try:
            data = connection.recv(1024).decode("utf-8")
            if not data:
                break
            buffer += data
            while "\n" in buffer:
                line, buffer = buffer.split("\n", 1)
                try:
                    message = json.loads(line)
                    if message.get("type") == "battery":
                        battery_soc = message.get("soc", 0)
                except json.JSONDecodeError:
                    pass
        except socket.timeout:
            continue
        except OSError as error:
            print(f"ERROR: 배터리 잔량 수신 실패 - {error}")
            break

# TCP 연결 설정
def setup_connection(event):
    connection = handle_connection(event)
    connection.settimeout(0.1)
    threading.Thread(target=receive_battery_soc, args=(connection, event), daemon=True).start()
    return connection

# 네트워크 처리
def handle_network(event):
    connection = None
    joystick = None
    try:
        joystick = joystick_handler.init_joystick()
        connection = setup_connection(event)
        while not event.is_set():
            try:
                connection.sendall(f"{json.dumps(joystick_handler.get_joystick_status(joystick), ensure_ascii=False)}\n".encode("utf-8"))
            except OSError:
                connection.close()
                connection = setup_connection(event)
            event.wait(config.G_WAGEN_TCP_NETWORK_INTERVAL)
    except (RuntimeError, KeyboardInterrupt):
        pass
    finally:
        cleanup_resources(connection=connection, joystick=joystick)

# 배터리 잔량 표시
def display_battery_soc(frame, battery_soc, battery_image, battery_mask):
    frame_height, frame_width = frame.shape[:2]
    bar_width, bar_height = config.BATTERY_SOC_BAR_WIDTH, config.BATTERY_SOC_BAR_HEIGHT
    bar_x, bar_y = (frame_width - bar_width) // 2 + config.BATTERY_SOC_BAR_OFFSET_X, frame_height + config.BATTERY_SOC_BAR_OFFSET_Y
    if battery_image is not None and battery_mask is not None:
        image_x, image_y = bar_x + bar_width, bar_y - bar_height
        image_h, image_w = battery_image.shape[:2]
        if image_y >= 0 and image_x >= 0 and image_y + image_h <= frame_height and image_x + image_w <= frame_width:
            frame[image_y:image_y+image_h, image_x:image_x+image_w][battery_mask] = battery_image[:, :, :3][battery_mask]
    overlay_frame = frame.copy()
    cv2.rectangle(overlay_frame, (bar_x, bar_y), (bar_x + bar_width, bar_y + bar_height), (255, 255, 255), -1)
    frame = cv2.addWeighted(overlay_frame, 0.5, frame, 0.5, 0)
    cv2.rectangle(frame, (bar_x, bar_y), (bar_x + int(bar_width * battery_soc / 100), bar_y + bar_height), (0, 0, 255), -1)
    cv2.rectangle(frame, (bar_x, bar_y), (bar_x + bar_width, bar_y + bar_height), (255, 255, 255), 5)
    return frame

if __name__ == "__main__":
    event = threading.Event()
    threading.Thread(target=handle_network, args=(event,), daemon=True).start()
    cap = None
    try:
        cap = camera.create_video_capture()
        camera.setup_fullscreen_window(config.WINDOW_NAME)
        while not event.is_set():
            ret, frame = cap.read()
            if not ret:
                print("프레임 읽기 실패")
                break
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            frame = cv2.flip(frame, -1)
            frame = display_battery_soc(frame, battery_soc, battery_image, battery_mask)
            cv2.imshow(config.WINDOW_NAME, frame)
            if cv2.waitKey(1) == 27:
                break
    except Exception as exception:
        print(exception)
    finally:
        print("프로그램 종료")
        event.set()
        cleanup_resources(cap)
