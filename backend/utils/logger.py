import logging
import os

def setup_logger(name, log_file, level=logging.INFO):
    formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s')

    handler = logging.FileHandler(log_file)        
    handler.setFormatter(formatter)

    logger = logging.getLogger(name)
    logger.setLevel(level)
    logger.addHandler(handler)

    return logger


def get_logger(name):
    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)
    return logger

training_logger = get_logger('training')
optimization_logger = get_logger('optimization')
app_logger = get_logger('app')

# Create logs directory if it doesn't exist
os.makedirs('logs', exist_ok=True)

# Set up loggers
training_logger = setup_logger('training_logger', 'logs/training.log')
optimization_logger = setup_logger('optimization_logger', 'logs/optimization.log')
app_logger = setup_logger('app_logger', 'logs/app.log')
