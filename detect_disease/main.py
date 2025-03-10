import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from detect_disease.server.server import Server_disease

def Run_server():
    server_instance = Server_disease()
    server_instance.run_server_disease()

if __name__ == "__main__":
    Run_server()
