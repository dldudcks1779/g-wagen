import RPi.GPIO as GPIO
import asyncio
import config

# LED 초기화
def setup_leds(state: dict):
    for pin in (config.HEADLIGHT_LED_PIN, config.HAZARD_LIGHT_FRONT_LED_PIN, config.HAZARD_LIGHT_BACK_LED_PIN, config.BRAKE_LIGHT_LED_PIN):
        GPIO.setup(pin, GPIO.OUT, initial=GPIO.LOW)
    state["headlight"] = False
    state["hazard_light"] = False
    state["previous_command"] = {"headlight": False, "hazard_light": False}

# 전조등 제어
def control_headlight(pressed: bool, state: dict):
    if pressed and not state["previous_command"]["headlight"]:
        state["headlight"] = not state["headlight"]
        GPIO.output(config.HEADLIGHT_LED_PIN, GPIO.HIGH if state["headlight"] else GPIO.LOW)
    state["previous_command"]["headlight"] = pressed

# 비상등 제어
def control_hazard_light(pressed: bool, state: dict):
    if pressed and not state["previous_command"]["hazard_light"]:
        state["hazard_light"] = not state["hazard_light"]
    state["previous_command"]["hazard_light"] = pressed

# 브레이크등 제어
def control_brake_light(brake_percent: float):
    GPIO.output(config.BRAKE_LIGHT_LED_PIN, GPIO.HIGH if brake_percent > 0 else GPIO.LOW)

# LED 제어
def control_leds(command: dict, state: dict):
    control_headlight(bool(command.get("headlight", False)), state)
    control_hazard_light(bool(command.get("hazard_light", False)), state)
    control_brake_light(float(command.get("brake_percent", 0.0)))

# 비상등 깜빡임 비동기 루프
async def hazard_light_blink_loop(state: dict):
    while True:
        if state.get("hazard_light", False):
            GPIO.output(config.HAZARD_LIGHT_FRONT_LED_PIN, GPIO.HIGH)
            GPIO.output(config.HAZARD_LIGHT_BACK_LED_PIN, GPIO.HIGH)
            await asyncio.sleep(0.5)
            if state.get("hazard_light", False):
                GPIO.output(config.HAZARD_LIGHT_FRONT_LED_PIN, GPIO.LOW)
                GPIO.output(config.HAZARD_LIGHT_BACK_LED_PIN, GPIO.LOW)
                await asyncio.sleep(0.5)
        else:
            GPIO.output(config.HAZARD_LIGHT_FRONT_LED_PIN, GPIO.LOW)
            GPIO.output(config.HAZARD_LIGHT_BACK_LED_PIN, GPIO.LOW)
            await asyncio.sleep(0.1)

# LED 정리
def cleanup_leds():
    for pin in (config.HEADLIGHT_LED_PIN, config.HAZARD_LIGHT_FRONT_LED_PIN, config.HAZARD_LIGHT_BACK_LED_PIN, config.BRAKE_LIGHT_LED_PIN):
        GPIO.output(pin, GPIO.LOW)