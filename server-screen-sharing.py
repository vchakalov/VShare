import pyautogui

import socket
from threading import Thread
from zlib import compress
import tkinter
from mss import mss
import codecs
import pickle

root = tkinter.Tk()


WIDTH = root.winfo_screenwidth()
HEIGHT = root.winfo_screenheight()


# WIDTH = 1200
# HEIGHT = 800

def retreive_screenshot(conn):
    with mss() as sct:
        # The region to capture
        rect = {'top': 0, 'left': 0, 'width': WIDTH, 'height': HEIGHT}

        while 'recording':
            # Capture the screen
            img = sct.grab(rect)
            # Tweak the compression level here (0-9)
            pixels = compress(img.rgb, 6)

            # Send the size of the pixels length
            size = len(pixels)
            size_len = (size.bit_length() + 7) // 8
            conn.send(bytes([size_len]))

            # Send the actual pixels length
            size_bytes = size.to_bytes(size_len, 'big')
            conn.send(size_bytes)

            # Send pixels
            conn.sendall(pixels)

def retrieve_mouse_input(socket_interaction):
    current_x = 0
    current_y = 0
    while 'moving':
        data = socket_interaction.recv(4096)
        incoming_position = data.decode()
        x,y,*tr = incoming_position.split(',')
        
        if x and y:
            int(x)
            int(y)
        
        if x is not current_x and y is not current_y:
            current_x = str(int(x) - 1920)
            current_y = y
            pyautogui.moveTo(current_x, current_y, duration=0.25)
            print(current_x, current_y)
        
        #unpickled = pickle.loads(codecs.decode(data.encode(), "base64"))
        
        
    

def main(host='127.0.0.1', port_screen=4325, port_mouse=4326):
    sock_sharing_screen = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock_sharing_screen.bind((host, port_screen))

    sock_mouse_movement = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock_mouse_movement.bind((host, port_mouse))
    try:
        sock_sharing_screen.listen(5)
        sock_mouse_movement.listen(5)
        print('Server started.')
        
        while 'connected':
            connection_streaming, addr = sock_sharing_screen.accept()
            print('Connected to %s', addr)
            streaming = Thread(target=retreive_screenshot, args=(connection_streaming,))
            streaming.start()
            
            mouse_interaction, addr_host = sock_mouse_movement.accept()
            interaction = Thread(target=retrieve_mouse_input, args=(mouse_interaction,))
            interaction.start()
            
    
    finally:
        sock_sharing_screen.close()
        sock_mouse_movement.close()


if __name__ == '__main__':
    main()