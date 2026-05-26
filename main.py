#!/usr/bin/env python3
import serial
import time
import os
import requests

SERIAL_PORT = os.getenv("SERIAL_PORT", "/dev/ttyACM0")
BAUD_RATE = int(os.getenv("BAUD_RATE", "2560"))
TIMEOUT = float(os.getenv("TIMEOUT", "0.1"))

ENABLE_UPTIME_KUMA = os.getenv("ENABLE_UPTIME_KUMA", "true").lower() == "true"
ENABLE_HOME_ASSISTANT = os.getenv("ENABLE_HOME_ASSISTANT", "true").lower() == "true"

REQUEST_HEX = os.environ["UPS_REQUEST_HEX"]
REQUEST = bytes.fromhex(REQUEST_HEX)

UPTIME_KUMA_URL = os.getenv("UPTIME_KUMA_URL")
HA_WEBHOOK_URL = os.getenv("HA_WEBHOOK_URL")


def push_kuma(status: str, msg: str):
    if not ENABLE_UPTIME_KUMA or not UPTIME_KUMA_URL:
        return
    try:
        requests.get(
            UPTIME_KUMA_URL,
            params={"status": status, "msg": msg, "ping": ""},
            timeout=5
        )
    except Exception as e:
        print("Error Uptime Kuma:", e)


def push_homeassistant(payload: dict):
    if not ENABLE_HOME_ASSISTANT or not HA_WEBHOOK_URL:
        return
    try:
        requests.post(
            HA_WEBHOOK_URL,
            json=payload,
            timeout=5
        )
    except Exception as e:
        print("Error Home Assistant:", e)


def parse_frame(data: bytes):
    hex_str = ''.join(f'{b:02x}' for b in data)

    if not (hex_str.startswith("aa21") and len(hex_str) >= 62):
        return None

    raw_battery = int(hex_str[22:24], 16)
    raw_charge  = int(hex_str[16:18], 16)
    raw_input   = int(hex_str[52:54], 16)
    raw_output  = int(hex_str[54:56], 16)
    raw_temp    = int(hex_str[30:32], 16)
    raw_load    = int(hex_str[28:30], 16)

    battery_charge  = round(raw_charge * 0.393)
    battery_voltage = round((raw_battery * 0.1342) / 2, 2)
    input_voltage   = round(raw_input * 1.06)
    output_voltage  = round(raw_output * 1.06)

    if input_voltage < 100:
        ups_status = "Low Battery" if battery_charge < 30 else "On Battery"
    else:
        ups_status = "Online"

    if battery_charge < 5:
        ups_status = "Replace Battery"

    return {
        "status": ups_status,
        "battery_percentage": battery_charge,
        "battery_voltage": battery_voltage,
        "input_voltage": input_voltage,
        "output_voltage": output_voltage,
        "load": raw_load,
        "temperature": raw_temp,
    }


def main():
    with serial.Serial(SERIAL_PORT, BAUD_RATE, timeout=TIMEOUT) as ser:
        while True:
            ser.reset_input_buffer()
            ser.write(REQUEST)
            time.sleep(0.5)

            metrics = parse_frame(ser.read(64))
            if not metrics:
                time.sleep(1)
                continue

            print("UPS:", metrics)

            if metrics["status"] == "Online":
                push_kuma("up", "ok")
            else:
                push_kuma("down", metrics["status"])

            push_homeassistant(metrics)

            time.sleep(1)


if __name__ == "__main__":
    main()
