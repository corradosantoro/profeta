#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
logger.py
"""

import logging


MAIN_LOG_FILENAME = './log/main.log'
EXEC_LOG_FILENAME = './log/executor.log'
ENGINE_LOG_FILENAME = './log/engine.log'
logging.basicConfig(level=logging.DEBUG)


main_handler = logging.FileHandler(MAIN_LOG_FILENAME,'w')

main_formatter = logging.Formatter("%(name)s:  %(message)s")
main_handler.setFormatter(main_formatter)
main_logger = logging.getLogger("Main")
main_logger.addHandler(main_handler)

def executor_logger():
    exec_handler = logging.FileHandler(EXEC_LOG_FILENAME)
    exec_logger = logging.getLogger("Main.Executor")
    exec_logger.addHandler(exec_handler)
    return exec_logger

def engine_logger():
    engine_handler = logging.FileHandler(ENGINE_LOG_FILENAME)
    engine_logger = logging.getLogger("Main.Engine")
    engine_logger.addHandler(engine_handler)
    return engine_logger
