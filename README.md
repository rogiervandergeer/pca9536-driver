# pca9536-driver
Easy-to-use python driver for the PCA9536 GPIO expander.

![GitHub Workflow Status](https://img.shields.io/github/actions/workflow/status/rogiervandergeer/pca9536-driver/test.yaml?branch=main) 
![PyPI](https://img.shields.io/pypi/v/pca9536-driver)
![PyPI - License](https://img.shields.io/pypi/l/pca9536-driver)
![PyPI - Downloads](https://img.shields.io/pypi/dm/pca9536-driver) 

## Installation

The package is available on [PyPI](https://pypi.org/project/pca9536-driver/). Installation is can be done with your favourite package manager. For example:

```bash
pip install pca9536-driver
```

## Usage

In order to initialise the device we need an open `SMBus` object. 
Depending on the machine that you are running on you may need to provide another bus number or path:
```python
from pca9536 import PCA9536
from smbus2 import SMBus


with SMBus(1) as bus:
    device = PCA9536(bus=bus)
```

The address of the `PCA9536` defaults to `0x41`. This is the (fixed) address of the PCA9536 devices, so you should
never have to change it. If you _do_ want to change it, you can provide it like `PCA9536(bus=bus, address=0x42)`.

### Controlling a pin

The PCA9536 has four GPIO pins, which are represented by `PCA9536Pin` objects that can be accessed by using index brackets:
```python
pin = device[0]
```
If desired, you can loop over all pins:
```python
for pin in device:
    ...
```

Reading the logic level of the pin is done with the `read()` method, which returns a boolean:
```python
logic_level = pin.read()
```

To switch the pin to output mode and write the logic level:
```python
from pca9536 import PinMode

pin.mode = PinMode.output  # or use "output"
pin.write(True)
```
Note that writing only sets the output flip-flops of the GPIO expander, and has therefore no
effect when the pin is in input mode.

### Simultaneous operations

If you have the need to read from, write to or set the mode of multiple pins simultaneously,
then you can use the respective methods and properties of the `PCA9536` object.

Reading returns a tuple of four booleans:
```python
pin_0, pin_1, pin_2, pin_3 = device.read()
```

Writing can be done to one or more pins at the same time:
```python
device.write(pin_0=True, pin_2=False)
```

Setting the same mode of all pins to the same value:
```python
device.mode = PinMode.input
```
or specify a value per pin by providing a tuple of four values:
```python
device.mode = PinMode.input, Pinmode.output, "input", None
```
Note that also here the values `PinMode.input` and `PinMode.output` may be used interchangeably with the strings
`"input"` and `"output"`. Providing `None` for any of the values will leave the mode of the respective pin unchanged.

### Polarity inversion

The PCA9536 offers functionality to invert the polarity of the input bits. Note that the outputs are not affected
by this setting.

Polarity inversion of a single pin can be enabled by:
```python
pin.polarity_inversion = True
```

Polarity inversion of all pins can be set at the same time in a similar manner to that of the pin mode:
```python
device.polarity_inversion = False
# or
device.polarity_inversion = False, True, True, None
```
where `None` will leave the current polarity inversion of a pin untouched.
