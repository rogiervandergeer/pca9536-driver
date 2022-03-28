from time import sleep

from pca9536 import PCA9536
from smbus2 import SMBus


def main():
    with SMBus(1) as bus:  # You may need to change the bus
        device = PCA9536(bus=bus)
        device.mode = "input"  # Set the mode of all pins to input.
        while True:
            inputs = device.read()
            print(f"Pin inputs: {inputs[0]}, {inputs[1]}, {inputs[2]}, {inputs[3]}")
            sleep(1)


if __name__ == "__main__":
    main()
