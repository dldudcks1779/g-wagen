import RPi.GPIO as GPIO
import config

# 스피커 PWM 객체
pwm_speaker = None

# 스피커 초기화
def setup_speaker():
    global pwm_speaker
    GPIO.setup(config.HONK_SPEAKER_PIN, GPIO.OUT, initial=GPIO.LOW)
    pwm_speaker = GPIO.PWM(config.HONK_SPEAKER_PIN, 500)
    pwm_speaker.start(0)

# 경적 제어
def honk(play: bool):
    if pwm_speaker:
        pwm_speaker.ChangeDutyCycle(50 if play else 0)

# 스피커 정리
def cleanup_speaker():
    honk(False)
    if pwm_speaker:
        pwm_speaker.stop()
