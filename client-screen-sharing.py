from socket import socket
from zlib import decompress


WIDTH = 800
HEIGHT = 600


def recvall(conn, length):
    """ Retreive all pixels. """

    buf = b''
    while len(buf) < length:
        data = conn.recv(length - len(buf))
        if not data:
            return data
        buf += data
    return buf


def main(host='127.0.0.1', port=5000):

    watching = True    

    sock = socket()
    sock.connect((host, port))
    try:
        while watching:
            
            # Retreive the size of the pixels length, the pixels length and pixels
            size_len = int.from_bytes(sock.recv(1), byteorder='big')
            size = int.from_bytes(sock.recv(size_len), byteorder='big')
            pixels = decompress(recvall(sock, size))

            # # Create the Surface from raw pixels
            # img = pygame.image.fromstring(pixels, (WIDTH, HEIGHT), 'RGB')

            # # Display the picture
            # screen.blit(img, (0, 0))
            # pygame.display.flip()
            # clock.tick(60)
    finally:
        sock.close()


if __name__ == '__main__':
    main()