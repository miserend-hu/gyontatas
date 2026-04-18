"""
Type1 device simulator – sends a binary CoAP payload to the CoAP bridge.

Binary layout (36 bytes):
  0– 7  IMEI   packed (f-prefixed hex → 8 bytes)
  8–15  IMSI   packed (f-prefixed hex → 8 bytes)
 16     version_product  (u8)
 17     version_code     (u8)
 18–19  battery_mv       (u16be)
 20     signal           (u8)
 21–25  reserved
 26     interrupt_3      (u8)
 27     input_3          (u8)
 28     interrupt_1      (u8)
 29     input_1          (u8)
 30     interrupt_2      (u8)
 31     input_2          (u8)
 32–35  time             (u32be, UNIX timestamp)
"""

import argparse
import asyncio
import struct
import time

import aiocoap


def pack_id(decimal_str: str) -> bytes:
    """Pack a 15-digit decimal IMEI/IMSI into 8 bytes using f-prefix padding."""
    return bytes.fromhex("f" + decimal_str)


def build_payload(
    imei: str,
    imsi: str,
    version_product: int,
    version_code: int,
    battery_mv: int,
    signal: int,
    interrupt_1: int,
    interrupt_2: int,
    interrupt_3: int,
    input_1: int,
    input_2: int,
    input_3: int,
) -> bytes:
    buf = bytearray(36)
    buf[0:8] = pack_id(imei)
    buf[8:16] = pack_id(imsi)
    buf[16] = version_product
    buf[17] = version_code
    struct.pack_into(">H", buf, 18, battery_mv)
    buf[20] = signal
    buf[26] = interrupt_3
    buf[27] = input_3
    buf[28] = interrupt_1
    buf[29] = input_1
    buf[30] = interrupt_2
    buf[31] = input_2
    struct.pack_into(">I", buf, 32, int(time.time()))
    return bytes(buf)


async def send(host: str, port: int, device_type: str, payload: bytes) -> None:
    context = await aiocoap.Context.create_client_context()
    request = aiocoap.Message(
        code=aiocoap.POST,
        uri=f"coap://{host}:{port}/update/{device_type}",
        payload=payload,
    )
    response = await context.request(request).response
    print(f"Response: {response.code}")
    await context.shutdown()


def main() -> None:
    parser = argparse.ArgumentParser(description="Type1 CoAP device simulator")
    parser.add_argument("--host", default="localhost")
    parser.add_argument("--port", type=int, default=5683)
    parser.add_argument("--imei", default="868927081504479")
    parser.add_argument("--imsi", default="901405180500280")
    parser.add_argument("--battery-mv", type=int, default=3600, metavar="MV")
    parser.add_argument("--signal", type=int, default=15)
    parser.add_argument("--version-product", type=int, default=4)
    parser.add_argument("--version-code", type=int, default=150)
    parser.add_argument("--interrupt-1", type=int, default=1, choices=[0, 1])
    parser.add_argument("--interrupt-2", type=int, default=0, choices=[0, 1])
    parser.add_argument("--interrupt-3", type=int, default=0, choices=[0, 1])
    parser.add_argument("--input-1", type=int, default=1, choices=[0, 1], help="1 = confession ongoing")
    parser.add_argument("--input-2", type=int, default=0, choices=[0, 1])
    parser.add_argument("--input-3", type=int, default=0, choices=[0, 1])
    args = parser.parse_args()

    payload = build_payload(
        imei=args.imei,
        imsi=args.imsi,
        version_product=args.version_product,
        version_code=args.version_code,
        battery_mv=args.battery_mv,
        signal=args.signal,
        interrupt_1=args.interrupt_1,
        interrupt_2=args.interrupt_2,
        interrupt_3=args.interrupt_3,
        input_1=args.input_1,
        input_2=args.input_2,
        input_3=args.input_3,
    )

    confession = args.input_1 + args.input_2 + args.input_3
    print(f"Sending to coap://{args.host}:{args.port}/update/type1")
    print(f"  IMEI={args.imei}  IMSI={args.imsi}")
    print(f"  battery={args.battery_mv / 1000:.3f}V  signal={args.signal}")
    print(f"  input_1={args.input_1}  input_2={args.input_2}  input_3={args.input_3}  confession={confession}")
    print(f"  payload ({len(payload)} bytes): {payload.hex()}")

    asyncio.run(send(args.host, args.port, "type1", payload))


if __name__ == "__main__":
    main()
