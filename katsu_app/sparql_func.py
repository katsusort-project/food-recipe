from SPARQLWrapper import SPARQLWrapper, JSON

class SPARQLQueryManager:
    def __init__(self, endpoint_url):
        self.sparql = SPARQLWrapper(endpoint_url)
        self.sparql.setReturnFormat(JSON)
    
    def execute_query(self, query):
        """
        Execute a SPARQL query and return results
        
        Args:
            query (str): SPARQL query to execute
        
        Returns:
            list: Query results as a list of dictionaries
        """
        try:
            self.sparql.setQuery(query)
            results = self.sparql.query().convert()
            
            # Process results from JSON format
            processed_results = []
            for result in results.get('results', {}).get('bindings', []):
                processed_result = {}
                for key, value in result.items():
                    processed_result[key] = value.get('value')
                processed_results.append(processed_result)
            
            return processed_results
        
        except Exception as e:
            # Log the error or handle it appropriately
            print(f"SPARQL Query Error: {e}")
            return []
    
    def construct_query(self, 
                        select_vars=['?s', '?p', '?o'], 
                        where_clause=None, 
                        limit=None):
        """
        Helper method to construct a basic SPARQL SELECT query
        
        Args:
            select_vars (list): Variables to select
            where_clause (str, optional): Custom WHERE clause
            limit (int, optional): Limit number of results
        
        Returns:
            str: Constructed SPARQL query
        """
        query = f"SELECT {' '.join(select_vars)} WHERE {{\n"
        
        if where_clause:
            query += f"  {where_clause}\n"
        else:
            query += "  ?s ?p ?o\n"
        
        query += "}"
        
        if limit:
            query += f" LIMIT {limit}"
        
        return query
