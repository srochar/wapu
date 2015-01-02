# -*- coding: utf-8 -*-

from wapu.utils import auth_required_decorator
from wapu.wrappers.base import BaseWrapper
from wapu.defaults import USER_AGENT
from wapu.errors import AuthException
from bs4 import BeautifulSoup
from exceptions import NotImplementedError, UserWarning
import requests
import ujson


# La intranet tira este mensaje cuando la sesion expira
AUTH_FAILED_MSG = 'Su sessi&oacute;n ha caducado ingrese por el portal de la'

# Listado de URLS a checkear en el wrapper
# Las urls de intranet usan un tipo de sesion en la URL ... weird
URLS = {
    'index': 'http://intranet.utem.cl',
    'login': 'http://intranet.utem.cl/{0}/intranet/inicio.php',
    'beneficios_arancel' : 'http://intranet.utem.cl/{0}/alumnos/beneficios_arancel.php',
    'cuenta_corriente' : 'http://intranet.utem.cl/{0}/alumnos/cuenta_corriente.php',
    'ficha_antecedentes' : 'http://intranet.utem.cl/{0}/personal/consultar_ficha.php',
    'convenios' : 'http://intranet.utem.cl/{0}/honorarios/consultar_convenio.php',
    'logout' : 'http://intranet.utem.cl/{0}/intranet/end_session.php',
    'notas' : 'http://intranet.utem.cl/{0}/alumnos/notas_dirdoc.php' # Esto no anda ni pa atrás, pero al menos sirve para checkear credenciales ...
}

# Decorador para checkear validez de credenciales, mira la url en el primer parámetro, si el body
# contiene el mensaje del segundo parámetro estamos mal
requires_auth = auth_required_decorator(URLS['contacto'], AUTH_FAILED_MSG)


class IntranetWrapper(BaseWrapper):

    def login(self, username, password):
        req = requests.get(URLS['index'], headers=self.__headers__)

        self.__token__ = req.url.split('/')[-3] # Este provee la autenticación
        data = {'rut': username, 'clave': password}
        req = requests.post(URLS['login'].format(self.__token__), data, headers=self.__headers__)

        if 'Error en la clave' in req.text:
            raise AuthException('Oops, fallamos en el login inicial, probablemente quieras llamar a login() nuevamente')

    @requires_auth
    def beneficios_arancel(self):
        raise NotImplementedError('TODO: implementar')

    @requires_auth
    def cuenta_corriente(self):
        raise NotImplementedError('TODO: implementar')

    @requires_auth
    def antecedentes(self):
        raise NotImplementedError('TODO: implementar')

    @requires_auth
    def convenios(self):
        raise NotImplementedError('TODO: implementar')

    @requires_auth
    def convenio(self, id):
        raise NotImplementedError('TODO: implementar')