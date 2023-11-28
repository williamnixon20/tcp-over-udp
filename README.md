# PinkPonk TCP over UDP

## Important!
If you're in Mac, try to do this first to allow for bigger datagrams
`sudo sysctl -w net.inet.udp.maxdgram=65535`

## How to run
1. Run the server
`sudo python src/server.py 123 test/18mb.jpg`

2. Run the client
`sudo python src/client.py 100 127.0.0.1 123 tesmee.jpg`

3. Wait and get file hashes 
`[WIN] Get-FileHash -Path ./tesmee -Algorithm MD5`

### Game tic tac toe:
1. Jalankan server tic tac toe
```
sudo python src/tic_tac_toe_server.py 123
```
2. Jalankan 2 client (player)
```
sudo python src/tic_tac_toe_client.py 100 127.0.0.1 123

sudo python src/tic_tac_toe_client.py 110 127.0.0.1 123
```
3. Happy playing!

### To run in 2 devices
1. Jalankan server dan client dengan flag `-h=[ip address dari device]` contoh: `-h=192.168.118.100`

## Simulating unstable network

### Linux
$ tc qdisc add dev lo root netem delay 100ms 50ms reorder 8% corrupt 5% duplicate 2% 5% loss 5%

Penting: Setelah menyelesaikan demo, lakukan perintah ini untuk mengembalikan konfigurasi network interface yang diubah untuk keperluan demo:
$ tc qdisc del dev lo root netem delay 100ms 50ms reorder 8% corrupt 5% duplicate 2% 5% loss 5%

### Win
Download clumsy.

## Progress:

1. Segment (Done)
2. Connection (Done)
3. Three Way Handshake (OK)
4. File Transfer (OK)
5. Tic tac toe (OK) -> Follow readme
6. ECC Hamming (OK) -> Enable _ECC to True add Segment.py
7. 2 Physical device 1 network (wifi) -> Follow readme
Status: Done!
