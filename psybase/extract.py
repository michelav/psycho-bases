#!/usr/bin/env python3
import yaml
import argparse
from logging import config, getLogger
from extractors import DefaultExtractor

def extractor_constructor(loader, node):
    options = loader.construct_mapping(node)
    name = options.pop('name')
    url = options.pop('url')
    ext = DefaultExtractor(name, url)
    ext.output = options['format']
    return ext

# Parsing arguments
parser = argparse.ArgumentParser()
parser.add_argument("query", help="Consulta a ser usada na base de pesquisa")
parser.add_argument("-b", "--base", type=str, action="append", dest="bases",
    help="Base a ser usada na pesquisa")
parser.add_argument("-a", "--arquivo", default="bases.csv",
    help="Nome do arquivo de saída")
parser.add_argument("-c", "--config", default="config.yaml", dest="config")
args=parser.parse_args()

def prepare_bases(bases):
    base_table = {}
    for base in bases:
        base_table[base.name] = base
    return base_table

def extract(bases):
    bases_map = prepare_bases(bases)
    queried_bases =  args.bases if args.bases else bases_map.keys()
    print(queried_bases)
    for base in queried_bases:
        extractor = bases_map[base]
        extractor.query(args.query)

def main():
    yaml.add_constructor(u'!extractor', extractor_constructor)
    with open(args.config, 'r') as f:
        config = yaml.load(f)
    extract(config['app']['bases'])


if __name__ == '__main__':
    main()

