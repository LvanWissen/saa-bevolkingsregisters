"""
SAA ontology to be used in direct conversion from SAA to Golden Agents. 
"""

from rdflib import Dataset, Graph, Namespace
from rdflib import XSD, RDF, RDFS, OWL
from rdflib import URIRef, BNode, Literal

from rdfalchemy.rdfSubject import rdfSubject
from rdfalchemy import rdfSingle, rdfMultiple, rdfContainer, rdfList

bio = Namespace("http://purl.org/vocab/bio/0.1/")
sem = Namespace("http://semanticweb.cs.vu.nl/2009/11/sem/")
rel = Namespace("http://purl.org/vocab/relationship/")
pnv = Namespace('https://w3id.org/pnv#')
skos = Namespace('http://www.w3.org/2004/02/skos/core#')
schema = Namespace('http://schema.org/')
dcterms = Namespace("http://purl.org/dc/terms/")

AS = Namespace("http://www.w3.org/ns/activitystreams#")
oa = Namespace("http://www.w3.org/ns/oa#")

void = Namespace("https://www.w3.org/TR/void/")

foaf = Namespace("http://xmlns.com/foaf/0.1/")

prov = Namespace("http://www.w3.org/ns/prov#")

roar = Namespace("https://w3id.org/roar#")

saa = Namespace(
    "https://data.create.humanities.uva.nl/datasets/bevolkingsregisters/")
saaRec = Namespace(
    "https://data.create.humanities.uva.nl/datasets/bevolkingsregisters/Index/"
)
saaPerson = Namespace(
    "https://data.create.humanities.uva.nl/datasets/bevolkingsregisters/Person/"
)
saaPersonName = Namespace(
    "https://data.create.humanities.uva.nl/datasets/bevolkingsregisters/PersonName/"
)
saaOrganisation = Namespace(
    "https://data.create.humanities.uva.nl/datasets/bevolkingsregisters/Organisation/"
)
saaLocation = Namespace(
    "https://data.create.humanities.uva.nl/datasets/bevolkingsregisters/Location/"
)
saaOccupation = Namespace(
    "https://data.create.humanities.uva.nl/datasets/bevolkingsregisters/Occupation/"
)
saaRole = Namespace(
    "https://data.create.humanities.uva.nl/datasets/bevolkingsregisters/Role/")

# Void


class VoidDataset(rdfSubject):
    rdf_type = void.Dataset

    subset = rdfMultiple(void.subset)

    title = rdfSingle(dcterms.title)
    description = rdfSingle(dcterms.description)

    label = rdfMultiple(RDFS.label)


#############
# SAA Index #
#############


class Entity(rdfSubject):
    rdf_type = prov.Entity
    label = rdfMultiple(RDFS.label)
    comment = rdfMultiple(RDFS.comment)

    wasDerivedFrom = rdfMultiple(prov.wasDerivedFrom)
    qualifiedDerivation = rdfSingle(prov.qualifiedDerivation,
                                    range_type=prov.Derivation)

    inDataset = rdfSingle(void.inDataset)

    hasLocation = rdfMultiple(roar.hasLocation)

    documentedIn = rdfSingle(roar.documentedIn)


class Document(Entity):
    rdf_type = roar.Document
    identifier = rdfSingle(schema.identifier)

    language = rdfSingle(schema.isInLanguage)

    inventoryNumber = rdfSingle(saa.inventoryNumber)
    sectionNumber = rdfSingle(saa.sectionNumber)
    sourceReference = rdfSingle(saa.sourceReference)
    urlScan = rdfMultiple(saa.urlScan)
    label = rdfMultiple(RDFS.label)

    description = rdfSingle(saa.description)

    mentionsRegistered = rdfMultiple(saa.mentionsRegistered)
    mentionsLocation = rdfMultiple(saa.mentionsLocation,
                                   range_type=saa.Location)

    onScan = rdfMultiple(roar.onScan)


class Derivation(rdfSubject):
    rdf_type = prov.Derivation
    label = rdfMultiple(RDFS.label)
    comment = rdfMultiple(RDFS.comment)

    hadActivity = rdfSingle(prov.hadActivity)
    entity = rdfMultiple(prov.entity)


class Activity(rdfSubject):
    rdf_type = prov.Activity
    label = rdfMultiple(RDFS.label)
    comment = rdfMultiple(RDFS.comment)

    wasAssociatedWith = rdfMultiple(prov.wasAssociatedWith,
                                    range_type=prov.Agent)
    qualifiedAssociation = rdfSingle(prov.qualifiedAssociation,
                                     range_type=prov.Association)


class Agent(rdfSubject):
    rdf_type = prov.Agent
    label = rdfMultiple(RDFS.label)
    comment = rdfMultiple(RDFS.comment)


##########
# Person #
##########


class Inventory(rdfSubject):
    notary = rdfMultiple(saa.notary)


class StructuredValue(rdfSubject):
    value = rdfSingle(RDF.value)

    role = rdfSingle(roar.role)

    hasTimeStamp = rdfSingle(sem.hasTimeStamp)
    hasBeginTimeStamp = rdfSingle(sem.hasBeginTimeStamp)
    hasEndTimeStamp = rdfSingle(sem.hasEndTimeStamp)
    hasEarliestBeginTimeStamp = rdfSingle(sem.hasEarliestBeginTimeStamp)
    hasLatestBeginTimeStamp = rdfSingle(sem.hasLatestBeginTimeStamp)
    hasEarliestEndTimeStamp = rdfSingle(sem.hasEarliestEndTimeStamp)
    hasLatestEndTimeStamp = rdfSingle(sem.hasLatestEndTimeStamp)

    label = rdfMultiple(RDFS.label)

##########
# Person #
##########


class Organisation(rdfSubject):
    rdf_type = saa.Organisation
    isInRecord = rdfSingle(saa.isInRecord)

    label = rdfMultiple(RDFS.label)


class Person(Entity):
    rdf_type = schema.Person
    isInRecord = rdfSingle(saa.isInRecord)

    hasName = rdfMultiple(pnv.hasName, range_type=pnv.PersonName)  # resource

    scanName = rdfSingle(saa.scanName)
    scanPosition = rdfSingle(saa.scanPosition)

    label = rdfMultiple(RDFS.label)

    birth = rdfSingle(bio.birth)
    death = rdfSingle(bio.death)
    event = rdfMultiple(bio.event)

    birthDate = rdfSingle(schema.birthDate)
    birthPlace = rdfSingle(schema.birthPlace)
    deathDate = rdfSingle(schema.deathDate)
    deathPlace = rdfSingle(schema.deathPlace)

    gender = rdfSingle(schema.gender)

    mother = rdfSingle(bio.mother)
    father = rdfSingle(bio.father)
    child = rdfSingle(bio.child)

    spouse = rdfMultiple(schema.spouse)
    parent = rdfMultiple(schema.parent)
    children = rdfMultiple(schema.children)

    hasOccupation = rdfMultiple(schema.hasOccupation)

    address = rdfSingle(schema.address)
    homeLocation = rdfSingle(schema.homeLocation)


class PersonObservation(Person):
    rdf_type = roar.PersonObservation


class PersonReconstruction(Person):
    rdf_type = roar.PersonReconstruction


class LocationObservation(Entity):
    rdf_type = roar.LocationObservation

    hasPerson = rdfMultiple(roar.hasPerson)
    address = rdfSingle(schema.address)


class LocationReconstruction(Entity):
    rdf_type = roar.LocationReconstruction


class PostalAddress(rdfSubject):
    rdf_type = schema.PostalAddress

    streetAddress = rdfSingle(schema.streetAddress)
    addressRegion = rdfSingle(schema.addressRegion)
    postalCode = rdfSingle(schema.postalCode)


class PersonName(rdfSubject):
    rdf_type = pnv.PersonName
    label = rdfSingle(RDFS.label)

    # These map to A2A
    literalName = rdfSingle(pnv.literalName)
    givenName = rdfSingle(pnv.givenName)
    surnamePrefix = rdfSingle(pnv.surnamePrefix)
    baseSurname = rdfSingle(pnv.baseSurname)

    # These do not
    prefix = rdfSingle(pnv.prefix)
    disambiguatingDescription = rdfSingle(pnv.disambiguatingDescription)
    patronym = rdfSingle(pnv.patronym)
    surname = rdfSingle(pnv.surname)

    nameSpecification = rdfSingle(pnv.nameSpecification)

    # Extra for the notarial acts
    personId = rdfSingle(saa.personId)
    scanName = rdfSingle(saa.scanName)
    scanPosition = rdfSingle(saa.scanPosition)
    uuidName = rdfSingle(saa.uuidName)


class Occupation(rdfSubject):
    rdf_type = schema.Occupation
    label = rdfMultiple(RDFS.label)
    name = rdfMultiple(schema.name)

    occupationalCategory = rdfMultiple(schema.occupationalCategory,
                                       range_type=schema.CategoryCode)


class OccupationObservation(Entity):
    rdf_type = roar.OccupationObservation
    label = rdfMultiple(RDFS.label)
    name = rdfMultiple(schema.name)

    occupationalCategory = rdfMultiple(schema.occupationalCategory,
                                       range_type=schema.CategoryCode)


class CategoryCode(rdfSubject):
    rdf_type = schema.CategoryCode
    inCodeSet = rdfSingle(schema.inCodeSet, range_type=schema.CategoryCodeSet)
    codeValue = rdfSingle(schema.codeValue)

    label = rdfMultiple(RDFS.label)
    name = rdfMultiple(schema.name)


class CategoryCodeSet(rdfSubject):
    rdf_type = schema.CategoryCodeSet
    label = rdfMultiple(RDFS.label)
    name = rdfMultiple(schema.name)

    # {
    #     "@context": "http://schema.org/",
    #     "@type": "Occupation",
    #     "name": "Film actor",
    #     "occupationalCategory": {
    #         "@type": "CategoryCode",
    #         "inCodeSet": {
    #             "@type": "CategoryCodeSet",
    #             "name": "HISCO"
    #         },
    #         "codeValue": "17320",
    #         "name": "Actor"
    #     }
    # }


#############
# Locations #
#############


class Location(rdfSubject):
    rdf_type = saa.Location
    isInRecord = rdfSingle(saa.isInRecord)

    label = rdfMultiple(RDFS.label)
    altLabel = rdfMultiple(skos.altLabel)
    sameAs = rdfMultiple(OWL.sameAs)


class Street(Location):
    rdf_type = saa.Street


#################
# Notarial acts #
#################

###############
# Annotations #
###############


class Scan(rdfSubject):
    rdf_type = (saa.Scan, AS.OrderedCollectionPage)

    # partOf a collection

    depiction = rdfSingle(foaf.depiction)

    imageFilename = rdfSingle(saa.imageFilename)
    imageWidth = rdfSingle(saa.imageWidth)
    imageHeight = rdfSingle(saa.imageHeight)

    regions = rdfMultiple(saa.regions)

    items = rdfList(AS.items)  # rdf:Collection
    prev = rdfSingle(AS.prev)
    next = rdfSingle(AS.next)


class Annotation(rdfSubject):
    rdf_type = oa.Annotation
    hasTarget = rdfSingle(oa.hasTarget)

    bodyValue = rdfSingle(oa.bodyValue)

    hasBody = rdfSingle(oa.hasBody)  # or multiple?

    motivatedBy = rdfSingle(oa.motivatedBy)

    depiction = rdfSingle(foaf.depiction)


class SpecificResource(rdfSubject):
    rdf_type = oa.SpecificResource

    hasSource = rdfSingle(oa.hasSource)
    hasSelector = rdfSingle(oa.hasSelector)
    hasState = rdfSingle(oa.hasState)
    hasPurpose = rdfSingle(oa.hasPurpose)


class Selector(rdfSubject):
    rdf_type = oa.Selector


class FragmentSelector(Selector):
    rdf_type = oa.FragmentSelector

    conformsTo = rdfSingle(dcterms.conformsTo)
    value = rdfSingle(RDF.value)


class TextQuoteSelector(Selector):
    rdf_type = oa.TextQuoteSelector


class TextPositionSelector(Selector):
    rdf_type = oa.TextPositionSelector
