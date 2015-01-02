# -*- coding: utf-8 -*-

from wapu.utils import auth_required_decorator, read_fecha, read_monto # TODO: hacer un import y referenciar por el nombre completo
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
    'beneficios_arancel': 'http://intranet.utem.cl/{0}/alumnos/beneficios_arancel.php',
    'cuenta_corriente': 'http://intranet.utem.cl/{0}/alumnos/cuenta_corriente.php',
    'ficha_antecedentes': 'http://intranet.utem.cl/{0}/personal/consultar_ficha.php',
    'convenios': 'http://intranet.utem.cl/{0}/honorarios/consultar_convenio.php',
    'detalle_convenio': 'http://intranet.utem.cl/{0}/honorarios/detalle_convenio.php?det={1}',
    'logout': 'http://intranet.utem.cl/{0}/intranet/end_session.php',
    'notas': 'http://intranet.utem.cl/{0}/alumnos/notas_dirdoc.php' # Esto no anda ni pa atrás, pero al menos sirve para checkear credenciales ...
}

# Decorador para checkear validez de credenciales, mira la url en el primer parámetro, si el body
# contiene el mensaje del segundo parámetro estamos mal
requires_auth = auth_required_decorator(URLS['notas'], AUTH_FAILED_MSG)


class IntranetWrapper(BaseWrapper):

    def login(self, username, password):
        req = requests.get(URLS['index'], headers=self.__headers__)

        self.__token__ = req.url.split('/')[-3] # Este provee la autenticación
        data = {'rut': username, 'clave': password}
        req = requests.post(URLS['login'].format(self.__token__), data, headers=self.__headers__)

        if 'Error en la clave' in req.text:
            raise AuthException('Oops, fallamos en el login inicial, probablemente quieras llamar a login() nuevamente')
        self.__cookies__ = req.cookies

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
        convenios = []
        req = requests.get(URLS['convenios'].format(self.__token__, headers=self.__headers__))

        dom = BeautifulSoup(req.text)
        raw_trs = dom.select('table:nth-of-type(2) tr')[1:]

        for i, tr in enumerate(raw_trs):
            convenio = {}
            tds = tr.select('td')
            convenio['id'] = i
            convenio['fecha_inicio'] = read_fecha(tds[1].text)
            convenio['fecha_termino'] = read_fecha(tds[2].text)
            convenios.append(convenio)

        return ujson.dumps(convenios, ensure_ascii=False)


    @requires_auth
    def convenio(self, id):
        data = {}
        cuotas = []

        req = requests.get(URLS['detalle_convenio'].format(self.__token__, id), headers=self.__headers__)
        dom = BeautifulSoup(req.text)
        convenio_td = dom.select('table:nth-of-type(1) td') # Los td de la primera tabla
        cargo_td = dom.select('table:nth-of-type(2) td:nth-of-type(1)') # Solo necesito el primer td
        cuotas_trs = dom.select('table:nth-of-type(3) tr')[1:] # En teoria podrían sacar un pago a muchas cuotas, igual lo dudo ...

        data['monto'] = read_monto(convenio_td[2].text)
        data['reparticion'] = convenio_td[4].text.rstrip()
        data['fecha_inicio'] = read_fecha(convenio_td[6].text)
        data['fecha_termino'] = read_fecha(convenio_td[7].text)
        data['resolucion'] = convenio_td[9].text.rstrip() if convenio_td[9].text.rstrip() else None
        data['fecha_resolucion'] = read_fecha(convenio_td[10].text.rstrip()) if convenio_td[9].text.rstrip() else None
        data['cargo'] = cargo_td[0].text.rstrip()

        for tr in cuotas_trs:
            cuota = {}
            tds = tr.select('td')

            cuota['id'] = int(tds[0].text)
            cuota['estado'] = tds[1].text.lstrip() # CON BANCARIO, REGISTRADA, etc
            cuota['monto'] = read_monto(tds[2].text)
            cuota['tipo_documento'] = tds[3].text.rstrip() if tds[3].text.rstrip() else None
            cuota['numero'] = int(tds[4].text.rstrip()) if tds[4].text.rstrip() else None
            cuota['fecha_documento'] = read_fecha(tds[5].text) if tds[5].text.rstrip() else None

            cuotas.append(cuota)
        data['cuotas'] = cuotas

        return ujson.dumps(data)