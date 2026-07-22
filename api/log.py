import logging

def ger(name: str = __name__, level: str = 'INFO', console_logs: bool = True, file_logs: bool = True, file_name: str = 'logs'):
    '''
    Configures and returns a logger.

    :param name: Name of the logger. Recommended to use __name__.
    :type name: str
    :param level: Logging level. Options: DEBUG, INFO, WARNING, ERROR, CRITICAL.
    :type level: str
    :param console_logs: Whether to show logs in the console.
    :type console_logs: bool
    :param file_logs: Whether to save logs to a file.
    :type file_logs: bool
    :param file_name: Name of the log file (only used if file_logs=True).
    :type file_name: str

    :return: Logger instance.
    '''

    logger = logging.getLogger(name)
        
    # avoiding duplicate handlers
    if logger.handlers:
        return logger
    
    # setting level
    level = level.upper()
    levels = {
        'DEBUG': logging.DEBUG,
        'INFO': logging.INFO,
        'WARNING': logging.WARNING,
        'ERROR': logging.ERROR,
        'CRITICAL': logging.CRITICAL,
    }
    try:
        log_level = levels[level]
    except:
        log_level = logging.INFO

    logger.setLevel(log_level)

    # setting format
    formatter = logging.Formatter(
        fmt = '%(asctime)s - %(levelname)s - %(message)s',
        datefmt = '%H:%M:%S | (%d/%m/%Y)',
    )

    # console handler
    if console_logs:
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(formatter)
        console_handler.setLevel(log_level)
        logger.addHandler(console_handler)

    # file handler
    if file_logs:
        file_handler = logging.FileHandler(f'{file_name}.log', encoding='utf-8', mode='a')
        file_handler.setFormatter(formatter)
        file_handler.setLevel(log_level)
        logger.addHandler(file_handler)

    return logger
