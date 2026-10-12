# mqttlog

Small CLI for MQTT-style **topic logs** sitting on disk. I use it when a broker dump is a text file and I want rotation + CSV without standing up mosquitto again.

No network. Records are one line:

```
<iso-timestamp> <topic> <payload...>
```

## Install

```
python3 -m pip install -e .
```

Or just run from the repo: `PYTHONPATH=. python3 -m mqttlog …`

## Commands

Simulate a few lab sensors:

```
$ PYTHONPATH=. python3 -m mqttlog sim --count 3
2026-10-13T20:11:00-07:00 sensors/lab/temp 20.0
2026-10-13T20:11:15-07:00 sensors/lab/rh 41
2026-10-13T20:11:30-07:00 sensors/door/state closed
```

Replay only `sensors/#` into rotating files:

```
$ PYTHONPATH=. python3 -m mqttlog replay sample.log --topic 'sensors/#' --out logs/ --max-bytes 4096
wrote 2 records to logs/mqttlog-000.log
```

CSV:

```
$ PYTHONPATH=. python3 -m mqttlog csv sample.log --topic 'sensors/+' --out -
ts,topic,payload
2026-10-13T20:11:00-07:00,sensors/lab/temp,20.0
```

`+` is one topic level. `#` is the rest of the path, MQTT-style.

## Tests

```
python3 -m unittest discover -s tests -v
```

MIT. Issues and small patches welcome.
