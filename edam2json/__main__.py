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

    edam_json_ld = json.loads(g.serialize(format='json-ld', context=context, indent=4).decode('utf-8'))
    return edam_json_ld

def listify(obj, key):
    value = obj.get(key,[])
    return value if isinstance(value, list) else [value]

def process_node(node, json_ld, extended):
    biotools_node = {'data': {'uri': node['@id']},
                     'children':[]}
    logging.debug("processing term %s" % node['@id'])
    text = node.get('rdfs:label')
    if text is not None:
        biotools_node['text'] = text
    else:
        logging.error("missing label for term %s" % node['@id'])
    if node.get('oboInOwl:hasExactSynonym'):
        biotools_node['exact_synonyms'] = listify(node, 'oboInOwl:hasExactSynonym')
    if node.get('oboInOwl:hasNarrowSynonym'):
        biotools_node['narrow_synonyms'] = listify(node, 'oboInOwl:hasNarrowSynonym')
    if node.get('oboInOwl:consider'):
        biotools_node['consider'] = [n['@id'] for n in listify(node, 'oboInOwl:consider')]
    if node.get('oboInOwl:replacedBy'):
        biotools_node['replacedBy'] = [n['@id'] for n in listify(node, 'oboInOwl:replacedBy')]
    if extended:
        description = node.get('oboInOwl:hasDefinition')
        if description is not None:
            biotools_node['definition'] = description
        else:
            logging.error("missing definition for term %s" % node['@id'])
        if node.get('rdfs:comment'):
            biotools_node['comment'] = listify(node, 'rdfs:comment')
        superclasses = listify(node,'rdfs:subClassOf')
        for superclass in superclasses:
            if superclass['@id'].startswith('_:'):
                term = [term for term in json_ld['@graph'] if term['@id']==superclass['@id']][0]
                property_name = term['owl:onProperty']['@id'].replace('http://edamontology.org/','')
                property_value = term['owl:someValuesFrom']['@id']
                biotools_node[property_name] = biotools_node.get(property_name,[]) + [property_value]
    for term in json_ld['@graph']:
        subclass_of = listify(term,'rdfs:subClassOf')
        if {'@id': node['@id']} in subclass_of:
            biotools_node['children'].append(process_node(term, json_ld, extended))
    if len(biotools_node['children'])==0:
        del biotools_node['children']
    return biotools_node

def print_jsonld(args):
    json_ld = get_json_ld(args.file)
    json.dump(json_ld, args.output, sort_keys=True,
                 indent=None if args.minified else 4, separators=(',', ': '))

def print_biotools(args):
    json_ld = get_json_ld(args.file) 
    root = args.root
    if root:
        try:
            root_node = [term for term in json_ld['@graph'] if term['@id']==root][0]
        except IndexError:
            print('Cannot find term "' + root +'" in EDAM ontology')
            return
        biotools_node = process_node(root_node, json_ld, args.extended)
    else:
        subroot_nodes =  [term for term in json_ld['@graph'] if term['@type']=='owl:Class' 
                            and 'rdfs:subClassOf' not in term 
                            and term['@id'].startswith('http://edamontology.org')
                            or term['@id'].startswith('owl:')]
        biotools_node = {'data': {'uri': 'owl:Thing'},
                     'children':[]}
        for subroot_node in subroot_nodes:
            biotools_node['children'].append(process_node(subroot_node, json_ld, args.extended))
    if args.extended:
        meta_node = [term for term in json_ld['@graph'] if term['@id']=='http://edamontology.org'][0]
        version = meta_node['doap:Version']
        if isinstance(version, dict) and '@value' in version:
            version = version['@value']
        biotools_node['meta'] = {
            'version': version,
            'date': meta_node['oboOther:date']
        }
    json.dump(biotools_node, args.output, sort_keys=True,
                  indent=None if args.minified else 4, separators=(',', ': '))

def main():
    parser = argparse.ArgumentParser(
                 description='EDAM file import tool')
    parser.add_argument('file',type=argparse.FileType('r'),
                        help="path to the EDAM file")
    subparsers = parser.add_subparsers(dest='action')
    subparsers.required = True
    parser_jsonld = subparsers.add_parser('jsonld')
    parser_jsonld.set_defaults(func=print_jsonld)
    parser_biotools = subparsers.add_parser('biotools')
    parser_biotools.add_argument('--root')
    parser_biotools.add_argument('--extended', action='store_true')
    parser_biotools.add_argument('--minified', action='store_true')
    parser_biotools.set_defaults(func=print_biotools)
    parser.add_argument('--output', '-o', type=argparse.FileType('w'), default='-',
                        help="path to the output file")
    args = parser.parse_args()
    args.func(args)
