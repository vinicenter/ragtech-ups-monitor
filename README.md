# Ragtech UPS Monitor

A Python-based monitoring solution for Ragtech UPS systems with serial communication support. This tool monitors UPS status and sends alerts to Uptime Kuma and Home Assistant.

This script was only tested with Ragtech 1200VA UPS, but it may work with other models as well, maybe with some adjustments.
This script only works if the UPS is connected via serial (USB). It does not support network monitoring.

If you have tested this with other models, please open an issue or PR.
Share with the community!

## Features

- 📊 Real-time UPS monitoring via serial communication
- 🔋 Battery voltage and charge percentage tracking
- 🌡️ Temperature monitoring
- ⚡ Load usage detection
- 📢 Uptime Kuma integration for status notifications
- 🏠 Home Assistant webhook support for metrics
- 🐳 Docker support with Docker Compose

## Monitored Metrics

- **UPS Status**: Online, On Battery, Low Battery, Replace Battery
- **Battery Percentage**: Current charge level
- **Battery Voltage**: Voltage measurement
- **Load**: Current load on the UPS
- **Temperature**: UPS temperature

## Requirements

- Python 3.12+ (or Docker)
- Serial connection to Ragtech UPS
- (Optional) Uptime Kuma instance
- (Optional) Home Assistant instance

## Installation

### Docker Compose (Recommended)

#### Option 1: Using Pre-built Image

1. Create a directory and download the configuration files:
```bash
mkdir ragtech-ups-monitor && cd ragtech-ups-monitor
wget https://raw.githubusercontent.com/vinicenter/ragtech-ups-monitor/main/docker-compose.yml
wget https://raw.githubusercontent.com/vinicenter/ragtech-ups-monitor/main/.env.example
cp .env.example .env
```

2. Update `docker-compose.yml` to use the pre-built image:
```yaml
version: '3.8'

services:
  ups-monitor:
    image: vinicenter/ragtech-ups-monitor:latest
    container_name: ragtech-ups-monitor
    restart: unless-stopped
    devices:
      - /dev/ttyUSB0:/dev/ttyUSB0
    env_file:
      - .env
    environment:
      - SERIAL_PORT=${SERIAL_PORT:-/dev/ttyUSB0}
      - BAUD_RATE=${BAUD_RATE:-2560}
      - TIMEOUT=${TIMEOUT:-0.1}
      - UPS_REQUEST_HEX=${UPS_REQUEST_HEX}
      - ENABLE_UPTIME_KUMA=${ENABLE_UPTIME_KUMA:-true}
      - ENABLE_HOME_ASSISTANT=${ENABLE_HOME_ASSISTANT:-true}
      - UPTIME_KUMA_URL=${UPTIME_KUMA_URL}
      - HA_WEBHOOK_URL=${HA_WEBHOOK_URL}
    privileged: true
```

3. Configure your `.env` file and start the service:
```bash
docker-compose up -d
```

#### Option 2: Building from Source

1. Clone the repository:
```bash
git clone https://github.com/vinicenter/ragtech-ups-monitor.git
cd ragtech-ups-monitor
```

2. Copy the example environment file:
```bash
cp .env.example .env
```

3. Edit `.env` with your configuration:
```env
# Serial port where the UPS is connected
SERIAL_PORT=/dev/ttyUSB0

# Baud rate for serial communication
BAUD_RATE=2560

# Timeout for serial communication in seconds
TIMEOUT=0.1

# Hex command to request UPS data
# Tested value for Ragtech 1200VA: AA0400801E9E
UPS_REQUEST_HEX=AA0400801E9E

# Enable/disable integrations
ENABLE_UPTIME_KUMA=true
ENABLE_HOME_ASSISTANT=true

# Your Uptime Kuma push URL
UPTIME_KUMA_URL=https://uptimekuma.example.com/api/push/YOUR_PUSH_KEY

# Your Home Assistant webhook URL
HA_WEBHOOK_URL=https://homeassistant.example.com/api/webhook/YOUR_WEBHOOK_ID
```

4. Adjust the serial port in `docker-compose.yml` if needed (default is `/dev/ttyUSB0`)

5. Start the service:
```bash
docker-compose up -d
```

6. View logs:
```bash
docker-compose logs -f
```

### Manual Installation

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Set environment variables or create a `.env` file.

3. Run the monitor:
```bash
python main.py
```

## Configuration

### Environment Variables

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `SERIAL_PORT` | No | `/dev/ttyACM0` | Serial port where UPS is connected |
| `BAUD_RATE` | No | `2560` | Baud rate for serial communication |
| `TIMEOUT` | No | `0.1` | Timeout for serial communication (seconds) |
| `UPS_REQUEST_HEX` | **Yes** | - | Hex command to request UPS data |
| `ENABLE_UPTIME_KUMA` | No | `true` | Enable Uptime Kuma integration |
| `ENABLE_HOME_ASSISTANT` | No | `true` | Enable Home Assistant integration |
| `UPTIME_KUMA_URL` | No* | - | Uptime Kuma push URL |
| `HA_WEBHOOK_URL` | No* | - | Home Assistant webhook URL |

\* Required if the corresponding integration is enabled

### Finding Your Serial Port

On Linux:
```bash
# List all serial devices
ls /dev/tty*

# Or use dmesg after connecting the UPS
dmesg | grep tty
```

Common ports: `/dev/ttyUSB0`, `/dev/ttyACM0`, `/dev/ttyS0`

### Finding the UPS Request Hex

The `UPS_REQUEST_HEX` value is specific to your UPS model. For Ragtech 1200VA, use: `AA0400801E9E`

If you have a different model, you may need to debug the protocol and find the correct command.
Maybe even modify the code to suit your model.
If you have tested other models, please open an issue or PR to share it with the community!

## Docker Compose Examples

### Basic Setup
```yaml
version: '3.8'

services:
  ups-monitor:
    build: .
    container_name: ragtech-ups-monitor
    restart: unless-stopped
    devices:
      - /dev/ttyUSB0:/dev/ttyUSB0
    environment:
      - SERIAL_PORT=/dev/ttyUSB0
      - BAUD_RATE=2560
      - UPS_REQUEST_HEX=AA0400801E9E
      - ENABLE_UPTIME_KUMA=true
      - ENABLE_HOME_ASSISTANT=true
      - UPTIME_KUMA_URL=https://uptimekuma.example.com/api/push/abc123
      - HA_WEBHOOK_URL=https://homeassistant.example.com/api/webhook/xyz789
    privileged: true
```

### With Pre-built Image
```yaml
version: '3.8'

services:
  ups-monitor:
    image: vinicenter/ragtech-ups-monitor:latest
    container_name: ragtech-ups-monitor
    restart: unless-stopped
    devices:
      - /dev/ttyUSB0:/dev/ttyUSB0
    env_file:
      - .env
    privileged: true
```

### Multiple UPS Monitoring
```yaml
version: '3.8'

services:
  ups-monitor-1:
    build: .
    container_name: ups-monitor-1
    restart: unless-stopped
    devices:
      - /dev/ttyUSB0:/dev/ttyUSB0
    environment:
      - SERIAL_PORT=/dev/ttyUSB0
      - UPS_REQUEST_HEX=AA0400801E9E
      - UPTIME_KUMA_URL=https://uptimekuma.example.com/api/push/ups1
      - HA_WEBHOOK_URL=https://homeassistant.example.com/api/webhook/ups1
    privileged: true

  ups-monitor-2:
    build: .
    container_name: ups-monitor-2
    restart: unless-stopped
    devices:
      - /dev/ttyUSB1:/dev/ttyUSB1
    environment:
      - SERIAL_PORT=/dev/ttyUSB1
      - UPS_REQUEST_HEX=AA0400801E9E
      - UPTIME_KUMA_URL=https://uptimekuma.example.com/api/push/ups2
      - HA_WEBHOOK_URL=https://homeassistant.example.com/api/webhook/ups2
    privileged: true
```

## Integrations

### Uptime Kuma

1. Create a new Push monitor in Uptime Kuma
2. Copy the push URL
3. Set it as `UPTIME_KUMA_URL` in your environment

The monitor will send:
- `status=up` with `msg=ok` when UPS is online
- `status=down` with the UPS status when on battery or having issues

### Home Assistant

1. Go to Settings → Automations & Scenes → Webhooks
2. Create a new webhook
3. Copy the webhook URL
4. Set it as `HA_WEBHOOK_URL` in your environment

The monitor sends a JSON payload with all metrics:
```json
{
  "status": "Online",
  "battery_percentage": 100,
  "battery_voltage": 13.5,
  "load": 25,
  "temperature": 28
}
```

You can create sensors in Home Assistant using the webhook data.

## Troubleshooting

### Permission Denied on Serial Port

If running without Docker:
```bash
sudo usermod -a -G dialout $USER
# Log out and back in
```

If using Docker, ensure `privileged: true` is set in docker-compose.yml.

### No Data Received

1. Verify the serial port is correct: `ls -l /dev/ttyUSB*`
2. Check the baud rate matches your UPS model
3. Verify the `UPS_REQUEST_HEX` value is correct
4. Check connections and cables

### Container Keeps Restarting

Check logs:
```bash
docker-compose logs ups-monitor
```

Common issues:
- Missing `UPS_REQUEST_HEX` environment variable
- Serial device not mounted correctly
- Invalid serial port configuration

## License

MIT License - feel free to use and modify as needed.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## Tested Hardware

- ✅ Ragtech 1200VA UPS (Request Hex: `AA0400801E9E`)

If you've tested this with other models, please open an issue or PR to update this list!

## Support

For issues and questions, please open an issue on GitHub.
