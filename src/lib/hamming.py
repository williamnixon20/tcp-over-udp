def bits_to_bytes(bits_list):
    # Ensure the length of bits_list is a multiple of 8
    padding = (8 - len(bits_list) % 8) % 8
    bits_list.extend([0] * padding)

    # Group bits into bytes
    bytes_list = [
        int("".join(map(str, bits_list[i : i + 8])), 2)
        for i in range(0, len(bits_list), 8)
    ]

    # Create a bytes object from the list of bytes
    byte_data = bytes(bytes_list)

    return byte_data


# hamming, turn 4 bits -> 8 bits.
# 1 last parity bit
def hamming_encode(data):
    # print("Data for hamming: " + str(data))
    if type(data) is not bytes:
        raise ValueError("Input must be a bytes object")

    encoded_bytes = b""

    # Iterate over each byte in the input data
    for byte in data:
        byte_value = int.from_bytes(bytes([byte]), byteorder="big")
        data_bits = format(byte_value, "08b")
        # 1 byte can get 2 passes in hamming
        base = 0
        for i in range(2):
            codeword = [
                0,
                0,
                int(data_bits[base + 0]),
                0,
                int(data_bits[base + 1]),
                int(data_bits[base + 2]),
                int(data_bits[base + 3]),
                0,  # Parity bit
            ]

            codeword[0] = (
                int(data_bits[base + 0])
                ^ int(data_bits[base + 1])
                ^ int(data_bits[base + 3])
            )
            codeword[1] = (
                int(data_bits[base + 0])
                ^ int(data_bits[base + 2])
                ^ int(data_bits[base + 3])
            )
            codeword[3] = (
                int(data_bits[base + 1])
                ^ int(data_bits[base + 2])
                ^ int(data_bits[base + 3])
            )
            for i in range(len(codeword) - 1):
                codeword[7] ^= codeword[i]

            base += 4
            encoded_bytes += bytes([int("".join(map(str, codeword)), 2)])
    return encoded_bytes


""" Receives a hamming encoding, which is 1 byte and turns it back into 4 bits.
"""


def hamming_decode(data):
    if type(data) is not bytes:
        raise ValueError("Input must be a bytes object")

    decoded_bits = []

    # Iterate over each byte in the input data
    for byte in data:
        byte_value = int.from_bytes(bytes([byte]), byteorder="big")
        data_bits = format(byte_value, "08b")

        # # Calculate syndrome bits
        s1 = (
            int(data_bits[0])
            ^ int(data_bits[2])
            ^ int(data_bits[4])
            ^ int(data_bits[6])
        )
        s2 = (
            int(data_bits[1])
            ^ int(data_bits[2])
            ^ int(data_bits[5])
            ^ int(data_bits[6])
        )
        s3 = (
            int(data_bits[3])
            ^ int(data_bits[4])
            ^ int(data_bits[5])
            ^ int(data_bits[6])
        )
        # Check for errors
        error_position = s1 * 1 + s2 * 2 + s3 * 4

        # Correct errors if any
        if error_position > 0:
            print("[!] Hamming detected errors! Trying my best to fix...")
            data_bits = list(data_bits)

            data_bits[error_position - 1] = (
                "0" if data_bits[error_position - 1] == "1" else "1"
            )
            data_bits = "".join(data_bits)

        # Append the correct 4 data bits to the decoded_bits
        decoded_bits.extend(
            [int(data_bits[2]), int(data_bits[4]), int(data_bits[5]), int(data_bits[6])]
        )

    return bits_to_bytes(decoded_bits)


def simulate_bit_corruption(data, position):
    # Simulate a 1-bit corruption at the specified position
    byte_index = position // 8
    bit_offset = position % 8

    # Convert the byte to a list of bits
    bits = list(format(data[byte_index], "08b"))

    # Flip the specified bit
    bits[bit_offset] = "1" if bits[bit_offset] == "0" else "0"

    # Convert the list of bits back to a byte
    corrupted_byte = int("".join(bits), 2).to_bytes(1, byteorder="big")

    # Replace the original byte with the corrupted byte
    corrupted_data = bytearray(data)
    corrupted_data[byte_index] = corrupted_byte[0]

    return bytes(corrupted_data)


if __name__ == "__main__":
    input_data = b"a\n"
    print(input_data)

    # for byte in input_data:
    #     byte_value = int.from_bytes(bytes([byte]), byteorder="big")
    #     data_bits = format(byte_value, "08b")
    #     print(data_bits)
    # print("ENCODE")
    encoded_data = hamming_encode(input_data)
    # print("ENCODED BITS")
    for byte in encoded_data:
        byte_value = int.from_bytes(bytes([byte]), byteorder="big")
        data_bits = format(byte_value, "08b")
        print(data_bits)
    print("Encoded Data:", encoded_data)

    decoded_data = hamming_decode(encoded_data)
    print("Decoded Data:", decoded_data)
    print("EEC Success:", input_data == decoded_data)

    print("Simulating 1 bit corruption")
    # Simulate 1 bit corruption at position 3 (for example)
    position_to_corrupt = 4
    print("Corrupting bit at position", position_to_corrupt)
    corrupted_data = simulate_bit_corruption(encoded_data, position_to_corrupt)

    decoded_data = hamming_decode(corrupted_data)
    print("Corrupted Data:", corrupted_data)
    print("Decoded Data:", decoded_data)
    print("EEC Success:", input_data == decoded_data)
