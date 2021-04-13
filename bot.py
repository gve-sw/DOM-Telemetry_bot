"""
Copyright (c) 2021 Cisco and/or its affiliates.
This software is licensed to you under the terms of the Cisco Sample
Code License, Version 1.1 (the "License"). You may obtain a copy of the
License at
               https://developer.cisco.com/docs/licenses
All use of the material herein must be in accordance with the terms of
the License. All rights not expressly granted by the License are
reserved. Unless required by applicable law or agreed to separately in
writing, software distributed under the License is distributed on an "AS
IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express
or implied.
"""

from flask import Flask, request, jsonify
from webexteamssdk import WebexTeamsAPI
import os

# get environment variables
WT_BOT_TOKEN = os.environ['WT_BOT_TOKEN']
WT_ROOM_ID = os.environ['WT_ROOM_ID']

# start Flask and WT connection
app = Flask(__name__)
api = WebexTeamsAPI(access_token=WT_BOT_TOKEN)

# defining the decorator and route registration for incoming alerts
@app.route('/', methods=['POST'])
def alert_received():
    raw_json = request.get_json()
    print(raw_json)
    state = raw_json['state']

    if state == 'alerting':
        alert_name = raw_json['ruleName']
        notification_alert = (
            f"🚨🚨🚨 **DOM Alert:** Thresholds exceeded for **{alert_name}** at following transceiver(s):"
        )
        api.messages.create(roomId=WT_ROOM_ID, markdown=notification_alert)

        evalMatches = raw_json['evalMatches']
        messages = []
        for match in evalMatches:
            exists = False
            for message in messages:
                if match['tags']['host'] == message['device']:
                    exists = True
                    break
            if exists == False:
                threshold_value = round(match['value'], 3)
                device = match['tags']['host']
                media_type = match['tags']['media_type']
                matches = (f"🔔 {media_type} at {device} reached a value of {threshold_value}.")
                message_add = {"threshold_value": threshold_value, "device": device, "media_type": media_type}
                messages.append(message_add)
                api.messages.create(roomId=WT_ROOM_ID, markdown=matches)

    return jsonify({'success': True})

if __name__=="__main__":
    app.run()