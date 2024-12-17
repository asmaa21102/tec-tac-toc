import socket

def main():
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client.connect(("127.0.0.1", 8080))
    client.settimeout(3000)

    while True:
        try:
            message = client.recv(1024).decode()
            print(message)
            if "Enter cell number" in message:
                move = input("Your move: ")
                client.sendall(move.encode())
        except:
            print("Disconnected from the server.")
            break

if __name__ == "__main__":
    main()
