from enum import Enum
from typing import List, Union

from smbus2 import SMBus


class PinMode(Enum):
    output = 0
    input = 1


class Pin:
    def __init__(self, device: "PCA9536", index: int):
        self._bitmask = 0x01 << index
        self._device = device
        self.index = index

    @property
    def mode(self) -> PinMode:
        data = self._device._read_bits(0x03, bitmask=self._bitmask) / self._bitmask
        return PinMode(data)

    @mode.setter
    def mode(self, value: Union[PinMode, str]) -> None:
        if not isinstance(value, PinMode):
            value = PinMode[value]
        data = value.value * self._bitmask
        self._device._write_bits(0x03, value=data, bitmask=self._bitmask)

    @property
    def polarity_inversion(self) -> bool:
        return bool(self._device._read_bits(0x02, bitmask=self._bitmask))

    @polarity_inversion.setter
    def polarity_inversion(self, value: bool) -> None:
        self._device._write_bits(0x02, value=0xFF * value, bitmask=self._bitmask)

    def read(self) -> bool:
        return bool(self._device._read_bits(0x00, bitmask=self._bitmask))

    def write(self, value: bool) -> None:
        self._device._write_bits(0x01, value=0xFF * value, bitmask=self._bitmask)


class PCA9536:
    def __init__(self, bus: SMBus, address: int = 0x41):
        self.address = address
        self.bus = bus

    @property
    def pins(self) -> List[Pin]:
        return [Pin(self, index) for index in range(4)]

    def _read_bits(self, register: int, bitmask: int) -> int:
        return self.bus.read_byte_data(self.address, register=register) & bitmask

    def _write_bits(self, register: int, value: int, bitmask: int) -> None:
        other_bits = self._read_bits(register=register, bitmask=0xFF - bitmask)
        value_bits = value & bitmask
        self.bus.write_byte_data(
            self.address, register=register, value=other_bits | value_bits
        )
