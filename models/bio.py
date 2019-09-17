"""
Bio ontology to be used in the enrichment of SAA indices by Golden Agents. 
"""

from rdflib import Dataset, Graph, Namespace
from rdflib import XSD, RDF, RDFS, OWL
from rdflib import URIRef, BNode, Literal

from rdfalchemy.rdfSubject import rdfSubject
from rdfalchemy.rdfsSubject import rdfsSubject
from rdfalchemy import rdfSingle, rdfMultiple, rdfContainer

bio = Namespace("http://purl.org/vocab/bio/0.1/")
sem = Namespace("http://semanticweb.cs.vu.nl/2009/11/sem/")
saa = Namespace("http://goldenagents.org/uva/SAA/ontology/")

#######
# BIO #
#######


class Event(rdfsSubject):
    rdf_type = bio.Event, sem.Event
    label = rdfMultiple(RDFS.label)

    date = rdfSingle(bio.date)

    followingEvent = rdfSingle(bio.followingEvent)
    precedingEvent = rdfSingle(bio.precedingEvent)

    hasTimeStamp = rdfSingle(sem.hasTimeStamp)
    hasBeginTimeStamp = rdfSingle(sem.hasBeginTimeStamp)
    hasEndTimeStamp = rdfSingle(sem.hasEndTimeStamp)
    hasEarliestBeginTimeStamp = rdfSingle(sem.hasEarliestBeginTimeStamp)
    hasLatestBeginTimeStamp = rdfSingle(sem.hasLatestBeginTimeStamp)
    hasEarliestEndTimeStamp = rdfSingle(sem.hasEarliestEndTimeStamp)
    hasLatestEndTimeStamp = rdfSingle(sem.hasLatestEndTimeStamp)

    place = rdfSingle(bio.place)  # multi-predicates?

    witness = rdfMultiple(bio.witness)
    spectator = rdfMultiple(bio.spectator)
    parent = rdfMultiple(bio.parent)

    hasActor = rdfMultiple(sem.hasActor, range_type=sem.Role)

    comment = rdfSingle(RDFS.comment)


class IndividualEvent(Event):
    rdf_type = bio.IndividualEvent, sem.Event
    principal = rdfSingle(bio.principal)

    label = rdfMultiple(RDFS.label)


class GroupEvent(Event):
    rdf_type = bio.GroupEvent, sem.Event
    partner = rdfMultiple(bio.partner)

    label = rdfMultiple(RDFS.label)


class Birth(IndividualEvent):
    rdf_type = bio.Birth, sem.Event


class Baptism(IndividualEvent):
    rdf_type = bio.Baptism, sem.Event


class Burial(IndividualEvent):
    rdf_type = bio.Burial, sem.Event


class Death(IndividualEvent):
    rdf_type = bio.Death, sem.Event


class Marriage(GroupEvent):
    rdf_type = bio.Marriage, sem.Event


class IntendedMarriage(GroupEvent):
    rdf_type = saa.IntendedMarriage
    hasDocument = rdfMultiple(saa.hasDocument)


class PrenuptialAgreement(GroupEvent):
    rdf_type = saa.PrenuptialAgreement


#######
# SEM #
#######


class Role(rdfsSubject):
    rdf_type = sem.Role
    value = rdfSingle(RDF.value)
    label = rdfMultiple(RDFS.label)
    roleType = rdfSingle(sem.roleType)


class RoleType(rdfsSubject):
    rdf_type = sem.RoleType
    label = rdfMultiple(RDFS.label)
