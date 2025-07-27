import time
import os
from logger import log_msg
from exceptions import GameError
from task.login import login_first
from task.phase6 import phase6
from task.phase5 import phase5
from task.phase4 import phase4
from task.phase3 import phase3
from task.phase2 import phase2
from task.phase1 import phase1

def new_acc_farm(serial):
    try:
        phase1(serial)
    except GameError as e:
        raise

    try:
        phase2(serial)
    except GameError as e:
        raise

    try:
        phase3(serial)
    except GameError as e:
        raise

    try:
        phase4(serial)
    except GameError as e:
        raise

    try:
        phase5(serial)
    except GameError as e:
        raise

    try:
        phase6(serial)
    except GameError as e:
        raise