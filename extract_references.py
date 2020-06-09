import pandas as pd
import pathlib
from pathlib import Path
import requests
import sys
import os
import socket
import multiprocessing
from multiprocessing import Pool
import re
import time
from datetime import datetime
import warnings
import json
from refextract import extract_references_from_file, extract_references_from_url



def get_refs_file(fp) -> list:
    return extract_references_from_file(fp)


def get_refs_web(url) -> list:
    return extract_references_from_url(url)


print(get_refs_web("https://www.medrxiv.org/content/10.1101/2020.05.21.20108621v1.full.pdf"))