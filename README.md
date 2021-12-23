# Script Python PyAmecycl [![](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)

Script python pour traiter les fichiers conformes au **schéma de données des aménagements cyclables**

Le script calcule la longueur et le linéaire par type d'aménagements. 
Ces données peuvent ensuite être consultées un client SQLite tel que [SQLiteBrowser](https://sqlitebrowser.org/)

Il produit les calques au format .geojson de chaque type d'aménagement. Ces calques peuvent être réutilisés pour produire une carte uMap.

Le fichier doit être conforme à la version **0.3.3** du schéma de données des aménagements cyclables 

Pour le détail du schéma de données voir : 
* https://schema.data.gouv.fr/etalab/schema-amenagements-cyclables/ 
* https://github.com/etalab/amenagements-cyclables



## Installation du script PyAmecycl :

- ouvrez une fenetre de commandes et ajouter le package python [geojson-length](https://pypi.org/project/geojson-length/) en tapant la commande suivante: pip install geojson-length

- dézipper le fichier PyAmecycl.zip dans un repertoire quelconque



## Utilisation du script PyAmecycl :

- via la fenêtre de commandes, positionnez vous dans le répertoire PyAmecycl qui contient le script **amecycl-calc.py**

- taper la commande : **python amecycl-calc.py epci.geojson** où epci.geojson est le fichier des aménagements cyclables à traiter



## Plus d'informations (en Français) :

[Amecycl – Script Python et création d’une carte uMap](https://randovelo.touteslatitudes.fr/pyamecycl-script-python/)

[Amecycl – Dessine moi les aménagements cyclables de ma ville … ](https://randovelo.touteslatitudes.fr/amecycl/)

