# Python satelles

Satelles for the Rerum Imperium project. In Python

## Setup

Create the config file from template (then edit it to suit your env)

```shell
cp config.template.yml config.yml
```

Create a virtualenv with

```shell
python3.13 -m venv venv
```

Install with sensor (need Raspberry Pi)

```shell
pip install -e '.[sensor]'
```

Install with dev dependencies

```shell
pip install -e '.[dev]'
```

## Run the satelles

```shell
python -m satelles_python
```

## Run lint

```shell
ruff check satelles_python
```

## Install as a service

In `/lib/systemd/system/satelles-python.service`, write

```
[Unit]
Description=Satelles python - run your things
Documentation=https://github.com/AymericBebert/satelles-python
After=network.target

[Service]
Type=simple
User=root
WorkingDirectory=/home/pi/satelles-python
ExecStart=/home/pi/.nvm/versions/node/v20.18.0/bin/node /home/pi/satelles-python/dist/server.js
Restart=on-failure

[Install]
WantedBy=multi-user.target
```

Then enable the service

```bash
sudo systemctl enable satelles-python
sudo systemctl start satelles-python
```
