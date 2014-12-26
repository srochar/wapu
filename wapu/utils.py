# -*- coding: utf-8 -*-

from functools import wraps
import requests
from .errors import AuthException

def auth_required_decorator(url, msg):
    def wrapper(f):
        @wraps(f)
        def returned_wrapper(*args, **kwargs):
            obj = args[0] # Instancia de algun wrapper, deberia tener un campo __cookie__ con ... la cookie
            req = requests.get(url, headers = obj.__headers__, cookies=obj.__cookies__, **kwargs)
            if msg in req.text:
                raise AuthException('Oh-Oh problema de autenticación! prueba realizando nuevamente el login')
            return f(*args, **kwargs)
        return returned_wrapper
    return wrapper