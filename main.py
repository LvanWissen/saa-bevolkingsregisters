"""


Built upon an adapted version of RDFAlchemy for Python (3.7). Install with:

```bash
pip install git+https://github.com/LvanWissen/RDFAlchemy.git
```

Questions:
    Leon van Wissen (l.vanwissen@uva.nl)
    Golden Agents (www.goldenagents.org)

"""
import os
import sys
import json

import logging
import itertools
import random
import uuid

import xmltodict

from datetime import datetime
import dateutil.parser

from collections import defaultdict

import multiprocessing

from models.bio import *
from models.saa import *

create = Namespace(
    "https://data.create.humanities.uva.nl/datasets/bevolkingsregisters/")
dc = Namespace("http://purl.org/dc/elements/1.1/")
dcterms = Namespace("http://purl.org/dc/terms/")

AS = Namespace("http://www.w3.org/ns/activitystreams#")
oa = Namespace("http://www.w3.org/ns/oa#")
foaf = Namespace("http://xmlns.com/foaf/0.1/")

import rdflib.graph
rdflib.graph.DATASET_DEFAULT_GRAPH_ID = create


def defaultify(d, defaultdict_type=None):
    """Transform a dict-structure to defaultdicts to always return None if no
    value is present. 

    Args:
        d (dict): The dictionary that needs modification
        defaultdict_type (type, optional): The defaultdict type of the new 
        dictionary. Defaults to None.

    Returns:
        dict: defaultdict
    """
    if isinstance(d, dict):
        return defaultdict(lambda: defaultdict_type,
                           {k: defaultify(v)
                            for k, v in d.items()})
    elif isinstance(d, list):
        return [defaultify(i) for i in d]
    else:
        return d


def xml2rdf(datafolder, trigfolder):
    """Convert every index in the `datafolder` to rdf in a pipeline fashion.
    
    Args:
        datafolder (str): Path to datafolder. Each index data files should be in
        separate dirs. Every dir will reflect the graph name in the quads.
        trigfolder (str): Destination path. The same dir structure is created. 
    """

    xmlfiles = []

    for root, dirs, files in os.walk(datafolder):
        fp = [i for i in files if i.endswith('.xml')]
        if fp is None:
            continue
        else:
            xmlfiles += [(trigfolder, root, f) for f in fp]
            random.shuffle(xmlfiles)

            _, indexName = root.rsplit(os.sep)
            os.makedirs(os.path.join(trigfolder, indexName), exist_ok=True)

    # with multiprocessing.Pool(processes=multiprocessing.cpu_count()) as pool:
    # with multiprocessing.Pool(processes=6) as pool:
    #     _ = pool.map(parsexml, xmlfiles)

    # for f in sorted(xmlfiles):
    #     parsexml(f)

    # with multiprocessing.Pool(processes=multiprocessing.cpu_count()) as pool:
    with multiprocessing.Pool(processes=3) as pool:
        _ = pool.map(parsexml, xmlfiles)


def parsexml(xmlfile):
    """Parse a SAA data file and convert it to a graph using rdflib.
    
    Args:
        xmlfile (tuple): combination of the destination folder, the root dir 
        and the filepointer (str).
    """

    trigfolder, root, f = xmlfile
    _, indexName = root.rsplit(os.sep)

    xmlfile = os.path.join(root, f)
    
    if not xmlfile.endswith('SAA_Index_op_bevolkingsregister_1874-1893_20181005_010.xml'):
        return

    targetfile = os.path.join(trigfolder, indexName,
                              f.replace('.xml', '.trig'))

    ds = Dataset()

    g = rdfSubject.db = ds.graph(identifier=create.term(indexName))

    # Bind prefixes
    ds.bind('saa', saa)
    ds.bind('saaRec', saaRec)
    ds.bind('rdfs', RDFS)
    ds.bind('xsd', XSD)
    ds.bind('pnv', pnv)
    ds.bind('schema', schema)
    ds.bind('dcterms', dcterms)
    ds.bind('saaPerson', saaPerson)
    ds.bind('saaLocation', saaLocation)
    ds.bind('bio', bio)
    ds.bind('sem', sem)
    ds.bind('skos', skos)
    ds.bind('roar', roar)
    ds.bind('prov', prov)

    # Read the file
    with open(xmlfile, 'rb') as xmlrbfile:

        print(xmlfile)

        # Since we are using >= Python3.7
        parse = xmltodict.parse(xmlrbfile, dict_constructor=dict)

        parse = defaultify(parse)
        records = parse['indexRecords']['indexRecord']

        # Parse record
        for n, record in enumerate(records):

            if n % 5000 == 0:
                print(f"{n}/{len(records)} from {f}")
                sys.stdout.flush()

            r = Document(
                saaRec.term(record['@id']),
                identifier=record['@id'],
                inventoryNumber=record['inventarisnummer'],
                sourceReference=record['bronverwijzing'],
                description=Literal(record['overigeGegevens'], lang='nl')
                if record['overigeGegevens'] is not None else None)

            pn = getPersonName(record['naam'])

            birth = Birth(
                None,
                place=record['geboorteplaats'],
                hasTimeStamp=Literal(record['geboortedatum'],
                                     datatype=XSD.datetime)
                if record['geboortedatum'] is not None else None,
                label=[Literal(f"Geboorte van {pn.label}", lang='nl')])

            address = record['straatMetKleinnummer'] or record['adres']

            p = PersonObservation(saaPerson.term(record['@id']),
                                  hasName=[pn],
                                  label=[pn.label],
                                  birth=birth,
                                  birthDate=birth.hasTimeStamp,
                                  birthPlace=birth.place,
                                  documentedIn=r,
                                  address=address)  # homeLocation?

            loc = LocationObservation(
                saaLocation.term(record['@id']),
                address=PostalAddress(None,
                                      streetAddress=address,
                                      addressRegion=record['buurtcode'],
                                      postalCode=record['buurtnummer']),
            )

            p.homeLocation = loc

            loc.hasPerson = [p]

            if record['beroep']:

                identifier = str(
                    uuid.uuid5(uuid.NAMESPACE_OID, record['beroep']))

                occupation = Occupation(
                    saaOccupation.term(identifier),
                    label=[Literal(record['beroep'], lang='nl')])
                p.hasOccupation = [occupation]

            birth.principal = p
            birth.hasActor = [
                Role(None,
                     value=p,
                     label=p.label,
                     roleType=RoleType(saaRole.term(
                         saaRole.term(
                             str(uuid.uuid5(uuid.NAMESPACE_OID, 'born')))),
                                       label=['Born']))
            ]

            r.mentionsRegistered = [p]

            if type(record['urlScan']) == list:
                r.urlScan = [URIRef(i) for i in record['urlScan']]
            elif record['urlScan'] is not None:
                r.urlScan = [URIRef(record['urlScan'])]

            # A bit of prov
            r.wasDerivedFrom = r.urlScan

        print(f"Writing the graph to: {targetfile}")
        sys.stdout.flush()
        ds.serialize(targetfile, format='trig')


def getPersonName(personname, record=None):
    """Convert a personname dictionary to a pnv:PersonName.
    
    Args:
        personname (dict): Dictionary from the xml2dict package that contains
        one or several PersonName fields. 
    
    Returns:
        PersonName: A RDF resource that can be used in rdflib
    """

    if personname is None:
        return PersonName(None, nameSpecification="Unknown", label='Unknown')

    if personname.get('uuidNaam', None) is not None:
        uuid = saaPersonName.term(personname['uuidNaam'])
    else:
        uuid = None

    pn = PersonName(
        uuid,
        givenName=personname['voornaam'],
        surnamePrefix=personname['tussenvoegsel'],
        baseSurname=personname['achternaam'],
        literalName=" ".join([
            i for i in [
                personname['voornaam'], personname['tussenvoegsel'],
                personname['achternaam']
            ] if i is not None
        ]))

    if pn.literalName == "":
        pn.literalName = "Unknown"
    else:
        pn.label = pn.literalName  # add a rdfs:label for readability

    return pn


if __name__ == "__main__":
    DATAPATH = "data/"
    TRIGPATH = "trig/"

    xml2rdf(datafolder=DATAPATH, trigfolder=TRIGPATH)