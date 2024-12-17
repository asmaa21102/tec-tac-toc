#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <winsock2.h>
#include <windows.h>

#pragma comment(lib, "ws2_32.lib")

#define BUFFER_SIZE 1024

int main() {
    WSADATA wsa;
    SOCKET client_sock;
    struct sockaddr_in server_addr;
    char buffer[BUFFER_SIZE];

    // Initialize Winsock
    if (WSAStartup(MAKEWORD(2, 2), &wsa) != 0) {
        printf("Winsock initialization failed. Error Code: %d\n", WSAGetLastError());
        return 1;
    }

    // Create socket
    if ((client_sock = socket(AF_INET, SOCK_STREAM, 0)) == INVALID_SOCKET) {
        printf("Socket creation failed. Error Code: %d\n", WSAGetLastError());
        WSACleanup();
        return 1;
    }

    // Set receive timeout (e.g., 10 seconds)
    int timeout = 1000000; // Timeout in milliseconds
    if (setsockopt(client_sock, SOL_SOCKET, SO_RCVTIMEO, (const char*)&timeout, sizeof(timeout)) < 0) {
        printf("Failed to set socket timeout. Error Code: %d\n", WSAGetLastError());
        closesocket(client_sock);
        WSACleanup();
        return 1;
    }

    // Configure server address
    server_addr.sin_family = AF_INET;
    server_addr.sin_port = htons(8080);
    server_addr.sin_addr.s_addr = inet_addr("127.0.0.1");

    // Connect to server
    if (connect(client_sock, (struct sockaddr *)&server_addr, sizeof(server_addr)) < 0) {
        printf("Connection failed. Error Code: %d\n", WSAGetLastError());
        closesocket(client_sock);
        WSACleanup();
        return 1;
    }

    printf("Connected to the server.\n");

    while (1) {
        // Receive message from server
        memset(buffer, 0, BUFFER_SIZE);
        int bytes_received = recv(client_sock, buffer, BUFFER_SIZE - 1, 0);

        if (bytes_received == SOCKET_ERROR) {
            if (WSAGetLastError() == WSAETIMEDOUT) {
                printf("No response from server. Connection timed out.\n");
                break;
            }
            printf("Disconnected from the server.\n");
            break;
        } else if (bytes_received == 0) {
            printf("Disconnected from the server.\n");
            break;
        }

        buffer[bytes_received] = '\0'; // Null-terminate the received string
        printf("%s\n", buffer);

        // If server requests input
        if (strstr(buffer, "Enter cell number") != NULL) {
            printf("Your move: ");
            fgets(buffer, BUFFER_SIZE, stdin);

            // Remove newline character from input
            buffer[strcspn(buffer, "\n")] = '\0';

            // Send the input back to the server
            send(client_sock, buffer, strlen(buffer), 0);
        }
    }

    // Clean up
    closesocket(client_sock);
    WSACleanup();

    return 0;
}
