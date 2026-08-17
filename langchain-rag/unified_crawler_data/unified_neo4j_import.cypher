MATCH (n) DETACH DELETE n;

CREATE CONSTRAINT artist_name_unique IF NOT EXISTS FOR (n:Artist) REQUIRE n.name IS UNIQUE;

CREATE CONSTRAINT museum_name_unique IF NOT EXISTS FOR (n:Museum) REQUIRE n.name IS UNIQUE;

CREATE CONSTRAINT artwork_name_unique IF NOT EXISTS FOR (n:Artwork) REQUIRE n.name IS UNIQUE;

CREATE (:Artwork {title: "Person: Charles Dickens", description: "Dickens, Charles", creation_date: "1812", medium: "", genre: "", subject_matter: [], current_location: "Harvard Art Museums", cultural_significance: "Dickens, Charles", provenance: ["Harvard Art Museums"], source_url: "https://www.harvardartmuseums.org/collections/person/2", external_id: "2", language: "", rights: ""});

CREATE (:Artist {name: "Charles Dickens", full_name: "Charles Dickens", biography: "Artist mentioned in Harvard Art Museums", notable_works: ["Person: Charles Dickens"], historical_significance: "Dickens, Charles", active_period: "1812", associated_locations: [""], source_references: ["https://www.harvardartmuseums.org/collections/person/2"]});

CREATE (:Museum {name: "Harvard Art Museums", full_name: "Harvard Art Museums", country: "United States", collection_focus: ["General collection"], notable_collections: ["Person: Charles Dickens"], website: "https://www.harvardartmuseums.org/collections/person/2", specialization: [""], source_data: "Europeana"});

CREATE (:Artwork {title: "Person: Aspasia Papanastasiou", description: "Papanastasiou, Aspasia", creation_date: "0-0", medium: "", genre: "", subject_matter: [], current_location: "Harvard Art Museums", cultural_significance: "Papanastasiou, Aspasia", provenance: ["Harvard Art Museums"], source_url: "https://www.harvardartmuseums.org/collections/person/5", external_id: "5", language: "", rights: ""});

CREATE (:Artist {name: "Aspasia Papanastasiou", full_name: "Aspasia Papanastasiou", biography: "Artist mentioned in Harvard Art Museums", notable_works: ["Person: Aspasia Papanastasiou"], historical_significance: "Papanastasiou, Aspasia", active_period: "0-0", associated_locations: [""], source_references: ["https://www.harvardartmuseums.org/collections/person/5"]});

CREATE (:Artwork {title: "Person: Aristotle University of Thessaloniki", description: "Aristotle University of Thessaloniki", creation_date: "0-0", medium: "", genre: "", subject_matter: [], current_location: "Harvard Art Museums", cultural_significance: "Aristotle University of Thessaloniki", provenance: ["Harvard Art Museums"], source_url: "https://www.harvardartmuseums.org/collections/person/6", external_id: "6", language: "", rights: ""});

CREATE (:Artist {name: "Aristotle University of Thessaloniki", full_name: "Aristotle University of Thessaloniki", biography: "Artist mentioned in Harvard Art Museums", notable_works: ["Person: Aristotle University of Thessaloniki"], historical_significance: "Aristotle University of Thessaloniki", active_period: "0-0", associated_locations: [""], source_references: ["https://www.harvardartmuseums.org/collections/person/6"]});

CREATE (:Artwork {title: "Person: Madison Art Center", description: "Madison Art Center", creation_date: "0-0", medium: "", genre: "", subject_matter: [], current_location: "Harvard Art Museums", cultural_significance: "Madison Art Center", provenance: ["Harvard Art Museums"], source_url: "https://www.harvardartmuseums.org/collections/person/7", external_id: "7", language: "", rights: ""});

CREATE (:Artist {name: "Madison Art Center", full_name: "Madison Art Center", biography: "Artist mentioned in Harvard Art Museums", notable_works: ["Person: Madison Art Center"], historical_significance: "Madison Art Center", active_period: "0-0", associated_locations: [""], source_references: ["https://www.harvardartmuseums.org/collections/person/7"]});

CREATE (:Artwork {title: "Person: University Gallery, University of Massachusetts", description: "University Gallery, University of Massachusetts", creation_date: "0-0", medium: "", genre: "", subject_matter: [], current_location: "Harvard Art Museums", cultural_significance: "University Gallery, University of Massachusetts", provenance: ["Harvard Art Museums"], source_url: "https://www.harvardartmuseums.org/collections/person/9", external_id: "9", language: "", rights: ""});

CREATE (:Artist {name: "University Gallery, University of Massachusetts", full_name: "University Gallery, University of Massachusetts", biography: "Artist mentioned in Harvard Art Museums", notable_works: ["Person: University Gallery, University of Massachusetts"], historical_significance: "University Gallery, University of Massachusetts", active_period: "0-0", associated_locations: [""], source_references: ["https://www.harvardartmuseums.org/collections/person/9"]});

CREATE (:Artwork {title: "Worlds within Worlds: The Rosenblum Collection of Chinese Scholar\\'s Rocks", creation_date: "1997", medium: "", genre: "Exhibition", subject_matter: [], current_location: "Harvard Art Museums", provenance: ["Harvard Art Museums"], source_url: "https://www.harvardartmuseums.org/visit/exhibitions/2", external_id: "2", language: "", rights: ""});

CREATE (:Artwork {title: "The American Line: 100 Years of Drawing", creation_date: "1959", medium: "", genre: "Exhibition", subject_matter: [], current_location: "Harvard Art Museums", provenance: ["Harvard Art Museums"], source_url: "https://www.harvardartmuseums.org/visit/exhibitions/3", external_id: "3", language: "", rights: ""});

CREATE (:Artwork {title: "George Grosz", creation_date: "1997", medium: "", genre: "Exhibition", subject_matter: [], current_location: "Harvard Art Museums", provenance: ["Harvard Art Museums"], source_url: "https://www.harvardartmuseums.org/visit/exhibitions/4", external_id: "4", language: "", rights: ""});

CREATE (:Artwork {title: "Vija Celmins - A Retrospective; Works 1964-1996", creation_date: "1996", medium: "", genre: "Exhibition", subject_matter: [], current_location: "Harvard Art Museums", provenance: ["Harvard Art Museums"], source_url: "https://www.harvardartmuseums.org/visit/exhibitions/5", external_id: "5", language: "", rights: ""});

CREATE (:Artwork {title: "Within the Atrium: A Context for Roman Daily Life", creation_date: "1997", medium: "", genre: "Exhibition", subject_matter: [], current_location: "Harvard Art Museums", provenance: ["Harvard Art Museums"], source_url: "https://www.harvardartmuseums.org/visit/exhibitions/6", external_id: "6", language: "", rights: ""});

MATCH (a {name: "Worlds within Worlds: The Rosenblum Collection of Chinese Scholar's Rocks"})
MATCH (b {name: "Harvard Art Museums"})
CREATE (a)-[:HOUSED_IN {collection_type: "Digital collection", access_type: "Online", source: "Europeana"}]->(b);

MATCH (a {name: "The American Line: 100 Years of Drawing"})
MATCH (b {name: "Harvard Art Museums"})
CREATE (a)-[:HOUSED_IN {collection_type: "Digital collection", access_type: "Online", source: "Europeana"}]->(b);

MATCH (a {name: "George Grosz"})
MATCH (b {name: "Harvard Art Museums"})
CREATE (a)-[:HOUSED_IN {collection_type: "Digital collection", access_type: "Online", source: "Europeana"}]->(b);

MATCH (a {name: "Vija Celmins - A Retrospective; Works 1964-1996"})
MATCH (b {name: "Harvard Art Museums"})
CREATE (a)-[:HOUSED_IN {collection_type: "Digital collection", access_type: "Online", source: "Europeana"}]->(b);

MATCH (a {name: "Within the Atrium: A Context for Roman Daily Life"})
MATCH (b {name: "Harvard Art Museums"})
CREATE (a)-[:HOUSED_IN {collection_type: "Digital collection", access_type: "Online", source: "Europeana"}]->(b);

