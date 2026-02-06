from litestar.exceptions import ValidationException

from app.db.enum import StorageDiskType, StorageDiskInterface
from app.db.model.storage import StorageDisk


def storage_model_func(x: float, a: float, b: float, c: float) -> float:
    return (a * x ** 2) + (b * x) + c


class StoragePricingModel:
    hdd_parameters = (0, 1, 0)
    sata_ssd_parameters = (0, 1, 0)
    nvme_ssd_parameters = (0, 1, 0)

    def compute(self, disk: StorageDisk) -> float:
        if disk.type == StorageDiskType.HDD:
            parameters = self.hdd_parameters
        elif disk.type == StorageDiskType.SSD:
            if disk.interface == StorageDiskInterface.SATA:
                parameters = self.sata_ssd_parameters
            elif disk.interface == StorageDiskInterface.NVME:
                parameters = self.nvme_ssd_parameters
            elif disk.interface == StorageDiskInterface.EMMC:
                parameters = self.hdd_parameters
            else:
                raise ValidationException("Invalid interface for SSD: " + disk.interface.__str__())
        else:
            raise ValidationException("Invalid configuration.")

        return max(storage_model_func(disk.size, *parameters), 0)
