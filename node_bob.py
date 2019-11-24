from cqc.pythonLib import CQCConnection, qubit
import random
import json
import time

N_QUBIT = 10
with open("n_qubit.config") as config_file:
    N_QUBIT = int(next(config_file).split()[0])

with CQCConnection("Bob") as Bob:
    # Preparing my qubits
    h_vector = [random.choice([0, 1]) for _ in range (N_QUBIT)]
    x_vector = [random.choice([0, 1]) for _ in range (N_QUBIT)]
    q_vector = []
    
    for _ in range(N_QUBIT):
        q_vector.append(qubit(Bob))
    
    for i in range(N_QUBIT):
        if x_vector[i] == 1:
            q_vector[i].X()
        if h_vector[i] == 1:
            q_vector[i].H()
    
    # Ask to Charlie (the commutor node as chosen for the network architecture)
    # if I am the master, stating who I am
    print("~Bob    # Am I the master, stating who I am (?_?)")
    Bob.sendClassical("Charlie", json.dumps( {"name": "Bob"} ).encode("utf-8"))
    charlie_attempt_response = Bob.recvClassical()
    im_master = json.loads(charlie_attempt_response.decode("utf-8"))
    
    # If Charlie responded than it's ready for receiving my qubits, I send them
    print("~Bob    # I'm sending the qubits to Charlie (T_T)")
    for qubit in q_vector:
        Bob.sendQubit(qubit, "Charlie")
    
    # Receive the resulting matrix from Charlie
    matrix = json.loads(Bob.recvClassical(msg_size=65536).decode("utf-8"))

    time.sleep(1)

    # Read vector H
    hother_vector = json.loads(Bob.recvClassical(msg_size=65536).decode("utf-8"))

    # Send vector H
    Bob.sendClassical("Alice", json.dumps(h_vector).encode("utf-8"))

    if im_master:
        # Flips the necessary bits based on matrix correlation
        for i in range(N_QUBIT):
            if matrix[i][1] == 0:
                x_vector[i] = "b"
                continue
            if h_vector[i] != hother_vector[i]:
                x_vector[i] = "h"
                continue
            if h_vector[i] == 1 and matrix[i][0] == 0:
                continue
            x_vector[i] = 1 if x_vector[i] == 0 else 0
    else:
        # Remove errors
        for i in range(N_QUBIT):
            if matrix[i][1] == 0:
                x_vector[i] = "b"
                continue
            if h_vector[i] != hother_vector[i]:
                x_vector[i] = "h"
                continue

    # Filtering key
    key = []
    for i in range(N_QUBIT):
        if type(x_vector[i]) is not str:
            key.append(x_vector[i])

    # Print the key obtained
    print("~Bob    # " + repr(key))
    print("~Bob    # Key length: " + str(len(key)))

    # Key symmetrization phase
    if not im_master:
        symmetr_length = int(len(key) / 3)
        Bob.sendClassical("Alice", json.dumps(key[:symmetr_length]).encode("utf-8"))
        symmetr_settlement = json.loads(Bob.recvClassical().decode("utf-8"))
        if symmetr_settlement == "CHARLIE_IS_EVIL":
            print("~Bob    # Charlie is evil: I'm destroying the key")
            key = None
        elif symmetr_settlement == "CHARLIE_IS_GOOD":
            print("~Bob    # Charlie is good: key is usable")
            print("~Bob    # Usable key: " + repr(key[symmetr_length:]))
    else:
        symmetr_key = json.loads(Bob.recvClassical(msg_size=65536).decode("utf-8"))
        symmetr_length = len(symmetr_key)
        key_errors = 0
        for i in range(symmetr_length):
            if symmetr_key[i] != key[i]:
                key_errors += 1
        qber = key_errors / symmetr_length
        print("~Bob    # QBER = " + str(qber))
        if symmetr_key == key[:symmetr_length]:
            Bob.sendClassical("Alice", json.dumps("CHARLIE_IS_GOOD").encode("utf-8"))
            print("~Bob    # Charlie is good: key is usable")
            print("~Bob    # Usable key: " + repr(key[symmetr_length:]))
        else:
            Bob.sendClassical("Alice", json.dumps("CHARLIE_IS_EVIL").encode("utf-8"))
            print("~Bob    # Charlie is evil: I'm destroying the key")
            key = None
