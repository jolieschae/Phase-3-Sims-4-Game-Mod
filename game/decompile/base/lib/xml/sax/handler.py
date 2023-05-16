# uncompyle6 version 3.9.0
# Python bytecode version base 3.7.0 (3394)
# Decompiled from: Python 3.7.16 (default, May 16 2023, 11:05:37) 
# [Clang 13.0.0 (clang-1300.0.29.30)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Lib\xml\sax\handler.py
# Compiled at: 2018-06-26 23:07:36
# Size of source mod 2**32: 14349 bytes
version = '2.0beta'

class ErrorHandler:

    def error(self, exception):
        raise exception

    def fatalError(self, exception):
        raise exception

    def warning(self, exception):
        print(exception)


class ContentHandler:

    def __init__(self):
        self._locator = None

    def setDocumentLocator(self, locator):
        self._locator = locator

    def startDocument(self):
        pass

    def endDocument(self):
        pass

    def startPrefixMapping(self, prefix, uri):
        pass

    def endPrefixMapping(self, prefix):
        pass

    def startElement(self, name, attrs):
        pass

    def endElement(self, name):
        pass

    def startElementNS(self, name, qname, attrs):
        pass

    def endElementNS(self, name, qname):
        pass

    def characters(self, content):
        pass

    def ignorableWhitespace(self, whitespace):
        pass

    def processingInstruction(self, target, data):
        pass

    def skippedEntity(self, name):
        pass


class DTDHandler:

    def notationDecl(self, name, publicId, systemId):
        pass

    def unparsedEntityDecl(self, name, publicId, systemId, ndata):
        pass


class EntityResolver:

    def resolveEntity(self, publicId, systemId):
        return systemId


feature_namespaces = 'http://xml.org/sax/features/namespaces'
feature_namespace_prefixes = 'http://xml.org/sax/features/namespace-prefixes'
feature_string_interning = 'http://xml.org/sax/features/string-interning'
feature_validation = 'http://xml.org/sax/features/validation'
feature_external_ges = 'http://xml.org/sax/features/external-general-entities'
feature_external_pes = 'http://xml.org/sax/features/external-parameter-entities'
all_features = [
 'feature_namespaces', 
 'feature_namespace_prefixes', 
 'feature_string_interning', 
 'feature_validation', 
 'feature_external_ges', 
 'feature_external_pes']
property_lexical_handler = 'http://xml.org/sax/properties/lexical-handler'
property_declaration_handler = 'http://xml.org/sax/properties/declaration-handler'
property_dom_node = 'http://xml.org/sax/properties/dom-node'
property_xml_string = 'http://xml.org/sax/properties/xml-string'
property_encoding = 'http://www.python.org/sax/properties/encoding'
property_interning_dict = 'http://www.python.org/sax/properties/interning-dict'
all_properties = [
 'property_lexical_handler', 
 'property_dom_node', 
 'property_declaration_handler', 
 'property_xml_string', 
 'property_encoding', 
 'property_interning_dict']