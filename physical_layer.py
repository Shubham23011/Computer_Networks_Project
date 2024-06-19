import uuid

class Device:
    def __init__(self, device_id, device_type):
        self.device_id = device_id
        self.device_type = device_type
    
    def send_data(self, data, connection):
        print(f"Device {self.device_id} sending data: {data}")
        connection.transmit_data(data, self)

    def receive_data(self, data):
        print(f"Device {self.device_id} received data: {data}")

class Hub(Device):
    def __init__(self, device_id):
        super().__init__(device_id, "hub")
        self.connected_devices = []

    def add_device(self, device):
        self.connected_devices.append(device)

    def broadcast_data(self, data, sender):
        for device in self.connected_devices:
            if device != sender:
                device.receive_data(data)

class Connection:
    def __init__(self, device1, device2):
        self.connection_id = str(uuid.uuid4())
        self.device1 = device1
        self.device2 = device2

    def transmit_data(self, data, sender):
        if sender == self.device1:
            self.device2.receive_data(data)
        else:
            self.device1.receive_data(data)

class NetworkSimulator:
    def __init__(self):
        self.devices = []
        self.connections = []

    def create_device(self, device_type):
        device_id = str(uuid.uuid4())
        if device_type == "hub":
            device = Hub(device_id)
        else:
            device = Device(device_id, device_type)
        self.devices.append(device)
        return device

    def create_connection(self, device1, device2):
        connection = Connection(device1, device2)
        self.connections.append(connection)
        return connection

    def send_data(self, sender, data, connection):
        sender.send_data(data, connection)

# Example Usage for Physical Layer
if __name__ == "__main__":
    simulator = NetworkSimulator()

    # Create devices
    device1 = simulator.create_device("end_device")
    device2 = simulator.create_device("end_device")
    hub = simulator.create_device("hub")

    # Create connections
    conn1 = simulator.create_connection(device1, hub)
    conn2 = simulator.create_connection(device2, hub)

    # Add devices to hub
    hub.add_device(device1)
    hub.add_device(device2)

    # Send data
    simulator.send_data(device1, "Hello, World!", conn1)

    # Testing Two End Devices with Dedicated Connection
    device3 = simulator.create_device("end_device")
    device4 = simulator.create_device("end_device")
    conn3 = simulator.create_connection(device3, device4)
    simulator.send_data(device3, "Test Message", conn3)

    # Testing Star Topology
    devices = [simulator.create_device("end_device") for _ in range(5)]
    hub2 = simulator.create_device("hub")

    con = []
    for device in devices:
        conn = simulator.create_connection(device, hub2)
        con.append(conn)
        hub2.add_device(device)

    for i, device in enumerate(devices):
        simulator.send_data(device, f"Message from device {i+1}", con[i])
