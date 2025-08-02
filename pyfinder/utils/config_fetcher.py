# -*- coding: utf-8 -*-
"""
This module provides a utility function to ensure that the INGV shakemap-conf-eu configuration
is available locally. If the configuration is missing, it automatically downloads and extracts it.
"""
import os
import requests
import zipfile
from io import BytesIO
import logging

def ensure_shakemap_config(target_dir="extern/shakemap-conf-eu"):
    """
    Ensures that the INGV shakemap-conf-eu configuration is available locally.
    If missing, it automatically downloads and extracts it.
    """
    if os.path.exists(target_dir):
        logging.info("ShakeMap configuration already present.")
        return target_dir

    url = "https://github.com/INGV/shakemap-conf-eu/archive/refs/heads/main.zip"
    logging.info("Downloading ShakeMap EU config...")
    
    try:
        response = requests.get(url, timeout=30)
        response.raise_for_status()
    except Exception as e:
        logging.error(f"Failed to download ShakeMap config: {e}")

    with zipfile.ZipFile(BytesIO(response.content)) as zf:
        zf.extractall("extern")

    extracted_path = os.path.join("extern", "shakemap-conf-eu-main")
    os.rename(extracted_path, target_dir)
    
    logging.info(f"ShakeMap config extracted to {target_dir}")
    return target_dir
