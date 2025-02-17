import logging

def get_logger(name: str) -> logging.Logger:
    logger = logging.getLogger(name)
    logger.setLevel(logging.DEBUG)  # Устанавливаем уровень для самого логгера

    # Проверяем, нет ли уже обработчиков у логгера
    if not logger.handlers:
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.DEBUG)  # Уровень для обработчика
        console_handler.setFormatter(formatter)

        logger.addHandler(console_handler)

    return logger