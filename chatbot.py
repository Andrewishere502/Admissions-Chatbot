import re
import datetime
from typing import Iterable

from nltk import pos_tag
from nltk.tokenize import word_tokenize
from nltk.stem import PorterStemmer
from nltk.corpus import stopwords

from question_types import QuestionError, How, What, When, Why, Misc


class Chatbot:
    def __init__(self) -> None:
        self.next_reply = None
        self.collect_data = None
        return

    @staticmethod
    def identify_instruction(sent: str) -> Iterable[str]:
        """Return a list of instruction key words. If no key words are
        found, return and empty list.

        This list should be narrowed down using the
        .refine_instructions method to obtain a single key word.
        """
        instruction_words = {"how": ("how",),
                             "when": ("when",),
                             "what": ("what",),
                             "why": ("why",),
                             "yn": ("do", "does", "is", "are", "will", "if")
                            }
        matched_instructions = set([])
        for word, triggers in instruction_words.items():
            for trigger in triggers:
                if re.match(trigger, sent):
                    matched_instructions.add(word)
        return tuple(matched_instructions)

    @staticmethod
    def refine_instructions(matched_instructions: Iterable[str]) -> str:
        """Return 'unknown' if an no possible instruction is found.
        If only on possible instruction is found, return this
        instruction.

        Note: it is impossible for multiple instructions to be matched
              because there is no overlap between the trigger words for
              each instruction.
        """
        if len(matched_instructions) == 0:
            instruction = "unknown"  # will return non from types
        elif len(matched_instructions) == 1:
            instruction = matched_instructions[0]
        else:  # Multiple instructions matched
            pass  # Not possible with the current instruction_words
        return instruction

    @staticmethod
    def make_nouns_singular(sent):
        """Return sent with all nouns changed to singular"""
        sent = sent.replace("children", "child")  # word stemmer won't
                                                  # catch children
        tagged_sent = pos_tag(word_tokenize(sent), tagset='universal')
        nouns = filter(lambda wpair: wpair[1] == "NOUN", tagged_sent)
        words_to_replace = [(wpair[0], PorterStemmer().stem(wpair[0]))
                            for wpair in nouns]
        new_sent = sent
        for wpair in words_to_replace:
            new_sent = new_sent.replace(*wpair)
        return new_sent

    def answer(self, sent: str) -> str:
        sent = sent.lower().strip()  # without this likely
                                     # get 'unknown: TYPE MISSING'
        if self.next_reply == None:
            possible_instructions = self.identify_instruction(sent)
            instruction = self.refine_instructions(possible_instructions)
            types = {"how": How,
                    "when": When,
                    "what": What,
                    "why": Why,
                    "yn": Misc
                    }

            sent = self.make_nouns_singular(sent)
            question_type = types.get(instruction)  # may return None
            try:
                answer = question_type().answer(sent)
            except TypeError:  # question_type is None, so no instance
                               # can be made of question_type.
                answer = "unknown: TYPE MISSING"
            if not isinstance(answer, str):  # detailed answer needs more input
                answer, self.next_reply, self.collect_data = answer  # answer is tuple
        else:
            data = self.collect_data(sent)
            # chatbot didn't find the data required from the input
            if isinstance(data, QuestionError):
                if data.msg == None:  # user asked something unrelated
                    self.next_reply = None
                    answer = self.answer(sent)
                else:
                    answer = data.msg  # message to explain user error
            else:  # follow up data was found
                answer = self.next_reply.format(data)
                self.next_reply = None
        return answer


if __name__ == "__main__":
    chatbot = Chatbot()
    # print(chatbot.answer("What are the medical check-up requirements for enrolling at ASW?"))
    print(chatbot.answer(input("")))
    # reg = re.search(r"old (.*) child (.*)* enroll", "How old should my child be to enroll at ASW")
    # print(reg)