import logging

def setup_logging():
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - p-%(process)d - %(levelname)-9s - %(name)-15s - %(message)s'
    )
    logging.getLogger("werkzeug").setLevel(logging.ERROR)


def debug_logging():
    # Print out all loggers and their handlers
    for name, logger in logging.Logger.manager.loggerDict.items():
        if isinstance(logger, logging.Logger):
            print(f"Logger: {name}, Handlers: {logger.handlers}")