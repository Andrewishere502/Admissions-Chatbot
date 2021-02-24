import re
import datetime

from pytable import Table
from data_tables import EnrollmentAgeChart


# remember to watch for these --> ’ it is not a '
            # ’ '

class QuestionError:
    def __init__(self, cause, msg=None):
        self.cause = cause
        self.msg = msg
        return


class QuestionType:
    def __init__(self, matches):
        self.matches = matches
        return

    def answer(self, sent):
        """Return an answer for the a question type."""
        for key in self.matches:
            if re.search(key, sent):
                # does not account for possibility of multiple matches
                # since any match immediately returns
                return self.matches[key]
        return "unknown: NO ANSWER"


class How(QuestionType):
    def __init__(self):
        matches = {
            r"(i|we) apply": "Please download and follow the step-by-step User Guide to Admissions 2020-2021 for specific information on each step. If you have any questions or queries about the application process, please contact the Admissions team.",
            r"old (.*) child (.*)* enroll": """Candidates for Pre-Kindergarten – Grade 1 will be placed strictly by age. Placement in Grades 2-12 is determined by evaluating the student’s age, development, and previous school experience. The final decision will be made by the School Principal after review and evaluation of the child’s application.
It is important that students have completed a full grade level (American system equivalent) before advancing to the next grade level. If a student has not completed a grade level when enrolling at ASW, he/she will be placed in the same grade level to ensure completion of that grade level.
Any student’s course of study must be completed before he/she reaches his/her 21st birthday.""",
            "space allocated": """The date of the application is the date when the application form has been submitted and the application fee paid. The application cannot be reviewed, however, until the supporting documentation has been submitted as well. Visit the FAQ for a more detailed answer""",
            "different academic year transit": """Each student's record is considered carefully. Normally, students who have just completed a grade level (American system equivalent) in their home country will not be promoted to the next grade level mid-year at ASW as this would mean skipping months or even
a full semester of that year's work and leading to gaps in learning. Additionally, students who in future years return to an alternative calendar are often significantly impacted even more. Review of a student's full record, relevant assessments, and other pertinent information may be used in making an alternative
placement, if the body of evidence supports that decision after being reviewed by school administration.""",
            r"long (.*)* day": """School starts at 8:30 and ends at 15:30. For grades 11 and 12, the school day starts at 8.20 and finishes at 15.20.
On Wednesdays, all students start school at 9:30 and end at 15:30.
There are a variety of after-school activities at the end of the school day.""",
            r"(i|we) apply (.*) special (.*)* needs": """Parents of students with identified learning needs are invited to submit an application form and all relevant assessment reports or evaluations that can help us understand their child’s learning needs.
Previous Learning Support plans (such as IEP/ILP/SSP/LSP, 504 plans or Accommodation Plans) must also be included. The school may request further assessment information, may wish to interview the parent and/or student, and may ask to contact the previous school. In cases where there is no formal evaluation but it is suspected that Learning Support services are needed, ASW may require such testing as a condition for admission or for re-enrollment.
Each admission is reviewed on a case-by-case basis by a team that includes the divisional counsellors, principals, learning support team members and the Head of Learning Support. The team carefully considers all of the available information to determine whether ASW will be able to support the student’s needs within our current program.
ASW may not admit a student or may withdraw its offer of admission in the case where information is withheld."""
        }
        super().__init__(matches)
        return
    

class When(QuestionType):
    def __init__(self):
        matches = {
            r"(i|we) apply": """Annual application process: Applications for the 2020-2021 school year can be submitted starting from September 2019. Families applying for mid-year enrolment can also apply one year ahead.
If you are interested in enrolling your child in more than 12 months from now, please complete our online inquiry form and we will contact you when applications open.
Most of the spaces are allocated by April but openings may become available in the months after that.""",
        }
        super().__init__(matches)
        return


class What(QuestionType):
    def __init__(self):
        matches = {
            "grade": ("It depends on their age. What is the date of their birth? (dd/mm/yyyy)", "They would be in {} at ASW.", self.get_grade),
            "academic year": "We typically start school in the second half of August and end the year mid June.",
            r"differ (.*) accept (.*) admiss": "A student is accepted when after evaluation of the application it is confirmed that he or she meets the acceptance requirements. Admission is when a space is available and the student can be placed in the class or program.",
            r"medical (.*) requir": """Each newly admitted student must have a medical check-up prior to enrolling. The Physical Examination form must be completed by a qualified, licensed health care provider. The check-up should be done no more than 12 months prior
to the student's start date. It must include proof of a Tuberculosis screening and a copy of the child's vaccination record. A student is not authorised to start school unless the completed Physical Examination form has been submitted to ASW.
Information about the student's health and medical history will be kept confidential at the school's Nurse's Office."""
            }
        super().__init__(matches)
        return

    @staticmethod
    def get_grade(msg):
        try:
            msg = msg.replace(" ", "")  # eliminates spaces, '1 / 2 / 2013' = '1/2/2013'
            birthdate = re.search(r"(?P<day>\d{1,2})(/|-)(?P<month>\d{1,2})(/|-)(?P<year>\d{4})", msg).groupdict()
        except AttributeError:
            cause = "User asked a different question, ignoring the follow up."
            return QuestionError(cause)

        birthdate = {key: int(value) for key, value in birthdate.items()}

        try:
            birthdate = datetime.date(**birthdate)
        except ValueError:
            cause = "User didn't enter the date in correctly."
            msg = "Sorry, that does not seem to be a valid dat in the dd/mm/yyyy format. So what was the birthdate again?"
            return QuestionError(cause, msg)

        querry = "bday_range_start <= <date>{bd} and bday_range_end >= <date>{bd}".format(bd=birthdate)
        results = EnrollmentAgeChart().search_by_value(querry, "us_grade")
        grade = results[0]
        return grade


class Why(QuestionType):
    def __init__(self):
        matches = {
            r"(child|kid|daughter|son) (.*)* waiting list": """ASW has maximum class sizes per grade level, as well as nationality capacity guidelines, and a limited number of spaces in selected programmes such as EAL (English as an Additional Language) and Learning Support.
As enrollment is dynamic, spaces may open at any time during the school year. Please contact the Admissions Office if you would like to know more about the current situation.""",
            }
        super().__init__(matches)
        return


class Misc(QuestionType):
    def __init__(self):
        matches = {
            r"take (.*) placement test": "Students applying for Grades 6-12 whose mother tongue is not English or who have not been using English as their primary academic language, will be asked to complete an English language test. Tests in math and foreign language may also be administered to determine appropriate placement in these courses.",
            "toilet trained": "Students applying for admission to Pre-Kindergarten must be fully toilet-trained before the first day of school (no diapers/nappies). They also must be able to feed and dress themselves reasonably independently.",
            r"child (.*) not (.*) admitted (.*) new (.*){0,1} year (.*)+ re-apply": """Once an application has been submitted, you do not need to re-apply nor pay the application fee again. We may ask you for updated information on your child’s academic progress.
Your child will remain on the waiting list and we will periodically provide you with an update on his or her admissions status. Should you decide to withdraw your child from the waiting list, please let us know in writing. Application fee is valid for one academic year.""",
            "applic fee refund": """The application fee is a non-refundable administrative fee, charged to cover the costs of processing your child's application, including testing and interviewing if required.
The application fee is only valid for the school year in which you are applying. The application fee will be charged for former students re-applying to ASW who are submitting an application for a second time.
Applications will not be processed until the full application fee has been paid.
Payment may be made in cash at the school's cashier office or by bank transfer. Please contact the Admissions Office for ASW's bank details.""",
            "meal provided": """Fresh, healthy meals and snacks are offered in our cafeteria for a fee. Students may also bring their own lunch from home.""",
            "transport provided": """A door-to-door bus service is available for a fee for students living in the wider Warsaw area. At the end of the school day buses depart right after school and again at the end of after-school activities.""",
            "uniform": """At ASW students do not wear a school uniform but are required to dress appropriately for school. Middle and High School students have a Physical Education uniform.""",
            r"accept (.*) special (.*) need": """ASW welcomes students with a wide range of abilities and interests.
Each division, Elementary, Middle and High School, has a Learning Support Program. The program is designed to provide assistance to struggling learners and students who have an identified mild to moderate learning disability or learning difference that requires educational support.
Students who require an intense level of learning support or a special education program are assessed on a case-by-case basis to determine if ASW has the programs and resources in place to serve their needs. Admission to ASW will be contingent upon outcome of this assessment.
Please contact us if your child has special learning needs and you have questions or concerns about the feasibility of an application.""",
            "provide boarding": """ASW does not offer boarding. Students enrolled at ASW must reside with their parents or a legal guardian.
If you are absent from home for a short period of time, an adult guardian must take responsibility for your child's welfare. You should also submit written notice of such temporary guardianship to the Principal's office.""",
            r"need (.*) all applic document": """Only complete applications can be evaluated for admission. A complete application consists of application forms, supporting documentation and payment of the USD$ 550 application fee. Please download and follow the User Guide to online application and admissions process for detailed instructions.""",
            }
        super().__init__(matches)
        return


if __name__ == "__main__":
    question_types = [How, When, What, Why, Misc]
    total = 0
    for question_type in question_types:
        for match in question_type().matches:
            total += 1
    print("There are a total of {} questions".format(total))