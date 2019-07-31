
import socket
from zlib import decompress
from multiprocessing import Process


import pygame
import tkinter
import pickle

from pymouse import PyMouse, PyMouseEvent
import pyautogui


root = tkinter.Tk()

WIDTH = root.winfo_screenwidth()
HEIGHT = root.winfo_screenheight()

class MouseMovement(PyMouseEvent):
    def __init__(self, socket, address):
        PyMouseEvent.__init__(self)
        self.socket = socket
        self.address = address
    def click(self, x, y, button, press):
        if button == 1:
            press
        else:  # Exit if any other mouse button used
            self.stop()             

def recvall(conn, length):
    """ Retreive all pixels. """

    buf = b''
    while len(buf) < length:
        data = conn.recv(length - len(buf))
        if not data:
            return data
        buf += data
    return buf


def retrieve_image(sock_sharing, screen, clock):
    while 'watching':
        # Retreive the size of the pixels length, the pixels length and pixels
        size_len = int.from_bytes(sock_sharing.recv(1), byteorder='big')
        size = int.from_bytes(sock_sharing.recv(size_len), byteorder='big')
        pixels = decompress(recvall(sock_sharing, size))

        # Create the Surface from raw pixels
        img = pygame.image.fromstring(pixels, (WIDTH, HEIGHT), 'RGB')

        #Display the picture
        screen.blit(img, (0, 0))
        pygame.display.flip()
        clock.tick(60)

def send_mouse_input(sock_interaction, address):
    # mouse = PyMouse()
    while 'moving':
        mouse_input = pyautogui.position()
        mouse_input_x = str(mouse_input[0])
        mouse_input_y = str(mouse_input[1])
        print(str(mouse_input_x + ',' + mouse_input_y))
        # encoded_input = pickle.dumps(((mouse_input_x)//2, mouse_input_y))
        sock_interaction.sendto(bytes(mouse_input_x + ',' + mouse_input_y, 'U8'), address)
        
        

def main(host='127.0.0.1', port_watching=4327, port_interaction=4326):
   
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    clock = pygame.time.Clock()
    
    sock_sharing = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock_sharing.connect((host, port_watching))
    
    sock_interaction = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    # sock_interaction.connect((host, port_interaction))
    
    sharing_proccess = Process(target=retrieve_image, args=(sock_sharing, screen, clock))
    interaction_proccess = Process(target=send_mouse_input, args=(sock_interaction, (host, port_interaction)))

    try:
        sharing_proccess.start()
        interaction_proccess.start()
    finally:
        sharing_proccess.join()
        interaction_proccess.join()
        sock_sharing.close()
        sock_interaction.close()


if __name__ == '__main__':
    main()
