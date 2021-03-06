import struct
import uuid

__all__ = [
    "BasePacker",
    "ShortPacker",
    "UnsignedShortPacker",
    "LongPacker",
    "UnsignedLongPacker",
    "LongLongPacker",
    "UnsignedLongLongPacker",
    "UUIDPacker",
    "PACKERS",
]


class BasePacker:
    """
    Abstract base class for packers.

    """

    def pack_pk(self, user_pk):
        """
        Create a short representation of the primary key of a user.

        Return bytes.

        """

    def unpack_pk(self, data):
        """
        Extract the primary key of a user from a signed token.

        Return the primary key and the remaining bytes.

        """


class StructPackerMeta(type):
    def __new__(cls, name, bases, namespace, **kwds):
        namespace["size"] = struct.calcsize(namespace["fmt"])
        return super().__new__(cls, name, bases, namespace, **kwds)


class StructPacker(BasePacker, metaclass=StructPackerMeta):
    fmt = ""

    @classmethod
    def pack_pk(cls, user_pk):
        return struct.pack(cls.fmt, user_pk)

    @classmethod
    def unpack_pk(cls, data):
        (user_pk,) = struct.unpack(cls.fmt, data[: cls.size])
        return user_pk, data[cls.size :]


class ShortPacker(StructPacker):
    fmt = "!h"


class UnsignedShortPacker(StructPacker):
    fmt = "!H"


class LongPacker(StructPacker):
    fmt = "!l"


IntPacker = LongPacker  # for backwards-compatibility


class UnsignedLongPacker(StructPacker):
    fmt = "!L"


UnsignedIntPacker = UnsignedLongPacker  # for consistency


class LongLongPacker(StructPacker):
    fmt = "!q"


class UnsignedLongLongPacker(StructPacker):
    fmt = "!Q"


class UUIDPacker(BasePacker):
    @staticmethod
    def pack_pk(user_pk):
        return user_pk.bytes

    @staticmethod
    def unpack_pk(data):
        return uuid.UUID(bytes=data[:16]), data[16:]


class BytesPacker(BasePacker):
    """
    Generic packer for bytestrings, from 0 to 255 bytes.

    In many cases, primary keys stored as bytes are likely to be fixed-length,
    which doesn't require a variable length encoding scheme.

    """

    @staticmethod
    def pack_pk(user_pk):
        length = len(user_pk)
        if length > 255:
            raise ValueError("Primary key is too large (%d bytes)" % length)
        return bytes([length]) + user_pk

    @staticmethod
    def unpack_pk(data):
        length = data[0]
        return data[1 : length + 1], data[length + 1 :]


class StrPacker(BytesPacker):
    """
    Generic packer for strings, from 0 to 255 UTF-8 encoded bytes.

    """

    @staticmethod
    def pack_pk(user_pk):
        user_pk = user_pk.encode()
        length = len(user_pk)
        if length > 255:
            raise ValueError("Primary key is too large (%d UTF-8 bytes)" % length)
        return bytes([length]) + user_pk

    @staticmethod
    def unpack_pk(data):
        length = data[0]
        return data[1 : length + 1].decode(), data[length + 1 :]


PACKERS = {
    # 2 bytes
    "SmallAutoField": ShortPacker,
    "SmallIntegerField": ShortPacker,
    "PositiveSmallIntegerField": UnsignedShortPacker,
    # 4 bytes
    "AutoField": LongPacker,
    "IntegerField": LongPacker,
    "PositiveIntegerField": UnsignedLongPacker,
    # 8 bytes
    "BigAutoField": LongLongPacker,
    "BigIntegerField": LongLongPacker,
    "PositiveBigIntegerField": UnsignedLongLongPacker,
    # 16 bytes
    "UUIDField": UUIDPacker,
    # Variable length
    "BinaryField": BytesPacker,
    "CharField": StrPacker,
    "TextField": StrPacker,
}
