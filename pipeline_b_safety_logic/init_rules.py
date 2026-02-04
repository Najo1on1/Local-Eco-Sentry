from neo4j import GraphDatabase

# CONNECTION SETTINGS
URI = "bolt://localhost:7687"
AUTH = ("neo4j", "password123")

def load_rules():
    driver = GraphDatabase.driver(URI, auth=AUTH)
    print("🔌 Connecting to Safety Graph...")

    query = """
    // 1. Clear old data (Start Fresh)
    MATCH (n) DETACH DELETE n;

    // 2. Create Hazards
    CREATE (f:Hazard {name: 'Fire', severity: 'CRITICAL'});
    CREATE (s:Hazard {name: 'Spill', severity: 'MODERATE'});
    CREATE (i:Hazard {name: 'Intruder', severity: 'HIGH'});

    // 3. Create Protocols
    CREATE (p1:Protocol {action: 'TRIGGER_EVACUATION', code: 'RED-1'});
    CREATE (p2:Protocol {action: 'DEPLOY_CLEANUP_BOT', code: 'AMBER-2'});
    CREATE (p3:Protocol {action: 'ALERT_SECURITY', code: 'RED-2'});

    // 4. Link them (The Logic)
    MERGE (f)-[:REQUIRES_ACTION]->(p1);
    MERGE (s)-[:REQUIRES_ACTION]->(p2);
    MERGE (i)-[:REQUIRES_ACTION]->(p3);
    """

    with driver.session() as session:
        # We split the query by semicolons to run multiple commands
        for command in query.split(';'):
            if command.strip():
                session.run(command)

    print("✅ Safety Rules Ingested Successfully!")
    print("   (Fire) --> (Evacuate)")
    print("   (Spill) --> (Cleanup)")
    driver.close()

if __name__ == "__main__":
    load_rules()