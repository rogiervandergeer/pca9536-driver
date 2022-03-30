# This example is functionally the same as example 0, but uses the simultaneous interface
from pca9536 import PCA9536
from smbus2 import SMBus


def main():
    with SMBus(1) as bus:  # You may need to change the bus
        device = PCA9536(bus=bus)
        # Set the mode of pin 0 to input, the mode of pin 1 to output, and do not change the other pins
        device.mode = "input", "output", None, None
        device.write(pin_1=True)  # Set the output of pin 1 to high
        inputs = device.read()
        print(f"Pin 0 input: {inputs[0]}")


if __name__ == "__main__":
    main()
