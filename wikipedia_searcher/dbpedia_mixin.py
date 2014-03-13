from rdflib import Graph, ConjunctiveGraph

class _DBPediaMixin(object):
    def __init__(self):
        self.graph = ConjunctiveGraph('SPARQLStore')

    def _get_media_api_host(self, language):
        return language + u'.wikipedia.org'

    def _get_dbpedia_url(self, language):
        return u'http://' +('' if language == u'en' else language + u'.') + u'dbpedia.org'

    def _fetch_dbpedia_query_result(self, query):
        result = self.graph.query( unicode(query) )
        return_fetch_results = [ [ unicode(e.n3()) if (not e is None) else ''  for e in fetch_result] for fetch_result in result ]
        return return_fetch_results
