# PinkPonk TCP over UDP

PinkPonk is a project that simulates a TCP-like protocol using UDP, incorporating essential TCP features such as reliability and congestion control through a Go-Back-N mechanism. This implementation also includes fun functionalities like a Tic Tac Toe game over the network.

---

## 🚨 Important!

### For macOS users:
Run the following command to allow larger datagrams:
```bash
sudo sysctl -w net.inet.udp.maxdgram=65535
```


## 💡 Features

- **TCP-like Protocol over UDP**:
  - Implements Three-Way Handshake
  - Reliable File Transfer with Go-Back-N ARQ
- **Error Detection and Correction**:
  - Hamming ECC for error correction
  - Checksum validation for data integrity
- **Network Simulation**:
  - Test robustness under simulated unstable network conditions
- **Interactive Networked Game**:
  - Tic Tac Toe game with two clients
---

## 🏃 How to Run

### 1. File Transfer
- **Run the server**:
  ```bash
  sudo python src/server.py 123 test/18mb.jpg
  ```
- **Run the client**:
  ```bash
  sudo python src/client.py 100 127.0.0.1 123 tesmee.jpg
  ```
- **Verify file integrity**:
  - On Windows:
    ```powershell
    Get-FileHash -Path ./tesmee -Algorithm MD5
    ```
  - On Linux/macOS:
    ```bash
    md5sum tesmee.jpg
    ```

### 2. Tic Tac Toe Game
- **Start the Tic Tac Toe server**:
  ```bash
  sudo python src/tic_tac_toe_server.py 123
  ```
- **Start two clients (players)**:
  ```bash
  sudo python src/tic_tac_toe_client.py 100 127.0.0.1 123
  sudo python src/tic_tac_toe_client.py 110 127.0.0.1 123
  ```
- Enjoy playing Tic Tac Toe over the network!

### 3. Running on Multiple Devices
To connect multiple devices, use the `-h` flag to specify the server IP address:
```bash
-h=[server IP address]
# Example: -h=192.168.118.100
```

---

## 🌐 Simulating an Unstable Network

### On Linux:
Use the following `tc` command to simulate network issues:
```bash
sudo tc qdisc add dev lo root netem delay 100ms 50ms reorder 8% corrupt 5% duplicate 2% loss 5%
```

### To reset the network configuration after testing:
```bash
sudo tc qdisc del dev lo root netem
```

### On Windows:
Use [Clumsy](https://jagt.github.io/clumsy/) to simulate an unstable network.

---

## ✅ Progress

- **Segment Implementation**: Done
- **Connection Management**: Done
- **Three-Way Handshake**: OK
- **File Transfer**: OK
- **Tic Tac Toe Game**: Fully Functional (Refer to instructions above)
- **Error Correction (ECC Hamming)**: Enable `_ECC=True` in `Segment.py`
- **Multi-Device Network (WiFi)**: Tested and Functional
