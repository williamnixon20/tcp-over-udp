# Kalau di mac, ada OS Error UDP terlalu gede. 
# Fix pake ini sudo sysctl -w net.inet.udp.maxdgram=65535
# Kalo komputer di reboot ga bs lagi, jadi harus di run lagi

Cara pake:
nyalain server
 sudo python3 src/server.py 123 test/18mb.jpg

nyalain klien
 sudo python src/client.py 100 123 tesmee

Progress:
1. Segment (Done)
2. Connection (Done)
3. Three Way Handshake (OK)
4. File Transfer (Edge cases not done, simulated on reliable network only)