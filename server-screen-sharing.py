
from pymouse import PyMouse
import socket
from threading import Thread
from zlib import compress

from mss import mss

def retreive_screenshot(conn, screen_width, screen_height):
    with mss() as sct:
        # The region to capture
        rect = {'top': 0, 'left': 0, 'width': screen_width, 'height': screen_height}

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

def retrieve_mouse_input(socket_interaction, mouse):
    current_x = 0
    current_y = 0
    
    while 'moving':
        data = socket_interaction.recv(1024)
        action = data.decode('utf-8')
        proccess_action(action, mouse, x=current_x, y=current_y)
        print(action)
        x,y,*leftovers = action.split(',')
        
        if x and y:
            x = int(x)
            y = int(y)
        
        if x is not current_x and y is not current_y:
            current_x = x - 1920
            current_y = y
            mouse.move(current_x, current_y)
            print(current_x, current_y)
        
  
def proccess_action(action, mouse, **input):
    command, movement = action.split(':')
    if command is 'CLICK':
        mouse.click()
    elif command is 'MOVE':
        current_x, current_y = input.get('x'), input.get('y')
        x,y = movement.split(',')
        if x and y:
            x = int(x)
            y = int(y)
        if x is not current_x and y is not current_y:
            current_x = x - 1920    
            current_y = y
            mouse.move(current_x, current_y)
            print(current_x, current_y)
            

def main(host='127.0.0.1', port_screen=4327, port_mouse=4326):
    mouse = PyMouse() 
    screen_width,screen_height = mouse.screen_size()
    
    
    sock_sharing_screen = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock_sharing_screen.bind((host, port_screen))

    sock_mouse_movement = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock_mouse_movement.bind((host, port_mouse))
    try:
        sock_sharing_screen.listen(5)
        print('Server started.')
        
        while 'connected':
            connection_streaming, addr = sock_sharing_screen.accept()
            print('Connected to %s', addr)
            streaming = Thread(target=retreive_screenshot, args=(connection_streaming, screen_width, screen_height, ))
            streaming.start()
            
            mouse_interaction =  sock_mouse_movement
            interaction = Thread(target=retrieve_mouse_input, args=(mouse_interaction,))
            interaction.start()
            
    
    finally:
        sock_sharing_screen.close()
        sock_mouse_movement.close()


if __name__ == '__main__':
    main()