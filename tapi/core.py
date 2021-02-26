from .runner import run_all_test_cases, open_test_report
from .parse import get_all_test_case
from .make import generate_test_case_scripts


def main(open_report=False):
    data = get_all_test_case()
    generate_test_case_scripts(data)
    run_all_test_cases()
    if open_report:
        open_test_report()


if __name__ == '__main__':
    main()
