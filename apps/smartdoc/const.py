# -*- coding: utf-8 -*-
#
import os

from .conf import ConfigManager
from pathlib import Path

__all__ = ['BASE_DIR', 'PROJECT_DIR', 'VERSION', 'CONFIG']

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PROJECT_DIR = os.path.dirname(BASE_DIR)
VERSION = '1.0.0'

CONFIG = ConfigManager.load_user_config(root_path=os.path.abspath('/opt/maxkb/conf')) if Path('/opt/maxkb/conf').exists() else ConfigManager.load_user_config(root_path=os.path.abspath('/Users/yunhai/Documents/CodeData/Project/MaxKB/conf'))

