import logging
import datetime


class Logger(logging.Logger):
    def __init__(
            self,
            config,
            name='cranberrypy',
            log_level=logging.DEBUG
    ):
        super().__init__(name, log_level)
        self.config = config
        self.name = name
        self.log_level = log_level

    def setup_logger(self):
        s_handler = logging.StreamHandler()
        f_handler = logging.FileHandler(
            f"{self.config.get('logger', 'logs_path')}/"
            f"{datetime.datetime.now().strftime('%Y_%m_%d_%H_%M_%S')}.log"
        )
        s_handler.setLevel(logging.INFO)
        f_handler.setLevel(self.log_level)

        s_format = logging.Formatter(self.config.get('logger', 's_format'))
        f_format = logging.Formatter(self.config.get('logger', 'f_format'))
        s_handler.setFormatter(s_format)
        f_handler.setFormatter(f_format)

        self.addHandler(s_handler)
        self.addHandler(f_handler)
