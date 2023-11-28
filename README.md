# Kalau di mac, ada OS Error UDP terlalu gede.

# Fix pake ini sudo sysctl -w net.inet.udp.maxdgram=65535

# Kalo komputer di reboot ga bs lagi, jadi harus di run lagi

Cara pake:
nyalain server
sudo python3 src/server.py 123 test/18mb.jpg

nyalain klien
sudo python src/client.py 100 123 tesmee

game tic tac toe:
1. Jalankan server tic tac toe
```
sudo python3 src/tic_tac_toe_server.py 123
```
2. Jalankan 2 client (player)
```
sudo python3 src/tic_tac_toe_client.py 100 [server ip address] 123

sudo python3 src/tic_tac_toe_client.py 110 [server ip address] 123
```

Untuk menjalankan di 2 device
1. Jalankan server dan client dengan flag `-h=[ip address dari device]` contoh: `-h=192.168.118.100`

linux unstable network

$ tc qdisc add dev lo root netem delay 100ms 50ms reorder 8% corrupt 5% duplicate 2% 5% loss 5%

Penting: Setelah menyelesaikan demo, lakukan perintah ini untuk mengembalikan konfigurasi network interface yang diubah untuk keperluan demo:
$ tc qdisc del dev lo root netem delay 100ms 50ms reorder 8% corrupt 5% duplicate 2% 5% loss 5%

Progress:

1. Segment (Done)
2. Connection (Done)
3. Three Way Handshake (OK)
4. File Transfer (Edge cases not done, simulated on reliable network only)
