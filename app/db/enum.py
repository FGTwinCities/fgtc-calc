from enum import Enum


class MemoryType(Enum):
    DDR = 1
    DDR2 = 2
    DDR3 = 3
    DDR4 = 4
    DDR5 = 5

    def __str__(self):
        return "DDR" + str(self.value)


class StorageDiskType(Enum):
    HDD = "hdd"
    SSD = "ssd"

    def __str__(self) -> str:
        match self:
            case StorageDiskType.HDD:
                return "HDD"
            case StorageDiskType.SSD:
                return "SSD"


class StorageDiskForm(Enum):
    INCH25 = "2.5"
    INCH35 = "3.5"
    M2 = "m2"
    PCIE = "pcie"
    SOLDERED = "soldered"

    def __str__(self) -> str:
        match self:
            case StorageDiskForm.INCH25:
                return "2.5\""
            case StorageDiskForm.INCH35:
                return "3.5\""
            case StorageDiskForm.M2:
                return "m.2"
            case StorageDiskForm.PCIE:
                return "PCIe"
            case StorageDiskForm.SOLDERED:
                return "Soldered"
            case _:
                return str(self.value)


class StorageDiskInterface(Enum):
    IDE = "ide"
    SAS = "sas"
    SATA = "sata"
    NVME = "nvme"
    EMMC = "emmc"

    def __str__(self) -> str:
        match self:
            case StorageDiskInterface.IDE | StorageDiskInterface.SAS | StorageDiskInterface.SATA:
                return str(self.value).upper()
            case StorageDiskInterface.NVME:
                return "NVMe"
            case StorageDiskInterface.EMMC:
                return "eMMC"
            case _:
                return str(self.value)


class WirelessNetworkingStandard(Enum):
    BG = "bg"
    N = "n"
    AC = "ac"
    AX = "ax"
    BE = "be"

    def __str__(self) -> str:
        match self:
            case WirelessNetworkingStandard.BG:
                return "802.11b/g"
            case WirelessNetworkingStandard.N:
                return "WiFi 4 (n)"
            case WirelessNetworkingStandard.AC:
                return "WiFi 5 (ac)"
            case WirelessNetworkingStandard.AX:
                return "WiFi 6 (ax)"
            case WirelessNetworkingStandard.BE:
                return "WiFi 7 (be)"
            case _:
                return "802.11" + str(self.value)


class BuildType(Enum):
    DESKTOP = "desktop"
    LAPTOP = "laptop"
    ALL_IN_ONE = "aio"
    SERVER = "server"
    TABLET = "tablet"
    OTHER = "other"
