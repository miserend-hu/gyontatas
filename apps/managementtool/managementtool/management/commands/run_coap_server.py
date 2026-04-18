import asyncio
import logging
import signal

import aiocoap
import aiocoap.resource as resource
from asgiref.sync import sync_to_async
from django.core.management.base import BaseCommand

from managementtool.repositories.device_repository import DeviceRepository
from managementtool.repositories.device_update_repository import DeviceUpdateRepository
from managementtool.repositories.miserend_repository import MiserendRepository
from managementtool.services.device_update_service import DeviceUpdateService
from managementtool.services.miserend_service import MiserendService

logger = logging.getLogger(__name__)


class UpdateResource(resource.Resource):
    def __init__(self, device_type: str, update_service: DeviceUpdateService):
        super().__init__()
        self.device_type = device_type
        self.update_service = update_service

    async def render_post(self, request):
        try:
            await sync_to_async(self.update_service.process_coap_update)(
                self.device_type, request.payload
            )
        except Exception:
            logger.exception("CoAP update processing failed for device_type=%s", self.device_type)
            return aiocoap.Message(code=aiocoap.numbers.codes.Code.INTERNAL_SERVER_ERROR)

        return aiocoap.Message(code=aiocoap.numbers.codes.Code.CHANGED)


class Command(BaseCommand):
    help = "Runs the CoAP server on UDP/5683"

    def handle(self, *args, **options):
        asyncio.run(self._run())

    async def _run(self):
        update_service = DeviceUpdateService(
            DeviceUpdateRepository(),
            DeviceRepository(),
            MiserendService(MiserendRepository()),
        )

        root = resource.Site()
        root.add_resource(["update", "type1"], UpdateResource("type1", update_service))
        root.add_resource(["update", "type2"], UpdateResource("type2", update_service))

        context = await aiocoap.Context.create_server_context(root)
        self.stdout.write(self.style.SUCCESS("CoAP server listening on UDP/5683"))

        loop = asyncio.get_running_loop()
        stop = loop.create_future()

        loop.add_signal_handler(signal.SIGTERM, stop.set_result, None)
        loop.add_signal_handler(signal.SIGINT, stop.set_result, None)

        await stop
        await context.shutdown()
        self.stdout.write("CoAP server stopped.")
