from config import MAIN_HOST, SWITCH_HOST, MQTT_BROKER_HOST, START_AT, END_AT, DATE_FMT, TIME_FMT
from lib.devices.fan import Fan
from optparse import OptionParser
from time import sleep
import traceback



class FanService:
    def __init__(self, quiet=False):
        self.__log('Starting fan lights')
        self.fan = Fan(gpio_pin=13, quiet=quiet)

    def __log(self, a, sep=' => ', flush=True, end="\n"):
        print(self.__class__.__name__, a, sep=sep, flush=flush, end=end)

    def run(self):
        self.fan.start()
        while True:
            sleep(1)

    def stop(self):
        print('', flush=True)
        self.__log('Exiting...')
        self.fan.stop()


if __name__ == '__main__':
    parser = OptionParser()
    parser.add_option("--off", action="store_true",
                      dest="terminate", default=False)
    parser.add_option("-q", "--quiet", action="store_true",
                      dest="quiet", default=False)
    (options, _) = parser.parse_args()

    main = FanService(quiet=options.quiet)
    try:
        if options.terminate == False:
            main.run()
        else:
            main.stop()
    except KeyboardInterrupt:
        main.stop()
        pass
    except:
        traceback.print_exc()
        pass
