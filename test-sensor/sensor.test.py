from machine import Pin, I2C
import time
import max30100

i2c = I2C(0, sda=Pin(0), scl=Pin(1), freq=400000)

sensor = max30100.MAX30100(i2c=i2c)

dinamic_average = 0
ALPHA = 0.96
last_beat = 0
beats = []

BEAT_LIMIT = 600
COOLDOWN = 400
MIN_IR = 7000

print("Reading sensor...")

spiked = False


def get_real_bpm(beats, bpm_temp):
    beats.append(bpm_temp)

    if len(beats) > 4:
        beats.pop(0)

    final_bpm = sum(beats) / len(beats)
    print(f"❤ BPM: {final_bpm:.1f}")
    return final_bpm


while True:
    try:
        ir, red = sensor.read_sensor()

        if ir > MIN_IR:
            if dinamic_average == 0:
                dinamic_average = ir

            dinamic_average = (dinamic_average * ALPHA) + (ir * (1.0 - ALPHA))
            signal = (ir - dinamic_average) * -1

            time_now = time.ticks_ms()
            time_diff = time.ticks_diff(time_now, last_beat)

            if signal > BEAT_LIMIT and time_diff > COOLDOWN:
                if not spiked:
                    spiked = True

                    bpm_temp = 60000 / time_diff

                    if 30 < bpm_temp < 220:
                        get_real_bpm(beats, bpm_temp)

                    last_beat = time_now

            if signal < (BEAT_LIMIT * 0.2):
                spiked = False

        else:
            dinamic_average = 0
            beats = []

        time.sleep(0.01)

    except Exception as e:
        print("Error:", e)
        time.sleep(1)
