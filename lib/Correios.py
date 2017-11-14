# -*- coding: utf-8 -*-

from lxml import html
import requests
import re
import sys


class Rastreio(object):
    def __init__(self, cod):
        self.cod = cod
        if self.isCod(cod):
            self.movimentacoes = self.rastreio(cod)
        else:
            self.movimentacoes = None

    def isCod(self, cod):
        return re.match('^[a-zA-Z]{2}[0-9]{9}[a-zA-Z]{2}$', cod)

    def isEntregue(self, obj):
        titles = [mov['title'] for mov in obj['movimentacoes']]
        return True in ['entregue' in title for title in titles]

    def escape(self, strarr):
        text = ' '.join(strarr)

        if sys.version_info.major == 2:
            text = text.encode('utf-8', 'ignore')

        text = text.replace('\r', ' ').replace('\t', ' ').strip()
        text = re.sub(' +', ' ', text)

        return text

    def rastreio(self, obj):
        movimentacoes = []
        s = requests.Session()

        obj_post = {
            'objetos': obj,
            'btnPesq': '+Buscar'
        }

        s.headers.update({
            'Host': 'www2.correios.com.br',
            'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:56.0) Gecko/20100101 Firefox/56.0',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'pt-BR,pt;q=0.8,en-US;q=0.5,en;q=0.3',
            'Accept-Encoding': 'gzip, deflate',
            'Referer': 'http://www2.correios.com.br/sistemas/rastreamento/default.cfm',
            'Content-Type': 'application/x-www-form-urlencoded',
            'Content-Length': '37',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1'
        })

        r = s.post('http://www2.correios.com.br/sistemas/rastreamento/resultado.cfm?', data=obj_post,
                   allow_redirects=True)
        r.encoding = 'ISO-8859-1'

        if r.status_code == 200:
            if r.text.find('listEvent') == -1:
                return None

            tree = html.fromstring(r.text.encode('latin1'))
            trs = tree.xpath('//table[contains(@class,"listEvent")]/tr')

            for tr in trs:
                tds = tr.xpath('./td')

                data = self.escape(tds[0].xpath('./text() | ./label/text()'))
                text = self.escape(tds[1].xpath('./text()'))
                title = tds[1].xpath('./strong/text()')[0]

                movimentacoes.append(Movimentacao(data.decode('utf-8', 'ignore'),
                                                  title.decode('utf-8', 'ignore'),
                                                  text.decode('utf-8', 'ignore')))

        return movimentacoes

    def __str__(self):
        pattern = "\n{0}" \
                  "\n{1}"

        parameters = [self.cod, self.movimentacoes]

        return pattern.format(*parameters)

    def __repr__(self):
        return self.__str__() + '\n'


class Movimentacao(object):
    def __init__(self, data, titulo, texto):
        self.data = data
        self.titulo = titulo
        self.texto = texto

    def __str__(self):
        pattern = "\n{0}" \
                  "\n{1}" \
                  "\n{2}"

        parameters = [self.data, self.titulo, self.texto]

        return pattern.format(*parameters)

    def __repr__(self):
        return self.__str__() + '\n'
