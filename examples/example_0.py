from pca9536 import PCA9536
from smbus2 import SMBus


def main():
    with SMBus(1) as bus:  # You may need to change the bus
        device = PCA9536(bus=bus)
        pin_0, pin_1 = device[0], device[1]
        pin_0.mode = "input"
        pin_1.mode = "output"
        pin_1.write(True)
        print(f"Pin 0 input: {pin_0.read()}")


if __name__ == "__main__":
    main()
