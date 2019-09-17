"""
Bio ontology to be used in the enrichment of SAA indices by Golden Agents. 
"""

from rdflib import Dataset, Graph, Namespace
from rdflib import XSD, RDF, RDFS, OWL
from rdflib import URIRef, BNode, Literal

from rdfalchemy.rdfSubject import rdfSubject
from rdfalchemy.rdfsSubject import rdfsSubject
from rdfalchemy import rdfSingle, rdfMultiple, rdfContainer

prov = Namespace("http://www.w3.org/ns/prov#")

########
# PROV #
########


class Entity(rdfsSubject):
    rdf_type = prov.Entity


class Derivation(rdfsSubject):
    rdf_type = prov.Derivation

    hadActivity = rdfSingle(prov.hadActivity, range_type=prov.Activity)
    entity = rdfMultiple(prov.entity, range_type=prov.Entity)


class Activity(rdfsSubject):
    rdf_type = prov.Activity

    wasAssociatedWith = rdfSingle(prov.wasAssociatedWith,
                                  range_type=prov.Agent)
    qualifiedAssociation = rdfSingle(prov.qualifiedAssociation,
                                     range_type=prov.Association)

    comment = rdfSingle(RDFS.comment)


class Association(rdfsSubject):
    rdf_type = prov.Association

    hadPlan = rdfSingle(prov.hadPlan, range_type=prov.Plan)
    agent = rdfSingle(prov.agent, range_type=prov.Agent)

    comment = rdfSingle(RDFS.comment)


class Plan(rdfsSubject):
    rdf_type = prov.Plan

    comment = rdfSingle(RDFS.comment)


class Agent(rdfsSubject):
    rdf_type = prov.Agent