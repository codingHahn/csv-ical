"""
This file reads the CSV file and saves an ical file.
There are a bunch of configurable variables
"""

from icalendar import Calendar, Event, Timezone
from icalendar.cal import Component
from typing import Dict, List  # NOQA
from platform import uname
from base64 import b64encode
import csv
import datetime
import pytz


DEFAULT_CONFIG = {
        'HEADER_ROWS_TO_SKIP':  0,

        # The variables below refer to the column indexes in the CSV
        'CSV_NAME': 0,
        'CSV_START_DATE': 1,
        'CSV_END_DATE': 1,
        'CSV_DESCRIPTION': 2,
        'CSV_LOCATION': 3,
        }

vtimezone_str = \
"""
BEGIN:VTIMEZONE
TZID:Europe/Berlin
TZURL:http://tzurl.org/zoneinfo/Europe/Berlin
X-LIC-LOCATION:Europe/Berlin
BEGIN:DAYLIGHT
TZOFFSETFROM:+0100
TZOFFSETTO:+0200
TZNAME:CEST
DTSTART:19810329T020000
RRULE:FREQ=YEARLY;BYMONTH=3;BYDAY=-1SU
END:DAYLIGHT
BEGIN:DAYLIGHT
TZOFFSETFROM:+0100
TZOFFSETTO:+0200
TZNAME:CEST
DTSTART:19160430T230000
RDATE:19160430T230000
RDATE:19170416T020000
RDATE:19180415T020000
RDATE:19400401T020000
RDATE:19430329T020000
RDATE:19440403T020000
RDATE:19450402T020000
RDATE:19460414T020000
RDATE:19470406T030000
RDATE:19480418T020000
RDATE:19490410T020000
RDATE:19800406T020000
END:DAYLIGHT
BEGIN:DAYLIGHT
TZOFFSETFROM:+0200
TZOFFSETTO:+0300
TZNAME:CEMT
DTSTART:19450524T010000
RDATE:19450524T010000
RDATE:19470511T020000
END:DAYLIGHT
BEGIN:DAYLIGHT
TZOFFSETFROM:+0300
TZOFFSETTO:+0200
TZNAME:CEST
DTSTART:19450924T030000
RDATE:19450924T030000
RDATE:19470629T030000
END:DAYLIGHT
BEGIN:STANDARD
TZOFFSETFROM:+0200
TZOFFSETTO:+0100
TZNAME:CET
DTSTART:19961027T030000
RRULE:FREQ=YEARLY;BYMONTH=10;BYDAY=-1SU
END:STANDARD
BEGIN:STANDARD
TZOFFSETFROM:+005328
TZOFFSETTO:+0100
TZNAME:CET
DTSTART:18930401T000000
RDATE:18930401T000000
END:STANDARD
BEGIN:STANDARD
TZOFFSETFROM:+0200
TZOFFSETTO:+0100
TZNAME:CET
DTSTART:19161001T010000
RDATE:19161001T010000
RDATE:19170917T030000
RDATE:19180916T030000
RDATE:19421102T030000
RDATE:19431004T030000
RDATE:19441002T030000
RDATE:19451118T030000
RDATE:19461007T030000
RDATE:19471005T030000
RDATE:19481003T030000
RDATE:19491002T030000
RDATE:19800928T030000
RDATE:19810927T030000
RDATE:19820926T030000
RDATE:19830925T030000
RDATE:19840930T030000
RDATE:19850929T030000
RDATE:19860928T030000
RDATE:19870927T030000
RDATE:19880925T030000
RDATE:19890924T030000
RDATE:19900930T030000
RDATE:19910929T030000
RDATE:19920927T030000
RDATE:19930926T030000
RDATE:19940925T030000
RDATE:19950924T030000
END:STANDARD
BEGIN:STANDARD
TZOFFSETFROM:+0100
TZOFFSETTO:+0100
TZNAME:CET
DTSTART:19460101T000000
RDATE:19460101T000000
RDATE:19800101T000000
END:STANDARD
END:VTIMEZONE"""


class Convert():
    def __init__(self):
        self.csv_data = []  # type: List[List[str]]
        self.cal = None  # type: Calendar

    def _generate_configs_from_default(self, overrides=None):
        # type: (Dict[str, int]) -> Dict[str, int]
        """ Generate configs by inheriting from defaults """
        config = DEFAULT_CONFIG.copy()
        if not overrides:
            overrides = {}
        for k, v in overrides.items():
            config[k] = v
        return config

    def read_ical(self, ical_file_location):  # type: (str) -> Calendar
        """ Read the ical file """
        with open(ical_file_location, 'r', encoding='utf-8') as ical_file:
            data = ical_file.read()
        self.cal = Calendar.from_ical(data)
        return self.cal

    def read_csv(self, csv_location, csv_configs=None):
        # type: (str, Dict[str, int]) -> List[List[str]]
        """ Read the csv file """
        csv_configs = self._generate_configs_from_default(csv_configs)
        with open(csv_location, 'r', encoding='utf-8') as csv_file:
            csv_reader = csv.reader(csv_file)
            self.csv_data = list(csv_reader)
        self.csv_data = self.csv_data[csv_configs['HEADER_ROWS_TO_SKIP']:]
        return self.csv_data

    def make_ical(self, csv_configs=None):
        # type: (Dict[str, int]) -> Calendar
        """ Make iCal entries """
        csv_configs = self._generate_configs_from_default(csv_configs)
        self.cal = Calendar()
        self.cal.add('version', '2.0')
        self.cal.add('prodid', 'Custom Rapla to csv to ics converter')
        timezone = Timezone()

        timezone = Component.from_ical(vtimezone_str)
        self.cal.add_component(timezone);
        for row in self.csv_data:
            event = Event()
            event.add('summary', row[csv_configs['CSV_NAME']])
            event.add('dtstart', row[csv_configs['CSV_START_DATE']])
            event.add('dtend', row[csv_configs['CSV_END_DATE']])
            event.add('description', row[csv_configs['CSV_DESCRIPTION']])
            event.add('location', row[csv_configs['CSV_LOCATION']])
            event.add('uid', b64encode((row[csv_configs['CSV_START_DATE']].strftime("%Y-%m-%d %H:%M") +
                row[csv_configs['CSV_END_DATE']].strftime("%Y-%m-%d %H:%M") +
                row[csv_configs['CSV_DESCRIPTION']] + '@' + uname()[1]).encode('utf-8')))
            event.add('dtstamp', datetime.datetime.now())
            self.cal.add_component(event)

        return self.cal

    def make_csv(self):  # type: () -> None
        """ Make CSV """
        for event in self.cal.subcomponents:
            if event.name != 'VEVENT':
                continue
        row = [
                event.get('SUMMARY'),
                event.get('DTSTART').dt,
                event.get('DTEND').dt,
                event.get('DESCRIPTION'),
                event.get('LOCATION'),
                ]
        row = [str(x) for x in row]
        self.csv_data.append(row)

    def save_ical(self, ical_location):  # type: (str) -> None
        """ Save the calendar instance to a file """
        data = self.cal.to_ical()
        with open(ical_location, 'wb') as ical_file:
            ical_file.write(data)

    def save_csv(self, csv_location):  # type: (str) -> None
        """ Save the csv to a file """
        with open(csv_location, 'w', encoding='utf-8') as csv_handle:
            writer = csv.writer(csv_handle)
        for row in self.csv_data:
            writer.writerow([r.strip() for r in row])
