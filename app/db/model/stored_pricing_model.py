from advanced_alchemy.base import UUIDAuditBase
from sqlalchemy.orm import Mapped
from sqlalchemy.testing.schema import mapped_column


class StoredPricingModel(UUIDAuditBase):
    __tablename__ = "pricing_model"

    memory_param_a: Mapped[float | None] = mapped_column()
    memory_param_b: Mapped[float | None] = mapped_column()
    memory_param_c: Mapped[float | None] = mapped_column()
    memory_param_d: Mapped[float | None] = mapped_column()
    memory_param_e: Mapped[float | None] = mapped_column()

    storage_hdd_param_a: Mapped[float | None] = mapped_column()
    storage_hdd_param_b: Mapped[float | None] = mapped_column()
    storage_hdd_param_c: Mapped[float | None] = mapped_column()
    storage_sata_ssd_param_a: Mapped[float | None] = mapped_column()
    storage_sata_ssd_param_b: Mapped[float | None] = mapped_column()
    storage_sata_ssd_param_c: Mapped[float | None] = mapped_column()
    storage_nvme_ssd_param_a: Mapped[float | None] = mapped_column()
    storage_nvme_ssd_param_b: Mapped[float | None] = mapped_column()
    storage_nvme_ssd_param_c: Mapped[float | None] = mapped_column()
