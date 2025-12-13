"""
NCBI E-utilities Search Functions
Implements keyword search for NCBI databases using esearch
"""

import requests
from typing import Dict, List, Optional, Union
import time


class NCBIEutilsSearcher:
    """
    A class for searching NCBI databases using E-utilities esearch.
    
    NCBI Usage Guidelines:
    - Without API key: max 3 requests/second
    - With API key: max 10 requests/second
    - Always provide email address
    """
    
    BASE_URL = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi"
    
    def __init__(self, email: str, api_key: Optional[str] = None):
        """
        Initialize the searcher.
        
        Args:
            email: Your email address (required by NCBI)
            api_key: Optional NCBI API key for higher rate limits
        """
        self.email = email
        self.api_key = api_key
        self.last_request_time = 0
        # Rate limiting: 3 requests/sec without key, 10 with key
        self.min_interval = 0.1 if api_key else 0.34
    
    def _rate_limit(self):
        """Enforce rate limiting between requests."""
        elapsed = time.time() - self.last_request_time
        if elapsed < self.min_interval:
            time.sleep(self.min_interval - elapsed)
        self.last_request_time = time.time()
    
    def _search(self, 
                db: str, 
                term: str, 
                retmax: int = 20,
                retstart: int = 0,
                sort: Optional[str] = None,
                **kwargs) -> Dict:
        """
        Generic search function for any NCBI database.
        
        Args:
            db: NCBI database name
            term: Search query
            retmax: Maximum number of results to return (default 20)
            retstart: Starting index for pagination (default 0)
            sort: Sort order (e.g., 'relevance', 'pub_date')
            **kwargs: Additional parameters for esearch
        
        Returns:
            Dict containing search results with 'idlist', 'count', etc.
        """
        self._rate_limit()
        
        params = {
            'db': db,
            'term': term,
            'retmax': retmax,
            'retstart': retstart,
            'retmode': 'json',
            'email': self.email
        }
        
        if self.api_key:
            params['api_key'] = self.api_key
        
        if sort:
            params['sort'] = sort
        
        # Add any additional parameters
        params.update(kwargs)
        
        try:
            response = requests.get(self.BASE_URL, params=params, timeout=30)
            response.raise_for_status()
            data = response.json()
            
            # Extract the esearchresult
            if 'esearchresult' in data:
                return data['esearchresult']
            else:
                return data
                
        except requests.exceptions.RequestException as e:
            return {
                'error': str(e),
                'idlist': [],
                'count': '0'
            }
    
    def search_gene(self, 
                    query: str, 
                    retmax: int = 20,
                    organism: Optional[str] = None) -> Dict:
        """
        Search NCBI Gene database.
        
        Args:
            query: Search query (e.g., gene symbol, gene name)
            retmax: Maximum number of results
            organism: Optional organism filter (e.g., "Homo sapiens[Organism]")
        
        Returns:
            Dict with 'idlist' (gene IDs), 'count' (total results), etc.
        
        Example:
            >>> searcher = NCBIEutilsSearcher("your@email.com")
            >>> results = searcher.search_gene("TP53")
            >>> print(f"Found {results['count']} genes")
            >>> print(f"Gene IDs: {results['idlist']}")
        """
        search_term = query
        if organism:
            search_term = f"{query} AND {organism}"
        
        return self._search('gene', search_term, retmax=retmax)
    
    def search_pubmed(self,
                      query: str,
                      retmax: int = 20,
                      retstart: int = 0,
                      sort: str = 'relevance',
                      mindate: Optional[str] = None,
                      maxdate: Optional[str] = None) -> Dict:
        """
        Search PubMed database.
        
        Args:
            query: Search query (keywords, authors, etc.)
            retmax: Maximum number of results
            retstart: Starting position for pagination
            sort: Sort order ('relevance', 'pub_date', etc.)
            mindate: Minimum date (YYYY/MM/DD format)
            maxdate: Maximum date (YYYY/MM/DD format)
        
        Returns:
            Dict with 'idlist' (PMIDs), 'count', etc.
        
        Example:
            >>> results = searcher.search_pubmed("CRISPR gene editing", retmax=10)
            >>> print(f"Found {results['count']} articles")
            >>> print(f"PMIDs: {results['idlist']}")
        """
        params = {}
        if mindate:
            params['mindate'] = mindate
        if maxdate:
            params['maxdate'] = maxdate
        
        return self._search('pubmed', query, retmax=retmax, 
                          retstart=retstart, sort=sort, **params)
    
    def search_taxonomy(self,
                       query: str,
                       retmax: int = 20) -> Dict:
        """
        Search NCBI Taxonomy database.
        
        Args:
            query: Search query (organism name, taxonomy ID)
            retmax: Maximum number of results
        
        Returns:
            Dict with 'idlist' (taxonomy IDs), 'count', etc.
        
        Example:
            >>> results = searcher.search_taxonomy("Escherichia coli")
            >>> print(f"Found {results['count']} taxa")
            >>> print(f"Tax IDs: {results['idlist']}")
        """
        return self._search('taxonomy', query, retmax=retmax)
    
    def search_medgen(self,
                     query: str,
                     retmax: int = 20) -> Dict:
        """
        Search MedGen (Medical Genetics) database.
        
        Args:
            query: Search query (disease name, phenotype, etc.)
            retmax: Maximum number of results
        
        Returns:
            Dict with 'idlist' (MedGen concept IDs), 'count', etc.
        
        Example:
            >>> results = searcher.search_medgen("breast cancer")
            >>> print(f"Found {results['count']} concepts")
            >>> print(f"Concept IDs: {results['idlist']}")
        """
        return self._search('medgen', query, retmax=retmax)
    
    def search_pmc(self,
                  query: str,
                  retmax: int = 20,
                  retstart: int = 0) -> Dict:
        """
        Search PubMed Central (PMC) full-text articles.
        Note: PubTator uses PubMed, but PMC is useful for full-text searches.
        
        Args:
            query: Search query
            retmax: Maximum number of results
            retstart: Starting position for pagination
        
        Returns:
            Dict with 'idlist' (PMC IDs), 'count', etc.
        
        Example:
            >>> results = searcher.search_pmc("machine learning genomics")
            >>> print(f"Found {results['count']} full-text articles")
            >>> print(f"PMC IDs: {results['idlist']}")
        """
        return self._search('pmc', query, retmax=retmax, retstart=retstart)


def search_all_databases(searcher: NCBIEutilsSearcher, 
                        query: str, 
                        retmax: int = 10) -> Dict[str, Dict]:
    """
    Search across all supported NCBI databases with a single query.
    
    Args:
        searcher: NCBIEutilsSearcher instance
        query: Search query
        retmax: Maximum results per database
    
    Returns:
        Dict mapping database names to their search results
    """
    results = {}
    
    databases = {
        'gene': lambda: searcher.search_gene(query, retmax=retmax),
        'pubmed': lambda: searcher.search_pubmed(query, retmax=retmax),
        'taxonomy': lambda: searcher.search_taxonomy(query, retmax=retmax),
        'medgen': lambda: searcher.search_medgen(query, retmax=retmax),
        'pmc': lambda: searcher.search_pmc(query, retmax=retmax)
    }
    
    for db_name, search_func in databases.items():
        try:
            results[db_name] = search_func()
        except Exception as e:
            results[db_name] = {'error': str(e), 'idlist': [], 'count': '0'}
    
    return results


# Example usage
if __name__ == "__main__":
    # Initialize searcher (replace with your email)
    searcher = NCBIEutilsSearcher(email="your.email@example.com")
    
    # Search for a gene
    print("=" * 60)
    print("Searching NCBI Gene for 'TP53'")
    print("=" * 60)
    gene_results = searcher.search_gene("TP53", retmax=5)
    print(f"Found {gene_results.get('count', 0)} genes")
    print(f"Gene IDs: {gene_results.get('idlist', [])}")
    print()
    
    # Search PubMed
    print("=" * 60)
    print("Searching PubMed for 'CRISPR'")
    print("=" * 60)
    pubmed_results = searcher.search_pubmed("CRISPR", retmax=5)
    print(f"Found {pubmed_results.get('count', 0)} articles")
    print(f"PMIDs: {pubmed_results.get('idlist', [])}")
    print()
    
    # Search Taxonomy
    print("=" * 60)
    print("Searching NCBI Taxonomy for 'Escherichia coli'")
    print("=" * 60)
    taxonomy_results = searcher.search_taxonomy("Escherichia coli", retmax=5)
    print(f"Found {taxonomy_results.get('count', 0)} taxa")
    print(f"Taxonomy IDs: {taxonomy_results.get('idlist', [])}")
    print()
    
    # Search MedGen
    print("=" * 60)
    print("Searching MedGen for 'diabetes'")
    print("=" * 60)
    medgen_results = searcher.search_medgen("diabetes", retmax=5)
    print(f"Found {medgen_results.get('count', 0)} concepts")
    print(f"Concept IDs: {medgen_results.get('idlist', [])}")
    print()
    
    # Search all databases
    print("=" * 60)
    print("Searching ALL databases for 'cancer'")
    print("=" * 60)
    all_results = search_all_databases(searcher, "cancer", retmax=3)
    for db, results in all_results.items():
        print(f"\n{db.upper()}:")
        print(f"  Count: {results.get('count', 0)}")
        print(f"  IDs: {results.get('idlist', [])}")
