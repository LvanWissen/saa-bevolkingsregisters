"""


Built upon an adapted version of RDFAlchemy for Python (3.7). Install with:

```bash
pip install git+https://github.com/LvanWissen/RDFAlchemy.git
```

Questions:
    Leon van Wissen (l.vanwissen@uva.nl)

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

dc = Namespace("http://purl.org/dc/elements/1.1/")
dcterms = Namespace("http://purl.org/dc/terms/")

AS = Namespace("http://www.w3.org/ns/activitystreams#")
oa = Namespace("http://www.w3.org/ns/oa#")
foaf = Namespace("http://xmlns.com/foaf/0.1/")

import rdflib.graph
rdflib.graph.DATASET_DEFAULT_GRAPH_ID = br


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

    with multiprocessing.Pool(processes=2) as pool:
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

    # if not xmlfile.endswith(
    #         'SAA_Index_op_bevolkingsregister_1851-1853_20181004_001.xml'):
    #     return

    targetfile = os.path.join(trigfolder, indexName,
                              f.replace('.xml', '.trig'))

    ds = Dataset()

    # The graph
    ds.add((br.term(indexName), RDF.type, void.Dataset))
    ds.add((br.term(indexName), dcterms.title, Literal(indexName)))
    ds.add((br.term(indexName), dcterms.modified,
            Literal(datetime.now().strftime('%Y-%m-%d'), datatype=XSD.date)))
    ds.add((br.term(indexName), dcterms.description,
            Literal(f"RDF conversion of {indexName}")))

    # The dataset
    ds.add((URIRef(
        "https://data.create.humanities.uva.nl/datasets/bevolkingsregisters"),
            RDF.type, void.Dataset))
    ds.add((URIRef(
        "https://data.create.humanities.uva.nl/datasets/bevolkingsregisters"),
            dcterms.title, Literal("Archief van het Bevolkingsregister")))
    ds.add((URIRef(
        "https://data.create.humanities.uva.nl/datasets/bevolkingsregisters"),
            dcterms.modified,
            Literal(datetime.now().strftime('%Y-%m-%d'), datatype=XSD.date)))

    # Subset
    ds.add((URIRef(
        "https://data.create.humanities.uva.nl/datasets/bevolkingsregisters"),
            void.subset, br.term(indexName)))

    # For backref
    g_void = br.term(indexName)

    # And the graph itself
    g = rdfSubject.db = ds.graph(identifier=br.term(indexName))

    # Bind prefixes
    ds.bind('br', br)
    ds.bind('bri', saaRec)
    ds.bind('brp', saaPerson)
    ds.bind('saa', saa)  # the ontology
    ds.bind('rdfs', RDFS)
    ds.bind('xsd', XSD)
    ds.bind('pnv', pnv)
    ds.bind('schema', schema)
    ds.bind('dcterms', dcterms)
    # ds.bind('saaLocation', saaLocation)
    # ds.bind('saaOccupation', saaOccupation)
    ds.bind('bio', bio)
    ds.bind('sem', sem)
    ds.bind('skos', skos)
    ds.bind('roar', roar)
    ds.bind('prov', prov)
    ds.bind('void', void)

    if '1851-1853' in indexName:

        earliestBeginTimeStamp = Literal("1851-01-01", datatype=XSD.datetime)
        latestBeginTimeStamp = Literal("1853-12-31", datatype=XSD.datetime)

        earliestEndTimeStamp = Literal("1851-01-01", datatype=XSD.datetime)
        latestEndTimeStamp = Literal("1853-12-31", datatype=XSD.datetime)
    elif '1853-1863' in indexName:

        earliestBeginTimeStamp = Literal("1853-01-01", datatype=XSD.datetime)
        latestBeginTimeStamp = Literal("1863-12-31", datatype=XSD.datetime)

        earliestEndTimeStamp = Literal("1853-01-01", datatype=XSD.datetime)
        latestEndTimeStamp = Literal("1863-12-31", datatype=XSD.datetime)
    elif '1874-1893' in indexName:

        earliestBeginTimeStamp = Literal("1874-01-01", datatype=XSD.datetime)
        latestBeginTimeStamp = Literal("1893-12-31", datatype=XSD.datetime)

        earliestEndTimeStamp = Literal("1874-01-01", datatype=XSD.datetime)
        latestEndTimeStamp = Literal("1893-12-31", datatype=XSD.datetime)

    saaLocation = Namespace(
        f"https://data.create.humanities.uva.nl/datasets/bevolkingsregisters/Location/{indexName}/"
    )
    saaOccupation = Namespace(
        f"https://data.create.humanities.uva.nl/datasets/bevolkingsregisters/Occupation/{indexName}/"
    )

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
                mentionsStreet=record['straatnaam'],
                mentionsOriginalStreet=record['straatnaamInBron'],
                mentionsNeighbourhoodCode=record['buurtcode'],
                mentionsNeihbourhoodNumber=record['buurtnummer'],
                mentionsStreetKlein=record['straatMetKleinnummer'],
                mentionsStreetExtra=record['huisnummertoevoeging'],
                mentionsOccupation=record['beroep'],
                description=Literal(record['overigeGegevens'], lang='nl')
                if record['overigeGegevens'] is not None else None,
                inDataset=g_void)

            pn = getPersonName(record['naam'])

            if record['geboorteplaats']:
                place = LocationObservation(saaLocation.term(
                    str(
                        uuid.uuid5(uuid.NAMESPACE_OID,
                                   record['geboorteplaats']))),
                                            label=[record['geboorteplaats']],
                                            documentedIn=r,
                                            inDataset=g_void)
            else:
                place = None

            birth = Birth(
                None,
                place=place,
                hasTimeStamp=Literal(record['geboortedatum'],
                                     datatype=XSD.datetime)
                if record['geboortedatum'] is not None else None,
                label=[Literal(f"Geboorte van {pn.label}", lang='nl')])

            # need a unique entry for the adres
            if record['huisnummertoevoeging'] and record['adres']:
                disambiguatingAddress = f"{record['adres']} {record['huisnummertoevoeging']}"
            else:
                disambiguatingAddress = None

            address = record[
                'straatMetKleinnummer'] or disambiguatingAddress or record[
                    'adres'] or record['straatnaamInBron'] or record[
                        'buurtnummer'] or record['buurtnummer']

            p = PersonObservation(saaPerson.term(record['@id']),
                                  hasName=[pn],
                                  label=[pn.label],
                                  birth=birth,
                                  birthDate=birth.hasTimeStamp,
                                  birthPlace=birth.place,
                                  documentedIn=r,
                                  inDataset=g_void)  # homeLocation?

            if address:
                identifier = str(uuid.uuid5(uuid.NAMESPACE_OID, address))

                loc = LocationObservation(
                    saaLocation.term(identifier),
                    address=PostalAddress(BNode(identifier),
                                          streetAddress=address,
                                          addressRegion=record['buurtcode'],
                                          postalCode=record['buurtnummer'],
                                          disambiguatingDescription=record[
                                              'huisnummertoevoeging']),
                    label=[address] if address else ["Unknown"],
                    documentedIn=r,
                    inDataset=g_void)

                p.homeLocation = loc

                loc.hasPerson = [
                    StructuredValue(
                        value=p,
                        role="resident",
                        hasEarliestBeginTimeStamp=earliestBeginTimeStamp,
                        hasLatestBeginTimeStamp=latestBeginTimeStamp,
                        hasEarliestEndTimeStamp=earliestEndTimeStamp,
                        hasLatestEndTimeStamp=latestEndTimeStamp,
                        label=p.label)
                ]

                homeLocation = StructuredValue(
                    value=loc,
                    role="home location",
                    hasEarliestBeginTimeStamp=earliestBeginTimeStamp,
                    hasLatestBeginTimeStamp=latestBeginTimeStamp,
                    hasEarliestEndTimeStamp=earliestEndTimeStamp,
                    hasLatestEndTimeStamp=latestEndTimeStamp,
                    label=loc.label)
            else:
                homeLocation = None

            if place:
                birthPlace = StructuredValue(value=place,
                                             role="birthplace",
                                             hasTimeStamp=birth.hasTimeStamp,
                                             label=place.label)
            else:
                birthPlace = None

            if birthPlace and homeLocation:
                p.hasLocation = [birthPlace, homeLocation]
            elif homeLocation:
                p.hasLocation = [homeLocation]
            elif place:
                p.hasLocation = [birthPlace]

            if record['beroep']:

                identifier = str(
                    uuid.uuid5(uuid.NAMESPACE_OID, record['beroep']))

                occupation = OccupationObservation(
                    saaOccupation.term(identifier),
                    label=[Literal(record['beroep'], lang='nl')],
                    documentedIn=r,
                    inDataset=g_void)
                p.hasOccupation = [occupation]

            birth.principal = p
            birth.hasActor = [
                Role(None,
                     value=p,
                     label=p.label,
                     roleType=RoleType(saaRole.term(
                         str(uuid.uuid5(uuid.NAMESPACE_OID, 'born'))),
                                       label=['Born']))
            ]

            r.mentionsRegistered = [p]

            if type(record['urlScan']) == list:
                r.onScan = [URIRef(i) for i in record['urlScan']]
            elif record['urlScan'] is not None:
                r.onScan = [URIRef(record['urlScan'])]

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
