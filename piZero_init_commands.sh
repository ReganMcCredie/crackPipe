chmod +x version[0-9]/shell_scripts/*
sudo apt update
sudo raspi-config nonint do_i2c 0
sudo raspi-config nonint do_spi 0
sudo raspi-config nonint do_ssh 0
sudo raspi-config nonint do_camera 0
sudo apt-get install -y i2c-tools libgpiod-dev python3-libgpiod python-smbus
sudo apt-get install -y aircrack-ng
sudo apt-get install -y expect
pip install --upgrade RPi.GPIO
pip install --upgrade adafruit-blinka
pip install adafruit-circuitpython-display-text
pip install adafruit-circuitpython-displayio-ssd1306
pip install adafruit-circuitpython-display-shapes
echo "Package installation complete."
echo "Restart your Pi zero to enable I2C."
