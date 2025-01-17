# Projet 1 - INF8810

## Auteur
Dominique Elias (*ELID14019800*)


## Partie 1 - Préparation des données

### 1.1 - Téléchargement des données

- Origine des données : les données proviennent de [Statistique Canada](https://www150.statcan.gc.ca/t1/tbl1/en/tv.action?pid=3310003601)
- Lien de téléchargement : Les données sont téléchargeables [ici](https://www150.statcan.gc.ca/n1/tbl/csv/33100036-eng.zip)
- Contexte du jeu de donnée : Ce jeu de données, intitulé "Daily average foreign exchange rates in Canadian dollars, Bank of Canada", présente les taux de change moyens quotidiens des devises étrangères exprimés en dollars canadiens (CAD), fournis par la Banque du Canada. Il inclut les taux de conversion pour différentes devises (par exemple, dollar américain (USD), euro (EUR), livre sterling (GBP), etc.).

Voici les étapes préliminaires avant de lancer les scripts Hadoop et Spark :

**N.B. Toutes les commandes doivent être exécutées dans la racine du projet. Assurez-vous d'avoir installé les [dépendances nécessaires](#dépendances) avant de lancer les scripts.**

Télécharger les données :

```bash
wget https://www150.statcan.gc.ca/n1/tbl/csv/33100036-eng.zip
```

Ensuite, il faut dézipper les données :

```bash
unzip 33100036-eng.zip -d 33100036-eng && rm 33100036-eng.zip
```

Voici un example de l'arborescence des fichiers :

```bash
$ tree
.
├── 33100036-eng
│   ├── 33100036.csv
│   └── 33100036_MetaData.csv
├── README.md
├── hadoop
│   ├── mapper.py
│   └── reducer.py
├── pretreatment.py
├── run-hadoop.sh
└── spark
    └── spark-run.py
```

### 1.2 - Prétraitement des données

Pour prétraiter les données, il suffit de lancer le script `pretreatment.py` : (avec `panda`)

```bash
python3 pretreatment.py
```

Le script va générer un fichier `33100036-eng/33100036-treated.csv` qui contient les données prétraitées.
Ce fichier est utilisé par les scripts Hadoop et Spark.

## Partie 2 - Hadoop

### 2.1 - Objectif

- L'objectif de ce traitement MapReduce est de calculer la moyenne **annuelle** du Canadian-Dollar Effective Exchange Rate Index (CERI) sur la période de données disponible. Le CERI mesure la valeur relative du dollar canadien (CAD) par rapport à un panier de devises étrangères. Ce traitement est utile pour analyser l'évolution annuelle du taux de change effectif du CAD par rapport à ses principaux partenaires commerciaux, ce qui peut aider à comprendre l'influence des fluctuations des taux de change sur l'économie canadienne.

### 2.2 - Étapes du traitement Hadoop

1. Mapper : Le mapper extrait les données du fichier CSV, en filtrant les lignes pour obtenir uniquement les valeurs du CERI. Il émet des clés (année) et des valeurs (CERI) pour chaque ligne.

2. Reducer : Le reducer agrège les valeurs du CERI pour chaque année, puis calcule la moyenne annuelle du CERI. Il émet des clés (année) et des valeurs (moyenne CERI) pour chaque année.

### 2.3 - Implémentation et Exécution hors de Hadoop

Il suffit de lancer la commande suivante :

```bash
cat 33100036-eng/33100036-treated.csv | python3 hadoop/mapper.py | python3 hadoop/reducer.py | tee hadoop/output
```

Cette command va afficher les résultats dans le terminal et les sauvegarder dans le fichier `hadoop/output`.

### 2.4 - Exécution du Traitement Hadoop

l'environnement Hadoop utilisé est un cluster Hadoop avec Docker. Voici un script bash qui simplifie le lancement du traitement Hadoop :

```bash
chmod +x run-hadoop.sh
sudo ./run-hadoop.sh
```

*`sudo` est nécessaire pour lancer les commandes docker*

Ca peut prendre quelques minutes pour l'execution et le traitement Hadoop. Les résultats seront disponibles dans le fichier `hadoop/part-00000` après l'exécution.
Ils seront également affichés dans le terminal.


### 2.5 - Résultats

Voici un exemple de résultats du traitement Hadoop :

```bash
tail -n 5 hadoop/part-00000
```

```bash
2009    106.0805
2010    116.9674
2011    120.2756
2012    120.0413
2013    117.2023
2014    109.7815
2015    98.0247
2016    95.0069
2017    97.1870
2018    100.1260
```

Les résultats en dessus de 100 indique une appréciation du CAD par rapport aux devises étrangères, tandis que les valeurs en dessous de 100 indiquent une dépréciation.

## Partie 3 - Spark

### 3.1 - Objectif

- L'objectif principal du traitement Spark est d'analyser l'évolution des taux de change mensuels entre le dollar américain (USD), l'EURO (EUR) et le dollar canadien (CAD) pendant la période COVID-19 (mars 2020 à juin 2021). Ce traitement permet de calculer la moyenne mensuelle des taux de change et la variation en pourcentage mois par mois.

- Ce traitement est utile pour observer l'impact de la pandémie sur la force relative de l'USD et l'EUR par rapport au CAD, en fournissant des données sur les fluctuations mensuelles. Les résultats peuvent aider à identifier des tendances économiques et des périodes de volatilité dans les marchés des changes.

### 3.2 - Étapes du traitement Spark

1. Initialisation et Chargement des Données : Création d'une session Spark et chargement des données CSV traitées dans un DataFrame Spark. Les colonnes de données sont définies avec leur schéma, et la colonne date est convertie en type DateType pour faciliter le filtrage par date

2. Filtrage pour la Période COVID-19 et le USD : Filtrage des données pour obtenir uniquement les taux d’échange USD/CAD quotidiens entre mars 2020 et juin 2021.

3. Calcul de la Moyenne Mensuelle : Les données sont regroupées par mois, et la moyenne des taux de change est calculée pour chaque mois. Ce regroupement donne une vue simplifiée des tendances mensuelles

4. Calcul de la Variation Mensuelle en Pourcentage : À l'aide de la fonction lag, la variation en pourcentage entre chaque mois et le mois précédent est calculée. Cette étape montre l’évolution du taux USD/CAD de manière relative d'un mois à l'autre, permettant de détecter des pics ou des baisses importantes

5. Faire le même traitement pour l'EUR : Les étapes 2 à 4 sont répétées pour les taux de change EUR/CAD, permettant de comparer les tendances du taux de change de l'EUR avec celles du CAD

6. Fusionner les Résultats : Les résultats des taux de change USD/CAD et EUR/CAD sont fusionnés en un seul DataFrame pour une comparaison directe des moyennes mensuelles et des variations en pourcentage

### 3.3 - Exécution du Traitement Spark

Il faut lancer cette commande dans la racine du projet :

```bash
sudo docker run -v $(pwd):/app -w /app apache/spark /opt/spark/bin/spark-submit spark/spark-run.py
```

### 3.4 - Résultats

Tableau des moyennes mensuelles et des variations en pourcentage des taux de change USD/CAD et EUR/CAD pendant la période COVID-19 :

|  Month  | Average_USD_Monthly | Monthly_USD_Percent_Change | Average_EUR_Monthly | Monthly_EUR_Percent_Change |
|---------|---------------------|----------------------------|---------------------|----------------------------|
| 2020-03 | 1.3952              | 0.0000                     | 1.5417              | 0.0000                     |
| 2020-04 | 1.4058              | 0.7551                     | 1.5276              | -0.9153                    |
| 2020-05 | 1.3970              | -0.6271                    | 1.5236              | -0.2564                    |
| 2020-06 | 1.3550              | -3.0021                    | 1.5257              | 0.1319                     |
| 2020-07 | 1.3498              | -0.3824                    | 1.5499              | 1.5904                     |
| 2020-08 | 1.3222              | -2.0480                    | 1.5646              | 0.9505                     |
| 2020-09 | 1.3228              | 0.0457                     | 1.5591              | -0.3538                    |
| 2020-10 | 1.3215              | -0.1012                    | 1.5553              | -0.2462                    |
| 2020-11 | 1.3068              | -1.1087                    | 1.5471              | -0.5273                    |
| 2020-12 | 1.2808              | -1.9933                    | 1.5586              | 0.7422                     |
| 2021-01 | 1.2724              | -0.6532                    | 1.5484              | -0.6485                    |
| 2021-02 | 1.2699              | -0.2002                    | 1.5356              | -0.8312                    |
| 2021-03 | 1.2574              | -0.9831                    | 1.4962              | -2.5616                    |
| 2021-04 | 1.2496              | -0.6190                    | 1.4963              | 0.0044                     |
| 2021-05 | 1.2126              | -2.9566                    | 1.4729              | -1.5658                    |
| 2021-06 | 1.2219              | 0.7602                     | 1.4719              | -0.0690                    |

## Dépendances

- python3
- pandas `sudo apt-get install python3-pandas`
- docker
- docker-compose `sudo apt-get install docker-compose`
