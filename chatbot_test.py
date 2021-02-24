import unittest

from chatbot import Chatbot


class ChatbotTest(unittest.TestCase):
    def setUp(self):
        self.chatbot = Chatbot()
        return

    def test_what_grade(self):
        """Test if the follow up question system works."""
        q = "What grade will my kid be in?"
        self.chatbot.answer(q)
        a = self.chatbot.answer("he was born on 1-10-2016")
        assert(a == "They would be in Pre-Kindergarden at ASW.")

    def test_what_grade_error(self):
        """Test if the chatbot can determine when a follow up question
        is ignored.
        """
        q = "What grade will my kid be in?"
        self.chatbot.answer(q)
        a = self.chatbot.answer("When do I apply")
        assert(a[:27] == "Annual application process:")

    def test_when_apply(self):
        """Test basic 'when' question"""
        q = "When do I apply?"
        a = self.chatbot.answer(q)
        # Only test that the beginning of the answer matches because
        # the full answer is obnoxiosly long
        assert(a[:27] == "Annual application process:")

    def test_age_to_enroll(self):
        """Test basic 'how' question"""
        q = "How old should my children be to enroll?"
        a = self.chatbot.answer(q)
        assert(a[:31] == "Candidates for Pre-Kindergarten")


if __name__ == "__main__":
    unittest.main()

