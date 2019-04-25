from logger.beep import Beep
from config import Config

_config = Config()

beep = Beep(_config.data['telemetry']['beep'])