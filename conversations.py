"""
:Name:
    conversations.py

:Authors:
    Soufian Salim (soufi@nsal.im)
"""


import xml.etree.cElementTree as ET
import xmltodict


class Conversation:
    def __init__(self, xml=None):
        self.id = id(self)
        self.subject = ""
        self.category = ""
        self.views = 0
        self.status = ""
        self.messages = []
        self.analysis = {}
        self.misc = {}

        if xml:
            self.xml_unserialize(xml)


    def xml_serialize(self):
        conversation = ET.Element("conversation")
        conversation.set("id", str(self.id))

        ET.SubElement(conversation, "subject").text = self.subject
        ET.SubElement(conversation, "category").text = self.category
        ET.SubElement(conversation, "views").text = str(self.views)
        ET.SubElement(conversation, "status").text = self.status

        if self.misc:
            misc = ET.SubElement(conversation, "misc")

            for key, value in self.misc.items():
                item = ET.SubElement(misc, "item")
                item.set("name", key)
                item.set("value", value)

        messages = ET.SubElement(conversation, "messages")

        for message in self.messages:
            messages.append(message.xml_serialize())

        return conversation


    def xml_unserialize(self, xml):
        c_data = xmltodict.parse(xml)["conversation"]

        self.id = c_data["@id"]
        self.subject = c_data["subject"]
        self.category = c_data["category"]
        self.views = 0 if isinstance(c_data["views"], basestring) else int(c_data["views"])
        self.status = c_data["status"]

        if not isinstance(c_data["messages"]["message"], list):
            messages = [c_data["messages"]["message"]]
        else:
            messages = c_data["messages"]["message"]

        for m_data in messages:
            m = Message()

            m.id = m_data["@id"]
            m.conversation_id = m_data["@conversationId"] if "@conversationId" in m_data else -1
            m.medium = m_data["context"]["medium"]
            m.private = m_data["context"]["private"]
            m.likes = m_data["context"]["likes"]
            m.views = m_data["context"]["views"]
            m.importance = m_data["context"]["importance"]
            m.subject = m_data["header"]["subject"]
            m.daytime = m_data["header"]["daytime"] if "daytime" in m_data["header"] else m_data["header"]["date"]
            m.encoding = m_data["header"]["encoding"]
            m.MIME = m_data["header"]["MIME"]
            m.body = m_data["content"]["body"]
            m.form = m_data["content"]["form"]
            m.kbitems = m_data["content"]["kbitems"] if "kbitems" in m_data["content"] else None
            m.analysis = m_data["analysis"]

            p_from = Participant()

            p_from.id = m_data["header"]["from"]["participant"]["@id"]
            p_from.role = m_data["header"]["from"]["participant"]["@role"]
            p_from.real_name = m_data["header"]["from"]["participant"]["@realname"]
            p_from.user_name = m_data["header"]["from"]["participant"]["@username"]
            p_from.email = m_data["header"]["from"]["participant"]["@email"]
            p_from.description = m_data["header"]["from"]["participant"]["@description"]

            m.participant_from = [p_from]

            if m_data["header"]["to"]:
                p_to = Participant()

                p_to.id = m_data["header"]["to"]["participant"]["@id"]
                p_to.role = m_data["header"]["to"]["participant"]["@role"]
                p_to.real_name = m_data["header"]["to"]["participant"]["@realname"]
                p_to.user_name = m_data["header"]["to"]["participant"]["@username"]
                p_to.email = m_data["header"]["to"]["participant"]["@email"]
                p_to.description = m_data["header"]["to"]["participant"]["@description"]

                m.participant_to = [p_to]

            self.messages.append(m)


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
        self.daytime = None
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
        self.misc = {}


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
        ET.SubElement(header, "daytime").text = self.daytime
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

        if self.misc:
            misc = ET.SubElement(message, "misc")

            for key, value in self.misc.items():
                item = ET.SubElement(misc, "item")
                item.set("name", key)
                item.set("value", value)

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
        self.misc = {}


    def xml_serialize(self):
        participant = ET.Element("participant")

        participant.set("id", str(self.id))
        participant.set("role", self.role)
        participant.set("realname", self.real_name)
        participant.set("username", self.user_name)
        participant.set("email", self.email)
        participant.set("description", self.description)

        if self.misc:
            misc = ET.SubElement(participant, "misc")

            for key, value in self.misc.items():
                item = ET.SubElement(misc, "item")
                item.set("name", key)
                item.set("value", value)

        return participant