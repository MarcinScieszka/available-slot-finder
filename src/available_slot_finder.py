import argparse
import os
from itertools import combinations
from datetime import datetime, timedelta
from operator import itemgetter
from pathlib import Path


def parse_arguments():
    """Parse arguments provided by the user"""

    parser = argparse.ArgumentParser()
    parser.add_argument("-calendars", "--calendars",
                        help="Folder containing calendars", type=str, required=True)
    parser.add_argument("-duration_in_minutes", "--duration-in-minutes",
                        help="Desired duration in minutes", type=int, metavar='positional-args', required=True)
    parser.add_argument("-minimum_people", "--minimum-people",
                        help="Minimum amount of people", type=int, required=True)

    args = parser.parse_args()

    return args.calendars, args.duration_in_minutes, args.minimum_people


def validate_calendars_path(calendars_path: Path) -> bool:
    if calendars_path.is_dir():
        dir_exists = True
    else:
        print(f"The system cannot find the path specified: {calendars_path}")
        dir_exists = False

    return dir_exists


def get_calendar_file_names(calendars_path, minimum_people):
    """Function returns file names for every calendar (*.txt file) specified in path provided by the user"""

    files: list[str] = []
    for file in os.listdir(calendars_path):
        if file.endswith(".txt"):
            files.append(file)

    if len(files) == 0:
        raise Exception(f"Could not find any calendar (.txt file) in the path specified: {calendars_path}") from None
    elif len(files) < minimum_people:
        raise Exception(f"Not enough calendars (.txt files) for desired minimum amount of people.\n"
              f"Found {len(files)} people's calendars - {minimum_people} was required.") from None

    return files


def get_calendar_date_ranges(calendar_files, calendars):
    """Function returns list of date ranges for each calendar"""

    calendar_date_ranges = {}
    current_date = datetime.now()
    for file in calendar_files:
        with open(os.path.join(calendars, file), 'r') as f:
            date_ranges = []
            for line in f:
                dates = line.strip('\n')
                start_date_time_obj, end_date_time_obj = validate_date_range_format(dates)
                if end_date_time_obj > current_date:  # keep ranges that end in the future
                    date_ranges.append((start_date_time_obj, end_date_time_obj))

            calendar_date_ranges[file] = date_ranges

    return calendar_date_ranges


def validate_date_range_format(dates):
    date_string = dates.split(" - ")
    try:
        start_date_time_obj = datetime.strptime(date_string[0], '%Y-%m-%d %H:%M:%S')
        end_date_time_obj = datetime.strptime(date_string[1], '%Y-%m-%d %H:%M:%S')
    except ValueError:
        try:
            entire_day_date_time_obj = datetime.strptime(date_string[0], '%Y-%m-%d')
            start_date_time_obj = entire_day_date_time_obj.replace(hour=0, minute=0, second=0)
            end_date_time_obj = entire_day_date_time_obj.replace(hour=23, minute=59, second=59)
        except ValueError:
            raise ValueError(f"time data '{date_string}' does not match format 'Y-%m-%d %H:%M:%S - Y-%m-%d %H:%M:%S' "
                  f"or format '%Y-%m-%d'") from None

    return start_date_time_obj, end_date_time_obj


def find_available_slot(calendar_date_ranges, duration_in_minutes, minimum_people):
    """Function returns the closest available time slot of duration_in_minutes that is suitable for minimum_people"""

    current_date_string = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    current_date = datetime.strptime(current_date_string, '%Y-%m-%d %H:%M:%S')

    comb = combinations(calendar_date_ranges, minimum_people)
    for calendar_combination in comb:
        #  find available slot within every possible calendar combination of len equal to minimum_people
        date_ranges = []  # list combining all date ranges within given combination

        for calendar in calendar_combination:
            date_ranges.append(calendar_date_ranges[calendar])

        # flatten multiple lists of ranges into one list
        date_ranges = [date_range for date_ranges in date_ranges for date_range in date_ranges]

        # sort date ranges based on range start
        date_ranges = sorted(date_ranges, key=lambda tup: tup[0])

        if not bool(date_ranges):
            # date_ranges is empty -> no restricting time range -> now is a good time for a meeting
            return datetime.now()

        if date_ranges[0][0] > current_date:
            # check if now will be suitable for a time slot
            slot_time = date_ranges[0][0] - current_date
            slot_time_in_minutes = slot_time.total_seconds() / 60
            if slot_time_in_minutes > duration_in_minutes:
                # current datetime is suitable for time slot
                return datetime.now()

        # set initial time slot as a biggest datetime value from time ranges
        available_time_slot = max(date_ranges, key=itemgetter(1))[1]

        i = -1
        shift = 0
        while i < (len(date_ranges) - 2):
            i += 1
            if date_ranges[i + shift][0] < date_ranges[i + 1][0] and \
                    date_ranges[i + shift][1] > date_ranges[i + 1][1]:
                # next range is contained within previous range (skip range i+1, keep range i)
                shift -= 1  # shift used to keep longer time range for further iterations
            elif date_ranges[i + 1][0] < date_ranges[i + shift][1] < date_ranges[i + 1][1]:
                # there is no available time slot (ranges intersect)
                shift = 0
                continue
            else:
                shift = 0

            time_slot_value = date_ranges[i + 1][0] - date_ranges[i + shift][1]
            available_time_slot_in_minutes = time_slot_value.total_seconds() / 60
            if available_time_slot_in_minutes > duration_in_minutes \
                    and date_ranges[i + shift][1] < available_time_slot:
                available_time_slot = date_ranges[i + shift][1]
                break

    return available_time_slot + timedelta(seconds=1)





def main():
    calendars_path, duration_in_minutes, minimum_people = parse_arguments()
    if not validate_calendars_path(Path(calendars_path)):
        return

    calendar_files = get_calendar_file_names(calendars_path, minimum_people)
    calendar_date_ranges = get_calendar_date_ranges(calendar_files, calendars_path)
    available_slot = find_available_slot(calendar_date_ranges, duration_in_minutes, minimum_people)
    print(f"Closest available slot: {available_slot}")


if __name__ == '__main__':
    main()
