# schema-org-graph

[![Build Status](https://travis-ci.com/Wikia/schema-org-graph.svg?branch=master)](https://travis-ci.com/Wikia/schema-org-graph)

Map articles metadata and relationship to [schema.org entities](https://schema.org/) and stores them in [RedisGraph database](https://oss.redislabs.com/redisgraph/).

## Demo

* [Midfielders in Premier League](https://wikia.github.io/schema-org-graph/football.html) (with transfers)
* [German players in Premier League](https://wikia.github.io/schema-org-graph/germany.html) (with transfers)
* [Liverpool's current squad](https://wikia.github.io/schema-org-graph/squad.html)
* [Liverpool's squad from 2017](https://wikia.github.io/schema-org-graph/squad_history.html)

## Data

![midfielders](https://user-images.githubusercontent.com/1929317/51246867-b8051480-198b-11e9-91ad-d33e3bbc12de.png)

This repository contains structured data for **3133 football teams** and **4760 football players** (with focus on Premier League and Serie A). [Football Wiki](http://football.wikia.com) infoboxes (and other templates) were used as a source.

### Nodes

We store basic information about each player and manager (birth date, nationality, height) and team (league membership, foundation year, stadium) as nodes. Both types of nodes - [`Person`](https://schema.org/Person) (a player or a manager) and [`SportsTeam`](https://schema.org/SportsTeam) - are connected with relations. A person can be a `coach` or an `athlete` for the club.

### Relations

* player career is described as `[:athlete]` relation (with `since` and `until` properties) with `SportsTeam` node.
* team's current squad is described as `[:athlete]` relation with `Person` node. Player position on the field and number is stored in relation's properies.

```
2019-01-09 12:50:59 RedisGraph                INFO     Committing graph with 7893 nodes and 18398 edges
```

## How data was collected?

> See `FootballWikiSource` Python class for implementation details.

`mwclient` Python module was used to get a list of articles from provided categories - players and teams. For each article we queried our [custom API that returnes a list of all templates](http://football.wikia.com/api/v1/Templates/Metadata?title=Zlatan%20Ibrahimović) (with parameters passed) that were used in a given article.

We assumed the following:

* `Infobox Biography` template describes a person (either a player or a manager, or even both)
* `Infobox Club` template described a team
* `Fs player` template is used to connect teams with players (i.e. set up a relation for the current team squad)

As we parse the list of parameters passed to templates we assume that:

* parameters with links form a relation (e.g. player played in this club, club has this person as a manager)
* parameters with plain values are source of data for properties (club foundation year, birth date, player's height)

We model collected data using [schema.org](https://schema.org/Person) types and properties. Each model is then represented as a node in graph database, while relation is an edge.

This approach will later on allow us to expose structured data and links between entities in HTML of rendered wiki articles.

## Run it

```
docker-compose up
```

[`redisgraph`](https://oss.redislabs.com/redisgraph/) binds to a local port `56379`:

```
redis-cli -p 56379
```

## Repository structure

* `grapher` is a Python 3.x project used to collect structured data from Football Wiki. Please set up virtual env and run `index_football_wiki` script there.
* Alternatively, tou can take graph dump stored in [`grapher/output/football.graph`](https://github.com/Wikia/schema-org-graph/tree/master/grapher/output) file and load it into RedisGraph instance.


## Some stats

```
127.0.0.1:56379> GRAPH.QUERY football "MATCH (t:SportsTeam)  RETURN count(t) AS teams"
1) 1) 1) "teams"
   2) 1) "3133.000000"
2) 1) "Query internal execution time: 2.656609 milliseconds"
127.0.0.1:56379> GRAPH.QUERY football "MATCH (p:Person)  RETURN count(p) as players"
1) 1) 1) "players"
   2) 1) "4760.000000"
2) 1) "Query internal execution time: 3.306746 milliseconds"
```

## Example models

```
<PersonModel https://schema.org/Person (Ole_Gunnar_Solskjr:Person) name = "Ole Gunnar Solskjær", birthDate = "1973", birthPlace = "Kristiansund", nationality = "Norway", height = "1.78">
    --[:athlete {"until": 1994, "since": 1990}]->(Clausenengen_FK:SportsTeam)
    --[:athlete {"until": 1996, "since": 1994}]->(Molde_FK:SportsTeam)
    --[:athlete {"until": 2007, "since": 1996}]->(Manchester_United_F_C:SportsTeam)
    --[:coach {"until": 2011, "since": 2008}]->(Manchester_United_F_C_Reserves_and_Academy:SportsTeam)
    --[:coach {"until": 2014, "since": 2011}]->(Molde_FK:SportsTeam)
    --[:coach {"until": 2014, "since": 2014}]->(Cardiff_City_F_C:SportsTeam)
    --[:coach {"until": 2016, "since": 2014}]->(Clausenengen_FK:SportsTeam)
    --[:coach {"until": 2018, "since": 2015}]->(Molde_FK:SportsTeam)
    --[:coach {"until": 2019, "since": 2018}]->(Manchester_United_F_C:SportsTeam)
```

```
<PersonModel https://schema.org/Person (Zlatan_Ibrahimovi:Person) name = "Zlatan Ibrahimović", birthDate = "1981", birthPlace = "Malmö", nationality = "Sweden", height = "1.95">
	--[:athlete {"until": 2001, "since": 1999}]->(Malm_FF:SportsTeam)
	--[:athlete {"until": 2004, "since": 2001}]->(AFC_Ajax:SportsTeam)
	--[:athlete {"until": 2006, "since": 2004}]->(Juventus_F_C:SportsTeam)
	--[:athlete {"until": 2009, "since": 2006}]->(Inter_Milan:SportsTeam)
	--[:athlete {"until": 2011, "since": 2009}]->(FC_Barcelona:SportsTeam)
	--[:athlete {"until": 2011, "since": 2010}]->(A_C_Milan:SportsTeam)
	--[:athlete {"until": 2012, "since": 2011}]->(A_C_Milan:SportsTeam)
	--[:athlete {"until": 2016, "since": 2012}]->(Paris_Saint_Germain_F_C:SportsTeam)
	--[:athlete {"until": 2018, "since": 2016}]->(Manchester_United:SportsTeam)
	--[:athlete {"until": 2018, "since": 2017}]->(Manchester_United:SportsTeam)
	--[:athlete {"until": null, "since": 2018}]->(LA_Galaxy:SportsTeam)
```

```
<SportsTeamModel https://schema.org/SportsTeam (Manchester_United_F_C:SportsTeam) name = "Manchester United F.C.", sport = "Football", foundingDate = "1878", ground = "Old Trafford", memberOf = "Premier League", url = "http://www.manutd.com/">
	--[:coach ]->(Ole_Gunnar_Solskjr:Person)
	--[:athlete {"number": 1, "position": "GK"}]->(David_de_Gea:Person)
	--[:athlete {"number": 2, "position": "DF"}]->(Victor_Lindelf:Person)
	--[:athlete {"number": 3, "position": "DF"}]->(Eric_Bailly:Person)
	--[:athlete {"number": 4, "position": "DF"}]->(Phil_Jones_born_1992:Person)
	--[:athlete {"number": 6, "position": "MF"}]->(Paul_Pogba:Person)
	--[:athlete {"number": 7, "position": "FW"}]->(Alexis_Snchez:Person)
	--[:athlete {"number": 8, "position": "MF"}]->(Juan_Mata:Person)
	--[:athlete {"number": 9, "position": "FW"}]->(Romelu_Lukaku:Person)
	--[:athlete {"number": 10, "position": "FW"}]->(Marcus_Rashford:Person)
	--[:athlete {"number": 11, "position": "FW"}]->(Anthony_Martial:Person)
	--[:athlete {"number": 12, "position": "DF"}]->(Chris_Smalling:Person)
	--[:athlete {"number": 13, "position": "GK"}]->(Lee_Grant_born_1983:Person)
	--[:athlete {"number": 14, "position": "MF"}]->(Jesse_Lingard:Person)
	--[:athlete {"number": 15, "position": "MF"}]->(Andreas_Pereira:Person)
	--[:athlete {"number": 16, "position": "DF"}]->(Marcos_Rojo:Person)
	--[:athlete {"number": 17, "position": "MF"}]->(Fred_born_1993:Person)
	--[:athlete {"number": 18, "position": "DF"}]->(Ashley_Young:Person)
	--[:athlete {"number": 20, "position": "DF"}]->(Diogo_Dalot:Person)
	--[:athlete {"number": 21, "position": "MF"}]->(Ander_Herrera:Person)
	--[:athlete {"number": 22, "position": "GK"}]->(Sergio_Romero:Person)
	--[:athlete {"number": 23, "position": "DF"}]->(Luke_Shaw:Person)
	--[:athlete {"number": 25, "position": "DF"}]->(Antonio_Valencia:Person)
	--[:athlete {"number": 27, "position": "MF"}]->(Marouane_Fellaini:Person)
	--[:athlete {"number": 31, "position": "MF"}]->(Nemanja_Mati:Person)
	--[:athlete {"number": 36, "position": "DF"}]->(Matteo_Darmian:Person)
	--[:athlete {"number": 39, "position": "MF"}]->(Scott_McTominay:Person)
	--[:athlete {"number": 24, "position": "DF"}]->(Timothy_Fosu_Mensah:Person)
	--[:athlete {"number": 38, "position": "DF"}]->(Axel_Tuanzebe:Person)
	--[:athlete {"number": 40, "position": "GK"}]->(Joel_Castro_Pereira:Person)
```

## Example queries

> Use `make redis` to access redis-cli and perform queries.

### Football players from Iceland playing in Premier League clubs

```
127.0.0.1:56379> GRAPH.QUERY football "MATCH (t:SportsTeam)<-[a:athlete]-(p:Person) WHERE t.memberOf = 'Premier League' AND p.nationality = 'Iceland' RETURN t.name,p.name,a.since,a.until"
1) 1) 1) "t.name"
      2) "p.name"
      3) "a.since"
      4) "a.until"
   2) 1) "Arsenal F.C."
      2) "\xc3\x93lafur Ingi Sk\xc3\xbalason"
      3) "2001.000000"
      4) "2005.000000"
   3) 1) "Tottenham Hotspur F.C."
      2) "Gylfi \xc3\x9e\xc3\xb3r Sigur\xc3\xb0sson"
      3) "2012.000000"
      4) "2014.000000"
   4) 1) "Everton F.C."
      2) "Gylfi \xc3\x9e\xc3\xb3r Sigur\xc3\xb0sson"
      3) "2017.000000"
      4) "NULL"
   5) 1) "Burnley F.C."
      2) "J\xc3\xb3hann Berg Gu\xc3\xb0mundsson"
      3) "2016.000000"
      4) "NULL"
2) 1) "Query internal execution time: 11.935366 milliseconds"
```

### A single player clubs history

```
127.0.0.1:56379>  GRAPH.QUERY football "MATCH (t:SportsTeam)<-[a:athlete]-(p:Person) WHERE p.name = 'Łukasz Fabiański' RETURN t.name,a.since,a.until"
1) 1) 1) "t.name"
      2) "a.since"
      3) "a.until"
   2) 1) "West Ham United F.C."
      2) "2018.000000"
      3) "NULL"
   3) 1) "Swansea_City_A_F_C"
      2) "2014.000000"
      3) "2018.000000"
   4) 1) "Arsenal F.C."
      2) "2007.000000"
      3) "2014.000000"
   5) 1) "Legia_Warsaw"
      2) "2005.000000"
      3) "2007.000000"
```

### Who played in both Manchester United and Liverpool

```
127.0.0.1:56379> GRAPH.QUERY football "MATCH (t:SportsTeam)<-[:athlete]-(c:Person)-[:athlete]->(t2:SportsTeam) WHERE t.name = 'Liverpool F.C.' and t2.name = 'Manchester United F.C.'  RETURN c.name,t.name,t2.name"
1) 1) 1) "c.name"
      2) "t.name"
      3) "t2.name"
   2) 1) "Peter Andrew Beardsley"
      2) "Liverpool F.C."
      3) "Manchester United F.C."
   3) 1) "Paul Emerson Carlyle Ince"
      2) "Liverpool F.C."
      3) "Manchester United F.C."
   4) 1) "Michael James Owen"
      2) "Liverpool F.C."
      3) "Manchester United F.C."
```

### Midfielders from Germany currently playing in Premier League

```
127.0.0.1:56379> GRAPH.QUERY football "MATCH (t:SportsTeam)-[a:athlete]->(p:Person) WHERE t.memberOf = 'Premier League' AND a.position = 'MF' AND p.nationality = 'Germany' RETURN t.name,p.name,a.number"
1) 1) 1) "t.name"
      2) "p.name"
      3) "a.number"
   2) 1) "Arsenal F.C."
      2) "Mesut \xc3\x96zil"
      3) "10.000000"
   3) 1) "Manchester City F.C."
      2) "\xc4\xb0lkay G\xc3\xbcndo\xc4\x9fan"
      3) "8.000000"
   4) 1) "Manchester City F.C."
      2) "Leroy San\xc3\xa9"
      3) "19.000000"
   5) 1) "Crystal Palace F.C."
      2) "Jeffrey Schlupp"
      3) "15.000000"
   6) 1) "Everton F.C."
      2) "Muhamed Be\xc5\xa1i\xc4\x87"
      3) "21.000000"
2) 1) "Query internal execution time: 4.901690 milliseconds"
```
