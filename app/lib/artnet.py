import socket


class ArtNet:
    def __init__(self, target_ip='127.0.0.1', udp_port=6454, universe=0, packet_size=512, receiver=True):
        self.TARGET_IP = target_ip
        self.UDP_PORT = udp_port
        self.SEQUENCE = 0
        self.UNIVERSE = universe
        self.PACKET_SIZE = self.__put_in_range(packet_size, 2, 512)
        self.HEADER = bytearray()
        self.BUFFER = bytearray(self.PACKET_SIZE)
        self.__receiver = receiver
        # UDP SOCKET
        self.__socket = None
        self.__init_socket()
        self.__make_header()

    def __del__(self):
        self.close()

    def __repr__(self):
        return vars(self)

    def __str__(self):
        return f"@{self.__class__.__name__}{self.__repr__()}"

    def __log(self, a, sep=' => ', flush=True, end="\n"):
        print(self.__class__.__name__, a, sep=sep, flush=flush, end=end)

    def __init_socket(self):
        # UDP SOCKET
        try:
            self.close()
        except:
            pass

        self.__socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        if self.__receiver:
            self.__socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self.__socket.bind((self.TARGET_IP, self.UDP_PORT))

    def __make_header(self):
        """Make packet header."""
        # 0 - id (7 x bytes + Null)
        self.HEADER = bytearray()
        self.HEADER.extend(bytearray('Art-Net', 'utf8'))
        self.HEADER.append(0x0)
        # 8 - opcode (2 x 8 low byte first)
        self.HEADER.append(0x00)
        self.HEADER.append(0x50)  # ArtDmx data packet
        # 10 - prototocol version (2 x 8 high byte first)
        self.HEADER.append(0x0)
        self.HEADER.append(14)
        # 12 - sequence (int 8), NULL for not implemented
        self.HEADER.append(self.SEQUENCE)
        # 13 - physical port (int 8)
        self.HEADER.append(0x00)
        # 14 - universe, (2 x 8 low byte first)
        v = self.__shift_this(self.UNIVERSE)			# convert to MSB / LSB
        self.HEADER.append(v[1])
        self.HEADER.append(v[0])
        # 16 - packet size (2 x 8 high byte first)
        v = self.__shift_this(self.PACKET_SIZE)		# convert to MSB / LSB
        self.HEADER.append(v[0])
        self.HEADER.append(v[1])

    def get_target_ip(self):
        return self.TARGET_IP

    def set_target_ip(self, target_ip):
        self.TARGET_IP = target_ip
        self.__init_socket()

    def get_udp_port(self):
        return self.UDP_PORT

    def set_udp_port(self, udp_port):
        self.UDP_PORT = udp_port
        self.__init_socket()

    def get_universe(self):
        return self.UNIVERSE

    def set_universe(self, universe):
        """Setter for universe (0 - 15 / 256).
        Mind if protocol has been simplified
        """
        # This is ugly, trying to keep interface easy
        # With simplified mode the universe will be split into two
        # values, (uni and sub) which is correct anyway. Net will always be 0
        self.UNIVERSE = self.__put_in_range(universe, 0, 255, False)
        self.__make_header()

    def set_packet_size(self, packet_size):
        """Setter for packet size (2 - 512, even only)."""
        self.PACKET_SIZE = self.__put_in_range(packet_size, 2, 512, True)
        self.__make_header()

    def send(self):
        """Finally send data."""
        packet = bytearray()
        packet.extend(self.HEADER)
        packet.extend(self.BUFFER)
        try:
            self.__socket.sendto(packet, (self.TARGET_IP, self.UDP_PORT))
        except Exception as e:
            print("ERROR: Socket error with exception: %s" % e)
        finally:
            self.SEQUENCE = (self.SEQUENCE + 1) % 256

    def close(self):
        """Close UDP socket."""
        self.__socket.close()

    def receive(self):
        raw_data = self.__socket.recv(1024)
        decodedData = self.__decodeData(raw_data[18:530])
        data = {
            "head": raw_data[0:8],
            "opcode": raw_data[8:10],
            "protocolHigh": raw_data[10:11],
            "protocolLow": raw_data[11:12],
            "sequence": raw_data[12:13],
            "physical": raw_data[13:14],
            "universe": round(int(raw_data[14:16].hex(), 16) / 256),
            "lengthHigh": raw_data[16:17],
            "lengthLow": raw_data[17:18],
            "binaryData": raw_data[18:530],
            "data": decodedData[0:510],
            "pixels_count": decodedData[511]
        }
        return data

    def clear(self):
        """Clear DMX buffer."""
        self.BUFFER = bytearray(self.PACKET_SIZE)

    def set_led_count(self, led_count):
        """Set buffer."""
        self.BUFFER[511] = self.__put_in_range(led_count, 0, 170, False)

    def set_value(self, address, value):
        """Set buffer."""
        self.BUFFER[address] = self.__put_in_range(value, 0, 255, False)

    def set_rgb(self, address, r, g, b):
        address = address * 3
        """Set RGB from start address."""
        if address > self.PACKET_SIZE:
            print("ERROR: Address given greater than defined packet size")
            return
        if address < 0 or address > 510:
            print("ERROR: Address out of range")
            return

        self.BUFFER[address] = self.__put_in_range(r, 0, 255, False)
        self.BUFFER[address + 1] = self.__put_in_range(g, 0, 255, False)
        self.BUFFER[address + 2] = self.__put_in_range(b, 0, 255, False)

    @staticmethod
    def __listIntoTuples(l):
        if len(l) % 3 != 0:
            raise Exception(f'bad len {len(l) % 3}')
        for i in range(0, len(l), 3):
            yield l[i:i+3]

    @staticmethod
    def __decodeData(binData):
        listdata = list()
        for i in range(len(binData)):
            listdata.append(binData[i])
        return listdata

    @staticmethod
    def __shift_this(number, high_first=True):
        """Utility method: extracts MSB and LSB from number.
        Args:
        number - number to shift
        high_first - MSB or LSB first (true / false)
        Returns:
        (high, low) - tuple with shifted values
        """
        low = (number & 0xFF)
        high = ((number >> 8) & 0xFF)
        if (high_first):
            return((high, low))
        else:
            return((low, high))
        print("Something went wrong")
        return False

    @staticmethod
    def __put_in_range(number, range_min, range_max, make_even=True):
        """Utility method: sets number in defined range.
        Args:
        number - number to use
        range_min - lowest possible number
        range_max - highest possible number
        make_even - should number be made even
        Returns:
        number - number in correct range
        """
        if (number < range_min):
            number = range_min
        if (number > range_max):
            number = range_max
        if (make_even and number % 2 != 0):
            number += 1
        return number
