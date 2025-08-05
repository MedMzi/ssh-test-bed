import json
import os
import struct
import random

def encode_ssh_string(s):
        encoded = s.encode()
        return struct.pack(">I", len(encoded)) + encoded

def name_list_to_bytes(name_list):
    # name-list is length(uint32) + comma-separated string bytes
    s = ",".join(name_list)
    return encode_ssh_string(s)

def wrap_ssh_packet(payload: bytes, block_size: int = 8) -> bytes:
    unpadded_len = len(payload) + 5
    padding_length = (block_size - (unpadded_len % block_size)) % block_size
    if padding_length < 4:
        padding_length += block_size

    packet_length = len(payload) + padding_length + 1  # +1 for padding_length field

    # 🧪 DEBUG INFO
    print("[DEBUG] --- Packet Construction ---")
    print(f"Payload length:       {len(payload)}")
    print(f"Unpadded length (+1): {unpadded_len}")
    print(f"Block size:           {block_size}")
    print(f"Padding length:       {padding_length}")
    print(f"Total packet_length:  {packet_length}")
    print(f"Total full length (with 4-byte prefix): {packet_length + 4}")
    print("----------------------")

    packet = struct.pack(">I", packet_length)
    packet += struct.pack("B", padding_length)
    packet += payload
    packet += os.urandom(padding_length)

    # Print hex of final output
    print("[DEBUG] Final packet (hex):")
    print(packet.hex())

    return packet



def kexinit_payload():
    cookie = os.urandom(16)
    msg_id = 20  # SSH_MSG_KEXINIT

    with open("Reference.json", "r") as f:
        ref = json.load(f)
    compression_algorithms = ["none", "zlib@openssh.com", "zlib"]

    payload = struct.pack("B", msg_id)  # message id
    payload += cookie

    payload += name_list_to_bytes(ref["KexAlgorithms"])
    payload += name_list_to_bytes(ref["HostKeyAlgorithms"])
    payload += name_list_to_bytes(ref["Ciphers"])  # client to server encryption algos
    payload += name_list_to_bytes(ref["Ciphers"])  # server to client encryption algos (using same list)
    payload += name_list_to_bytes(ref["MACs"])     # client to server MAC algos
    payload += name_list_to_bytes(ref["MACs"])     # server to client MAC algos
    payload += name_list_to_bytes(compression_algorithms)  # client to server compression
    payload += name_list_to_bytes(compression_algorithms)  # server to client compression
    payload += name_list_to_bytes([])  # languages client to server (empty)
    payload += name_list_to_bytes([])  # languages server to client (empty)

    payload += struct.pack("B", 0)     # first_kex_packet_follows = False
    payload += struct.pack(">I", 0)    # reserved uint32 = 0

    payload = wrap_ssh_packet(payload) 

    with open("kexinit_payload.bin", "wb") as f:
        f.write(payload)

    print("kexinit_payload.bin created.")

def disconnect_payload(DESCRIPTION="byebye", LANGUAGE_TAG="en"):
    msg_id = 1 # SSH_MSG_DISCONNECT
    REASON_CODE = 0xFEAAAAAA  # Private-use code

    # Build the payload
    payload = bytearray()
    payload.append(msg_id)
    payload += struct.pack(">I", REASON_CODE)
    payload += encode_ssh_string(DESCRIPTION)
    payload += encode_ssh_string(LANGUAGE_TAG)

    payload = wrap_ssh_packet(payload)

    # Write to file
    with open("disconnect_payload.bin", "wb") as f:
        f.write(payload)

    print("disconnect_payload.bin created.")

def servicereq_payload(service_name):
    msg_id = 5  # SSH_MSG_SERVICE_REQUEST
    

    payload = bytearray()
    payload.append(msg_id)
    payload += encode_ssh_string(service_name)

    payload = wrap_ssh_packet(payload)

    with open(f"{service_name}_payload.bin", "wb") as f:
        f.write(payload)

    print(f"{service_name}_payload.bin created.")

def unimplemented_payload():
    msg_id = 3  # SSH_MSG_UNIMPLEMENTED
    payload = bytearray()
    payload.append(msg_id)
    payload += struct.pack(">I", 1)  

    payload = wrap_ssh_packet(payload)

    with open("unimplemented_payload.bin", "wb") as f:
        f.write(payload)

    print("unimplemented_payload.bin created.")

def newkeys_payload():
    msg_id = 21  # SSH_MSG_NEWKEYS
    payload = bytearray()
    payload.append(msg_id)

    payload = wrap_ssh_packet(payload)

    with open("newkeys_payload.bin", "wb") as f:
        f.write(payload)

    print("newkeys_payload.bin created.")

def userauthsuccess_payload():
    msg_id = 52  # SSH_MSG_USERAUTH_SUCCESS
    payload = bytearray()
    payload.append(msg_id)

    payload = wrap_ssh_packet(payload)

    with open("userauthsuccess_payload.bin", "wb") as f:
        f.write(payload)

    print("userauthsuccess_payload.bin created.")

def userauthfail_payload():
    msg_id = 51  # SSH_MSG_USERAUTH_FAILURE
    payload = bytearray()
    payload.append(msg_id)
    payload += encode_ssh_string("password")
    payload += struct.pack("B", 0)  # partial success

    payload = wrap_ssh_packet(payload)

    with open("userauthfail_payload.bin", "wb") as f:
        f.write(payload)

    print("userauthfail_payload.bin created.")

def userauthbanner_payload(message="Coucou.", language_tag="fr"):
    msg_id = 53  # SSH_MSG_USERAUTH_BANNER
    payload = bytearray()
    payload.append(msg_id)
    payload += encode_ssh_string(message)  # banner message
    payload += encode_ssh_string(language_tag)  # language tag

    payload = wrap_ssh_packet(payload)

    with open("userauthbanner_payload.bin", "wb") as f:
        f.write(payload)

    print("userauthbanner_payload.bin created.")

def userauthrequest_payload(username="betise", service="ssh-connection", method="password", password="1234"):
    msg_id = 50  # SSH_MSG_USERAUTH_REQUEST
    payload = bytearray()
    payload.append(msg_id)
    
    payload += encode_ssh_string(username)  # username
    payload += encode_ssh_string(service)   # service name
    payload += encode_ssh_string(method)    # authentication method
    payload += struct.pack("B", 0)           # boolean for "is this a password?" (0 for false)
    
    if method == "password":
        payload += encode_ssh_string(password)  # password string
    else:
        raise ValueError("Unsupported authentication method")

    payload = wrap_ssh_packet(payload)

    with open("userauthrequest_payload.bin", "wb") as f:
        f.write(payload)

    print("userauthrequest_payload.bin created.")

if __name__ == "__main__":
    #kexinit_payload()
    #disconnect_payload()
    servicereq_payload("ssh-userauth")
    servicereq_payload("ssh-connection")
    servicereq_payload("servicereqQuelconque")
    #unimplemented_payload()
    #newkeys_payload()
    #userauthsuccess_payload()
    #userauthfail_payload()  
    #userauthbanner_payload()
    userauthrequest_payload() 

