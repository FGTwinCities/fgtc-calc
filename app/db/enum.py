from enum import Enum


class MemoryType(Enum):
    DDR = 1
    DDR2 = 2
    DDR3 = 3
    DDR4 = 4
    DDR5 = 5


class StorageDiskType(Enum):
    HDD = "hdd"
    SSD = "ssd"


class StorageDiskForm(Enum):
    INCH25 = "2.5"
    INCH35 = "3.5"
    M2 = "m2"
    PCIE = "pcie"


class StorageDiskInterface(Enum):
    IDE = "ide"
    SAS = "sas"
    SATA = "sata"
    NVME = "nvme"


class WirelessNetworkingStandard(Enum):
    BG = "bg"
    N = "n"
    AC = "ac"
    AX = "ax"
    BE = "be"


class BuildType(Enum):
    DESKTOP = "desktop"
    LAPTOP = "laptop"
    ALL_IN_ONE = "aio"
    SERVER = "server"
    TABLET = "tablet"
    OTHER = "other"
