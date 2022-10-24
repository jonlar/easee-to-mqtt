import asyncio
from operator import eq
import os
from datetime import datetime, timezone, timedelta
from xmlrpc.client import _iso8601_format
from dateutil import parser
from typing import List
from pyeasee import Easee, Charger, Site, Circuit, Equalizer, DatatypesStreamData, EqualizerStreamData
import random
import mqtt
import json

async def async_main():
    usernameEnv = 'EASEE_USERNAME'
    passwordEnv = 'EASEE_PASSWORD'
    mqttBroker = 'MQTT_BROKER'

    for k in [usernameEnv, passwordEnv]:
        if k not in os.environ:
            raise Exception('{} is not set in environment'.format(k))

    easee = Easee(os.environ.get(usernameEnv), os.environ.get(passwordEnv))
    broker = mqtt.connect(os.environ.get(mqttBroker, "127.0.0.1"))

    chargers: List[Charger] = await easee.get_chargers()
    equalizers = []
    sites: List[Site] = await easee.get_sites()
    for site in sites:
        equalizers_site = site.get_equalizers()
        for equalizer in equalizers_site:
            equalizers.append(equalizer)

    for equalizer in equalizers:
        lastPulse = None
        while True:
            state = await equalizer.get_state()
            data = state.get_data()
            latestPulse = parser.isoparse('{}'.format(
                data.get('latestPulse')).replace(' ', 'T'))
            if lastPulse and lastPulse == latestPulse:
                await asyncio.sleep(4)

            if lastPulse != latestPulse:
                power = {'latestPulse': '{}'.format(latestPulse),
                         'activePowerImport': round(float(data.get('activePowerImport')) * 1000, 2),
                         'currentL1': float(data.get('currentL1')),
                         'currentL2': float(data.get('currentL2')),
                         'currentL3': float(data.get('currentL3')),
                         'voltageL1': float(data.get('voltageNL1')),
                         'voltageL2': float(data.get('voltageNL2')),
                         'voltageL3': float(data.get('voltageNL3'))
                         }
                broker.publish('easee/equalizer', json.dumps(power))
                lastPulse = latestPulse

            now = datetime.now(timezone.utc)
            nextPulse = latestPulse + timedelta(seconds=10)
            sleepTime = (nextPulse - now).total_seconds()

            await asyncio.sleep(sleepTime + 3)

    await easee.close()


if __name__ == "__main__":
    asyncio.run(async_main())

