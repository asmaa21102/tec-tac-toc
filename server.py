import socket
import threading
import time

board = [str(i) for i in range(1, 10)]
current_player = "X"
players = []
lock = threading.Lock()
game_started = False  

def print_board():
    return f"""
     {board[0]} | {board[1]} | {board[2]} 
    ---+---+---
     {board[3]} | {board[4]} | {board[5]} 
    ---+---+---
     {board[6]} | {board[7]} | {board[8]} 
    """

def is_winner():
    win_patterns = [
        [0, 1, 2], [3, 4, 5], [6, 7, 8],  # Rows
        [0, 3, 6], [1, 4, 7], [2, 5, 8],  # Columns
        [0, 4, 8], [2, 4, 6]              # Diagonals
    ]
    for pattern in win_patterns:
        if board[pattern[0]] == board[pattern[1]] == board[pattern[2]]:
            return True
    return False

def is_draw():
    return all(cell in ["X", "O"] for cell in board)

def broadcast(message):
    for player in players:
        player.sendall(message.encode())

def reset_game():
    global board, current_player
    board = [str(i) for i in range(1, 10)]  
    current_player = "X"  

def handle_client(client, player_symbol):
    global current_player, game_started
    client.sendall(f"Welcome, Player {player_symbol}!\n".encode())

    while len(players) < 2:
        pass

    if len(players) == 2 and not game_started:
        game_started = True  
        broadcast("Both players connected. Let the game begin!\n")
        broadcast(print_board())

    waiting_message_sent = False  
    while True:
        try:
            with lock:
                if current_player == player_symbol:
                    waiting_message_sent = False  
                    client.sendall("Your move. Enter cell number: ".encode())
                    move = client.recv(1024).decode().strip()
                    if move.isdigit() and int(move) in range(1, 10) and board[int(move) - 1] not in ["X", "O"]:
                        board[int(move) - 1] = player_symbol
                        broadcast(print_board())

                        if is_winner():
                            broadcast(f"Player {player_symbol} ({player_symbol}) wins!\n")
                            client.sendall(f"Congratulations! You win!\n".encode())  
                            time.sleep(2)  
                            reset_game() 
                            broadcast("The game is restarting...\n")
                            broadcast(print_board())
                            break
                        elif is_draw():
                            broadcast("It's a draw!\n")
                            time.sleep(2)  
                            reset_game()  
                            broadcast("The game is restarting...\n")
                            broadcast(print_board())
                            break

                        current_player = "O" if current_player == "X" else "X"
                    else:
                        client.sendall("Invalid move! Try again.\n".encode())
                else:
                    if not waiting_message_sent and current_player != player_symbol:
                        client.sendall("Waiting for the other player...\n".encode())
                        waiting_message_sent = True
        except Exception as e:
            print(f"Error: {e}")
            break


    if len(players) == 2:
        handle_client(players[0], "X")
        handle_client(players[1], "O")

def main():
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind(("127.0.0.1", 8080))
    server.listen(2)

    print("Server started. Waiting for players...")
    while len(players) < 2:
        client, addr = server.accept()
        print(f"Player {len(players) + 1} connected: {addr}")
        players.append(client)
        player_symbol = "X" if len(players) == 1 else "O"
        threading.Thread(target=handle_client, args=(client, player_symbol)).start()

if __name__ == "__main__":
    main()