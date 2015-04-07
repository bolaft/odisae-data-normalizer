#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
:Name:
    xml_to_tsv.py

:Authors:
    Soufian Salim (soufi@nsal.im)
"""

import codecs
import doctest
import os
import nltk.data

from nltk import pos_tag
from nltk.stem.wordnet import WordNetLemmatizer
from nltk.tokenize import word_tokenize
from progressbar import ProgressBar
from optparse import OptionParser
from conversations import Conversation
from utility import timed_print, save_to_file

tokenizer = nltk.data.load("tokenizers/punkt/french.pickle")

progress = ProgressBar()


def xml_to_tsv(opts, args):
    """
    Converts messages from the ODISAE format to Webanno TSV (old)
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

        txt = convert_to_txt(conversation)

        save_to_file(txt, xml_file.replace("xml", "txt"))

    timed_print("Done")


def convert_to_txt(conversation):
    sentences = []

    for message in conversation.messages:
        sentences.extend(tokenize(message.body))

    return "\n".join(sentences)


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


def generate_sentences(text):
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

    for sentence in sentences:
        yield sentence


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
        xml_to_tsv(options, arguments)