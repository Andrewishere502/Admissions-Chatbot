import datetime
from typing import Iterable, Union

class Table:
    def __init__(self, column_names: Iterable[str], rows_content: Iterable[Iterable[Union[int, str]]]=None) -> None:
        for col_name in column_names:
            if " " in col_name:
                raise ValueError("can not have ' ' in column name")
        self.column_names = column_names
        self.rows = []
        if rows_content != None:
            self.add_rows(rows_content)
        return

    def __repr__(self):
        repr_table = (self.column_names, self.rows)
        return str(repr_table)

    def __getitem__(self, i):
        return self.rows[i]

    def add_row(self, row_content: Iterable) -> None:
        if len(row_content) < len(self.column_names):
            raise ValueError("not enough rows to add")
        self.rows.append(tuple(row_content))
        return

    def add_rows(self, rows_content: Iterable[Iterable[Union[int, str]]]) -> None:
        for row_content in rows_content:
            self.add_row(row_content)
        return

    def del_row(self, row_num: int) -> None:
        self.rows.pop(row_num)
        return

    def search_by_col(self, column_name: str) -> Iterable[str]:
        col_num = self.column_names.index(column_name)
        return [row[col_num] for row in self.rows]

    def search_by_value(self, condition: str, display_col: Union[str, int]="all") -> None:
        conditions = condition.split(" and ")
        for i, _ in enumerate(conditions):
            conditions[i] = conditions[i].split()
            col_name, opp, value = conditions[i]
            if value[0:6] == "<date>":
                value = value[6:]
                value = value.split("-")
                value = [int(i) for i in value]
                value = datetime.date(*value)
            elif not (value[0] == "'" or value[-1] == "'"):  # value is not meant to be str
                value = int(value)
            else:
                value = value[1:-1]
            conditions[i] = col_name, opp, value

        matched_rows = self.rows.copy()
        for col_name, opp, value in conditions:
            for row in matched_rows.copy():
                col_num = self.column_names.index(col_name)
                if opp == "==":
                    if row[col_num] != value:
                        matched_rows.remove(row)
                elif opp == ">":
                    if row[col_num] <= value:
                        matched_rows.remove(row)
                elif opp == "<":
                    if row[col_num] >= value:
                        matched_rows.remove(row)
                elif opp == ">=":
                    if row[col_num] < value:
                        matched_rows.remove(row)
                elif opp == "<=":
                    if row[col_num] > value:
                        matched_rows.remove(row)

        if display_col != "all":
            display_col_num = self.column_names.index(display_col)
            matched_rows = [row[display_col_num] for row in matched_rows]
        return matched_rows


if __name__ == "__main__":
    employees = Table(("num", "name", "likes_to_skydive"))
    employees.add_rows(((1, "Joe", True), (2, "Jane", False), (3, "Joe", False), (4, "Harry", False)))
    results = employees.search_by_value("name == 'Joe' and num > 1")
    print(results)
