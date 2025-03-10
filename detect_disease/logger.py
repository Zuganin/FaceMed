import logging

def get_logger(name: str) -> logging.Logger:
    """
        Создаёт и настраивает логгер с заданным именем.

        :param name: Имя логгера (обычно имя модуля или сервиса)
        :return: Объект настроенного логгера
    """
    logger = logging.getLogger(name)

    # Устанавливаем уровень для самого логгера
    logger.setLevel(logging.DEBUG)

    # Проверяем, нет ли уже обработчиков у логгера
    if not logger.handlers:
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

        console_handler = logging.StreamHandler()

        # Уровень для обработчика
        console_handler.setLevel(logging.DEBUG)
        console_handler.setFormatter(formatter)

        logger.addHandler(console_handler)

    return logger