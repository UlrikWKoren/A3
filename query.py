from SPARQLWrapper import SPARQLWrapper, JSON

# Imports SPQRQLWrapper JSON and interface.
# SPARQLWrapper is used to communicate with the local instance of blazegraph that is running.
#IP = input('Write the ip-address that blazegraph runs on:')
IP = "http://10.0.13.167:9999/blazegraph/"

# example address http://10.111.19.76:9999/blazegraph/

sparql = SPARQLWrapper(f'{IP}namespace/VIN/sparql')  # local ip adress of the running blazegraph.
# The ip address must be same as the one blazegraph runs on your computer. Check your command line after starting
# blazegraph.




# This is a function that dynamically adds filtering to the SPARQL query based on different parameters it receives.
def createFilter(name,country, region, subRegion):


    filter = """
        prefix ns1: <http://example.org/>
    prefix ns2: <https://schema.org/>
    prefix ns3: <http://www.w3.org/2002/07/owl#>
    prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#>
    prefix xsd: <http://www.w3.org/2001/XMLSchema#>
    SELECT DISTINCT ?ID ?name ?country ?region ?subregion ?countryid ?sugar ?acid ?grapes ?alcohol ?price ?tannins ?fullness ?freshness ?typeDrink ?volume ?vintage ?bundleSize ?food WHERE { ?ID ns1:name ?name. 
      
      ?ID ns1:ingredients ?ingredients.
      ?ingredients ns1:sugarLevels ?sugar.
      ?ingredients ns1:acid ?acid.
      
      ?ID ns1:description ?description.
      ?description ns1:hasTannins ?tannins.
      ?description ns1:hasFreshness ?freshness.
      ?description ns1:hasFullness ?fullness.
    
    
      
      ?ID ns1:basic ?basic.
      ?basic ns1:alcoholPercentage ?alcohol.
      ?basic ns1:volumeLiter ?volume.
      
      ?basic ns1:Vintage ?vintage.
      ?basic ns1:bottlesPerSale ?bundleSize.
      
    
      ?ID ns1:priceDetails ?priceDetails.
      ?priceDetails ns2:price ?price.
      ?ID ns1:grapeDetails ?grapeDetails.
      ?grapeDetails ns1:typeOfGrapes ?grapes.
      
      ?ID ns1:origin ?origin.
      ?origin ns1:countryOfOrigin ?country.
      ?origin ns1:region ?region.
      ?origin ns1:subRegion ?subregion.
      ?origin ns1:iso31661Code ?countryid.
      
      
      ?ID ns1:classifications ?classifications.
      ?classifications ns1:drink ?typeDrink.""" + f'''
      FILTER(CONTAINS(?region,"{region}")).
      FILTER(CONTAINS(?subregion,"{subRegion}")).
      FILTER(CONTAINS(?country,"{country}")).                                                                                                                                                                              
      FILTER(CONTAINS(?name,"{name}")).''' +'\n}' + '\nORDER BY ASC((?volume))\nLIMIT 12'

    return filter






# Function that takes care of assembling and sending/ receiving the query.
# receives the results and returns a list with a dictionary inside for each of the products.
def requestDrinks(name = '' ,country = '', region = '', subRegion = ''): # receives the different parameters so it can pass the
    # forward to the createFilter function.
    drinkList = [] # list for all the dictionaries.
    filter = createFilter(name,country,region,subRegion)
    sparql.setQuery(filter)
    sparql.setReturnFormat(JSON)
    results = sparql.query().convert()
    for result in results["results"]["bindings"]: # loops through the result and adds the dictionaries to the list.
        result['link'] = result.pop('ID')
        result['link']['value'] = f'https://www.vinmonopolet.no/p/{result["link"]["value"].split("/")[-1]}'
        # Creates the link to the products page at vinmonopolet.no
        drinkList.append(result)
    return drinkList