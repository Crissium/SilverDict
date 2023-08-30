from .compressor import MAX_MEMBER_SIZE, compress_member
from .api import (
    IdzipFile, compress, decompress, open as dzopen,
    IdzipWriter as Writer)

# get a copy of the open standard file open before overwriting
fopen = open
open = dzopen


__all__ = [
    "MAX_MEMBER_SIZE", "compress_member",
    "IdzipFile", "compress", "decompress",
    "Writer", "open"
]
