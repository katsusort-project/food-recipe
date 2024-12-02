from django.shortcuts import render
from django.http import JsonResponse
from katsu_app.sparql_func import SPARQLQueryManager

# Create your views here.
def show_main(request):


    return render(request, 'index.html')

# sparql_endpoint = "http://localhost:7200/repositories/<namarepo>"
# sparql = SPARQLWrapper(sparql_endpoint)

# sparql_query = f"""
# PREFIX exv: <http://example.org/vocab#>

# SELECT ?s
# WHERE {{
#     ?s a exv:Episode ;
#         exv:title ?o .
#     FILTER(?o = ?title)
# }}
# LIMIT 1
# """

# sparql.setQuery(sparql_query)
# sparql.setReturnFormat(JSON)
# response = self.sparql.query()
# results = response.convert()["results"]["bindings"]


def get_recipe(request):
 
    endpoint = "http://localhost:7200/repositories/food-recipe"
    query_manager = SPARQLQueryManager(endpoint)
    
    # Get genre from query parameters
    recipe = request.GET.get('recipe')
    print(recipe)
    
    query = f"""
        PREFIX schema: <http://schema.org/>
        PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
        
        SELECT ?recipe ?name ?description ?ingredients ?cookTime WHERE {{
            ?recipe a schema:Recipe .
            ?recipe rdfs:label ?name .
            OPTIONAL {{ ?recipe schema:description ?description }}
            OPTIONAL {{ ?recipe schema:recipeIngredient ?ingredients }}
            OPTIONAL {{ ?recipe schema:cookTime ?cookTime }}
            
            FILTER (
                CONTAINS(LCASE(?name), LCASE("{recipe}")))
            )
        }}
    """
    
    results = query_manager.execute_query(query)
    return render(request, 'search-result.html', {'recipes': results, 'query_input': recipe})
    # return JsonResponse(results, safe=False)