from enum import Enum
from typing import List, Union, Tuple, Optional, Iterator

from smbus2 import SMBus


class PinMode(Enum):
    output = 0
    input = 1


class PCA9536Pin:
    def __init__(self, device: "PCA9536", index: int):
        self.device = device
        self.index = index

    @property
    def mode(self) -> PinMode:
        return self.device.mode[self.index]

    @mode.setter
    def mode(self, value: Union[PinMode, str]) -> None:
        self.device.mode = self._value_to_list(value)

    @property
    def polarity_inversion(self) -> bool:
        return self.device.polarity_inversion[self.index]

    @polarity_inversion.setter
    def polarity_inversion(self, value: bool) -> None:
        self.device.polarity_inversion = self._value_to_list(value)

    def read(self) -> bool:
        return self.device.read()[self.index]

    def write(self, value: bool) -> None:
        self.device.write(*self._value_to_list(value))

    def _value_to_list(self, value):
        result = [None, None, None, None]
        result[self.index] = value
        return tuple(result)


class PCA9536:
    def __init__(self, bus: SMBus, address: int = 0x41):
        self.address = address
        self.bus = bus
        self._pins: List[PCA9536Pin] = [PCA9536Pin(self, index) for index in range(4)]

    def __getitem__(self, item: int) -> PCA9536Pin:
        return self._pins[item]

    def __iter__(self) -> Iterator[PCA9536Pin]:
        yield from self._pins

    @property
    def mode(self) -> Tuple[PinMode, PinMode, PinMode, PinMode]:
        data = _read_bits(
            bus=self.bus, address=self.address, register=0x03, bitmask=0x0F
        )
        return (
            PinMode(data & 0x01),
            PinMode((data & 0x02) >> 1),
            PinMode((data & 0x04) >> 2),
            PinMode((data & 0x08) >> 3),
        )

    @mode.setter
    def mode(
        self,
        value: Union[
            PinMode,
            str,
            Tuple[
                Optional[Union[PinMode, str]],
                Optional[Union[PinMode, str]],
                Optional[Union[PinMode, str]],
                Optional[Union[PinMode, str]],
            ],
        ],
    ) -> None:
        if not isinstance(value, tuple):
            value = value, value, value, value
        values: List[Optional[PinMode]] = [
            PinMode[v] if isinstance(v, str) else v for v in value
        ]
        bitmask = _bools_to_bits(*(value is not None for value in values))
        mode = _bools_to_bits(*(value == PinMode.input for value in values))
        _write_bits(
            bus=self.bus,
            address=self.address,
            register=0x03,
            value=mode,
            bitmask=bitmask,
        )

    @property
    def polarity_inversion(self) -> Tuple[bool, bool, bool, bool]:
        data = _read_bits(
            bus=self.bus, address=self.address, register=0x02, bitmask=0x0F
        )
        return (
            bool(data & 0x01),
            bool((data & 0x02) >> 1),
            bool((data & 0x04) >> 2),
            bool((data & 0x08) >> 3),
        )

    @polarity_inversion.setter
    def polarity_inversion(
        self,
        value: Union[
            bool,
            Tuple[
                Optional[bool],
                Optional[bool],
                Optional[bool],
                Optional[bool],
            ],
        ],
    ):
        if not isinstance(value, tuple):
            value = value, value, value, value
        bitmask = _bools_to_bits(*(value is not None for value in value))
        polarity = _bools_to_bits(*(value is True for value in value))
        _write_bits(
            bus=self.bus,
            address=self.address,
            register=0x02,
            value=polarity,
            bitmask=bitmask,
        )

    def read(self) -> Tuple[bool, bool, bool, bool]:
        data = _read_bits(
            bus=self.bus, address=self.address, register=0x00, bitmask=0x0F
        )
        return _bits_to_bools(data)

    def write(
        self,
        pin_0: Optional[bool] = None,
        pin_1: Optional[bool] = None,
        pin_2: Optional[bool] = None,
        pin_3: Optional[bool] = None,
    ):
        pins = (pin_0, pin_1, pin_2, pin_3)
        value = _bools_to_bits(*(pin is True for pin in pins))
        bitmask = _bools_to_bits(*(pin is not None for pin in pins))
        _write_bits(
            bus=self.bus,
            address=self.address,
            register=0x01,
            value=value,
            bitmask=bitmask,
        )


def _bools_to_bits(bool_0: bool, bool_1: bool, bool_2: bool, bool_3: bool) -> int:
    return (bool_0 * 0x01) | (bool_1 * 0x02) | (bool_2 * 0x04) | (bool_3 * 0x08)


def _bits_to_bools(bits: int) -> Tuple[bool, bool, bool, bool]:
    return (
        bool(bits & 0x01),
        bool(bits & 0x02),
        bool(bits & 0x04),
        bool(bits & 0x08),
    )


def _read_bits(bus: SMBus, address: int, register: int, bitmask: int) -> int:
    return bus.read_byte_data(address, register=register) & bitmask


def _write_bits(
    bus: SMBus, address: int, register: int, value: int, bitmask: int
) -> None:
    other_bits = _read_bits(
        bus=bus, address=address, register=register, bitmask=0xFF - bitmask
    )
    value_bits = value & bitmask
    bus.write_byte_data(address, register=register, value=other_bits | value_bits)
