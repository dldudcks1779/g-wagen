import asyncio
import functools
import json
import signal
import RPi.GPIO as GPIO
import config
import led
import dc_motor
import servo_motor
import speaker
import battery

# 상태 딕셔너리
state = {}

# 현재 연결된 TCP 클라이언트 목록
ACTIVE_WRITERS = set()

# 모듈 (LED, DC 모터, 서보 모터, 스피커) 설정
def setup_modules(state: dict):
    led.setup_leds(state)
    dc_motor.setup_dc_motors(state)
    servo_motor.setup_servo_motors(state)
    speaker.setup_speaker()

# 모듈 (LED, DC 모터, 서보 모터, 스피커) 제어
async def control_modules(command: dict, state: dict):
    led.control_leds(command, state)
    dc_motor.control_dc_motors(command, state)
    servo_motor.control_servo_motors(command, state)
    speaker.honk(bool(command.get("horn", False)))

# 모듈 (LED, DC 모터, 서보 모터, 스피커) 정리
def cleanup_modules():
    try:
        led.cleanup_leds()
        dc_motor.cleanup_dc_motors()
        servo_motor.cleanup_servo_motors()
        speaker.cleanup_speaker()
    except Exception as exception:
        print(f"ERROR: 모듈 정리 실패 - {exception}")

# 리소스 (I2C, GPIO) 정리
def cleanup_resources(smbus=None):
    if smbus:
        try:
            smbus.close()
        except Exception as exception:
            print(f"ERROR: SMBus 종료 실패 - {exception}")
    try:
        GPIO.cleanup()
    except Exception as exception:
        print(f"ERROR: GPIO 정리 실패 - {exception}")

# SIGTERM 신호 처리기
def handle_sigterm(signum, frame):
    raise KeyboardInterrupt()

# SIGTERM 신호 처리 등록
signal.signal(signal.SIGTERM, handle_sigterm)

# TCP 연결 처리 비동기 루프
async def handle_connection_loop(stream_reader: asyncio.StreamReader, stream_writer: asyncio.StreamWriter, state: dict):
    peername = stream_writer.get_extra_info("peername")
    print(f"클라이언트 접속: {peername}")
    ACTIVE_WRITERS.add(stream_writer)
    try:
        while True:
            line = await stream_reader.readline()
            if not line:
                break
            try:
                command = json.loads(line.decode("utf-8").strip())
                await control_modules(command, state)
            except json.JSONDecodeError as error:
                print(f"ERROR: JSON 파싱 실패 - {error} (내용: {line.strip()})")
            except Exception as error:
                print(f"ERROR: 명령 처리 중 오류 - {error}")
    except (asyncio.CancelledError, ConnectionResetError):
        pass
    finally:
        print(f"클라이언트 연결 종료: {peername}")
        ACTIVE_WRITERS.discard(stream_writer)
        stream_writer.close()
        await stream_writer.wait_closed()

# 배터리 잔량 전송 비동기 루프
async def send_battery_soc_loop(smbus: battery.smbus2.SMBus):
    while True:
        try:
            soc = battery.get_battery_soc(smbus)
            print(f"배터리 잔량: {soc}%")
            message = json.dumps({"type": "battery", "soc": round(soc, 2)}).encode() + b"\n"
            ACTIVE_WRITERS.difference_update({w for w in ACTIVE_WRITERS if w.is_closing()})
            for stream_writer in list(ACTIVE_WRITERS):
                try:
                    stream_writer.write(message)
                    await stream_writer.drain()
                except (ConnectionResetError, BrokenPipeError):
                    ACTIVE_WRITERS.discard(stream_writer)
        except Exception as exception:
            print(f"ERROR: 배터리 잔량 전송 오류 - {exception}")
        await asyncio.sleep(config.BATTERY_CHECK_INTERVAL_SECONDS)

# 메인 비동기 함수
async def main(state: dict, smbus):
    client = functools.partial(handle_connection_loop, state=state)
    server = await asyncio.start_server(client, config.HOST, config.PORT)
    async with server:
        await asyncio.gather(
            server.serve_forever(),
            led.hazard_light_blink_loop(state),
            servo_motor.update_brake_loop(state),
            send_battery_soc_loop(smbus)
        )

if __name__ == "__main__":
    try:
        GPIO.setmode(GPIO.BCM)
        setup_modules(state)
        smbus = battery.init_smbus()        
        asyncio.run(main(state, smbus))
    except Exception as exception:
        print(exception)
    finally:
        print("프로그램 종료")
        cleanup_modules()
        cleanup_resources(smbus)
