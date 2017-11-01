#! /usr/bin/env python
# -*- coding: utf-8 -*-

import os
import logging
import argparse
import json

from rdflib import Graph, plugin
from rdflib.serializer import Serializer
from rdflib.extras.infixowl import AllProperties

def get_json_ld(edam_owl_file):
    g = Graph().parse(edam_owl_file)
    context = {}

    for ns in g.namespaces():
        if str(ns[0])!='':
            context[str(ns[0])] = str(ns[1])

    for p in AllProperties(g):
        if p.qname!='':
            context[p.qname.lstrip(':')] = str(p.identifier)

    context["next_id"] = "http://edamontology.org/next_id"

    edam_json_ld = json.loads(g.serialize(format='json-ld', context=context, indent=4))
    return edam_json_ld

def listify(obj, key):
    value = obj.get(key,[])
    return value if isinstance(value, list) else [value]

def process_node(node):
    biotools_node = {'text': node['rdfs:label'],
                     'data': {'uri': node['@id']},
                     'children':[]}
    biotools_node['exact_synonyms'] = node.get('oboInOwl:hasExactSynonym',[])
    biotools_node['narrow_synonyms'] = node.get('oboInOwl:hasNarrowSynonym',[])
    for term in json_ld['@graph']:
        subclass_of = listify(term,'rdfs:subClassOf')
        if {'@id':node['@id']} in subclass_of:
            biotools_node['children'].append(process_node(term))
    return biotools_node

if __name__ == '__main__':
    parser = argparse.ArgumentParser(
                 description='EDAM file import tool')
    parser.add_argument('file',
                        help="path to the EDAM file")
    args = parser.parse_args()

    json_ld = get_json_ld(args.file)
    root = 'topic_0003'
    root_node = [term for term in json_ld['@graph'] if term['@id']=='http://edamontology.org/'+root][0]
    biotools_node = process_node(root_node)
    print(json.dumps(biotools_node, sort_keys=True,
              indent=4, separators=(',', ': ')))
