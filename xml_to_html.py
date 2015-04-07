#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
:Name:
    xml_to_html.py

:Authors:
    Soufian Salim (soufi@nsal.im)
"""

import codecs
import hashlib
import doctest
import os
import xml.etree.cElementTree as ET
import nltk.data

from progressbar import ProgressBar
from optparse import OptionParser
from conversations import Conversation
from utility import timed_print


tokenizer = nltk.data.load("tokenizers/punkt/french.pickle")

progress = ProgressBar()

def xml_to_html(opts, args):
    """
    Converts messages from the ODISAE format to HTML
    """
    input_folder = args[0]

    xml_files = []

    for dirpath, dirnames, filenames in os.walk(input_folder):
        for filename in filenames:
            if filename.endswith(".xml"):
                xml_files.append(os.path.join(dirpath, filename))

    timed_print("Converting {0} xml files from {1}...".format(len(xml_files), input_folder))

    for xml_file in progress(xml_files):
        xml = codecs.open(xml_file, encoding="utf-8").read()
        conversation = Conversation(xml)

        tree = build_html_tree(conversation)
        tree.write(xml_file.replace("xml", "html"))

    timed_print("Done")


def build_html_tree(conversation):
    root = ET.Element("html")

    head = ET.SubElement(root, "head")
    
    meta = ET.SubElement(head, "meta")
    meta.set("name", "viewport")
    meta.set("content", "width=device-width, initial-scale=1.0")

    link = ET.SubElement(head, "link")
    link.set("type", "text/css")
    link.set("rel", "stylesheet")
    link.set("href", "dist/css/bootstrap.min.css")

    link = ET.SubElement(head, "link")
    link.set("type", "text/css")
    link.set("href", "dist/css/style.css")

    title = ET.SubElement(head, "title")
    title.text = conversation.subject

    body = ET.SubElement(root, "body")

    script = ET.SubElement(body, "script")
    script.set("src", "dist/js/jquery-1.11.2.min.js")
    script.text  = " "

    script = ET.SubElement(body, "script")
    script.set("src", "dist/js/script.js")
    script.text  = " "

    section = ET.SubElement(body, "section")
    section.set("class", "conversation")

    button = ET.SubElement(section, "button")
    button.set("type", "button")
    button.set("class", "save btn btn-default btn-large btn-warning")
    button.set("style", "float: left;")
    button.text = "SAVE SESSION"

    table = ET.SubElement(section, "table")
    table.set("class", "table table-bordered table-condensed")
    table.set("style", "background-color: lightgray; width: 100%;")

    tr = ET.SubElement(table, "tr")
    td = ET.SubElement(tr, "td")
    td.set("width", "10%")
    strong = ET.SubElement(td, "strong")
    strong.text = "Conversation ID"
    td = ET.SubElement(tr, "td")
    td.text = conversation.id

    tr = ET.SubElement(table, "tr")
    td = ET.SubElement(tr, "td")
    strong = ET.SubElement(td, "strong")
    strong.text = "Subject"
    td = ET.SubElement(tr, "td")
    td.text = conversation.subject

    if hasattr(conversation, "mediums"):
        tr = ET.SubElement(table, "tr")
        td = ET.SubElement(tr, "td")
        strong = ET.SubElement(td, "strong")
        strong.text = "Mediums"
        td = ET.SubElement(tr, "td")
        td.text = conversation.mediums

    tr = ET.SubElement(table, "tr")
    td = ET.SubElement(tr, "td")
    strong = ET.SubElement(td, "strong")
    strong.text = "Category"
    td = ET.SubElement(tr, "td")
    td.text = conversation.category

    ET.SubElement(section, "hr")

    for message in conversation.messages:
        if message.medium == "email":
            author = u"{0} <{1}>".format(message.participant_from[0].real_name, message.participant_from[0].email)
        elif message.medium == "forum":
            author = message.participant_from[0].user_name

        div = ET.SubElement(section, "div")
        div.set("class", "message")

        color = make_color(author)

        table = ET.SubElement(div, "table")
        table.set("class", "table table-bordered table-condensed")
        table.set("style", "background-color: #{0}".format(color))

        tr = ET.SubElement(table, "tr")
        td = ET.SubElement(tr, "td")
        td.set("width", "10%")
        strong = ET.SubElement(td, "strong")
        strong.text = "Message ID"
        td = ET.SubElement(tr, "td")
        td.set("colspan", "2")
        td.text = message.id

        tr = ET.SubElement(table, "tr")
        td = ET.SubElement(tr, "td")
        strong = ET.SubElement(td, "strong")
        strong.text = "Author"
        td = ET.SubElement(tr, "td")
        td.set("colspan", "2")
        td.text = author

        if hasattr(message, "date"):
            tr = ET.SubElement(table, "tr")
            td = ET.SubElement(tr, "td")
            strong = ET.SubElement(td, "strong")
            strong.text = "Timestamp"
            td = ET.SubElement(tr, "td")
            td.set("colspan", "2")
            td.text = message.date

        sentences = tokenize(message.body) if message.body else []

        for i, sentence in enumerate(sentences):
            tr = ET.SubElement(table, "tr")

            td = ET.SubElement(tr, "td")
            td.set("style", "background-color: white")
            td.set("message-id", message.id)
            td.set("conversation-id", conversation.id)
            td.set("sentence-number", str(i + 1))
            td.set("sentence-id", "m{0}s{1}".format(message.id, i))
            td.set("contenteditable", "")
            td.set("class", "annotation")

            td = ET.SubElement(tr, "td")
            td.set("style", "text-align: center;")
            td.set("width", "35px")
            td.text = str(i + 1)

            td = ET.SubElement(tr, "td")

            p = ET.SubElement(td, "p")
            p.set("class", "sentence")
            p.text = sentence

    return ET.ElementTree(root)


def make_color(text, scalefactor=1.5):
    hex_color = hashlib.md5(text.encode("utf-8")).hexdigest()[:6]

    if scalefactor < 0 or len(hex_color) != 6:
        return hex_color

    r, g, b = int(hex_color[:2], 16), int(hex_color[2:4], 16), int(hex_color[4:], 16)

    r = clamp(r * scalefactor)
    g = clamp(g * scalefactor)
    b = clamp(b * scalefactor)

    return "%02x%02x%02x" % (r, g, b)


def clamp(val, minimum=0, maximum=255):
    if val < minimum:
        return minimum
    if val > maximum:
        return maximum
    return val


def tokenize(text):
    lines = text.split("\n")
    lines = [l.strip() for l in lines if not l.strip().startswith(">") and len(l.strip()) > 0]

    true_lines = []

    for line in lines:
        if line.startswith("--"):
            break

        if line.startswith(">") or not len(line) > 0:
            continue

        line = line.replace("<br>", "<br>\n")
        line = line.replace("</p>", "</p>\n")

        if len(line) < 65 and len(line) > 0:
            line += "\n"
        else:
            line += " "

        true_lines.append(line)

    true_lines = "".join(true_lines).split("\n")

    sentences = []

    for line in true_lines:
        if len(line.strip()) == 0:
            continue

        tokens = tokenizer.tokenize(line)

        for token in tokens:
            sentences.append(token)

    return sentences


def parse_args():
    """
     Parse command line opts and arguments 
    """

    op = OptionParser(usage="usage: %prog [opts] input_folder")

    op.add_option("--test",
        dest="test",
        default=False,
        action="store_true",
        help="executes the test suite")

    return op.parse_args()


if __name__ == "__main__":
    options, arguments = parse_args()

    if not arguments[0].endswith("/"):
        arguments[0] = arguments[0] + "/"

    if options.test:
        doctest.testmod() # unit testing
    else:
        xml_to_html(options, arguments)