#!/usr/bin/env python3
""" Script to get MyEnergi Zappi data and send it to InfluxDB """

import sys
import time
import datetime
import signal
import json
import argparse
import requests
from requests.auth import HTTPDigestAuth

# load the settings.json file
try:
    with open("settings.json", encoding="utf8") as f:
        settings = json.load(f)
except FileNotFoundError:
    print("settings.json not found.")
    print("Make sure you copy settings.json.example to settings.json and edit it.")
    sys.exit(1)
except json.decoder.JSONDecodeError as e:
    print(f"Error in settings.json - {e}")
    sys.exit(1)


def signal_handler(sig, frame):
    """
    Signal handler to exit gracefully
    """
    # avoid unused variable warning
    if frame:
        pass

    # print a message and exit
    print(f"\nExiting on signal {sig}")
    sys.exit(0)


def get_data_from_myenergi(url):
    """
    Get the data from the myenergi API

    :param url:
    :type url:
    :return:
    :rtype:
    """

    headers = {"User-Agent": "Wget/1.14 (linux-gnu)"}
    response = requests.get(
        url,
        headers=headers,
        auth=HTTPDigestAuth(settings["myenergi"]["serial"], settings["myenergi"]["apikey"]),
        timeout=settings["myenergi"].get("timeout", 5),
    )

    if response.status_code == 200:
        pass  # "Login successful..")
    elif response.status_code == 401:
        print("Login unsuccessful. Please check username, password or URL.")
        sys.exit(2)
    else:
        print("Login unsuccessful. Return code: " + str(response.status_code))
        sys.exit(2)
    return response.json()


def dayhour_results(year, month, day, hour=None):
    """
    Get the data for a specific day

    :param year:
    :type year: str
    :param month:
    :type month: str
    :param day:
    :type day: str
    :param hour:
    :type hour: str
    :return:
    :rtype: dict
    """
    dayhour_url = settings["myenergi"]["dayhour_url"] + settings["myenergi"]["serial"]
    response_data = get_data_from_myenergi(dayhour_url + "-" + str(year) + "-" + str(month) + "-" + str(day))
    charge_amount = 0
    import_amount = 0
    export_amount = 0
    genera_amount = 0

    if response_data.get("U" + settings["myenergi"]["serial"], False):
        for item in response_data["U" + settings["myenergi"]["serial"]]:
            if hour and item.get("hr", -1) == int(hour):
                charge_amount = item.get("h1d", 0)
                import_amount = item.get("imp", 0)
                export_amount = item.get("exp", 0)
                genera_amount = item.get("gep", 0)
                break
            charge_amount += item.get("h1d", 0)
            import_amount += item.get("imp", 0)
            export_amount += item.get("exp", 0)
            genera_amount += item.get("gep", 0)

    data = {
        "Charge": (charge_amount / 3600 / 1000),
        "Import": (import_amount / 3600 / 1000),
        "Export": (export_amount / 3600 / 1000),
        "Genera": (genera_amount / 3600 / 1000),
    }

    return data


def parse_zappi_data():
    """
    Parse the data from the myenergi to get the values we want

    :return: data
    :rtype: dict
    """
    myenergi_data = get_data_from_myenergi(settings["myenergi"]["zappi_url"])

    now = datetime.datetime.now()
    day_data = dayhour_results(now.strftime("%Y"), now.strftime("%m"), now.strftime("%d"), now.strftime("%-H"))

    # just extract the specific fields we want here
    if "zappi_fields" in settings["myenergi"]:
        zappi_data = dict(
            (k, myenergi_data["zappi"][0][k])
            for k in settings["myenergi"]["zappi_fields"]
            if k in myenergi_data["zappi"][0]
        )
    else:
        zappi_data = myenergi_data["zappi"][0]

    return zappi_data | day_data


def send_data_to_influx(data):
    """
    Sends data to influxDB

    :param data: data to send to InfluxDB
    :type data: dict
    :return: None
    """

    # minimalist activity indicator
    print(" ^", end="\r")

    # format the data to send
    data_to_send = "myenergi,device=zappi " + ",".join([f"{key}={value}" for key, value in data.items()])

    # send to InfluxDB
    url = f"{settings['influx']['url']}/write?db={settings['influx']['db']}&precision=s"
    try:
        response = requests.post(
            url,
            auth=(settings["influx"]["user"], settings["influx"]["password"]),
            data=data_to_send,
            timeout=settings["influx"].get("timeout", 5),
        )
        response.raise_for_status()
    except requests.exceptions.RequestException as ex:
        print(f"Error sending data to InfluxDB - {ex}")

    # minimalist activity indicator
    print(" _", end="\r")


def main():
    """
    The main function
    """

    # register the signal handler for ctrl-c
    signal.signal(signal.SIGINT, signal_handler)

    # parse the command line arguments
    arg_parse = argparse.ArgumentParser(description="Send MyEnergi Zappi data to InfluxDB")
    arg_parse.add_argument(
        "-d",
        "--dump",
        required=False,
        action="store_true",
        help="dump the Zappi data from myenergi to the console",
    )
    arg_parse.add_argument(
        "-p",
        "--print",
        required=False,
        action="store_true",
        help="print the data rather than sending it to InfluxDB",
    )
    args = arg_parse.parse_args()

    # dump the data if required and exit
    if args.dump:
        zappi_data = parse_zappi_data()
        print(json.dumps(zappi_data, indent=4))
        sys.exit(0)

    # main loop to collect and send data to InfluxDB
    next_update = time.time()
    while True:
        next_update += settings["interval"]

        # get the parsed data
        data = parse_zappi_data()

        # print or send the data
        if args.print:
            blob = {"time": time.strftime("%a, %d %b %Y, %H:%M:%S %Z", time.localtime()), "data": data}
            print(json.dumps(blob, indent=4))
        else:
            send_data_to_influx(data)

        # Sleep until the next interval
        sleep_time = max(0, next_update - time.time())
        time.sleep(sleep_time)


if __name__ == "__main__":
    main()
