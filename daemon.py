import yaml
import time
import bottle
import json
import tempfile
import subprocess
import os
import shutil
import periphery
import pykwalify.core

PHANTOMJS_PATH = '/usr/bin/phantomjs' # '/home/pi/photoframe-web/phantomjs-raspberrypi/bin/phantomjs'
MOUNT_DEV = '/dev/sda1'
MOUNT_ROOT = '/mnt/photoframe'
MOUNT_PATH = '/mnt/photoframe/JPG'
UNMOUNT_WAIT = 2
GPIO = 18

def load_config():
    """Load the configuration file and validate it."""
    with open('./config.yml', 'r') as stream:
        config = yaml.safe_load(stream)
        validator = pykwalify.core.Core(source_data=config, schema_files=['./config.schema.yml'])
        validator.validate(raise_exception=True)
        return config

def capture(url, outputpath, wait):
    """Capture a website using PhantomJS."""
    _, pngpath = tempfile.mkstemp('.png')
    script = bottle.template('./capture.js.tpl', {'url': json.dumps(url), 'output': json.dumps(pngpath), 'wait': json.dumps(wait)})
    sfd, scriptpath = tempfile.mkstemp('.js')
    with os.fdopen(sfd, 'w') as s:
        s.write(script)
    try:
        #subprocess.check_call([PHANTOMJS_PATH, '--local-url-access=false', scriptpath])
        subprocess.check_call([PHANTOMJS_PATH, scriptpath])
        subprocess.check_call(['convert', pngpath, '-background', 'white', '-alpha', 'remove', outputpath])
    finally:
        os.remove(scriptpath)
        os.remove(pngpath)

def main():
    subprocess.call(['umount', MOUNT_DEV])
    time.sleep(UNMOUNT_WAIT)
    gpio_mount = periphery.GPIO(GPIO, 'out')
    gpio_mount.write(False)

    while True:
        delay = 15
        try:
            print 'Start ...'
            config = load_config()

            slides = []
            for slide in config['slides']:
                if isinstance(slide, basestring):
                    slide = {'url': slide}
                if 'duration' in slide:
                    duration = int(slide['duration'])
                else:
                    duration = 1
                if 'wait' in slide:
                    wait = int(slide['wait'])
                else:
                    wait = 0

                try:
                    print 'Capture %s ...' % (slide['url'])
                    path = './tmp/slide-%05d.jpg' % len(slides)
                    capture(slide['url'], path, wait)
                    slides.append((path, duration))
                except subprocess.CalledProcessError, e:
                    print e

            print 'Mount USB flash ...'
            gpio_mount.write(True)
            while not os.path.exists(MOUNT_DEV):
                time.sleep(1)
            subprocess.check_call(['mount', MOUNT_DEV, MOUNT_ROOT])

            print 'Remove old frames ...'
            shutil.rmtree(MOUNT_PATH, True)
            os.mkdir(MOUNT_PATH)
            i = 0
            for slide in slides:
                for j in range(slide[1]):
                    filename = '%s/frame-%05d.jpg' % (MOUNT_PATH, i)
                    print 'Copy frame %s ...' % (filename)
                    shutil.copyfile(slide[0], filename)
                    i += 1

            print 'Unmount USB flash ...'
            subprocess.check_call(['umount', MOUNT_DEV])
            time.sleep(UNMOUNT_WAIT)
            gpio_mount.write(False)

            print 'Done.'

            if 'interval' in config:
                delay = int(config['interval'])
        except RuntimeError, e:
            print e
        time.sleep(delay)

if __name__ == '__main__':
    main()
