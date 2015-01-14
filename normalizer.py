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


QUICK_RUN_MESSAGE_LIMIT = 100


class Conversation:
    def __init__(self):
        self.id = id(self)
        self.mediums = []
        self.subject = ""
        self.category = ""
        self.views = 0
        self.status = ""
        self.messages = []
        self.analysis = {}


    def add_message(self, message):
        self.messages.append(message)

        if message.medium not in self.mediums:
            self.mediums.append(message.medium)


    def json_serialize(self):
        return {
            "id": self.id,
            "mediums": self.mediums,
            "subject": self.subject,
            "category": self.category,
            "views": self.views,
            "status": self.status,
            "messages": [m.json_serialize() for m in self.messages],
            "analysis": self.analysis
        }


    def xml_serialize(self):
        conversation = ET.Element("conversation")
        conversation.set("id", str(self.id))

        ET.SubElement(conversation, "mediums").text = " ".join(self.mediums)
        ET.SubElement(conversation, "subject").text = self.subject
        ET.SubElement(conversation, "category").text = self.category
        ET.SubElement(conversation, "views").text = str(self.views)
        ET.SubElement(conversation, "status").text = self.status

        messages = ET.SubElement(conversation, "messages")

        for message in self.messages:
            messages.append(message.xml_serialize())

        return conversation


class Message:
    def __init__(self):
        self.id = id(self)
        self.conversation_id = None
        self.medium = ""
        self.private = False
        self.likes = 0
        self.views = 0
        self.importance = ""
        self.subject = ""
        self.date = None
        self.encoding = ""
        self.MIME = ""
        self.participant_from = []
        self.participant_to = []
        self.participant_cc = []
        self.participant_bcc = []
        self.body = ""
        self.form = {}
        self.kbitems = []
        self.analysis = None


    def json_serialize(self):
        return {
            "id": self.id,
            "medium": self.medium,
            "private": self.private,
            "likes": self.likes,
            "views": self.views,
            "importance": self.importance,
            "subject": self.subject,
            "date": self.date,
            "encoding": self.encoding,
            "MIME": self.MIME,
            "participant_from": [p.json_serialize() for p in self.participant_from],
            "participant_to": [p.json_serialize() for p in self.participant_to],
            "participant_cc": [p.json_serialize() for p in self.participant_cc],
            "participant_bcc": [p.json_serialize() for p in self.participant_bcc],
            "body": self.body,
            "form": self.form,
            "kbitems": self.kbitems,
            "analysis": self.analysis
        }


    def xml_serialize(self):
        message = ET.Element("message")

        message.set("id", str(self.id))
        message.set("conversationId", str(self.conversation_id))

        in_reply_to = ""

        if (len(self.participant_to) > 0):
            in_reply_to = str(self.participant_to[0].email)

        message.set("inReplyTo", in_reply_to)

        context = ET.SubElement(message, "context")

        ET.SubElement(context, "medium").text = self.medium
        ET.SubElement(context, "private").text = str(self.private).lower()
        ET.SubElement(context, "likes").text = str(self.likes)
        ET.SubElement(context, "views").text = str(self.views)
        ET.SubElement(context, "importance").text = self.importance

        header = ET.SubElement(message, "header")

        ET.SubElement(header, "subject").text = self.subject
        ET.SubElement(header, "date").text = self.date
        ET.SubElement(header, "encoding").text = self.encoding
        ET.SubElement(header, "MIME").text = self.MIME

        participant_from = ET.SubElement(header, "from")

        for participant in self.participant_from:
            participant_from.append(participant.xml_serialize())

        participant_to = ET.SubElement(header, "to")

        for participant in self.participant_to:
            participant_to.append(participant.xml_serialize())

        participant_cc = ET.SubElement(header, "cc")

        for participant in self.participant_cc:
            participant_cc.append(participant.xml_serialize())

        participant_bcc = ET.SubElement(header, "bcc")

        for participant in self.participant_bcc:
            participant_bcc.append(participant.xml_serialize())

            ET.SubElement(header, "meta")

        content = ET.SubElement(message, "content")

        ET.SubElement(content, "body").text = self.body
        ET.SubElement(content, "form")
        ET.SubElement(content, "attachments")
        ET.SubElement(content, "kbitems")

        ET.SubElement(message, "analysis")

        return message


class Participant:
    def __init__(self):
        self.id = id(self)
        self.role = ""
        self.real_name = ""
        self.user_name = ""
        self.email = ""
        self.description = ""


    def json_serialize(self):
        return {
            "id": self.id,
            "role": self.role,
            "real_name": self.real_name,
            "user_name": self.user_name,
            "email": self.email,
            "description": self.description
        }


    def xml_serialize(self):
        participant = ET.Element("participant")

        participant.set("id", str(self.id))
        participant.set("role", self.role)
        participant.set("realname", self.real_name)
        participant.set("username", self.user_name)
        participant.set("email", self.email)
        participant.set("description", self.description)

        return participant


def normalize(opts, args):
    """
    Converts messages to the ODISAE format
    """

    output_folder, label = args

    timed_print("Extracting JSON data")

    data = extract_data(opts.email, opts.forum, test=opts.quick)

    if opts.xml:
        timed_print("Converting {0} conversations to XML".format(len(data)))

        xmls = []

        for conversation in [conversation.xml_serialize() for conversation in data]:
            xml = "<?xml version=\"1.0\" encoding=\"UTF-8\"?>"
            xml += ET.tostring(conversation)

            xmls.append(xml)

        timed_print("Exporting to {0}".format(output_folder))

        for i, xml in enumerate(xmls):
            save_to_file(xml, "{0}{1}_{2}.xml".format(output_folder, label, i + 1))


    if opts.json:
        timed_print("Converting {0} conversations to JSON".format(len(data)))

        json_data = json.dumps([conversation.json_serialize() for conversation in data], ensure_ascii=False)

        timed_print("Exporting to {0}data.json".format(output_folder))

        save_to_file(json_data, output_folder + "data.json")


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

    progress = ProgressBar()

    for initial_email in progress(data):
        conversation = Conversation()
        conversation.subject = initial_email["subject"]
        conversation.category = category
        
        for message in parse_email_tree(initial_email, conversation.id):
            conversation.add_message(message)

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
    message.date = item["datetime"]
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
                message.date = post["datetime"]
                message.encoding = "UTF-8"
                message.MIME = "text/html"
                message.body = post["content"]

                participant = Participant()
                participant.user_name = post["author"]
                participant.description = str(post["author_id"])

                message.participant_from.append(participant)

                conversation.add_message(message)

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