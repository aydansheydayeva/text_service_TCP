# About "text_service.py" app

Client-server CLI based application where client passes 2 files to the server that, in turn, processes file contents according to 2 modes and returns processed data inside the new txt file to client.  

## Scenario

First, client sends 2 files to the server in the one of next 2 modes:

- **change_text:** if this mode is provided, client should send one .txt and one .json file. Server will replace all occurences of .txt file words according to the json file.
 **Note:** replacament of words is case-sensitive, therefore consider it while creating .json file

- **encode_decode:** in this case, client sends 1 .txt file and other .txt file, where second file is the key file. This mode encodes (XOR operation) first file with the key inside the second file, if the first file is in plaintext format. However, if the first file is encoded file, then this mode will perform decoding process.

First mode will create **processed_by_change_text.txt** file, second mode will create **processed_by_encode_decode.txt** file. Both of these files will be sent to client and saved inside the directory of original 2 files.



## Installation

To download app, you need to type following command:

```bash
git clone https://github.com/aydansheydayeva/text_service_TCP
```
 Then install requirements to have all packets needed for this project:

```bash
pip install requirements.txt
```

## Usage

To use this app, 2 terminals should be opened. Next 2 commands should be run in terminals:

**Server terminal:**
```
python3 text_service.py server "" -p 5555
```
Here "" represents the interface for server to accept incoming data and "-p" is for port number. In this example, port is 5555. If not mentioned, port selected by default is 4444.

**Client terminal:**
```
python3 text_service.py client hostname -p 5555 --mode change_text file1.txt file2.json
```
OR
```
python3 text_service.py client hostname -p 5555 --mode encode_decode file.txt key.txt
```
Here instead of "hostname", hostname of your local machine should be written. Default port to connect is 4444.
