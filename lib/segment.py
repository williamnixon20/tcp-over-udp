import struct

class SegmentFlag:
    SYN_CONST = 0x02
    ACK_CONST = 0x10
    FIN_CONST = 0x01

    def __init__(self, syn=False, ack=False, fin=False):
        self.syn = syn
        self.ack = ack
        self.fin = fin

    def get_flag_bytes(self):
        flags = self.get_flag_int()
        return struct.pack('!B', flags)

    def get_flag_int(self):
        flags = 0
        if self.syn:
            flags |= self.SYN_CONST
        if self.ack:
            flags |= self.ACK_CONST
        if self.fin:
            flags |= self.FIN_CONST
        return flags

class Segment:
    FORMAT_STRING = 'IIBxH' 
    MAX_PAYLOAD_SIZE = 32756  
    endian="!"

    def __init__(self, sequence_number=0, acknowledgment_number=0, flags=0, checksum=0, data_payload=b''):
        self.sequence_number = sequence_number
        self.acknowledgment_number = acknowledgment_number
        self.flags = flags if not isinstance(flags, SegmentFlag) else flags.get_flag_int()
        self.checksum = checksum
        self.data_payload = data_payload

        if len(self.data_payload) > self.MAX_PAYLOAD_SIZE:
          raise ValueError(f"Data payload size exceeds the maximum allowed size of {self.MAX_PAYLOAD_SIZE} bytes.")
        
        # TODO: Do we pad or not? if not pad hati2 CRC dkk
        if len(data_payload) < self.MAX_PAYLOAD_SIZE:
            padding_size = self.MAX_PAYLOAD_SIZE - len(data_payload)
            self.data_payload += b'\x00' * padding_size

    def __str__(self):
        output = ""
        output += f"{'SeqNum':12}\t\t| {self.sequence_number}\n"
        output += f"{'AckNum':12}\t\t| {self.acknowledgment_number}\n"
        output += f"{'FlagSYN':12}\t\t| {bool(self.flags & SegmentFlag.SYN_CONST)}\n"
        output += f"{'FlagACK':12}\t\t| {bool(self.flags & SegmentFlag.ACK_CONST)}\n"
        output += f"{'FlagFIN':12}\t\t| {bool(self.flags & SegmentFlag.FIN_CONST)}\n"
        output += f"{'Checksum':24}| {self.checksum}\n"
        output += f"{'MsgSize':24}| {len(self.data_payload)}\n"
        output += f"{'Valid Checksum':24}| {self.is_valid_checksum()}\n"
        return output

    def to_bytes(self):
        self.checksum = self.calculate_checksum() 
        header = struct.pack(self.endian + self.FORMAT_STRING, self.sequence_number, self.acknowledgment_number, self.flags, self.checksum)
        return header + self.data_payload

    ## TODO: Pastiin ini bener (?) ini supposedly pake yg 16 bit 1's complement
    def calculate_checksum(self):
        # Bikin segment data dari awal, tapi checksumnya 0
        segment_data = struct.pack(self.endian + self.FORMAT_STRING, self.sequence_number, self.acknowledgment_number, self.flags, 0) + self.data_payload
        checksum = sum(((segment_data[i] << 8) + segment_data[i + 1]) for i in range(0, len(segment_data), 2))
        while (checksum >> 16):
            checksum = (checksum & 0xFFFF) + (checksum >> 16)
        checksum = 0xFFFF - checksum  # One's complement
        return checksum

    @staticmethod
    def from_bytes(data):
        header_size = struct.calcsize(Segment.endian + Segment.FORMAT_STRING)
        header_data = data[:header_size]
        data_payload = data[header_size:]
        sequence_number, acknowledgment_number, flags, checksum = struct.unpack(Segment.endian + Segment.FORMAT_STRING, header_data)
        return Segment(sequence_number, acknowledgment_number, flags, checksum, data_payload)

    def is_valid_checksum(self):
        return (self.calculate_checksum() == self.checksum)

    @staticmethod
    def syn(seq_num):
        return Segment(sequence_number=seq_num, flags=SegmentFlag(syn=True))

    @staticmethod
    def ack(seq_num, ack_num):
        return Segment(sequence_number=seq_num, acknowledgment_number=ack_num, flags=SegmentFlag(ack=True))

    @staticmethod
    def syn_ack():
        return Segment(flags=SegmentFlag(syn=True, ack=True))

    @staticmethod
    def fin():
        return Segment(flags=SegmentFlag(fin=True))


## CHECKSUM BAKAL DIKALKULASI KALAU TO_BYTES DIPANGGIL
if __name__ == "__main__":
    sequence_number = 12345
    acknowledgment_number = 54321
    flags = SegmentFlag(syn=True, ack=True)
    data_payload = b'\x01' * 32756 

    segment = Segment(sequence_number, acknowledgment_number, flags, 0, data_payload)
    packed_data = segment.to_bytes()
    print(f"Initial Segment \n{segment}")
    
    print("\n\n PACKET_LENGTH semestinya sepanjang header + payload" + str(len(packed_data)) + "\n\n")


    corrupted_data = packed_data[:-2] + b'\x00\x01'  # Corrupting the checksum
    corrupted_segment = Segment.from_bytes(corrupted_data)
    print("CORRUPTED SEGMENT\n" + corrupted_segment)


    syn_segment = Segment.syn(12345) 
    syn_segment.to_bytes() # Biar checksum keisi
    print("SYN SEGMENT \n " + str(syn_segment))
    ack_segment = Segment.ack(54321, 12345)  
    ack_segment.to_bytes() # Biar checksum keisi
    print("ACK SEGMENT \n " + str(ack_segment))
    syn_ack_segment = Segment.syn_ack() 
    syn_ack_segment.to_bytes() # Biar checksum keisi
    print("SYN-ACK SEGMENT \n " + str(syn_ack_segment))
    fin_segment = Segment.fin()
    fin_segment.to_bytes() # Biar checksum keisi
    print("FIN SEGMENT \n " + str(fin_segment))
