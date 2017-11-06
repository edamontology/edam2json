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

def process_node(node, json_ld, extended):
    biotools_node = {'data': {'uri': node['@id']},
                     'children':[]}
    text = node.get('rdfs:label')
    if text is not None:
        node['text'] = text
    biotools_node['exact_synonyms'] = node.get('oboInOwl:hasExactSynonym',[])
    biotools_node['narrow_synonyms'] = node.get('oboInOwl:hasNarrowSynonym',[])
    biotools_node['consider'] = node.get('oboInOwl:consider',[])
    biotools_node['replacedBy'] = node.get('oboInOwl:replacedBy',[])
    if extended:
        description = node.get('oboInOwl:hasDefinition')
        if description is not None:
            biotools_node['definition'] = description
    for term in json_ld['@graph']:
        subclass_of = listify(term,'rdfs:subClassOf')
        if {'@id':node['@id']} in subclass_of:
            biotools_node['children'].append(process_node(term, json_ld, extended))
    return biotools_node

def print_jsonld(args):
    json_ld = get_json_ld(args.file)
    print(json.dumps(json_ld, sort_keys=True,
                  indent=4, separators=(',', ': ')))

def print_biotools(args):
    json_ld = get_json_ld(args.file) 
    root = args.root
    try:
        root_node = [term for term in json_ld['@graph'] if term['@id']==root][0]
    except IndexError:
        print('Cannot find term "' + root +'" in EDAM ontology')
        return
    biotools_node = process_node(root_node, json_ld, args.extended)
    print(json.dumps(biotools_node, sort_keys=True,
                  indent=4, separators=(',', ': ')))

if __name__ == '__main__':
    parser = argparse.ArgumentParser(
                 description='EDAM file import tool')
    parser.add_argument('file',
                        help="path to the EDAM file")
    subparsers = parser.add_subparsers(dest='action')
    subparsers.required = True
    parser_jsonld = subparsers.add_parser('jsonld')
    parser_jsonld.set_defaults(func=print_jsonld)
    parser_biotools = subparsers.add_parser('biotools')
    parser_biotools.add_argument('--root',default='http://edamontology.org/topic_0003')
    parser_biotools.add_argument('--extended', action='store_true')
    parser_biotools.set_defaults(func=print_biotools)
    args = parser.parse_args()
    args.func(args)
