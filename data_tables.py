import datetime

from pytable import Table

class EnrollmentAgeChart(Table):
    def __init__(self) -> None:
        column_names = ("age", "bday_range_start", "bday_range_end", "us_grade", "uk_year", "section")
        current_year = datetime.datetime.now().year
        rows_content = (
                (3, 
                 datetime.date(current_year - 4, 10, 1),
                 datetime.date(current_year - 3, 9, 30),
                 "Pre-Kindergarden",
                 "Nursery",
                 "Elementary School"
                    ),
                (4, 
                 datetime.date(current_year - 5, 10, 1),
                 datetime.date(current_year - 4, 9, 30),
                 "Pre-Kindergarden",
                 "Reception",
                 "Elementary School"
                    ),
                (5, 
                 datetime.date(current_year - 6, 10, 1),
                 datetime.date(current_year - 5, 9, 30),
                 "Kindergarden",
                 "Year 1",
                 "Elementary School"
                    ),
                (6, 
                 datetime.date(current_year - 7, 10, 1),
                 datetime.date(current_year - 6, 9, 30),
                 "Grade 1",
                 "Year 2",
                 "Elementary School"
                    ),
                (7, 
                 datetime.date(current_year - 8, 10, 1),
                 datetime.date(current_year - 7, 9, 30),
                 "Grade 2",
                 "Year 3",
                 "Elementary School"
                    ),
                (8, 
                 datetime.date(current_year - 9, 10, 1),
                 datetime.date(current_year - 8, 9, 30),
                 "Grade 3",
                 "Year 4",
                 "Elementary School"
                    ),
                (9,
                 datetime.date(current_year - 10, 10, 1),
                 datetime.date(current_year - 9, 9, 30),
                 "Grade 4",
                 "Year 5",
                 "Elementary School"
                    ),
                (10,
                 datetime.date(current_year - 11, 10, 1),
                 datetime.date(current_year - 10, 9, 30),
                 "Grade 5",
                 "Year 6",
                 "Elementary School"
                    ),
                (11,
                 datetime.date(current_year - 12, 10, 1),
                 datetime.date(current_year - 11, 9, 30),
                 "Grade 6",
                 "Year 7",
                 "Middle School"
                    ),
                (12,
                 datetime.date(current_year - 13, 10, 1),
                 datetime.date(current_year - 12, 9, 30),
                 "Grade 7",
                 "Year 8",
                 "Middle School"
                    ),
                (13,
                 datetime.date(current_year - 14, 10, 1),
                 datetime.date(current_year - 13, 9, 30),
                 "Grade 8",
                 "Year 9",
                 "Middle School"
                    ),
                (14,
                 datetime.date(current_year - 15, 10, 1),
                 datetime.date(current_year - 14, 9, 30),
                 "Grade 9",
                 "Year 10",
                 "High School"
                    ),
                (15,
                 datetime.date(current_year - 16, 10, 1),
                 datetime.date(current_year - 15, 9, 30),
                 "Grade 10",
                 "Year 11",
                 "High School"
                    ),
                (16,
                 datetime.date(current_year - 17, 10, 1),
                 datetime.date(current_year - 16, 9, 30),
                 "Grade 11",
                 "Year 12",
                 "High School"
                    ),
                (17,
                 datetime.date(current_year - 18, 10, 1),
                 datetime.date(current_year - 17, 9, 30),
                 "Grade 12",
                 "Year 13",
                 "High School"
                    )
            )
        super().__init__(column_names, rows_content=rows_content)
        return


if __name__ == "__main__":
    print(EnrollmentAgeChart().search_by_value("bday_range_start <= <date>2012-11-12 and bday_range_end >= <date>2012-11-12", "us_grade"))
