#!/usr/bin/python3
# -*- coding: utf-8 -*-

"""
    amecycl-calq
    script d'éclatement d'un fichier .geojson conforme au schéma de données des Aménagement cyclables
    Le script créé dans le repertoire amecycl autant de calques .geojson qu'il y a de types d'aménagement.
    La base de données amecycl_database comporte une table Stats avec les longueurs de chaque type d'aménagements
    
    dependance : geojson-length (https://pypi.org/project/geojson-length/)
"""

__author__ = "ToutesLatitudes"
__copyright__ = "Copyright 2021, ToutesLatitudes"
__license__ = "GPL"
__version__ = "1.1.0"
__email__ = "contact@touteslatitudes.fr"
__status__ = "Production"

import argparse
import os
import json
import time
import sqlite3

# module geojson-length (https://pypi.org/project/geojson-length/ ) 
# à installer via la commande : pip install geojson-length
from geojson_length import calculate_distance, Unit

# filtrage des proprietes commençant par un undescore
def underscored(key):
    if (key[0] == '_'):
        return True
    else:
        return False


start = time.time()


parser = argparse.ArgumentParser(description='Création des couches Aménagements Cyclables')
parser.add_argument('filename', metavar='F', type=str, nargs='+',
   help='le nom du fichier .geojson correspondant au jeu de données')

args = parser.parse_args()
ame_file = args.filename[0]

print()

# repertoire des calques resultats - fichiers au format .geojson
amecycl_layers_dir = 'amecycl'

# nom de la base de données amecycl
amecycl_db_name = 'amecycl.db'

# Liste des aménagements cyclables schema version 0.3.3
# donne le coefficient de calcul de la longueur / longueur cyclable
ame_list = {
    'ACCOTEMENT REVETU HORS CVCB': ['accotement-revetu', 1],
    'AMENAGEMENT MIXTE PIETON VELO HORS VOIE VERTE': ['amenagement-mixte', 0.5],
    'AUCUN': ['aucun', 1],
    'AUTRE': ['autre', 0.5],
    'BANDE CYCLABLE': ['bande-cyclable', 1],
    'CHAUSSEE A VOIE CENTRALE BANALISEE': ['cvcb', 1],
    'COULOIR BUS+VELO': ['couloir-busvelo', 1],
    'DOUBLE SENS CYCLABLE BANDE': ['dsc-bande', 1],
    'DOUBLE SENS CYCLABLE NON MATERIALISE': ['dsc-non-materialise', 1],
    'DOUBLE SENS CYCLABLE PISTE': ['dsc-piste', 1],
    'GOULOTTE': ['goulotte', 0.5],
    'PISTE CYCLABLE' : ['piste-cyclable', 1],
    'RAMPE': ['rampe', 0.5],
    'VELO RUE': ['velo-rue', 0.5],
    'VOIE VERTE': ['voie-verte', 0.5]
    }

def drop_schema_table():
    drop_table_query = '''DROP TABLE IF EXISTS Schema;'''
    cursor.execute(drop_table_query)

def create_schema_table():
    create_table_query = '''CREATE TABLE IF NOT EXISTS Schema (
                                id INTEGER PRIMARY KEY,
                                id_osm INTEGER NOT NULL,
                                ame_d TEXT, 
                                sens_d TEXT, 
                                ame_g TEXT, 
                                sens_g TEXT, 
                                longueur REAL,
                                feature BLOB);'''
    cursor.execute(create_table_query)

def add_schema_entry(id_osm, ame_d, sens_d, ame_g, sens_g, longueur, feature):
    cursor.execute("INSERT INTO Schema VALUES (NULL, ?, ?, ?, ?, ?, ?, ?)",
                   (id_osm, ame_d, sens_d, ame_g, sens_g, longueur, feature))


def drop_stats_table():
    drop_table_query = '''DROP TABLE IF EXISTS Stats;'''
    cursor.execute(drop_table_query)

def create_stats_table():
    create_table_query = '''CREATE TABLE IF NOT EXISTS Stats (
                                id INTEGER PRIMARY KEY,
                                ame TEXT,
                                nb_unid INTEGER, 
                                m_unid REAL, 
                                nb_unig INTEGER, 
                                m_unig REAL, 
                                nb_bid INTEGER, 
                                m_bid REAL, 
                                nb_big INTEGER, 
                                m_big REAL, 
                                nb INTEGER, 
                                km REAL, 
                                kmc REAL);'''
    cursor.execute(create_table_query)

def add_stats_entry(ame, nb_unid, m_unid, nb_unig, m_unig, nb_bid, m_bid, nb_big, m_big, nb, km, kmc):
    cursor.execute("INSERT INTO Stats VALUES (NULL, ?, ?, ?, ?, ?, ?, ?, ?, ? ,?, ?, ?)",
                   (ame, nb_unid, m_unid, nb_unig, m_unig, nb_bid, m_bid, nb_big, m_big, nb, km, kmc))



# ===================================================== creation de la base Amecycl

amecycl_database = sqlite3.connect(amecycl_db_name)

cursor = amecycl_database.cursor()

# ===================================================== creation et alimentation de la table schema

# Suppression de la table Schema si elle existe
drop_schema_table()

# Creation de la table Schema
create_schema_table()

with open(ame_file) as json_data:
    data_dict = json.load(json_data)
    for feature in data_dict['features']:
        longueur = calculate_distance(feature, Unit.meters)
        # formattage 2 digits apres la virgule
        longueur = format(longueur, '.2f')
        # ajout de la longueur aux proprietes
        feature['properties']['longueur'] = longueur
        # suppression de la propriete geom si elle existe
        if ('geom' in feature['properties']):
            del feature['properties']['geom']
        # filtrage des proprietes. on ecarte les proprietes qui commencent par '_'
        fprop = {}
        for key, value in feature['properties'].items():
            if not underscored(key):
                fprop[key] = value
        # tri des proprietes sur la clé
        sfprop = {}
        for elem in sorted(fprop.items()):
            sfprop[elem[0]] = elem[1]

        # sauvegarde de la couche au format geojson
        fdic = {"type": "Feature", "geometry": feature['geometry'], "properties": sfprop}
        json_string = json.dumps(fdic, separators=(',', ':'))

        add_schema_entry(
            feature['properties']['id_osm'],
            feature['properties']['ame_d'],
            feature['properties']['sens_d'],
            feature['properties']['ame_g'],
            feature['properties']['sens_g'],
            feature['properties']['longueur'],
            json_string
        )

    amecycl_database.commit()


# ===================================================== creation et alimentation de la table stats

# Suppression de la table stats si elle existe
drop_stats_table()

# Creation de la table stats
create_stats_table()

# Pour chacun des types d'aménagements on fait une extraction des features pour alimenter les statistiques

# selection des aménagements unidirectionnel à droite
select_unid_query = '''SELECT ame_d, COUNT(ame_d), SUM(longueur) FROM Schema 
                        WHERE sens_d = 'UNIDIRECTIONNEL'  
                        GROUP BY ame_d'''
cursor.execute(select_unid_query)
res_unid = cursor.fetchall()

# selection des aménagements bidirectionnel à droite
select_bid_query = '''SELECT ame_d, COUNT(ame_d), SUM(longueur) FROM Schema 
                        WHERE sens_d = 'BIDIRECTIONNEL'  
                        GROUP BY ame_d'''
cursor.execute(select_bid_query)
res_bid = cursor.fetchall()

# selection des aménagements unidirectionnel à gauche
select_unig_query = '''SELECT ame_g, COUNT(ame_g), SUM(longueur) FROM Schema 
                        WHERE sens_g = 'UNIDIRECTIONNEL'  
                        GROUP BY ame_g'''
cursor.execute(select_unig_query)
res_unig = cursor.fetchall()

# selection des aménagements bidirectionnel à gauche
select_big_query = '''SELECT ame_g, COUNT(ame_g), SUM(longueur) FROM Schema 
                        WHERE sens_g = 'BIDIRECTIONNEL'  
                        GROUP BY ame_g'''
cursor.execute(select_big_query)
res_big = cursor.fetchall()


# Insertion dans la table stats des statistiques
# liste des amenagements trouvés
ames = []

# droite unidirectionnel
unid = {}
if len(res_unid):
    for row in res_unid:
        ames.append(row[0])
        unid[row[0]] = {}
        unid[row[0]]['nb'] = row[1]
        unid[row[0]]['m'] = row[2]

# droite bidirectionnel
bid = {}
if len(res_bid):
    for row in res_bid:
        ames.append(row[0])
        bid[row[0]] = {}
        bid[row[0]]['nb'] = row[1]
        bid[row[0]]['m'] = row[2]

# gauche unidirectionnel
unig = {}
if len(res_unig):
    for row in res_unig:
        ames.append(row[0])
        unig[row[0]] = {}
        unig[row[0]]['nb'] = row[1]
        unig[row[0]]['m'] = row[2]

# gauche bidirectionnel
big = {}
if len(res_big):
    for row in res_big:
        ames.append(row[0])
        big[row[0]] = {}
        big[row[0]]['nb'] = row[1]
        big[row[0]]['m'] = row[2]

# type d'amenagements distincts
ames = list(set(ames))
ames.sort()

# controle des types - verification des labels ame_d et ame_g / schema de données
# en cas de non conformité on arrete le script et on rappelle la liste des labels attendus

errors = []
for ame in ames:
    if not ame in ame_list.keys():
        errors.append(ame)
        
if len(errors):
    for error in errors:
        print("{} : label erroné.".format(error))
    print("\nVoici la liste des labels attendus pour décrire le type d'aménagement (ame_d ou ame_g) : \n")
    for key in ame_list.keys():
        print(key)
    print("\nSortie du script en erreur! - Veuillez corriger le fichier {}".format(ame_file))
    quit()  # sortie du script - correction du fichier requise



if len(ames):
    # statistiques tous types d'aménagement confondus
    nbt = 0
    kmt = 0.
    kmct = 0.

    for ame in ames:

        nb_unid = unid[ame]['nb'] if ame in unid.keys() else 0
        m_unid = unid[ame]['m'] if ame in unid.keys() else 0

        nb_bid = bid[ame]['nb'] if ame in bid.keys() else 0
        m_bid = bid[ame]['m'] if ame in bid.keys() else 0

        nb_unig = unig[ame]['nb'] if ame in unig.keys() else 0
        m_unig = unig[ame]['m'] if ame in unig.keys() else 0

        nb_big = big[ame]['nb'] if ame in big.keys() else 0
        m_big = big[ame]['m'] if ame in big.keys() else 0

        nb = nb_unid + nb_bid + nb_unig + nb_big # nombre de ways osm

        if ame_list[ame][1] < 1:
            kmc = (m_unid + m_unig + m_bid + m_big) / 1000  # linéaire cyclable en km
            km = kmc / 2   # longueur de la voie
        else:
            km = (m_unid + m_unig + m_bid + m_big) / 1000  # linéaire cyclable en km
            kmc = (m_unid + (2 * m_bid) + m_unig + (2 * m_big)) / 1000     # longueur de la voie

        add_stats_entry(ame, nb_unid, m_unid, nb_unig, m_unig, nb_bid, m_bid, nb_big, m_big, nb, km, kmc)

        nbt = nbt + nb
        kmt = kmt + km
        kmct = kmct + kmc

amecycl_database.commit()

# ===================================================== creation des couches (fichiers .geojson)

# Selection des aménagements non vides à droite - peu importe ce qu'il y a à gauche
selectd_query = '''SELECT ame_d, feature FROM Schema 
                        WHERE ame_d <> 'AUCUN'  
                        ORDER BY ame_d ASC'''
cursor.execute(selectd_query)
resd = cursor.fetchall()

# Selection des aménagements non vides à gauche et vide à droite
selectg_query = '''SELECT ame_g, feature FROM Schema 
                        WHERE (ame_g <> 'AUCUN') AND (ame_d = 'AUCUN') 
                        ORDER BY ame_g ASC'''
cursor.execute(selectg_query)
resg = cursor.fetchall()

# Selection des aménagements vide à droite et vide à gauche
selectdg_query = '''SELECT ame_g, feature FROM Schema 
                        WHERE (ame_d = 'AUCUN') AND (ame_g = 'AUCUN') 
                        ORDER BY ame_d ASC'''
cursor.execute(selectdg_query)
resdg = cursor.fetchall()

layers = {}
for row in resd:
    if not row[0] in layers.keys():
        layers[row[0]] = []
    layers[row[0]].append(row[1])

for row in resg:
    if not row[0] in layers.keys():
        layers[row[0]] = []
    layers[row[0]].append(row[1])

for row in resdg:
    if not row[0] in layers.keys():
        layers[row[0]] = []
    layers[row[0]].append(row[1])


if len(layers.keys()):
    # creation du repertoire des calques résultats si il n'existe pas
    if not os.path.exists(amecycl_layers_dir):
        os.makedirs(amecycl_layers_dir)
    header = '{"type":"FeatureCollection","name":"%s","features":['
    footer = ']}'
    
    nbc = 0 # nbre de calques

    for key in sorted(layers.keys()):
        headertype = header % (key)
        linefeature = []
        nbf = 0 # nbre de features du calque
        for feature in layers[key]:
            linefeature.append(feature)
            nbf = nbf + 1
        content = headertype + ','.join(linefeature) + footer

        file_ext = '-' + ame_list[key][0]
        pathname, extension = os.path.splitext(ame_file)
        filenames = pathname.split('/')
        filename = filenames[-1] + file_ext + '.geojson'

        print('{} - {} features'.format(filename,nbf))
        
        nbc = nbc + 1

        with open(amecycl_layers_dir + '/' + filename, 'w', encoding='utf-8') as f:
            f.write(content)
            f.write('\n')
    
    print ('\n{} calque(s) amenagement(s) cyclables créés'.format(nbc))

# Suppression de la table Schema de la base
drop_schema_table()

cursor.close()

end = time.time()
elapsed = end - start
elapsed = format(elapsed, '.3f')

print("\nTemps d'exécution: {} secondes.".format(elapsed))

