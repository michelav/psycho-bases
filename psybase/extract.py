#!/usr/bin/env python3
import yaml
import argparse
from logging import config
from extractors import DefaultExtractor
from pathlib import Path
import csv

def extractor_constructor(loader, node):
    params = loader.construct_mapping(node)
    name = params['name']
    url = params['url']
    options = params['options']
    ext = DefaultExtractor(name, url, options)
    ext.output = params['output']
    return ext

def interval(interval_str):
    limits = interval_str.split('..')
    my_interval = [str(x) for x in range(int(limits[0]), int(limits[1]) + 1)]
    return my_interval

# Parsing arguments
parser = argparse.ArgumentParser()
parser.add_argument("query", help="Consulta a ser usada na base de pesquisa")
parser.add_argument("-b", "--base", type=str, action="append", dest="bases",
    help="Base a ser usada na pesquisa")
parser.add_argument("-a", "--arquivo", default="bases.csv", dest='arquivo',
    help="Nome do arquivo de saída")
parser.add_argument("-c", "--config", default="config.yaml", dest="config")
parser.add_argument("-i", "--interval", dest="interval", type=interval,
    help="Intervalo de tempo a que se refere a consulta no formato YYYY..YYYY")
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
    articles = []
    for base in queried_bases:
        extractor = bases_map[base]
        queried = extractor.query(args.query, args.interval)
        print('Queried: {}'.format(len(queried)))
        articles.append(queried)
    print('Articles: {}'.format(len(articles)))
    return articles

def write_csv(docs):
    with open(args.arquivo, 'w') as csvfile:
        fieldnames = list(docs[0].keys())
        writer = csv.DictWriter(csvfile, delimiter='|', fieldnames=fieldnames)
        for doc in docs:
            writer.writerow(doc)

def process_articles(articles):
    processed_articles = []
    temp_base = {}

    # Copying first dict
    for k, doc in articles[0].items():
        print(doc)
        processed_articles.append(doc)

    # Finding Duplicates
    temp_base.update(articles[0])
    for i in range(1, len(articles)):
        for title, doc in articles[i]:
            try:
                temp_base[title]
                doc['status'] = 'duplicado'
            except KeyError:
                pass
            finally:
                print("adicionando ao que vai ser salvo")
                processed_articles.append(doc)
        temp_base.update(articles[i])
    print('Articles: {}'.format(len(processed_articles)))
    write_csv(processed_articles)

def setup_dirs(dirs):
    for place in dirs:
        cur_dir = Path(place)
        if not cur_dir.exists():
            cur_dir.mkdir()

def main():
    yaml.add_constructor(u'!extractor', extractor_constructor)
    with open(args.config, 'r') as f:
        yaml_file = yaml.load(f)
    setup_dirs(yaml_file['app']['dirs'])
    config.dictConfig(yaml_file['logging'])
    articles = extract(yaml_file['app']['bases'])
    process_articles(articles)

if __name__ == '__main__':
    main()

