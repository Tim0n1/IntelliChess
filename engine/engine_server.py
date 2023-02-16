import engine
import socket
import json

# Define the server address and port
SERVER_ADDRESS = '192.168.1.102'
SERVER_PORT = 5555

# Create a socket object
server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# Bind the socket to a specific address and port
server_socket.bind((SERVER_ADDRESS, SERVER_PORT))

# Listen for incoming connections
server_socket.listen(1)

while True:
    # Wait for a client to connect
    print('Waiting for a client to connect...')
    client_socket, client_address = server_socket.accept()
    print(f'Client connected: {client_address}')

    while True:
        # Receive a message from the client
        try:
            data = client_socket.recv(1024).decode()
        except ConnectionResetError:
            break

        if not data:
            # If the client has closed the connection, break out of the loop
            break

        # Parse the message as JSON
        try:
            message = json.loads(data)
            input1 = message['message']
            print(f'Received message: {input1}')
            if input1[0:4] == '-fen':
                print('fen->',input1[6:])
            if input1[0:3] == '-bm':


            # Create a response message
            response = {'message': 'kvo staa bace'}
            response_json = json.dumps(response)

            # Send the response back to the client
            client_socket.send(response_json.encode())
        except Exception as e:
            print(f'Error parsing JSON: {e}')

    # Close the client connection
    client_socket.close()
    print(f'Client disconnected: {client_address}')

# Close the server socket
server_socket.close()


