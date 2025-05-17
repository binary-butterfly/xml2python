"""
Copyright (c) 2025, binary butterfly GmbH
Use of this source code is governed by an MIT-style license that can be found in the LICENSE.txt.
"""

from collections import defaultdict
from typing import Any, List, Optional, Tuple

from lxml import etree


class Xml2Python:
    """
    Helper for converting data from XML strings to dicts.
    """

    @staticmethod
    def string_to_xml_etree(content_string: str) -> etree.Element:
        """
        Take a string object and (try to) convert it to an XML etree Element
        """
        content_tag: etree.Element = etree.fromstring(content_string, parser=etree.XMLParser(resolve_entities=False))  # noqa: S320

        return content_tag

    @staticmethod
    def xml_to_dict(
        tag: etree.Element,
        ensure_array_keys: Optional[List[Tuple[str, str]]] = None,
        remote_type_tags: Optional[List[str]] = None,
        conditional_remote_type_tags: Optional[List[Tuple[str, str]]] = None,
        ignore_attributes: Optional[List[str]] = None,
    ) -> dict:
        """ """
        # default empty lists for the optional arguments:
        if ensure_array_keys is None:
            ensure_array_keys = []
        if remote_type_tags is None:
            remote_type_tags = []
        if conditional_remote_type_tags is None:
            conditional_remote_type_tags = []
        if ignore_attributes is None:
            ignore_attributes = []

        tag_name = etree.QName(tag).localname

        # only parse attributes if there are any of them not in the ignore list
        ignore_all_attribs: bool = False
        if tag.attrib:
            ignore_all_attribs = True
            for key in tag.attrib.keys():
                if key not in ignore_attributes:
                    ignore_all_attribs = False

        tag_dict = {tag_name: {} if (tag.attrib and not ignore_all_attribs) else None}
        children = list(tag)
        if children:
            aggregated_child_dict = defaultdict(list)
            for child in children:
                child_dict = Xml2Python.xml_to_dict(
                    child,
                    ensure_array_keys,
                    remote_type_tags,
                    conditional_remote_type_tags,
                    ignore_attributes,
                )
                for key, value in child_dict.items():
                    aggregated_child_dict[key].append(value)
            tag_dict: dict[str, Any] = {tag_name: {}}
            for key, value in aggregated_child_dict.items():
                if key == 'class':
                    key = 'class_'
                if len(value) == 1 and (tag_name, key) not in ensure_array_keys:
                    value = value[0]
                tag_dict[tag_name][key] = value

        if tag.attrib and not ignore_all_attribs:
            for key, value in tag.attrib.items():
                if key not in ignore_attributes:
                    tag_dict[tag_name][key.replace('{http://www.w3.org/2001/XMLSchema-instance}', '')] = value

        if tag.text:
            text = tag.text.strip()
            if children or (tag.attrib and not ignore_all_attribs):
                if text:
                    tag_dict[tag_name]['_text'] = text
            else:
                tag_dict[tag_name] = text

        # filter out remote type tags at the child level:
        if isinstance(tag_dict[tag_name], dict):
            tag_items: list[tuple[str, str]] = [(key, value) for key, value in tag_dict[tag_name].items()]  # noqa: C416
            # it only works if there is exactly one key-value-pair at the child level!
            if len(tag_items) == 1:
                child_key = tag_items[0][0]
                child_value = tag_items[0][1]
                # filter second level:
                if child_key in remote_type_tags or (tag_name, child_key) in conditional_remote_type_tags:
                    tag_dict[tag_name] = child_value

        # finally, filter out remote type tags at the top level:
        if isinstance(tag_dict[tag_name], dict) and tag_name in remote_type_tags:
            # the return value still has to be a dict!
            tag_dict = tag_dict[tag_name]

        return tag_dict

    @staticmethod
    def xml_string_to_dict(
        xml_string: str,
        ensure_array_keys: Optional[List[Tuple[str, str]]] = None,
        remote_type_tags: Optional[List[str]] = None,
        conditional_remote_type_tags: Optional[List[Tuple[str, str]]] = None,
        ignore_attributes: Optional[List[str]] = None,
    ) -> dict:
        """
        Wrapper around 'string_to_xml_etree' and 'xml_to_dict'
        """
        result_tag: etree.Element = Xml2Python.string_to_xml_etree(xml_string)
        result_dict: dict = Xml2Python.xml_to_dict(
            result_tag,
            ensure_array_keys,
            remote_type_tags,
            conditional_remote_type_tags,
            ignore_attributes,
        )
        return result_dict
