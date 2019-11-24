from cqc.pythonLib import CQCConnection
import json

N_QUBIT = 10
with open("n_qubit.config") as config_file:
    N_QUBIT = int(next(config_file).split()[0])

while True:
    with CQCConnection("Charlie") as Charlie:
        master_not_chosen = True
        received_from = []
        first_node_qubits = []
        second_node_qubits = []
        
        # Waiting for the first node :)
        print("~Charlie# Waiting for the first node :)")
        first_node_attempt = Charlie.recvClassical(msg_size=65536)
        attempt = json.loads(first_node_attempt.decode("utf-8"))
        received_from.append(attempt["name"])
        Charlie.sendClassical(received_from[-1], json.dumps(master_not_chosen).encode("utf-8"))
        for _ in range(N_QUBIT):
            first_node_qubits.append(Charlie.recvQubit())
        master_not_chosen = False  # I'm the master!

        # Waiting for the second node :(
        print("~Charlie# Waiting for the second node :(")
        second_node_attempt = Charlie.recvClassical(msg_size=65536)
        attempt = json.loads(second_node_attempt.decode("utf-8"))
        received_from.append(attempt["name"])
        Charlie.sendClassical(received_from[-1], json.dumps(master_not_chosen).encode("utf-8"))
        for _ in range(N_QUBIT):
            second_node_qubits.append(Charlie.recvQubit())
        
        # Ok, I have all the qubits, now let's elaborate them
        
        # Nope! I'm the *evil* Charlie, so I do not do what I am supposed to do :)
        # ...
        
        # Finally create and send the matrix of measurements
        measurements_matrix = []
        for i in range(N_QUBIT):
            first = first_node_qubits[i].measure()
            second = second_node_qubits[i].measure()
            measurements_matrix.append([first, second])
        
        print("~Charlie# Sending matrix")
        measurements_message = json.dumps(measurements_matrix).encode("utf-8")
        Charlie.sendClassical(received_from[0], measurements_message)
        Charlie.sendClassical(received_from[1], measurements_message)
        
        # Release all qubits so I can be ready for another key distribution
        print("~Charlie# Done :)")

        Charlie.release_all_qubits()
