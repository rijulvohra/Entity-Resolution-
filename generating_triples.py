from rdflib import Graph, URIRef, Literal, XSD, Namespace, RDF, RDFS
import json
import jsonlines
import warnings

warnings.catch_warnings()


def create_graph():
    # Create namespace
    FOAF = Namespace('http://xmlns.com/foaf/0.1/')
    MYNS = Namespace('http://inf558.org/myfakenamespace#')
    SCHEMA = Namespace('http://schema.org/')
    # json file
    json_file = open('Rijul_Vohra_hw03_imdb_afi_el.json', 'r')
    obj = json.load(json_file)
    py_obj = json.loads(obj)
    my_kg = Graph()
    my_kg.bind('my_ns', MYNS)
    my_kg.bind('foaf', FOAF)
    my_kg.bind('schema', SCHEMA)
    # Movie
    movie_node = URIRef(MYNS['Movie'])
    my_kg.add((MYNS['Movie'], RDF.type, SCHEMA['Class']))
    my_kg.add((MYNS['Movie'], RDFS.subClassOf, SCHEMA['Movie']))
    # movie_name
    my_kg.add((movie_node, SCHEMA['name'], XSD.text))
    # Production Company
    prod_node_uri = URIRef(MYNS['productionCompany'])
    my_kg.add((prod_node_uri, RDF.type, SCHEMA['Class']))
    my_kg.add((prod_node_uri, RDFS.subClassOf, SCHEMA['Organization']))
    my_kg.add((movie_node, SCHEMA['productionCompany'], prod_node_uri))
    # release date
    my_kg.add((movie_node, SCHEMA['datePublished'], XSD.date))
    # Certificate
    certificate_node = URIRef(MYNS['certificate'])
    my_kg.add((certificate_node, RDF.type, SCHEMA['Class']))
    my_kg.add((certificate_node, RDFS.subClassOf, SCHEMA['contentRating']))
    my_kg.add((movie_node, SCHEMA['contentRating'], certificate_node))
    # runtime
    my_kg.add((movie_node, SCHEMA['duration'], XSD.duration))
    # genre
    my_kg.add((movie_node, SCHEMA['genre'], XSD.text))
    # producer
    my_kg.add((movie_node, SCHEMA['producer'], XSD.Person))
    # rating
    my_kg.add((movie_node, SCHEMA['aggregateRating'], XSD.aggregateRating))
    # metascore
    my_kg.add((movie_node, SCHEMA['aggregateRating'], XSD.aggregateRating))

    # votes
    my_kg.add((movie_node, SCHEMA['commentCount'], XSD.integer))
    # writer
    writer_node = URIRef(MYNS['writer'])
    my_kg.add((writer_node, RDF.type, SCHEMA['Class']))
    my_kg.add((writer_node, RDFS.subClassOf, SCHEMA['author']))
    my_kg.add((movie_node, SCHEMA['author'], writer_node))

    # cinematographer
    cinematographer_node = URIRef(MYNS['cinematographer'])
    my_kg.add((cinematographer_node, RDF.type, SCHEMA['Class']))
    my_kg.add((cinematographer_node, RDFS.subClassOf, SCHEMA['director']))
    my_kg.add((movie_node, SCHEMA['director'], cinematographer_node))

    # Gross Income
    my_kg.add((movie_node, SCHEMA['currency'], XSD.text))

    for test_obj in py_obj:

        node_uri = URIRef(MYNS[test_obj['imdb_movie']])
        imdb_movie = test_obj['imdb_movie']
        afi_movie = test_obj['afi_movie']
        imdb_jl = jsonlines.open('imdb.jl', 'r')
        afi_jl = jsonlines.open('afi.jl', 'r')
        for obj in imdb_jl:
            # print(obj)
            if obj['url'] == imdb_movie:
                # print('yes')
                my_kg.add((node_uri, RDF.type, MYNS['Movie']))
                my_kg.add((node_uri, SCHEMA['name'], Literal(obj['name'])))
                if 'certificate' in obj and obj['certificate'] != 'Not Rated':
                    local_certificate = obj['certificate'].lower()
                    local_certificate_uri = URIRef(MYNS[local_certificate])
                    my_kg.add((node_uri, SCHEMA['contentRating'], local_certificate_uri))
                    my_kg.add((local_certificate_uri, FOAF['certificate'], Literal(obj['certificate'])))
                    my_kg.add((local_certificate_uri, RDF.type, certificate_node))
                if 'runtime' in obj:
                    my_kg.add((node_uri, SCHEMA['duration'], Literal(obj['runtime'])))
                if 'genre' in obj:
                    my_kg.add((node_uri, SCHEMA['genre'], Literal(obj['genre'])))
                if 'rating' in obj:
                    my_kg.add((node_uri, SCHEMA['aggregateRating'], Literal(obj['rating'])))
                if 'metascore' in obj:
                    my_kg.add((node_uri, SCHEMA['aggregateRating'], Literal(obj['metascore'])))
                if 'votes' in obj:
                    my_kg.add((node_uri, SCHEMA['commentCount'], Literal(obj['votes'])))
                if 'gross' in obj:
                    my_kg.add((node_uri, SCHEMA['currency'], Literal(obj['gross'])))

                break
        if test_obj['afi_movie'] != None:
            for afi_obj in afi_jl:
                if afi_obj['url'] == test_obj['afi_movie']:
                    if 'release_date' in afi_obj:
                        my_kg.add((node_uri, SCHEMA['datePublished'], Literal(afi_obj['release_date'])))
                    if 'producer' in afi_obj:
                        my_kg.add((node_uri, SCHEMA['producer'], Literal(afi_obj['producer'])))
                    if 'production_company' in afi_obj:
                        # prod_com = URIRef(MYNS[afi])
                        comp_name = afi_obj['production_company'].lower().split()
                        comp_name_uri = '_'.join(comp_name)
                        local_prod_node = URIRef(MYNS[comp_name_uri])
                        my_kg.add((node_uri, SCHEMA['productionCompany'], local_prod_node))
                        my_kg.add((local_prod_node, FOAF['name'], Literal(afi_obj['production_company'])))
                        my_kg.add((local_prod_node, RDF.type, prod_node_uri))
                    if 'writer' in afi_obj:
                        writer_name = afi_obj['writer'].lower().split()
                        writer_name_uri = '_'.join(writer_name)
                        local_writer_node = URIRef(MYNS[writer_name_uri])
                        my_kg.add((node_uri, SCHEMA['author'], local_writer_node))
                        my_kg.add((local_writer_node, FOAF['name'], Literal(afi_obj['writer'])))
                        my_kg.add((local_writer_node, RDF.type, writer_node))
                    if 'cinematographer' in afi_obj:
                        cinemat_name = afi_obj['cinematographer'].lower().split()
                        cinemat_name_uri = '_'.join(cinemat_name)
                        local_cinemat_node = URIRef(MYNS[cinemat_name_uri])
                        my_kg.add((node_uri, SCHEMA['director'], local_cinemat_node))
                        my_kg.add((local_cinemat_node, FOAF['name'], Literal(afi_obj['cinematographer'])))
                        my_kg.add((local_cinemat_node, RDF.type, writer_node))

                    break

if __name__ == "__main__":
    create_graph()