# -*- coding: utf-8 -*-
import re
import mwclient
from dbpedia_mixin import _DBPediaMixin

class WikipediaSearcher(_DBPediaMixin):

    def __init__(self):
        _DBPediaMixin.__init__(self)

    def _full_text_search(self, word, language):

        client = mwclient.Site(self._get_media_api_host(language))
        titles = []
        offset = -1

        # Fetch titles
        while True:
            if offset < 0:
                result = client.api(action='query', list='search', srwhat='text', srsearch=word)
            else:
                result = client.api(action='query', list='search', srwhat='text', srsearch=word, sroffset=offset)

            if result['query']['searchinfo']['totalhits'] == 0:
                break
            for article in result['query']['search']:
                titles.append(article['title'])
            if not result.has_key('query-continue'):
                break
            else:
                offset = result['query-continue']['search']['sroffset']

        urls = [u'http://' + self._get_media_api_host(language) + u'/wiki/' + re.sub(u'[　 ]+', u'_', title) for title in titles ]

        fetch_results = []
        for url in urls:
            query = """
            PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
            PREFIX dbo: <http://dbpedia.org/ontology/>
            PREFIX foaf: <http://xmlns.com/foaf/0.1/>

            select distinct  ?title, ?abstract, ?redirectTitle where {
              ?srcUrl foaf:isPrimaryTopicOf <%s> .
              ?srcUrl rdfs:label ?title
              {
                ?srcUrl dbo:abstract ?abstract
                FILTER langMatches( lang(?abstract), "%s" )
              } UNION {
                ?srcUrl dbo:wikiPageRedirects ?redirectUrl .
                ?redirectUrl rdfs:label ?redirectTitle .
                FILTER langMatches( lang(?redirectTitle), "%s" )
              }

              FILTER langMatches( lang(?title), "%s" )
            }
            """ % (url, language.upper(), language.upper(), language.upper() )

            fetch_result = self._fetch_dbpedia_query_result(query)
            fetch_results.append(fetch_result)

        return zip(urls, fetch_results)


    def simple_entry_search(self, word, action='exact', language='en'):
        """
        Search articles in Wikipedia by some simple ways

        Returns list of [ URL(Wikipedia Article), Title, Abstract, RedirectURL(If any)]
    
        Search ways are passed by 'action' argument and valid actions are below.
        exact   : exact match
        forward : forward match
        full    : full text search

        Target language is specified by 'language' argument.

        Returns empty string when 'word' argument is empty.
        """
        self.graph.open(self._get_dbpedia_url(language)+'/sparql')

        if word.strip() == '':
            return ''

        result = []
        if action == 'exact' or action == 'forward':
            if action == 'exact':
                filter_query = u'FILTER ( STR(LCASE(?_labelSrc)) = "%s" )'
            elif action == 'forward':
                filter_query = u'FILTER regex( ?_labelSrc, "^%s", "i" )'


            language = language.encode('utf-8')
            query_fetch_dest_url = """
            PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
            PREFIX foaf: <http://xmlns.com/foaf/0.1/>
            PREFIX dbo: <http://dbpedia.org/ontology/>

            select distinct ?url, ?_labelSrc as ?title, ?abstract, ?redirectTitle where {
              ?srcUrl rdfs:label ?_labelSrc .
              ?srcUrl foaf:isPrimaryTopicOf ?url .
              {
                ?srcUrl dbo:abstract ?abstract
                FILTER langMatches( lang(?abstract), "%s" )
              } UNION {
                ?srcUrl dbo:wikiPageRedirects ?redirectUrl .
                ?redirectUrl rdfs:label ?redirectTitle .
                FILTER langMatches( lang(?redirectTitle), "%s" )
              }
              FILTER langMatches( lang(?_labelSrc), "%s" )
              ?_labelSrc bif:contains '"%s"'
            """ + filter_query + """
            }
            """ 
            query_fetch_dest_url = query_fetch_dest_url % (language.upper(), language.upper(), language.upper(), word.lower(), word.lower())
            result = self._fetch_dbpedia_query_result(query_fetch_dest_url)
        elif action == 'full':
            result = self._full_text_search(word, language)
        else:
            raise ValueError('Invalid accion name')

        return result

    def relational_entry_search(self, word, action='exact', language='en'):
        """
        Search all relational articles

        Search targets are below.
        1. Articles whose article includes or matches 'word' 
        2. Relational articles with the articles described in 1.
        
        Search way (exact match or including) is specified by 'action' argument.
        """
        if action == 'exact':
            filter_query = u'FILTER ( STR(LCASE(?_labelSrc)) = "%s" )'
        elif action == 'forward':
            filter_query = u'FILTER regex( ?_labelSrc, "^%s", "i" )'
        else:
            raise ValueError('Invalid action')

        self.graph.open(self._get_dbpedia_url(language)+'/sparql')
        query = """
        PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
        PREFIX dbo: <http://dbpedia.org/ontology/>
        select distinct ?labelResult where {
          ?srcUrl rdfs:label ?labelSrc .
          {
            # Not redirects or ambiguates
            ?srcUrl rdfs:label ?labelResult .
          } UNION {
            # Redirects
            ?srcUrl dbo:wikiPageRedirects ?redirectUrl .
            {
              # Not ambiguates
              ?redirectUrl rdfs:label ?labelResult .
            } UNION {
              # Ambiguates
              ?redirectUrl dbo:wikiPageDisambiguates ?ambiguityRedirectsUrl .
              ?ambiguityRedirectsUrl rdfs:label ?labelResult .
            } 

          } UNION {
            # Ambiguates
            ?srcUrl dbo:wikiPageDisambiguates ?ambiguityUrl .
            ?ambiguityUrl rdfs:label ?labelResult .
           }

          FILTER langMatches( lang(?labelSrc), "%s" )
          FILTER langMatches( lang(?labelResult), "%s" )
          ?labelSrc bif:contains '"%s"'
        """ + filter_query + """
        }
        """ 
        query = query % (language.upper(), language.upper(),  word.lower(), word.lower())

        
        result = self._fetch_dbpedia_query_result(query)
        return result
