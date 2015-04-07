#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
:Name:
    normalizer.py

:Authors:
    Soufian Salim (soufi@nsal.im)
"""

import codecs
import doctest
import json
import os
import xml.etree.cElementTree as ET

from optparse import OptionParser
from progressbar import ProgressBar
from utility import timed_print, remove_extension, save_to_file
from conversations import Conversation, Message, Participant


QUICK_RUN_MESSAGE_LIMIT = 100

progress = ProgressBar()


def normalize(opts, args):
    """
    Converts messages to the ODISAE format
    """

    output_folder, label = args

    timed_print("Extracting JSON data")

    data = extract_data(opts.email, opts.forum, test=opts.quick)

    timed_print("Converting {0} conversations to XML".format(len(data)))

    xmls = []

    for conversation in progress([conversation.xml_serialize() for conversation in data]):
        xml = "<?xml version=\"1.0\" encoding=\"UTF-8\"?>"
        xml += ET.tostring(conversation)

        xmls.append(xml)

    timed_print("Exporting to {0}".format(output_folder))

    for i, xml in progress(enumerate(xmls)):
        save_to_file(xml, "{0}{1}_{2}.xml".format(output_folder, label, i + 1))


def extract_data(email_folder, forum_folder, test=False):
    """
    Extracts data from email and forum JSON files
    """
    data = []

    if email_folder:
        email_files = os.listdir(email_folder)

        timed_print("Parsing {0} email files from {1}...".format(len(email_files), email_folder))

        for filename in  email_files:
            json_data = parse_json_file("{0}/{1}".format(email_folder, filename))
            data.extend(parse_email_data(json_data, category=remove_extension(filename), test=test))

    if forum_folder:
        forum_files = os.listdir(forum_folder)

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

    for initial_email in progress(data):
        conversation = Conversation()
        conversation.subject = initial_email["subject"]
        conversation.category = category
        
        for message in parse_email_tree(initial_email, conversation.id):
            conversation.messages.append(message)

        conversations.append(conversation)

    return conversations


def parse_email_tree(item, conversation_id, to=None, test=False):
    """
    Recursively parses an email message
    """

    message = Message()   
    message.medium = "email"
    message.conversation_id = conversation_id
    message.subject = item["subject"]
    message.daytime = item["datetime"]
    message.encoding = "UTF-8"
    message.MIME = "text/plain"
    message.body = item["content"]

    participant = Participant()
    participant.real_name = item["author_name"]
    participant.email = item["author_address"]

    message.participant_from.append(participant)

    if to:
        message.participant_to.append(to)

    messages = [message]

    if "answers" in item:
        for answer in item["answers"]:
            messages.extend(parse_email_tree(answer, conversation_id, to=participant))

            if test and len(messages) >= QUICK_RUN_MESSAGE_LIMIT:
                break

    return messages


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

            conversation = Conversation()
            conversation.subject = thread["name"]
            conversation.category = forum["description"]
            conversation.status = "closed" if thread["closed"] else "open"

            for post in thread["posts"]:
                if test and message_number >= QUICK_RUN_MESSAGE_LIMIT:
                    break;

                message = Message()
                message.medium = "forum"
                message.subject = thread["name"]
                message.daytime = post["datetime"]
                message.encoding = "UTF-8"
                message.MIME = "text/html"
                message.body = post["content"]

                if post["signature"]:
                    message.misc["signature"] = post["signature"]

                participant = Participant()
                participant.user_name = post["author"]
                participant.description = str(post["author_id"])

                message.participant_from.append(participant)

                conversation.messages.append(message)

                message_number += 1

            conversations.append(conversation)

    return conversations


def parse_args():
    """
     Parse command line opts and arguments 
    """

    op = OptionParser(usage="usage: %prog [opts] output_folder label")

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

    op.add_option("--email",
        dest="email",
        default=False,
        type="string",
        help="folder containing email data")

    op.add_option("--forum",
        dest="forum",
        default=False,
        type="string",
        help="folder containing forum data")

    ########################################

    return op.parse_args()


if __name__ == "__main__":
    options, arguments = parse_args()

    ########################################

    if not arguments[0].endswith("/"):
        arguments[0] += "/"

    ########################################

    if options.test:
        doctest.testmod() # unit testing
    else:
        normalize(options, arguments)