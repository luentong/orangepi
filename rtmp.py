import asyncio
import os
import logging

from pyrtmp import StreamClosedException
from pyrtmp.flv import FLVFileWriter, FLVMediaType
from pyrtmp.session_manager import SessionManager
from pyrtmp.rtmp import SimpleRTMPController, RTMPProtocol, SimpleRTMPServer

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


class RTMP2FLVController(SimpleRTMPController):

    def __init__(self, output_directory: str):
        self.output_directory = output_directory
        super().__init__()

    async def on_ns_publish(self, session, message) -> None:
        print("ns_publish")
        print(message.payload)
        print(message.msg_type_id)
        # message.msg_type_id = 9
        print("message:", message)
        publishing_name = message.publishing_name
        publishing_name = "output_flv"
        print("publish",publishing_name)
        file_path = os.path.join(self.output_directory, f"{publishing_name}.flv")
        session.state = FLVFileWriter(output=file_path)
        await super().on_ns_publish(session, message)

    async def on_metadata(self, session, message) -> None:
        print("metadata")
        session.state.write(0, message.to_raw_meta(), FLVMediaType.OBJECT)
        await super().on_metadata(session, message)

    async def on_video_message(self, session, message) -> None:
        print("video")
        print("message:",message)
        session.state.write(message.timestamp, message.payload, FLVMediaType.VIDEO)

    async def on_audio_message(self, session, message) -> None:
        print("audio")
        session.state.write(message.timestamp, message.payload, FLVMediaType.AUDIO)
        await super().on_audio_message(session, message)

    async def on_stream_closed(self, session: SessionManager, exception: StreamClosedException) -> None:
        print("closed")
        session.state.close()
        await super().on_stream_closed(session, exception)

class SimpleServer(SimpleRTMPServer):

    def __init__(self, output_directory: str):
        self.output_directory = output_directory
        super().__init__()

    async def create(self, host: str, port: int):
        loop = asyncio.get_event_loop()
        self.server = await loop.create_server(
            lambda: RTMPProtocol(controller=RTMP2FLVController(self.output_directory)),
            host=host,
            port=port,
        )

async def main():
    current_dir = os.path.dirname(os.path.abspath(__file__))
    server = SimpleServer(output_directory=current_dir)
    await server.create(host='192.168.1.2', port=1935)
    await server.start()
    await server.wait_closed()

if __name__ == "__main__":
    asyncio.run(main())