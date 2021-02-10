from lib.devices.fan import Fan
from optparse import OptionParser
from time import sleep



class FanService:
    def __init__(self, quiet=False):
        self.__log('Starting fan lights')
        self.fan = Fan(gpio_pin=13, led_count=11, ips=['192.168.1.13'], start_at='17:55:00',
                            end_at='23:30:00', date_fmt='%Y/%m/%d ', time_fmt='%H:%M:%S', quiet=quiet)

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
            raise Exception()
    except:
        pass
    finally:
        main.stop()
        pass
