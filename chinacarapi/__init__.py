"""ChinaCarAPI: Chinese used-car data (Dongchedi + Che168) as one REST API. Key required: https://chinacarapi.com

This package is the China entry point of ``encarapi`` (one client for Korean and
Chinese used car data). It keeps the ``chinacarapi`` name and API:
``ChinaCarAPI(key).catalog()``, ``.vehicle()``, ``.inspection()``, ``.bulk()``, ...
"""
from encarapi import ChinaCarAPI, ChinaCarAPIError, EnCarAPI, MissingApiKeyError

__all__ = ["ChinaCarAPI", "ChinaCarAPIError", "MissingApiKeyError", "EnCarAPI"]
__version__ = "1.0.0"
