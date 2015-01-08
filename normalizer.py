#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
:Name:
    normalizer.py

:Authors:
    Soufian Salim (soufi@nsal.im)
"""

import codecs
import dicttoxml
import doctest
import json
import hashlib
import io
import os

from optparse import OptionParser
from progressbar import ProgressBar
from utility import timed_print, remove_extension, save_to_file


QUICK_RUN_MESSAGE_LIMIT = 100


def normalize(opts, args):
    """
    Converts messages to the ODISAE format
    """
    email_folder, forum_folder, output_folder = args

    timed_print("Extracting JSON data")

    data = extract_data(email_folder, forum_folder, test=opts.quick)

    if opts.xml:
        timed_print("Converting {0} conversations to XML".format(len(data)))

        xml_data = convert_to_XML(data)

        timed_print("Exporting to {0}data.xml".format(output_folder))

        save_to_file(xml_data, output_folder + "data.xml")

    if opts.json:
        timed_print("Exporting to {0}data.json".format(output_folder))

        save_to_file(json.dumps(data, ensure_ascii=False), output_folder + "data.json")


def extract_data(email_folder, forum_folder, test=False):
    """
    Extracts data from email and forum JSON files
    """
    data = []

    email_files = os.listdir(email_folder)
    forum_files = os.listdir(forum_folder)

    timed_print("Parsing {0} email files from {1}...".format(len(email_files), email_folder))

    for filename in  email_files:
        json_data = parse_json_file("{0}/{1}".format(email_folder, filename))
        data.extend(parse_email_data(json_data, category=remove_extension(filename), test=test))

    timed_print("Parsing {0} forum files from {1}...".format(len(forum_files), forum_folder))

    for filename in  forum_files:
        json_data = parse_json_file("{0}/{1}".format(forum_folder, filename))
        data.extend(parse_forum_data(json_data, test=test))

    return data


def parse_json_file(filename):
    """
    Reads a JSON file
    """
    file_data = codecs.open(filename, encoding="utf-8").read()

    return json.loads(file_data)


def parse_email_data(data, category=None, test=False):
    """
    Parses JSON email data
    """
    conversations = []

    progress = ProgressBar()

    for message in progress(data):
        conversation_id = make_identifier(message)

        conversations.append({
            "id": conversation_id,
            "mediums": ["email"],
            "subject": message["subject"],
            "category": category,
            "status": None,
            "views": None,
            "roles": [{
                "type": "user",
                "value": None
            }],
            "type": "mailing list",
            "messages": parse_email_tree(message, conversation_id)
        })

    return conversations


def parse_email_tree(item, conversation_id, parent_id=None, test=False):
    """
    Recursively parses an email message
    """
    message_id = make_identifier(item)

    messages = [{
        "conversation_id": conversation_id,
        "id": message_id,
        "context": {
            "medium": "email",
            "private": False,
            "nb_likes": None,
            "importance": None,
        },
        "header": {
            "subject": item["subject"],
            "datetime": item["datetime"],
            "type": "initial" if message_id == conversation_id else "non_initial",
            "encoding": "UTF-8",
            "MIME": "text/plain",
            "inReplyTo": [{"message_id": parent_id, "conversation_id": conversation_id}] if parent_id else [],
            "to": [],
            "from": [{"type": "user", "description": "{0} <{1}>".format(item["author_name"], item["author_address"])}],
            "meta": []
        },
        "content": {
            "body": item["content"],
            "form": None,
            "attachments": None,
            "kbitems": [],
        }
    }]

    if "answers" in item:
        for answer in item["answers"]:
            messages.extend(parse_email_tree(answer, conversation_id, parent_id=message_id))

            if test and len(messages) >= QUICK_RUN_MESSAGE_LIMIT:
                break

    return messages


def make_identifier(message):
    return hashlib.md5(message["datetime"]).hexdigest()


def parse_forum_data(data, test=False):
    """
    Parses JSON forum data
    """
    message_number = 0

    conversations = []

    progress = ProgressBar()

    for forum in progress(data):
        if test and message_number >= QUICK_RUN_MESSAGE_LIMIT:
            continue;

        for thread in forum["threads"]:
            if test and message_number >= QUICK_RUN_MESSAGE_LIMIT:
                break;

            conversation_id = make_identifier(thread["posts"][0])

            messages = []

            for post in thread["posts"]:
                if test and message_number >= QUICK_RUN_MESSAGE_LIMIT:
                    break;

                message_id = make_identifier(post)

                messages.append({
                    "conversation_id": conversation_id,
                    "id": message_id,
                    "context": {
                        "medium": "forum",
                        "private": False,
                        "nb_likes": None,
                        "importance": None,
                    },
                    "header": {
                        "subject": thread["name"],
                        "datetime": post["datetime"],
                        "type": "initial" if message_id == conversation_id else "non_initial",
                        "encoding": "UTF-8",
                        "MIME": "text/plain",
                        "inReplyTo": [{"message_id": conversation_id, "conversation_id": conversation_id}],
                        "to": [],
                        "from": [{"type": "user", "description": u"{0} <{1}>".format(post["author"], post["author_id"])}],
                        "meta": []
                    },
                    "content": {
                        "body": post["content"],
                        "form": None,
                        "attachments": None,
                        "kbitems": [],
                    }
                })

                message_number += 1

            conversations.append({
                "id": conversation_id,
                "mediums": ["forum"],
                "subject": thread["name"],
                "category": forum["description"],
                "status": "closed" if thread["closed"] else "open",
                "views": None,
                "roles": [{
                    "type": "user",
                    "value": None
                }],
                "type": "forum thread",
                "messages": messages
            })

    return conversations


def convert_to_XML(data):
    """
    Converts data to XML
    """
    return dicttoxml.dicttoxml(data).decode("utf-8")


def parse_args():
    """
     Parse command line opts and arguments 
    """

    op = OptionParser(usage="usage: %prog [opts] email_folder forum_folder output_folder")

    ########################################

    op.add_option("--test",
        dest="test",
        default=False,
        action="store_true",
        help="executes the test suite")

    op.add_option("--quick",
        dest="quick",
        default=False,
        action="store_true",
        help="quick run for testing purposes (stops around 100 messages of each type)")

    op.add_option("--json",
        dest="json",
        default=False,
        action="store_true",
        help="exports a JSON file")

    op.add_option("--xml",
        dest="xml",
        default=False,
        action="store_true",
        help="exports an XML file")

    ########################################

    return op.parse_args()


if __name__ == "__main__":
    options, arguments = parse_args()

    ########################################

    for i in xrange(len(arguments)):
        if not arguments[i].endswith("/"):
            arguments[i] += "/"

    ########################################

    if options.test:
        doctest.testmod() # unit testing
    else:
        normalize(options, arguments)