from __future__ import annotations

import asyncio
import struct


class SofarProtocolError(Exception):
    """Protocol-level communication error."""


def _crc16_modbus(data: bytes) -> int:
    crc = 0xFFFF
    for byte in data:
        crc ^= byte
        for _ in range(8):
            if crc & 0x0001:
                crc = (crc >> 1) ^ 0xA001
            else:
                crc >>= 1
    return crc & 0xFFFF


def build_request(logger_serial: int, start_register: int, end_register: int) -> bytes:
    if not 0 <= logger_serial <= 0xFFFFFFFF:
        raise ValueError("Logger serial number must fit in 32 bits")
    if end_register < start_register:
        raise ValueError("End register must be >= start register")

    count = end_register - start_register + 1

    frame = bytearray.fromhex("a5170010450000")
    frame.extend(struct.pack("<I", logger_serial))
    frame.extend(bytes.fromhex("020000000000000000000000000000"))

    business = bytearray()
    business.extend(b"\x00\x03")
    business.extend(struct.pack(">H", start_register))
    business.extend(struct.pack(">H", count))

    crc16 = _crc16_modbus(bytes(business))
    business.extend(struct.pack("<H", crc16))
    frame.extend(business)

    checksum = sum(frame[1:]) & 0xFF
    frame.append(checksum)
    frame.append(0x15)
    return bytes(frame)


def _validate_response(response: bytes) -> None:
    if len(response) < 13:
        raise SofarProtocolError(f"Response too short: {len(response)} bytes")

    if response[0] != 0xA5:
        raise SofarProtocolError(
            f"Unexpected response start byte: 0x{response[0]:02X}"
        )

    expected_payload_length = len(response) - 13
    if response[1] != expected_payload_length:
        raise SofarProtocolError(
            f"Length mismatch: header={response[1]}, actual={expected_payload_length}"
        )

    checksum = sum(response[1:-2]) & 0xFF
    if checksum != response[-2]:
        raise SofarProtocolError(
            f"Checksum mismatch: calculated=0x{checksum:02X}, "
            f"received=0x{response[-2]:02X}"
        )


async def read_register_block(
    host: str,
    port: int,
    logger_serial: int,
    start_register: int,
    end_register: int,
    timeout: float = 10.0,
) -> bytes:
    request = build_request(
        logger_serial,
        start_register,
        end_register,
    )

    writer = None

    try:
        reader, writer = await asyncio.wait_for(
            asyncio.open_connection(host, port),
            timeout=timeout,
        )

        writer.write(request)
        await writer.drain()

        chunks = []
        loop = asyncio.get_running_loop()
        deadline = loop.time() + timeout

        first = True

        while True:
            remaining = deadline - loop.time()
            if remaining <= 0:
                if not chunks:
                    raise asyncio.TimeoutError()
                break

            wait_for = remaining if first else min(0.1, remaining)

            try:
                chunk = await asyncio.wait_for(
                    reader.read(4096),
                    timeout=wait_for,
                )
            except asyncio.TimeoutError:
                if chunks:
                    break
                raise

            if not chunk:
                break

            chunks.append(chunk)
            first = False

        response = b"".join(chunks)
        if len(response) >= 2 and response[0] == 0xA5:
            frame_length = response[1] + 13
            if len(response) > frame_length:
                response = response[:frame_length]


        _validate_response(response)

        register_count = end_register - start_register + 1
        data_length = register_count * 2

        data = response[-(data_length + 4):-4]

        if len(data) != data_length:
            raise SofarProtocolError(
                f"Register data length mismatch: expected {data_length}, got {len(data)}"
            )

        return data

    except asyncio.TimeoutError as err:
        raise SofarProtocolError("TCP timeout") from err
    except asyncio.IncompleteReadError as err:
        raise SofarProtocolError(
            f"Incomplete TCP response: got {len(err.partial)} bytes"
        ) from err
    except (ConnectionError, OSError) as err:
        raise SofarProtocolError(
            f"{type(err).__name__}: {err!r}"
        ) from err
    finally:
        if writer is not None:
            writer.close()
            try:
                await writer.wait_closed()
            except Exception:
                pass


def u16be(data: bytes, offset: int, scale: float = 1.0) -> float:
    return struct.unpack_from(">H", data, offset)[0] * scale


def i16be(data: bytes, offset: int, scale: float = 1.0) -> float:
    return struct.unpack_from(">h", data, offset)[0] * scale


def u32be(data: bytes, offset: int, scale: float = 1.0) -> float:
    return struct.unpack_from(">I", data, offset)[0] * scale


def parse_block(start_register: int, data: bytes) -> dict[str, float]:
    if start_register == 0x0400:
        return {
            "ambient_temperature": i16be(data, 48),
            "radiator_temperature": i16be(data, 52),
            "generation_time_today": u16be(data, 76),
            "total_generation_time": u32be(data, 78),
            "total_inverter_work_time": u32be(data, 82),
        }

    if start_register == 0x0480:
        return {
            "current_power": u16be(data, 10, 10),
            "phase_r_voltage": u16be(data, 26, 0.1),
            "phase_r_current": u16be(data, 28, 0.01),
            "phase_s_voltage": u16be(data, 48, 0.1),
            "phase_s_current": u16be(data, 50, 0.01),
            "phase_t_voltage": u16be(data, 70, 0.1),
            "phase_t_current": u16be(data, 72, 0.01),
        }

    if start_register == 0x0580:
        return {
            "string_1_voltage": u16be(data, 8, 0.1),
            "string_1_current": u16be(data, 10, 0.01),
            "string_1_power": u16be(data, 12, 0.01),
            "string_2_voltage": u16be(data, 14, 0.1),
            "string_2_current": u16be(data, 16, 0.01),
            "string_2_power": u16be(data, 18, 0.01),
        }

    if start_register == 0x0680:
        return {
            "energy_today": u32be(data, 8, 0.01),
            "energy_total": u32be(data, 12, 0.1),
        }

    return {}
