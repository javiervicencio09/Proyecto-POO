import os
import sys

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
ECOTECH_DIR = os.path.join(BASE_DIR, "ecotech")

if ECOTECH_DIR not in sys.path:
    sys.path.insert(0, ECOTECH_DIR)

os.chdir(ECOTECH_DIR)

from main import main

if __name__ == "__main__":
    main()
