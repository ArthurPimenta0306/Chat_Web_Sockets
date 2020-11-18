import websockets
import asyncio
@asyncio.coroutine
def client_handler(websocket, path):
    print('Novo cliente', websocket)
    print(' ({} clientes existentes)'.format(len(clients)))

    # Loop que verifica se o nome não é repetido
    while 1:
        nome_aceitavel = True
        name = yield from websocket.recv()
        for client in clients.values():
            if name == client:
                nome_aceitavel = False
        if nome_aceitavel:
            break
        else:
            yield from websocket.send("Este nome já esta sendo utilizado. Entre com outro nome")

    #boas vindas
    yield from websocket.send('Bem vindo ao servidor de chat escrito em python com asyncio e Websockets, {}'.format(name))
    yield from websocket.send('Existem {} outros usuários conectados: {}'.format(len(clients), list(clients.values())))
    clients[websocket] = name

    #notifica todos os outros usuarios de que um novo entrou
    for client, _ in clients.items():
        yield from client.send(name + ' Entrou no chat')

    # loop de mensagens
    while True:
        message = yield from websocket.recv()
        #caso tenha se desconectado:
        if message is None:
            their_name = clients[websocket]
            del clients[websocket]
            print('Cliente desconectou', websocket)
            for client, _ in clients.items():
                yield from client.send(their_name + ' Saiu do chat')
            break

        #mensagem privada:
        if message[0:4] == "priv":
            #loop para encontrar o fim do nome do cliente privado
            for i in range(len(message)):
                if message[i]==":":
                    break

            private_client_name = message[5:i]
            #loop para encontrar o socket do cliente privado
            for client in clients.items():
                client_sock = client[0]
                client_name = client[1]
                if client_name == private_client_name:
                    yield  from client_sock.send('{}: {}'.format(name, message[i+2:len(message)]))
                   # yield from client_sock.send(message[i+2:len(message)])
                    break

        else: #mensagem publica
            for client, _ in clients.items():
                yield from client.send('{}: {}'.format(name, message))

clients = {} #: {websocket: name}
LISTEN_ADDRESS = ('0.0.0.0', 9898)
start_server = websockets.serve(client_handler, *LISTEN_ADDRESS)
asyncio.get_event_loop().run_until_complete(start_server)
asyncio.get_event_loop().run_forever()