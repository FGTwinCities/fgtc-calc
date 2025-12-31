from litestar.exceptions import ValidationException
from numpy.polynomial.polynomial import Polynomial
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.enum import StorageDiskType, StorageDiskInterface
from app.db.model.storage import StorageDisk
from app.lib.math import mb2gb


class StoragePricingModel:
    hdd_size_func: Polynomial
    sata_size_func: Polynomial
    nvme_size_func: Polynomial

    def compute(self, disk: StorageDisk) -> float:
        if disk.type == StorageDiskType.HDD:
            return self.hdd_size_func(mb2gb(disk.size))
        elif disk.type == StorageDiskType.SSD:
            if disk.interface == StorageDiskInterface.SATA:
                return self.sata_size_func(mb2gb(disk.size))
            elif disk.interface == StorageDiskInterface.NVME:
                return self.nvme_size_func(mb2gb(disk.size))
            else:
                raise ValidationException("Invalid interface for SSD: " + disk.interface.__str__())
        else:
            raise ValidationException("Invalid configuration.")


async def provide_storage_pricing_model(db_session: AsyncSession) -> StoragePricingModel:
    model = StoragePricingModel()

    #TODO: Use database
    model.hdd_size_func = Polynomial([0, 0.03, 0])
    model.sata_size_func = Polynomial([0, 0.13, 0])
    model.nvme_size_func = Polynomial([0, 0.2, 0])

    return model