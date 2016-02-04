import requests
from string import Template

class DefaultExtractor(object):

    @property
    def name(self):
        return self._name

    @property
    def url(self):
        return self._url

    @property
    def output(self):
        return self._output

    @output.setter
    def output(self, value):
        self._output = value


    def __init__(self, name, url):
        self._name = name
        self._url = url
        self._output = None

    def query(self, qstr):
        print(self._url)
        template = Template(self._url)
        query = template.substitute(output=self._output, count='0', qstr=qstr, base=self._name)
        print(query)

