# -*- coding: utf-8 -*-

from wapu.utils import auth_required_decorator
from wapu.defaults import USER_AGENT
from wapu.errors import AuthException
from bs4 import BeautifulSoup
from exceptions import NotImplementedError, UserWarning
import requests
import ujson


# Cuando no estas autenticado dirdoc dice esto
AUTH_FAILED_MSG = 'al parecer no estas ingresando como persona autorizada'

# Listado de URLS a checkear en el wrapper
URLS = {
    'contacto' : 'http://dirdoc.utem.cl/alumnos/contacto.php',
    'login': 'http://dirdoc.utem.cl/valida.php',
    'situacion_arancelaria': 'http://dirdoc.utem.cl/alumnos/certificado_aranceles.php',
    'notas': 'http://dirdoc.utem.cl/curricular/notas',
    'notas_semestre_previo': 'http://dirdoc.utem.cl/curricular/notas_anterior',
    'curso': 'http://dirdoc.utem.cl/curricular/notas/{0}'
}

# Decorar para checkear validez de credenciales, mira la url en el primer parámetro, si el body
# contiene el mensaje del segundo parámetro estamos mal
requires_auth = auth_required_decorator(URLS['contacto'], AUTH_FAILED_MSG)

class DirdocWrapper(object):

    def __init__(self, username, password, user_agent=USER_AGENT): # No haré persistencia de las credenciales
        self.__headers__ = {'User-Agent': USER_AGENT}
        #self.__cache__ = {}
        self.login(username, password)

    def login(self, username, password):
        data = {'rut': username, 'password': password, 'tipo': 0}
        req = requests.post(URLS['login'], data, headers=self.__headers__)

        if AUTH_FAILED_MSG in req.text:
            raise AuthException('Oops, fallamos en el login inicial, probablemente quieras llamar a login() nuevamente')
        self.__cookies__ = req.cookies

    @requires_auth
    def estudiante(self, **kwargs):
        req = requests.get(URLS['situacion_arancelaria'], headers=self.__headers__, cookies=self.__cookies__)

        dom = BeautifulSoup(req.text)
        raw_tds = dom.table.select('td')
        data = [value.text for value in raw_tds[:5]] + [raw_tds[6].text]
        heads = ['rut', 'nombres', 'codigo_carrera', 'carrera', 'plan_carrera', 'anio_ingreso']

        return ujson.dumps(dict(zip(heads, data)), ensure_ascii=False)

    @requires_auth
    def avance_malla(self, num=0): # Donde num es un indice del listado mostrado en el avance de malla
        raise NotImplementedError('Oopsie! aún no hago esto')

    @requires_auth
    def horario(self): # Solo puedo obtener el horario del semestre _actual_ damn you dirdoc
        raise NotImplementedError('Oopsie! aún no hago esto')

    @requires_auth
    def cursos(self, semestre=1): # semestre indica los dos semestre que dirdoc puede ver, actual y anterior
        data = []
        # semestre = -1 indica el anterior
        if semestre != 1 and semestre != -1: # Paso mal el semestre
            raise UserWarning('Solo se puede llamar semestre = 1 o -1')

        url = URLS['notas'] if semestre == 1 else URLS['notas_semestre_previo']
        req = requests.get(url, headers=self.__headers__, cookies=self.__cookies__)
        dom = BeautifulSoup(req.text)

        raw_trs = dom.select('table:nth-of-type(2) tr')[1:]
        for row in raw_trs:
            curso = {}
            raw_tds = row.select('td')
            curso['codigo'] = raw_tds[0].text
            curso['nombre'] = raw_tds[1].text
            url = raw_tds[-1].a
            curso['id'] = int(url.get('href').split('/')[-1])

            data.append(curso)
        return ujson.dumps(data, ensure_ascii=False)

    @requires_auth
    def curso(self, id):
        url = URLS['curso'].format(id)
        req = requests.get(url, headers=self.__headers__, cookies=self.__cookies__)

        if 'No registra incripci&oacute;n aceptada en el curso seleccionado' in req.text:
            raise UserWarning('Según dirdoc no tienes registrado este curso, checkea el id!')

        dom = BeautifulSoup(req.text)

        raise UserWarning('Luego seguiré implementando esto...')