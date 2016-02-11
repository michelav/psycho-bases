import requests
from string import Template
from lxml import etree
from xml.sax.handler import ContentHandler
from lxml.sax import saxify
from collections import OrderedDict
import logging

""" Module-wide logger """
logger = logging.getLogger(__name__)

""" Fast pass for isEnableFor(DEBUG). """
is_debug_enabled = logger.isEnabledFor(logging.DEBUG)

class DefaultContentHandler(ContentHandler):

    @property
    def found(self):
        return self._found

    @property
    def articles(self):
        return self._articles

    @property
    def found(self):
        return self._found

    def _get_title(self):
        try:
            title = self._doc['titulo_pt']
        except KeyError:
            try:
                title = self._doc['titulo_es']
            except KeyError:
                title = self._doc['titulo_en']
        return title

    def _get_abstract(self):
        try:
            abstract = self._doc['resumo_pt']

        except KeyError:
            try:
                abstract = self._doc['resumo_es']
            except KeyError:
                abstract = self._doc['resumo_en']
        return abstract


    def _save_doc(self):
        self._count = self._count + 1
        logger.debug('** Saving document %s **', self._count)
        title = self._get_title()
        logger.debug('Titulo => {}'.format(title))
        abstract = self._get_abstract()
        saved_doc = OrderedDict()
        # saved_doc['base'] = self._name
        # saved_doc['descritor'] = self._descriptor
        saved_doc['titulo'] = title
        saved_doc['resumo'] = abstract
        saved_doc['autores'] = self._doc['autores']
        logger.debug('Autores => {}'.format(self._doc['autores']))
        saved_doc['ano'] = self._doc['ano'][0:4]
        logger.debug('Ano => {}'.format(self._doc['ano']))
        saved_doc['lingua'] = self._doc['lingua']
        saved_doc['pais'] = self._doc['pais']
        saved_doc['status'] = 'aberto'
        saved_doc['categoria'] = ''
        saved_doc['exclusao'] = ''

        self._articles[title] = saved_doc
        # if is_debug_enabled:
        logger.debug('Articles saved: %s', len(list(self._articles.keys())))


    def _doc_tag(self, attributes):
        if self._doc:
            self._save_doc()
        self._title = None
        self._doc = {}

    def _result_tag(self, attributes):
        self._found = int(attributes[(None, 'numFound')])

    def _arr_tag(self, attributes):
        try:
            self._current = self._attrs[attributes[(None, 'name')]]
        except KeyError:
            self._current = None

    def _str_tag(self, attributes):
        try:
            self._current = self._attrs[attributes[(None, 'name')]]
        except KeyError:
            pass


    def __init__(self):
        self._current = None
        self._found = 0
        self._articles = {}
        self._title = None
        self._doc = {}
        self._tags = {'result': self._result_tag,
                      'doc': self._doc_tag, 'arr': self._arr_tag, 'str': self._str_tag}

        self._attrs = {'ab_en': 'resumo_en', 'ab_es': 'resumo_es',
                        'ab_pt': 'resumo_pt', 'au': 'autores', 'cp': 'pais',
                        'da': 'ano', 'la': 'lingua', 'ti_en': 'titulo_en',
                        'ti_pt': 'titulo_pt', 'ti_es': 'titulo_es'}

        # if is_debug_enabled:
        self._count = 0

    def startElementNS(self, name, qname, attributes):
        uri, localname = name
        try:
            self._tags[localname](attributes)
        except KeyError:
            self._current = None
            pass

    def characters(self, data):
        if self._current == 'autores':
            try:
                # if is_debug_enabled:
                # logger.debug('Storing %s => %s', self._current, data)
                authors = self._doc['autores']
                authors.append(data)
            except KeyError:
                self._doc[self._current] = [data]
        elif self._current:
            # if is_debug_enabled:
            # logger.debug('Storing %s => %s', self._current, data)
            self._doc[self._current] = data

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


    def __init__(self, name, url, options):
        print(options)
        self._name = name
        self._url = url
        self._descriptor = None
        # self._base = options['db']
        self._options = options
        self._output = None

    def query(self, qstr, interval):
        self._descriptor = qstr
        query_opts = {"output":self._output, "from":'0', "qstr":qstr}
        if interval:
            year_cluster = '"{0}"'.format('" OR "'.join(interval))
        else: # Last 3 years
            cur_year = date.today().year
            year_cluster = '"{0}"'.format('" OR "'.join([str(x) for x in range(cur_year -3, cur_year)]))
        query_opts['interval'] = year_cluster
        query_opts.update(self._options)
        template = Template(self._url)
        query = template.substitute(query_opts)
        logger.debug('Querying base: %s\n', self._options['db'])
        response = requests.get(query)
        root = etree.XML(str.encode(response.text, 'UTF-8'))
        handler = DefaultContentHandler()
        saxify(root, handler)
        # if is_debug_enabled:
        logger.debug('Query used: %s\nFound: %s', query, handler.found)
        logger.debug('Len: %s', len(handler.articles))
        return handler.articles