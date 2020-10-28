import socket, argparse, os, sys

class Server:

    def __init__(self, host, port):
        self.host = host
        self.port = port
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    def recvall(self, conn, length):
        data = b''
        while len(data) < length :
            more = conn.recv(length - len(data))
            if not more:
                raise EOFError('was expecting %d bytes but only received'
                                ' %d bytes before the socket closed'
                                % (length, len(data)))
            data += more
        return data

    def xor(self,cont1, cont2):
        len1 = len(cont1)
        len2 = len(cont2)
        if len1 > len2:
            cont2 = (cont2 * (len1//len2+1))[:len1]
        elif len2 > len1:
            cont1 = (cont1 * (len2//len1+1))[:len2]
        return bytes([_a ^ _b for _a, _b in zip(cont1.encode(), cont2.encode())])

    def xor_files_and_get_content(self, filename):
        f = open(filename, "rb")
        content = (f.read()).decode()
        
        file_part = (content.split("%"*21))[0]
        key_part = (content.split("%"*21))[1]

        content_for_new_file = self.xor(file_part, key_part)
        f.close()
        return content_for_new_file

    def process_json(self, file_c, json_file):
        json_dict = eval(json_file)
        new_content = file_c
        for key,value in json_dict.items():
                new_content = new_content.replace(key, value)

        return new_content.encode()

    def make_json_changes_to_txt_file(self, filename):
        f = open(filename, "rb")
        content = (f.read()).decode()
        
        file_part = (content.split("%"*21))[0]
        json_part = (content.split("%"*21))[1]

        content_for_new_file = self.process_json(file_part, json_part)
        f.close()
        return content_for_new_file        

    def start_working(self):
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.sock.bind((self.host, self.port))
        self.sock.listen(1)

        print("Server is listening at ", self.sock.getsockname())
        print("---"*18)

        while True:
            conn, sockname = self.sock.accept()
            mode = (conn.recv(1024)).decode()
            print("Connection established with ", sockname)
            print('  Socket name:', conn.getsockname())
            print('  Socket peer:', conn.getpeername())

            # ------- receiving joined files -------
            length = conn.recv(1024)
                
            new_file_name = "temporary_server_file.txt"
            f = open(new_file_name, "wb")
            whole_message = self.recvall(conn, int(length.decode()))
            
            print("Receiving files ...")
            f.write(whole_message)
            f.close()

            # ------- receiving joined files -------
            
            if mode == "change_text":
                result_content_of_json_changes = self.make_json_changes_to_txt_file(new_file_name)
                conn.send(str(len(result_content_of_json_changes)).encode())
                conn.sendall(result_content_of_json_changes)
            elif mode == "encode_decode":
                result_content_of_xor = self.xor_files_and_get_content(new_file_name)
                conn.send(str(len(result_content_of_xor)).encode())
                conn.sendall(result_content_of_xor)

            os.remove("temporary_server_file.txt")

            print("Files were processed and final file was sent to client !!!")
            answer = "Server reply: Files were processed and final file was sent to client !!!"
            conn.sendall(answer.encode())
            conn.close()
            #break
        #self.sock.close()


class Client:

    def __init__(self, host, port):
        self.host = host
        self.port = port
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    def recvall(self, conn, length):
        data = b''
        while len(data) < length :
            more = conn.recv(length - len(data))
            if not more:
                raise EOFError('was expecting %d bytes but only received'
                                ' %d bytes before the socket closed'
                                % (length, len(data)))
            data += more
        return data

    def output_file(self, original_filename_for_path, mode):
        processed_content_length = self.sock.recv(1024)
        processed_content = self.recvall(self.sock, int(processed_content_length.decode()))
        contennt = processed_content.decode()
        dir_path = os.path.dirname(os.path.realpath(original_filename_for_path))
        if mode == "change_text":
            filee_name = "processed_by_change_text.txt"
        elif mode == "encode_decode":
            filee_name = "processed_by_encode_decode.txt"
        file_name_in_original_file_directory = os.path.join(dir_path, filee_name)
        f = open(file_name_in_original_file_directory, "w")
        f.write(contennt)
        f.close()


    def start_working(self, filename1, filename2, mode):
        self.sock.connect((self.host, self.port))
        self.sock.send(mode.encode())
        print("Client socket: ", self.sock.getsockname())

        f1 = open(filename1, "rb")
        f1_size = os.path.getsize(filename1)
        f1_content = f1.read()

        f2 = open(filename2, "rb")
        f2_size = os.path.getsize(filename2)
        f2_content = f2.read()

        common_size = f1_size + f2_size + 21
        self.sock.send(str(common_size).encode())

        common_content = f1_content + ("%"*21).encode() + f2_content
        self.sock.sendall(common_content)
        f1.close()
        f2.close()
        print("Sending files ... ")

        #processed result
        self.output_file(filename1, mode)

        final_result = self.sock.recv(1024)
        print(final_result.decode())
        self.sock.close()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description = "TCP file transfer")
    choices = {"server": Server, "client": Client}
    parser.add_argument('role', choices = choices, help = "server or client")
    parser.add_argument("host", help="interface server listens at, hostname client sends to")
    parser.add_argument("-p", metavar="PORT", type=int, default=4444, help="UDP port (default 4444)")

    if sys.argv[1] == "client":
        parser.add_argument('--mode', type = str, help = "change_text/encode_decode")
        parser.add_argument('file1', type = str, help = "path to the file1")
        parser.add_argument('file2', type = str, help = "path to the file2")

    args = parser.parse_args()
    function = choices[args.role]

    if args.role == "server":
        server_obj = function(args.host, args.p)
        server_obj.start_working()

    elif args.role == "client":
        client_obj = function(args.host, args.p)
        client_obj.start_working(args.file1, args.file2, args.mode)