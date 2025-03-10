import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from predict_age.server.server import Server_age

def Run_server():
    server_instance = Server_age()
    server_instance.run_server_age()


if __name__ == "__main__":
    Run_server()