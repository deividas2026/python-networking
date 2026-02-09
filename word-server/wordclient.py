import sys
import socket

# How many bytes is the word length?
WORD_LEN_SIZE = 2
BYTES_TO_RECV = 1

def usage():
    print("usage: wordclient.py server port", file=sys.stderr)

packet_buffer = b''

def get_next_word_packet(s):
    """
    Return the next word packet from the stream.

    The word packet consists of the encoded word length followed by the
    UTF-8-encoded word.

    Returns None if there are no more words, i.e. the server has hung
    up.
    """

    global packet_buffer
    # TODO -- Write me!
    while True:
        if len(packet_buffer) > WORD_LEN_SIZE:
            word_length = int.from_bytes(packet_buffer[:WORD_LEN_SIZE], "big")
            remaining_packet_buffer_length = len(packet_buffer[WORD_LEN_SIZE:])
            if remaining_packet_buffer_length >= word_length:
                word_packet = packet_buffer[:word_length + WORD_LEN_SIZE]
                packet_buffer = packet_buffer[word_length + WORD_LEN_SIZE:]
                return word_packet
                
        packet_bytes = s.recv(BYTES_TO_RECV)
        if not packet_bytes:
            return

        packet_buffer += packet_bytes


def extract_word(word_packet):
    """
    Extract a word from a word packet.

    word_packet: a word packet consisting of the encoded word length
    followed by the UTF-8 word.

    Returns the word decoded as a string.
    """

    # TODO -- Write me!
    word_len = int.from_bytes(word_packet[:WORD_LEN_SIZE], "big")
    word_bytes = word_packet[WORD_LEN_SIZE:]
    return word_bytes.decode("UTF-8")

# Do not modify:

def main(argv):
    try:
        host = argv[1]
        port = int(argv[2])
    except:
        usage()
        return 1

    s = socket.socket()
    s.connect((host, port))

    print("Getting words:")

    while True:
        word_packet = get_next_word_packet(s)
        if word_packet is None:
            break

        word = extract_word(word_packet)
        print(f"    {word}")

    s.close()

if __name__ == "__main__":
    sys.exit(main(sys.argv))
