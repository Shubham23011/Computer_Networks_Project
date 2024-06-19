import uuid
import random
from network_layer import NetworkSimulator, Router, ARPEntry
from data_link_layer import SlidingWindow 

# Transport Layer Protocols
class TransportLayer:
    def __init__(self):
        self.port_table = {}

    def assign_port(self, process_name, port_type='well-known'):
        if port_type == 'well-known':
            port = random.randint(0, 1023)
        else:
            port = random.randint(1024, 65535)
        self.port_table[port] = process_name
        return port

    def get_process_by_port(self, port):
        return self.port_table.get(port, None)

class TCP:
    def __init__(self, window_size):
        self.window = SlidingWindow(window_size)

    def send(self, data, send_func):
        self.window.send(data, send_func)

    def receive_ack(self, ack_num):
        self.window.receive_ack(ack_num)

class UDP:
    def send(self, data, send_func):
        send_func(data)

# Application Layer Services
class Telnet:
    def __init__(self, transport_layer):
        self.transport_layer = transport_layer
        self.port = self.transport_layer.assign_port('Telnet', 'well-known')

    def connect(self, destination_port):
        print(f"Connecting to Telnet service on port {destination_port}")

    def send_data(self, data, tcp_connection):
        tcp_connection.send(data, self.send_func)

    def send_func(self, data, seq_num):
        print(f"Telnet sending data: {data} with sequence number: {seq_num}")

class FTP:
    def __init__(self, transport_layer):
        self.transport_layer = transport_layer
        self.port = self.transport_layer.assign_port('FTP', 'well-known')

    def connect(self, destination_port):
        print(f"Connecting to FTP service on port {destination_port}")

    def send_data(self, data, tcp_connection):
        tcp_connection.send(data, self.send_func)

    def send_func(self, data, seq_num):
        print(f"FTP sending data: {data} with sequence number: {seq_num}")

# Testing the Full Protocol Stack
if __name__ == "__main__":
    # Instantiate Network Simulator and Transport Layer
    simulator = NetworkSimulator()
    transport_layer = TransportLayer()

    # Create devices and connections
    devices = [simulator.create_device("end_device") for _ in range(5)]
    router = Router(str(uuid.uuid4()))

    for device in devices:
        simulator.create_connection(router, device)

    # Assign IP addresses to devices and add ARP entries to router
    for i, device in enumerate(devices):
        ip_address = f"192.168.0.{i+1}/24"
        device.ip_address = ip_address
        arp_entry = ARPEntry(ip_address, device.device_id)
        router.arp_table[device.device_id] = arp_entry  # Add ARP entry to router
        router.routing_table[ip_address.split('/')[0]] = arp_entry

    # Test ARP
    arp_entry = router.arp_table[devices[0].device_id]
    print(f"ARP Entry: IP Address: {arp_entry.ip_address}, MAC Address: {arp_entry.mac_address}")

    # Test Static Routing
    simulator.send_data(devices[0], "Test data for routing", simulator.connections[0])

    # Test Transport Layer
    tcp = TCP(window_size=2)
    udp = UDP()

    # Test Application Layer Services
    telnet_service = Telnet(transport_layer)
    ftp_service = FTP(transport_layer)

    # Connect Telnet and FTP services to destination ports
    telnet_service.connect(telnet_service.port)
    ftp_service.connect(ftp_service.port)

    # Send data using Telnet and FTP services
    telnet_service.send_data("Telnet Test Data", tcp)
    ftp_service.send_data("FTP Test Data", tcp)

    # Simulate receiving acknowledgments for TCP
    for i in range(2):
        tcp.receive_ack(i)
