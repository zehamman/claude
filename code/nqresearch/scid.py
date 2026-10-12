"""Reader for Sierra Chart intraday (.scid) files.

Format (Sierra Chart "Intraday Data File Format", cross-checked against the
open-source Go implementation RileyR387/sc-data-util):

Header, 56 bytes::

    char     FileTypeUniqueHeaderID[4]   # b"SCID"
    uint32   HeaderSize                  # 56
    uint32   RecordSize                  # 40
    uint16   Version
    uint16   Unused1
    uint32   UTCStartIndex
    char     Reserve[36]

Record, 40 bytes::

    int64    DateTime      # microseconds since 1899-12-30 00:00:00 UTC
    float32  Open          # tick data: 0.0 = single trade with bid/ask,
                           #   -1.99900095e37 first sub-trade of unbundled trade,
                           #   -1.99900197e37 last sub-trade of unbundled trade
    float32  High          # tick data: ask price at the time of the trade
    float32  Low           # tick data: bid price at the time of the trade
    float32  Close         # tick data: trade price
    uint32   NumTrades
    uint32   TotalVolume
    uint32   BidVolume     # volume traded at the bid  -> sell aggressor
    uint32   AskVolume     # volume traded at the ask  -> buy aggressor

Caveat on timestamps: Sierra Chart may use the sub-millisecond part of the
DateTime as a uniqueness counter for trades sharing a millisecond. The audit
measures this; analysis code must never treat sub-millisecond digits as real
time resolution (``ts_ms`` floors to milliseconds for that reason).
"""

from __future__ import annotations

import os
from dataclasses import dataclass
from typing import Iterator

import numpy as np

HEADER_SIZE = 56
RECORD_SIZE = 40
MAGIC = b"SCID"

# Microseconds between 1899-12-30 and 1970-01-01 (25569 days).
SC_EPOCH_OFFSET_US = 25569 * 86400 * 1_000_000

OPEN_SINGLE_TRADE = np.float32(0.0)
OPEN_FIRST_SUB_TRADE = np.float32(-1.99900095e37)
OPEN_LAST_SUB_TRADE = np.float32(-1.99900197e37)

RECORD_DTYPE = np.dtype(
    [
        ("dt", "<i8"),
        ("open", "<f4"),
        ("high", "<f4"),
        ("low", "<f4"),
        ("close", "<f4"),
        ("num_trades", "<u4"),
        ("volume", "<u4"),
        ("bid_volume", "<u4"),
        ("ask_volume", "<u4"),
    ]
)
assert RECORD_DTYPE.itemsize == RECORD_SIZE

HEADER_DTYPE = np.dtype(
    [
        ("magic", "S4"),
        ("header_size", "<u4"),
        ("record_size", "<u4"),
        ("version", "<u2"),
        ("unused1", "<u2"),
        ("utc_start_index", "<u4"),
        ("reserve", "V36"),
    ]
)
assert HEADER_DTYPE.itemsize == HEADER_SIZE


@dataclass(frozen=True)
class ScidHeader:
    magic: bytes
    header_size: int
    record_size: int
    version: int
    utc_start_index: int


@dataclass(frozen=True)
class ScidInfo:
    path: str
    file_size: int
    header: ScidHeader
    n_records: int
    trailing_bytes: int  # bytes after the last whole record (should be 0)


def read_header(path: str) -> ScidHeader:
    with open(path, "rb") as fh:
        raw = fh.read(HEADER_SIZE)
    if len(raw) < HEADER_SIZE:
        raise ValueError(f"{path}: file shorter than SCID header ({len(raw)} bytes)")
    h = np.frombuffer(raw, dtype=HEADER_DTYPE, count=1)[0]
    return ScidHeader(
        magic=bytes(h["magic"]),
        header_size=int(h["header_size"]),
        record_size=int(h["record_size"]),
        version=int(h["version"]),
        utc_start_index=int(h["utc_start_index"]),
    )


def info(path: str) -> ScidInfo:
    header = read_header(path)
    if header.magic != MAGIC:
        raise ValueError(f"{path}: bad magic {header.magic!r}, expected {MAGIC!r}")
    if header.header_size != HEADER_SIZE or header.record_size != RECORD_SIZE:
        raise ValueError(
            f"{path}: unexpected header_size={header.header_size} "
            f"record_size={header.record_size}"
        )
    size = os.path.getsize(path)
    body = size - HEADER_SIZE
    return ScidInfo(
        path=path,
        file_size=size,
        header=header,
        n_records=body // RECORD_SIZE,
        trailing_bytes=body % RECORD_SIZE,
    )


def open_records(path: str) -> np.memmap:
    """Read-only memory map over all whole records (no data is loaded yet)."""
    inf = info(path)
    return np.memmap(
        path, dtype=RECORD_DTYPE, mode="r", offset=HEADER_SIZE, shape=(inf.n_records,)
    )


def iter_chunks(
    path: str, chunk_records: int = 25_000_000, start: int = 0, stop: int | None = None
) -> Iterator[tuple[int, np.ndarray]]:
    """Yield ``(first_record_index, records)`` in-memory copies of record chunks.

    25M records = 1 GB per chunk. Lower ``chunk_records`` on small-RAM machines.
    """
    mm = open_records(path)
    n = mm.shape[0] if stop is None else min(stop, mm.shape[0])
    for i in range(start, n, chunk_records):
        yield i, np.array(mm[i : min(i + chunk_records, n)])


def to_unix_us(dt: np.ndarray) -> np.ndarray:
    """SCID DateTime (us since 1899-12-30) -> Unix epoch microseconds (UTC)."""
    return dt.astype(np.int64) - SC_EPOCH_OFFSET_US


def to_datetime64(dt: np.ndarray) -> np.ndarray:
    return to_unix_us(dt).astype("datetime64[us]")


def ts_ms(dt: np.ndarray) -> np.ndarray:
    """Unix epoch milliseconds, floored. Use this, not microseconds, for analysis."""
    return to_unix_us(dt) // 1000


def from_unix_us(us: np.ndarray | int) -> np.ndarray | int:
    return np.asarray(us, dtype=np.int64) + SC_EPOCH_OFFSET_US


def write_scid(path: str, records: np.ndarray) -> None:
    """Write records with a standard header. Used for tests / small extracts."""
    hdr = np.zeros(1, dtype=HEADER_DTYPE)
    hdr["magic"] = MAGIC
    hdr["header_size"] = HEADER_SIZE
    hdr["record_size"] = RECORD_SIZE
    hdr["version"] = 1
    with open(path, "wb") as fh:
        fh.write(hdr.tobytes())
        fh.write(np.ascontiguousarray(records, dtype=RECORD_DTYPE).tobytes())
