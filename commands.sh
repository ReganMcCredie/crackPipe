sudo apt update
sudo raspi-config nonint do_i2c 0
sudo raspi-config nonint do_spi 0
sudo raspi-config nonint do_ssh 0
sudo raspi-config nonint do_camera 0
sudo apt-get install -y i2c-tools libgpiod-dev python3-libgpiod python-smbus
sudo pip install --upgrade RPi.GPIO
sudo pip install --upgrade adafruit-blinka
sudo pip install adafruit-circuitpython-display-text
sudo pip install adafruit-circuitpython-displayio-ssd1306
sudo pip install adafruit-circuitpython-display-shapes
echo "Package installation complete."
echo "Restart your Pi zero to enable I2C."


