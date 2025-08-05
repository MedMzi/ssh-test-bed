import os
import socket
import sys
import time
import threading

banner = "SSH-2.0-betiseSSH\r\n"
with open("kexinit_payload.bin", "rb") as f:
    kexinit = f.read()

with open("disconnect_payload.bin", "rb") as f:
    disconnect = f.read()

with open("ssh-connection_payload.bin", "rb") as f:
    ssh_connection = f.read()

with open("ssh-userauth_payload.bin", "rb") as f:
    ssh_userauth = f.read()

with open("servicereqQuelconque_payload.bin", "rb") as f:
    UnTrucQuelconque = f.read()

with open("unimplemented_payload.bin", "rb") as f:
    unimplemented = f.read()

with open("newkeys_payload.bin", "rb") as f:
    newkeys = f.read()

def sniffer(sock):
    """ Continuously read from the socket and print whatever is received """
    while True:
        try:
            data = sock.recv(4096)
            if not data:
                break
            print(f"\n[Sniffer] Received:\n {data.decode(errors='ignore')}\n end.")
        except Exception as e:
            print(f"[Sniffer] Error: {e}")
            break

def Client(port):
    tcp_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    tcp_socket.connect(("localhost", port))
    



    print(f"[Client] Sending banner: {banner.strip()}")
    tcp_socket.sendall(banner.encode())
    server_banner = tcp_socket.recv(4096).decode(errors='ignore').strip()
    print(f"[Client] Received server banner: {server_banner}")



    # Start sniffer in parallel
    threading.Thread(target=sniffer, args=(tcp_socket,), daemon=True).start()
    #data = tcp_socket.recv(1024)

    
    while True:
        try:
            time.sleep(1)
        except KeyboardInterrupt:
            print("[Client] Interrupted by user.")
            break

    tcp_socket.send(kexinit)
    print(f"[Client] sending KEXINIT payload ({len(kexinit)} bytes)")
    
    
    #threading.Thread(target=sniffer, args=(tcp_socket,), daemon=True).start()
   

    while True:
        try:
            time.sleep(1)
        except KeyboardInterrupt:
            print("[Client] Interrupted by user.")
            break
    
    tcp_socket.send(newkeys)
    print(f"[Client] sending UNIMPLEMENTED payload ({len(newkeys)} bytes)")
    

    while True:
        try:
            time.sleep(1)
        except KeyboardInterrupt:
            print("[Client] Interrupted by user.")
            break

    print(f"[Client] sending DISCONNECT payload ({len(disconnect)} bytes)")
    tcp_socket.send(disconnect)

    while True:
        try:
            time.sleep(1)
        except KeyboardInterrupt:
            print("[Client] Interrupted by user.")
            break


    tcp_socket.close()
    print("[Client] Connection closed.")

Client(2222)

