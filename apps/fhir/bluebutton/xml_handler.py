#!/usr/bin/env python
# -*- coding: utf-8 -*-
# vim: ai ts=4 sts=4 et sw=4

"""
hhs_oauth_server
FILE: xml_handler.py
Created: 3/28/17 3:00 PM

File created by: ''
"""
import logging
import xml.etree.ElementTree as ET
from lxml.etree import tostring
import xml.dom.minidom as XDM

from apps.fhir.bluebutton.utils import get_resource_names
from apps.fhir.fhir_core.utils import valid_interaction


FHIR_NAMESPACE = {'fhir': 'http://hl7.org/fhir'}
# ns_string will get value from first key in above dict
# ns_string can receive a dict to allow the default to be overridden

logger = logging.getLogger('hhs_server.%s' % __name__)


def xml_to_dom(xml_string):
    """
    convert an text string to an xml document we can manipulate
    using ElementTree. 
    
    Import ElementTree as ET to allow changing the underlying library
    without impacting code.
    """

    ns = ns_string()
    logger.debug("Name SPACE=%s" % ns)

    # Take the xml text and convert to a DOM
    dom = string_to_dom(xml_string)

    return dom


def dom_conformance_filter(dom, ns=FHIR_NAMESPACE):
    """
    filter conformance statement to remove unsupported resources and
    interactions
    :param dom: 
    :param ns: 
    :return: 
    """

    # Now we need to filter the Dom Conformance Statement
    dom = filter_dom(dom, ns)

    # Then convert back to text to allow publishng
    back_to_xml = ET.tostring(dom).decode("utf-8")

    # logger.debug("New XML:\n%s" % back_to_xml)
    # logger.debug("XML is type:%s" % type(back_to_xml))

    return back_to_xml
    # return xml_to_dict


def string_to_dom(content):
    """
    Use ElementTree to parse content

    :param content: 
    :return: 
    """
    ns = FHIR_NAMESPACE

    root = ET.fromstring(content)

    return root


def filter_dom(root, ns=FHIR_NAMESPACE):
    """
    remove unwanted elements from dom
    :param dom: 
    :return: 
    """

    # Get the published fhir resources as a list
    pub_resources = get_resource_names()

    element_rest = root.findall('{%s}rest' % ns_string(), ns)
    for rest in element_rest:
        # print("REST:%s" % rest.tag)
        # We want the resource elements
        child_list = get_named_child(rest,
                                     '{%s}resource' % ns_string())
        # print("Rest KIDS:%s" % child_list)
        for resource in child_list:
            # logger.debug("Resource:%s" % resource.tag)

            # Now we need to find the type element in resource
            element_type = resource.findall('{%s}type' % ns_string())
            element_interaction = resource.findall('{%s}'
                                                   'interaction' % ns_string())
            for t in element_type:
                # print("R:%s" % no_ns_name(t.attrib))
                if no_ns_name(t.attrib) in pub_resources:
                    logger.debug("Publishing:%s" % no_ns_name(t.attrib))

                    # this resource is to be published
                    # We need to remove unsupported interactions
                    # get all interactions in resource
                    # check interaction code against supported resource type
                    # actions
                    # remove disabled actions
                    pub_interactions = valid_interaction(no_ns_name(t.attrib))
                    for e in element_interaction:
                        pub_interactions = get_named_child(e,
                                                           'code',
                                                           x_field='value')
                        print("Interactions:%s" % pub_interactions)

                else:
                    # remove this node from child_list
                    logger.debug("Removing:%s" % no_ns_name(t.attrib))
                    # print("Resource:%s" % resource)
                    rest.remove(resource)
                    # print("Child_list:%s" % child_list)
                    
        # kid.remove(rest)
        print("Root:%s" % root)
        # root.SubElement(root, rest)

    return root


def get_named_child(root, named=None, x_field='tag'):
    """
    Traverse the Document segment
    :param root: 
    :param named=None
    :param x_field='tag|value'
    :return: 
    """
    kids = []
    # print(root)
    for child in root:
        # logger.debug("Evaluating:%s" % child)
        # print("%s:%s" % (named, child.get(x_field)))
        if named:
            if child.tag == named:
                # print("%s child:%s" % (named, no_ns_name(child.tag)))
                kids.append(child)

            else:
                pass

    return kids


def no_ns_name(name_string, ns=FHIR_NAMESPACE):
    """
    Strip the name space from the element name
    :param name: 
    :param ns: 
    :return: 
    """

    nspace = ns[next(iter(ns))]
    # print("Name:%s in %s" % (nspace, name_string))
    # Remove name space prefix
    if type(name_string) is dict:
        new_name_string = name_string[next(iter(name_string))]
        # print("From:%s to %s" % (name_string, new_name_string))
    else:
        new_name_string = name_string
    short_name = new_name_string.replace("{%s}" % nspace, "")

    return short_name


def ns_string(ns=FHIR_NAMESPACE):
    """ 
    get the namespace string from the global variable: FHIR_NAMESPACE
    """
    nss = ns

    return nss[next(iter(nss))]
