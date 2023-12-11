#!/usr/bin/env python3

import data
import json
import pickle


def process_data():
    names = {
        "6c:4a:85:36:c0:14": "Apple TV",
        "68:37:e9:d2:26:0d": "Amazon Echo Dot",
        "80:7d:3a:2f:dc:51": "Smart bulb",
        "d8:0d:17:33:c2:52": "Smart bulb"
    }
    records = json.loads(data.data)
    filtered = []
    for record in records:
        if record["macAddress"] in names:
            record["device"] = names[record["macAddress"]]
            filtered.append(record)

    return sorted(
        filtered, key=lambda r: r["lastAccessed"], reverse=True)[:130]


def process_data_json():
    return json.dumps(process_data(), separators=(',', ':'))


if __name__ == "__main__":
    neo = process_data()
    print(neo[0])
    print(neo[-1])
    print(len(neo))
    print(process_data_json())
    print(len(process_data_json()))
