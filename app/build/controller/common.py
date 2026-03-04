from app.build.schema import BuildCreate
from app.db.model import BuildBase, Processor, BuildProcessorAssociation, GraphicsProcessor, \
    BuildGraphicsAssociation, MemoryModule, StorageDisk, Display, Battery
from app.db.service.graphics import GraphicsProcessorService
from app.db.service.processor import ProcessorService
from app.lib.attrs import attrcopy
from app.passmark.passmark_scraper import attempt_cpu_parse, attempt_gpu_parse


async def _deduplicate_processors(build: BuildBase, data: BuildCreate, processor_service: ProcessorService):
    """
    Copy processor attributes from data to build, while searching the database for existing processors by model name.
    :param build: database object to copy data to
    :param data: Creation DTO schema to copy attributes from
    :param processor_service: CPU database service [injected]
    """
    # Find existing processors by name
    for i in range(0, len(data.processors)):
        data.processors[i].model = attempt_cpu_parse(data.processors[i].model)

        # For some dumb reason, model.is_() breaks everything when using postgres, so query by contains and do final comparison here
        # TODO: Please find a fix
        found_processors = await processor_service.list(Processor.model.contains(data.processors[i].model))

        is_found = False
        for processor in found_processors:
            if processor.model == data.processors[i].model:
                build.processor_associations.append(BuildProcessorAssociation(
                    processor=processor,
                    upgradable=data.processors[i].upgradable,
                ))
                is_found = True
                break

        if not is_found:
            new_processor = Processor(
                model=data.processors[i].model,
            )
            new_processor = await processor_service.create(new_processor, auto_commit=True, auto_refresh=True)
            build.processor_associations.append(BuildProcessorAssociation(
                processor=new_processor,
                upgradable=data.processors[i].upgradable,
            ))


async def _deduplicate_graphics_processors(build: BuildBase, data: BuildCreate,
                                           graphics_service: GraphicsProcessorService):
    """
    Copy GPU attributes from data DTO to build, while searching database for existing GPUs by model name.
    :param build: database object to copy data to
    :param data: DTO schema to copy data from
    :param graphics_service: GPU database service [injected]
    """
    # Find existing GPUs by name
    for i in range(0, len(data.graphics)):
        data.graphics[i].model = attempt_gpu_parse(data.graphics[i].model)

        found_gpus = await graphics_service.list(GraphicsProcessor.model.contains(data.graphics[i].model))

        is_found = False
        for gpu in found_gpus:
            if gpu.model == data.graphics[i].model:
                build.graphics_associations.append(BuildGraphicsAssociation(
                    graphics=gpu,
                    upgradable=data.graphics[i].upgradable,
                ))
                is_found = True
                break

        if not is_found:
            new_gpu = GraphicsProcessor(
                model=data.graphics[i].model,
            )
            new_gpu = await graphics_service.create(new_gpu, auto_commit=True, auto_refresh=True)
            build.graphics_associations.append(BuildGraphicsAssociation(
                graphics=new_gpu,
                upgradable=data.graphics[i].upgradable,
            ))


def _convert_create_dto_to_model(build: BuildBase, data: BuildCreate):
    """ Copies attributes from the BuildCreate DTO object to the Build database model object, as well as handling subobject creation """
    build.memory = []
    for mem in data.memory:
        module = MemoryModule()
        attrcopy(mem, module)
        build.memory.append(module)

    build.storage = []
    for store in data.storage:
        disk = StorageDisk()
        attrcopy(store, disk)
        build.storage.append(disk)

    build.display = []
    if data.display:
        display = Display()
        attrcopy(data.display, display)
        build.display.append(display)

    build.batteries = []
    for batt in data.batteries:
        # Remove any batteries with 0 design capacity as they are invalid
        if batt.design_capacity <= 0:
            continue

        battery = Battery()
        attrcopy(batt, battery)
        build.batteries.append(battery)

    # Copy all attributes except the once done manually above between the creation object and the model object
    attr_blocklist = ["processors", "graphics", "memory", "storage", "display", "batteries"]
    attrcopy(data, build, attr_blocklist)