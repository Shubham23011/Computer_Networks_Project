import uuid
import random
import time
from physical_layer import *

class Frame:
    def __init__(self, source_mac, destination_mac, data):
        self.source_mac = source_mac
        self.destination_mac = destination_mac
        self.data = data

class Bridge(Device):
    def __init__(self, device_id):
        super().__init__(device_id, "bridge")
        self.ports = {}

    def add_port(self, port, device):
        self.ports[port] = device

    def forward_frame(self, frame, incoming_port):
        for port, device in self.ports.items():
            if port != incoming_port:
                device.receive_data(frame.data)

class Switch(Device):
    def __init__(self, device_id):
        super().__init__(device_id, "switch")
        self.mac_address_table = {}
        self.ports = {}

    def add_port(self, port, device):
        self.ports[port] = device

    def learn_mac_address(self, port, mac_address):
        self.mac_address_table[mac_address] = port

    def forward_frame(self, frame):
        if frame.destination_mac in self.mac_address_table:
            port = self.mac_address_table[frame.destination_mac]
            self.ports[port].receive_data(frame.data)
        else:
            for port, device in self.ports.items():
                if device.device_id != frame.source_mac:
                    device.receive_data(frame.data)

# Error Control Protocol: Parity Check
def parity_check(data):
    return data + str(data.count('1') % 2)

def verify_parity(data_with_parity):
    data = data_with_parity[:-1]
    parity = data_with_parity[-1]
    return parity == str(data.count('1') % 2)

# Access Control Protocol: CSMA/CD
def csma_cd(send_func):
    while True:
        if random.random() > 0.1:  # Simulating a 90% chance of no collision
            send_func()
            print("Data sent successfully.")
            break
        else:
            print("Collision detected! Retrying...")

# Sliding Window Protocol: Go-Back-N ARQ
class SlidingWindow:
    def __init__(self, window_size):
        self.window_size = window_size
        self.send_base = 0
        self.next_seq_num = 0
        self.buffer = []
        self.sent_data = {}

    def send(self, data, send_func):
        if self.next_seq_num < self.send_base + self.window_size:
            self.buffer.append(data)
            seq_num = self.next_seq_num
            send_func(data, seq_num)
            self.sent_data[seq_num] = data
            self.next_seq_num += 1
        else:
            print("Window is full. Waiting for acknowledgment...")

    def receive_ack(self, ack_num):
        if ack_num in self.sent_data:
            del self.sent_data[ack_num]
            if ack_num == self.send_base:
                self.send_base += 1
                while self.send_base in self.sent_data:
                    self.send_base += 1
            print(f"Acknowledgment received for sequence number: {ack_num}")
        else:
            print(f"Invalid acknowledgment: {ack_num}")

# Go-Back-N ARQ Protocol
def transmission(i, N, tf, send_func_gbn):
    tt = 0
    while i <= tf:
        z = 0
        for k in range(i, min(i + N, tf + 1)):
            send_func_gbn(f"Data {k}", k)
            tt += 1
        for k in range(i, min(i + N, tf + 1)):
            f = random.randint(0, 1)
            if not f:
                print(f"Acknowledgment for Frame {k}...")
                z += 1
            else:
                print(f"Timeout!! Frame Number: {k} Not Received")
                print("Retransmitting Window...")
                break
        print("\n")
        i += z
    return tt

def send_data_with_parity(data, connection):
    data_with_parity = parity_check(data)
    connection.transmit_data(data_with_parity, None)

# Testing Data Link Layer Functionalities
if __name__ == "__main__":
    simulator = NetworkSimulator()

    devices = [simulator.create_device("end_device") for _ in range(5)]
    switch = Switch(str(uuid.uuid4()))
    for i, device in enumerate(devices):
        switch.add_port(i, device)
        switch.learn_mac_address(i, device.device_id)

    frame = Frame(devices[0].device_id, devices[1].device_id, "Frame data")
    switch.forward_frame(frame)

    # Test Parity Check
    data = "1010101"
    data_with_parity = parity_check(data)
    print(f"Data with parity: {data_with_parity}")
    print(f"Parity verification: {verify_parity(data_with_parity)}")

    # Test CSMA/CD
    device1 = simulator.create_device("end_device")
    device2 = simulator.create_device("end_device")
    conn1 = simulator.create_connection(device1, device2)

    def send_func():
        simulator.send_data(device1, "Data with CSMA/CD", conn1)

    csma_cd(send_func)

    # Define send_func_gbn for Sliding Window and Go-Back-N ARQ
    def send_func_gbn(data, seq_num):
        print(f"Sending data: {data} with sequence number: {seq_num}")
        simulator.send_data(device1, data, conn1)

    # Test Sliding Window (Go-Back-N ARQ) using transmission function
    tf = 5  # Total number of frames
    N = 3  # Window size
    i = 1
    total_transmissions = transmission(i, N, tf, send_func_gbn)
    print(f"Total number of frames which were sent and resent are: {total_transmissions}")
