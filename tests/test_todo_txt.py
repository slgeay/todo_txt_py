from datetime import date

import pytest
from click.testing import CliRunner

import todo_txt.app as app
from todo_txt.task import Task

todo_file = "todo.txt"
todo_str: str


@pytest.fixture(autouse=True)
def setup_function(pytester: pytest.Pytester):
    # Prepare fresh todo.txt for each test
    pytester.copy_example(todo_file)
    with open(todo_file, "r") as file:
        global todo_str
        todo_str = file.read()


def assert_file(expected=None):
    with open(todo_file, "r") as file:
        if not expected:
            global todo_str
            expected = todo_str
        assert file.read() == expected


def test_task_inout():
    line = "x 2021-04-12 Do this task"
    task = Task(line)

    assert str(task) == line


def test_list():
    runner = CliRunner()
    result = runner.invoke(app.list)

    assert result.exit_code == 0
    assert result.output == (
        "[0]: Post signs around the neighborhood +GarageSale\n"
        "[1]: (B) Schedule Goodwill pickup +GarageSale @phone\n"
        "[2]: (A) Thank Mom for the meatballs @phone\n"
        "[3]: @GroceryStore Eskimo pies\n"
        "[4]: x 2011-03-03 Call Mom\n"
    )


def test_list_sorted():
    runner = CliRunner()
    result = runner.invoke(app.list, ["-s"])

    assert result.exit_code == 0
    assert result.output == (
        "[2]: (A) Thank Mom for the meatballs @phone\n"
        "[1]: (B) Schedule Goodwill pickup +GarageSale @phone\n"
        "[0]: Post signs around the neighborhood +GarageSale\n"
        "[3]: @GroceryStore Eskimo pies\n"
        "[4]: x 2011-03-03 Call Mom\n"
    )


def test_list_filtered():
    runner = CliRunner()
    result = runner.invoke(app.list, ["-f", "Mom"])

    assert result.exit_code == 0
    assert (
        result.output
        == "[2]: (A) Thank Mom for the meatballs @phone\n\
[4]: x 2011-03-03 Call Mom\n"
    )


def test_complete():
    runner = CliRunner()
    result = runner.invoke(app.complete, ["0"])

    assert result.exit_code == 0
    assert_file(
        f"x {date.today()} Post signs around the neighborhood +GarageSale\n"
        "(B) Schedule Goodwill pickup +GarageSale @phone\n"
        "(A) Thank Mom for the meatballs @phone\n"
        "@GroceryStore Eskimo pies\n"
        "x 2011-03-03 Call Mom\n"
    )


def test_complete_index_error():
    runner = CliRunner()
    result = runner.invoke(app.complete, ["9"])

    assert result.exit_code == 1
    assert isinstance(result.exception, IndexError)
    assert_file()


def test_add():
    runner = CliRunner()
    result = runner.invoke(
        app.add, ["2011-03-01 Review Tim's pull request +TodoTxtTouch @github"]
    )

    assert result.exit_code == 0
    assert_file(
        "Post signs around the neighborhood +GarageSale\n"
        "(B) Schedule Goodwill pickup +GarageSale @phone\n"
        "(A) Thank Mom for the meatballs @phone\n"
        "@GroceryStore Eskimo pies\n"
        "x 2011-03-03 Call Mom\n"
        "2011-03-01 Review Tim's pull request +TodoTxtTouch @github\n"
    )


def test_delete():
    runner = CliRunner()
    result = runner.invoke(app.delete, ["2"])

    assert result.exit_code == 0
    assert_file(
        "Post signs around the neighborhood +GarageSale\n"
        "(B) Schedule Goodwill pickup +GarageSale @phone\n"
        "@GroceryStore Eskimo pies\n"
        "x 2011-03-03 Call Mom\n"
    )


def test_delete_index_error():
    runner = CliRunner()
    result = runner.invoke(app.delete, ["8"])

    assert result.exit_code == 1
    assert isinstance(result.exception, IndexError)
    assert_file()


def test_report():
    runner = CliRunner()
    result = runner.invoke(app.report)

    assert result.exit_code == 0
    assert result.output == (
        "5 tasks, 1 completed (20.0%)\n"
        "Task counts by priority:\n"
        "(A) -> 1\n"
        "(B) -> 1\n"
    )


def test_prioritise():
    runner = CliRunner()
    result = runner.invoke(app.prioritise, ["3", "D"])

    assert result.exit_code == 0
    assert_file(
        "Post signs around the neighborhood +GarageSale\n"
        "(B) Schedule Goodwill pickup +GarageSale @phone\n"
        "(A) Thank Mom for the meatballs @phone\n"
        "(D) @GroceryStore Eskimo pies\n"
        "x 2011-03-03 Call Mom\n"
    )


def test_prioritise_same():
    runner = CliRunner()
    result = runner.invoke(app.prioritise, ["1", "B"])

    assert result.exit_code == 0
    assert_file()


def test_prioritise_override():
    runner = CliRunner()
    result = runner.invoke(app.prioritise, ["1", "D"])

    assert result.exit_code == 0
    assert_file(
        "Post signs around the neighborhood +GarageSale\n"
        "(D) Schedule Goodwill pickup +GarageSale @phone\n"
        "(A) Thank Mom for the meatballs @phone\n"
        "@GroceryStore Eskimo pies\n"
        "x 2011-03-03 Call Mom\n"
    )


def test_prioritise_index_error():
    runner = CliRunner()
    result = runner.invoke(app.prioritise, ["9", "D"])

    assert result.exit_code == 1
    assert isinstance(result.exception, IndexError)
    assert_file()


def test_prioritise_priority_correct():
    runner = CliRunner()
    result = runner.invoke(app.prioritise, ["3", "DD"])

    assert result.exit_code == 0
    assert_file(
        "Post signs around the neighborhood +GarageSale\n"
        "(B) Schedule Goodwill pickup +GarageSale @phone\n"
        "(A) Thank Mom for the meatballs @phone\n"
        "(D) @GroceryStore Eskimo pies\n"
        "x 2011-03-03 Call Mom\n"
    )


def test_prioritise_priority_error():
    runner = CliRunner()
    result = runner.invoke(app.prioritise, ["3", "3"])

    assert result.exit_code == 1
    assert isinstance(result.exception, AssertionError)
    assert_file()


def test_deprioritise():
    runner = CliRunner()
    result = runner.invoke(app.deprioritise, ["2"])

    assert result.exit_code == 0
    assert_file(
        "Post signs around the neighborhood +GarageSale\n"
        "(B) Schedule Goodwill pickup +GarageSale @phone\n"
        "Thank Mom for the meatballs @phone\n"
        "@GroceryStore Eskimo pies\n"
        "x 2011-03-03 Call Mom\n"
    )


def test_deprioritise_index_error():
    runner = CliRunner()
    result = runner.invoke(app.deprioritise, ["9"])

    assert result.exit_code == 1
    assert isinstance(result.exception, IndexError)
    assert_file()
