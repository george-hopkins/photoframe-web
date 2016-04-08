# Photoframe Web

[![Hackaday.io](http://badge.s.co/hackaday/skulls/10808.svg)](https://hackaday.io/project/10808-photoframe-web)
![License](https://img.shields.io/github/license/george-hopkins/photoframe-web.svg)

As my digital photo frame was just lying around, I spent a few hours on this little project to turn it into something useful.

A Raspberry Pi continuously captures various websites and shows them on the photo frame. This setup allows you to display any content you like (e.g. weather maps, webcams, timetables, ...). Because my photo frame automatically turns into a USB flash disk as soon as the USB cable is plugged in, you have to physically disconnect the frame before any pictures are displayed. In order to get around this limitation, the USB power rail is controlled by a GPIO pin.

## Usage

Simply adjust the constants in `daemon.py` to your needs and startup the daemon: `python daemon.py`

You can specify the websites you want to display in `config.yml`:

```yaml
interval: 300 # seconds to wait between updates
slides:
    - 'http://i.imgur.com/X2n0NGK.png'
    - url: 'http://fullscreengooglemaps.com/'
      duration: 2
      wait: 2000 # in case the website loads content dynamically
```

## Dependencies

```bash
sudo apt-get install python-pip phantomjs imagemagick
pip install PyYAML bottle python-periphery pykwalify
```

Note: In case PhantomJS is not working, you might want to download a precompiled binary from [Nils Måsén](https://github.com/piksel/phantomjs-raspberrypi).

## Circuit

To enable/disable USB power, simply put a MOSFET in between of the 5V rail and connected the gate to a GPIO pin. A BJT might work as well too (the device will be powered by ~4.3V due to the voltage drop introduced by the transistor).
