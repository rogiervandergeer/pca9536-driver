from pytest import fixture, mark, raises

from pca9536.pca9536 import PCA9536, _read_bits, _write_bits, PCA9536Pin, PinMode


class TestPCA9536:
    @fixture(scope="function")
    def device(self, mocker) -> PCA9536:
        bus = mocker.Mock()
        bus.read_byte_data.return_value = 0xA5
        return PCA9536(bus=bus)

    def test_getitem(self, device: PCA9536):
        pin = device[2]
        assert isinstance(pin, PCA9536Pin)
        assert pin.device == device
        assert pin.index == 2
        with raises(IndexError):
            _ = device[4]

    def test_iter(self, device: PCA9536):
        for pin in device:
            assert isinstance(pin, PCA9536Pin)

    def test_mode(self, device: PCA9536):
        modes = device.mode
        assert modes == (PinMode.input, PinMode.output, PinMode.input, PinMode.output)

    @mark.parametrize(
        "value, write_byte",
        [
            (PinMode.input, 0xAF),
            (PinMode.output, 0xA0),
            ("input", 0xAF),
            ("output", 0xA0),
            (("input", "output", "output", "input"), 0xA9),
            ((PinMode.output, PinMode.input, None, None), 0xA6),
            ((None, None, None, None), 0xA5),
        ],
    )
    def test_set_mode(self, device: PCA9536, value, write_byte):
        device.mode = value
        device.bus.write_byte_data.assert_called_once_with(  # type: ignore
            0x41, register=0x03, value=write_byte
        )

    def test_polarity(self, device: PCA9536):
        assert device.polarity_inversion == (True, False, True, False)

    @mark.parametrize(
        "value, write_byte",
        [
            (True, 0xAF),
            (False, 0xA0),
            ((True, False, False, True), 0xA9),
            ((False, True, None, None), 0xA6),
            ((None, None, None, None), 0xA5),
        ],
    )
    def test_set_polarity(self, device: PCA9536, value, write_byte):
        device.polarity_inversion = value
        device.bus.write_byte_data.assert_called_once_with(  # type: ignore
            0x41, register=0x02, value=write_byte
        )

    def test_read(self, device: PCA9536):
        assert device.read() == (True, False, True, False)

    def test_write(self, device: PCA9536):
        device.write(pin_0=True, pin_2=False)
        device.bus.write_byte_data.assert_called_once_with(  # type: ignore
            0x41, register=0x01, value=0xA1
        )


class TestPCA9536Pin:
    @fixture(scope="function")
    def pin(self, mocker) -> PCA9536Pin:
        bus = mocker.Mock()
        bus.read_byte_data.return_value = 0xA5
        device = PCA9536(bus=bus)
        return device[2]

    def test_mode(self, pin: PCA9536Pin):
        assert pin.mode == PinMode.input

    def test_set_mode(self, pin: PCA9536Pin):
        pin.mode = PinMode.output
        pin.device.bus.write_byte_data.assert_called_once_with(  # type: ignore
            0x41, register=0x03, value=0xA1
        )

    def test_polarity(self, pin: PCA9536Pin):
        assert pin.polarity_inversion is True

    def test_set_polarity(self, pin: PCA9536Pin):
        pin.polarity_inversion = False
        pin.device.bus.write_byte_data.assert_called_once_with(  # type: ignore
            0x41, register=0x02, value=0xA1
        )

    def test_read(self, pin: PCA9536Pin):
        assert pin.read() is True

    def test_write(self, pin: PCA9536Pin):
        pin.write(True)
        pin.device.bus.write_byte_data.assert_called_once_with(  # type: ignore
            0x41, register=0x01, value=0xA5
        )


def test_read_bits(mocker):
    bus = mocker.Mock()
    bus.read_byte_data.return_value = 0xFF
    assert _read_bits(bus, address=0x00, register=0x00, bitmask=0xAA) == 0xAA
    bus.read_byte_data.assert_called_once_with(0x00, register=0x00)


def test_write_bits(mocker):
    bus = mocker.Mock()
    bus.read_byte_data.return_value = 0x55
    _write_bits(bus=bus, address=0x00, register=0x00, value=0xAA, bitmask=0xF0)
    bus.write_byte_data.assert_called_once_with(0x00, register=0x00, value=0xA5)
