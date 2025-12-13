# TogoMCP Usage Guide

A step-by-step workflow for answering user questions using TogoMCP tools.

---

## Workflow Steps

### Step 1: Extract Keywords from User Question
- Identify key scientific terms, entities, or concepts
- Note specific IDs if mentioned (e.g., "P04637", "CID2244", "aspirin")
- Determine the domain: proteins, chemicals, diseases, genes, pathways, etc.

### Step 2: Select Appropriate Databases
Run `list_databases()` and choose relevant databases based on the question domain:

| Domain | Recommended Databases |
|--------|----------------------|
| Proteins | `uniprot`, `pdb`, `ensembl`, `ncbigene` |
| Small molecules | `pubchem`, `chembl`, `chebi`, `rhea` |
| Diseases | `mondo`, `nando`, `mesh`, `medgen`, `clinvar` |
| Pathways | `reactome`, `rhea`, `go` |
| Genes | `ncbigene`, `ensembl`, `uniprot` |
| Microorganisms | `bacdive`, `mediadive`, `taxonomy` |
| Literature | `pubmed`, `pubtator` |
| Glycobiology | `glycosmos` |

### Step 3: Perform Keyword Search
Use specialized search tools when available:

#### Available Search Tools:
- `search_uniprot_entity(query, limit=20)` - for proteins
- `search_chembl_molecule(query, limit=20)` - for small molecules
- `search_chembl_target(query, limit=20)` - for drug targets
- `search_pdb_entity(db, query, limit=20)` - for structures (db: "pdb", "cc", "prd")
- `search_reactome_entity(query, rows=30)` - for pathways
- `search_rhea_entity(query, limit=100)` - for biochemical reactions
- `search_mesh_entity(query, limit=10)` - for medical concepts

#### Getting Search Instructions:
If unsure how to search a database, run:
```
keyword_search_instructions(dbname)
```

### Step 4: Study the Database Schema
**CRITICAL:** Before writing SPARQL queries, always run:
```
get_MIE_file(dbname)
```

The MIE file contains:
- **Shape expressions**: Data structure and relationships
- **Sample RDF entries**: Real data examples
- **SPARQL query examples**: Working queries for reference
- **Cross-references**: How to link to other databases
- **Anti-patterns**: Common mistakes to avoid
- **Performance tips**: Database-specific optimizations

### Step 5: Retrieve Detailed Information
Using the IDs from Step 3 and knowledge from Step 4:

#### Option A: Use SPARQL Queries
Run `run_sparql(dbname, sparql_query)` following the MIE file examples:

**Critical Rules:**
- **UniProt**: Always filter `up:reviewed 1` for quality data
- **PubChem**: Use explicit `FROM <graph>` clauses for bioassays/proteins
- **ChEMBL**: Filter by specific entity types early
- Always use `LIMIT` (typically 20-100)
- Split property paths when using `bif:contains`

#### Option B: Use Helper Functions
For specific databases:
- `get_pubchem_compound_id(compound_name)` - get PubChem CID
- `get_compound_attributes_from_pubchem(pubchem_compound_id)` - get attributes

### Step 6: Connect Database IDs
Use TogoID tools to find relationships between different database IDs:

#### Core TogoID Tools:
```python
# Convert IDs between databases
togoid_convertId(ids="P04637,P17612", route="uniprot,pdb")

# Count convertible IDs
togoid_countId(source="uniprot", target="pdb", ids="P04637,P17612")

# Get available conversion routes
togoid_getAllRelation()

# Get dataset configurations
togoid_getDataset(dataset="uniprot")
```

**Common ID Conversions:**
- UniProt ↔ PDB, NCBI Gene, ChEMBL, Reactome
- PubChem ↔ ChEBI, ChEMBL
- NCBI Gene ↔ Ensembl, UniProt
- MeSH ↔ MONDO, ChEBI

### Step 7: Synthesize and Present Results
- Combine information from multiple databases
- Highlight key findings and relationships
- Cite data sources appropriately
- Note any limitations or gaps in the data

---

## Quick Reference

### Database Selection by Question Type

**"What is the structure of [protein]?"**
→ `uniprot` + `pdb`

**"What drugs target [protein]?"**
→ `chembl` + `uniprot` + `pubchem`

**"What pathways involve [gene/protein]?"**
→ `reactome` + `go` + `uniprot`

**"What are the properties of [chemical compound]?"**
→ `pubchem` + `chebi` + `chembl`

**"What diseases are associated with [gene]?"**
→ `ncbigene` + `clinvar` + `mondo` + `medgen`

**"What reactions involve [compound]?"**
→ `rhea` + `reactome` + `pubchem`

---

## Best Practices

1. **Always read MIE files before SPARQL** - Prevents common errors and timeouts
2. **Use specialized search tools first** - Faster and more reliable than raw SPARQL
3. **Start with small limits** - Use LIMIT 20-50 for initial exploration
4. **Check anti-patterns** - Every MIE file lists common mistakes to avoid
5. **Combine databases** - Use TogoID to link complementary data sources
6. **Filter early** - Apply type and reviewed status filters at the start of queries

---

## Common Pitfalls

❌ Writing SPARQL without reading MIE file
❌ Forgetting `up:reviewed 1` in UniProt queries
❌ Omitting `FROM <graph>` in PubChem bioassay/protein queries
❌ Using `bif:contains` with property paths (split them first)
❌ Running aggregations without LIMIT
❌ Assuming all databases use the same schema patterns

✅ Read MIE → Use examples → Adapt to your needs
✅ Use specialized search functions when available
✅ Apply database-specific optimizations
✅ Connect related data with TogoID tools