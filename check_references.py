import csv

def load_csv(filename):
    with open(filename) as f:
        csvreader = csv.reader(f, delimiter=',', quotechar='"')
        rows = [row for row in csvreader]
    return rows

def load_grounding_map(filename):
    gm_rows = load_csv(filename)
    g_map = {}
    for row in gm_rows:
        key = row[0]
        db_refs = {'TEXT': key}
        keys = [entry for entry in row[1::2] if entry != '']
        values = [entry for entry in row[2::2] if entry != '']
        if len(keys) != len(values):
            print 'ERROR: Mismatched keys and values in row %s' % str(row)
            continue
        else:
            db_refs.update(dict(zip(keys, values)))
            if len(db_refs.keys()) > 1:
                g_map[key] = db_refs
            else:
                g_map[key] = None
    return g_map

def load_entity_list(filename):
    with open(filename) as f:
        csvreader = csv.reader(f, delimiter=',', quotechar='"')
        entities = [row[0] for row in csvreader]
    return entities

def load_relationships(filename):
    relationships = []
    with open(filename) as f:
        csvreader = csv.reader(f, delimiter=',', quotechar='"')
        for row in csvreader:
            relationships.append(((row[0], row[1]), row[2], (row[3], row[4])))
    return relationships

def update_id_prefixes(filename):
    gm_rows = load_csv(filename)
    updated_rows = []
    for row in gm_rows:
        key = row[0]
        keys = [entry for entry in row[1::2]]
        values = [entry for entry in row[2::2]]
        if 'GO' in keys:
            go_ix = keys.index('GO')
            values[go_ix] = 'GO:%s' % values[go_ix]
        if 'CHEBI' in keys:
            chebi_ix = keys.index('CHEBI')
            values[chebi_ix] = 'CHEBI:%s' % values[chebi_ix]
        if 'CHEMBL' in keys:
            chembl_ix = keys.index('CHEMBL')
            values[chembl_ix] = 'CHEMBL%s' % values[chembl_ix]
        updated_row = [key]
        for pair in zip(keys, values):
            updated_row += pair
        updated_rows.append(updated_row)
    return updated_rows

if __name__ == '__main__':
    # Check the entity list for duplicates
    entities = load_entity_list('entities.csv')
    if len(entities) != len(set(entities)):
        print "ERROR: Duplicate entities in entity list."

    # Load the grounding map
    gm = load_grounding_map('grounding_map.csv')
    # Look through grounding map and find all instances with an 'INDRA' db
    indra_ids = []
    for text, db_refs in gm.items():
        if db_refs is not None:
            for db_key, db_id in db_refs.items():
                if db_key == 'INDRA' and db_id not in entities:
                    print "ERROR: ID %s referenced in grounding map " \
                          "is not in entities list." % db_id

    # Load the relationships
    relationships = load_relationships('relations.csv')
    # Check the relationships for consistency with entities
    for subj, rel, obj in relationships:
        for term in (subj, obj):
            term_ns = term[0]
            term_id = term[1]
            if term_ns == 'INDRA' and term_id not in entities:
                print "ERROR: ID %s referenced in relations " \
                      "is not in entities list." % term_id
