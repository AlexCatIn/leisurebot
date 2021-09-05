from bot.bot import run_bot
import sys
import logging
from logging import StreamHandler, Formatter


logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

handler = StreamHandler(stream=sys.stdout)
handler.setFormatter(Formatter(fmt='[%(asctime)s: %(levelname)s] %(message)s'))
logger.addHandler(handler)

logger.debug('debug information')


if __name__ == "__main__":
    run_bot()