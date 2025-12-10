from machine import Pin, I2C
import time
import network
import max30100
from umqtt.simple import MQTTClient
import ssl
import json

WIFI_SSID = "Jupiter"
WIFI_PASSWORD = "seilamano"


MQTT_BROKER = "61082143c5fe40d491e1af60d78419ae.s1.eu.hivemq.cloud"
MQTT_USER = "hivemq.webclient.1765288998517"
MQTT_PASSWORD = "01Q$*V9g<7,itwFOkGuP"
MQTT_CLIENT_ID = "PicoW_Sensor_MAX30100"
MQTT_TOPIC = b"sensor/batimentos"
MQTT_PORT = 8883


i2c = I2C(0, sda=Pin(0), scl=Pin(1), freq=400000)
sensor = max30100.MAX30100(i2c=i2c)

beat_led = Pin(2, Pin.OUT)
mqtt_led = Pin(3, Pin.OUT)

dynamic_average = 0
ALPHA = 0.96
last_beat = 0
beats = []
BEAT_LIMIT = 600
COOLDOWN = 400
MIN_IR = 7000


def wifi_connect():
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    if not wlan.isconnected():
        print("Conecting to Wi-Fi...")
        wlan.connect(WIFI_SSID, WIFI_PASSWORD)
        while not wlan.isconnected():
            beat_led.value(1)
            time.sleep(0.6)
            print(".", end="")
            beat_led.value(0)
            time.sleep(0.4)
    print("\nWi-Fi conected, IP:", wlan.ifconfig()[0])


def mqtt_connect():
    print("Conecting to HiveMQ Cloud...")
    mqtt_led.value(1)
    try:
        contexto_ssl = {"server_hostname": MQTT_BROKER}

        client = MQTTClient(
            client_id=MQTT_CLIENT_ID,
            server=MQTT_BROKER,
            port=MQTT_PORT,
            user=MQTT_USER,
            password=MQTT_PASSWORD,
            keepalive=60,
            ssl=True,
            ssl_params=contexto_ssl,
        )
        client.connect()
        print("Conected to HiveMQ!")

        return client
    except Exception as e:
        print("Failed while connecting to HiveMQ:", e)
        return None


wifi_connect()
client = mqtt_connect()
mqtt_led.value(0)
print("Reading sensor...")

spiked = False


while True:
    try:
        ir, red = sensor.read_sensor()

        if ir > MIN_IR:
            if dynamic_average == 0:
                dynamic_average = ir

            dynamic_average = (dynamic_average * ALPHA) + (ir * (1.0 - ALPHA))
            signal = (ir - dynamic_average) * -1

            time_now = time.ticks_ms()
            time_diff = time.ticks_diff(time_now, last_beat)

            if signal > BEAT_LIMIT and time_diff > COOLDOWN:
                if not spiked:
                    spiked = True

                    bpm_temp = 60000 / time_diff
                    beat_led.value(1)
                    bpm_final = None
                    if 30 < bpm_temp < 120:
                        beats.append(bpm_temp)
                        if len(beats) > 4:
                            beats.pop(0)

                        bpm_final = sum(beats) / len(beats)
                        print(f"❤ BPM: {bpm_final:.1f}")

                    if client:
                        try:
                            msg = {"final_bpm": bpm_final, "temp_bpm": bpm_temp, "timestamp": time.ticks_ms()}
                            mqtt_led.value(1)
                            client.publish(MQTT_TOPIC, json.dumps(msg))
                            time.sleep(0.35)
                        except OSError:
                            print("Reconecting to MQTT")
                            client = mqtt_connect()
                        finally:
                            mqtt_led.value(0)
                    beat_led.value(0)
                    last_beat = time_now

            if signal < (BEAT_LIMIT * 0.2):
                spiked = False

        else:
            dynamic_average = 0
            beats = []

        time.sleep(0.01)

    except Exception as e:
        print("Error:", e)
        time.sleep(1)
