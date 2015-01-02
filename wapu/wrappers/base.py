# -*- coding: utf-8 -*-

from exceptions import NotImplementedError
from wapu.defaults import USER_AGENT

class BaseWrapper(object):

    def __init__(self, username, password, user_agent=USER_AGENT):
        self.__headers__ = {'User-Agent': user_agent}
        self.__token__ = None
        self.__cookies__ = None
        self.login(username, password)

    def login(self, username, password): # No haré persistencia de las credenciales
        raise NotImplementedError('Debes implementar este método!')