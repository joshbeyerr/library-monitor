import requests
from bs4 import BeautifulSoup
from art import *
import random
import webbrowser
import time
import threading


def is_valid_24h_time(input_str):
    # Split the input string using ":"
    time_parts = input_str.split(":")

    if len(time_parts) != 2:
        return False
    try:
        if len(time_parts[0]) != 2:
            return False

        hours = int(time_parts[0])
        minutes = int(time_parts[1])

        if 0 <= hours <= 23 and 0 <= minutes <= 59:
            return True
        else:
            return False
    except ValueError:
        # Conversion to integers failed
        return False


def is_time_afer():
    pass


class library:
    def __init__(self):
        self.year = '2023'
        self.library = None
        self.lid = None
        self.gid = None
        self.day = None
        self.month = None
        self.date_format = None
        self.start = None
        self.end = None
        self.username = None
        self.password = None
        self.s = requests.session()
        self.available_slots = None
        self.org = None
        self.data_time = None
        self.matching = None
        self.stop_monitor = False
        self.length = None  # in minutes
        self.matchingCount = None

        self.s.headers.update({
            'authority': 'calendar.lib.uwo.ca',
            'Referer': 'https://calendar.lib.uwo.ca/r/new/availability?',
            'Origin': 'https://calendar.lib.uwo.ca',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/117.0.0.0 Safari/537.36',
            'X-Requested-With': 'XMLHttpRequest'
        })
        if (self.s.get('https://calendar.lib.uwo.ca/r/new')).status_code != 200:
            print("Error Connecting To UWO")
            quit()

    def settingTimes(self):
        self.date_format = '{}/{}/{}'.format(self.year, self.month, self.day)

        # end of inputs needed
        self.start = '{}-{}-{}'.format(self.year, self.month, self.day)
        self.end = '{}-{}-{}'.format(self.year, self.month, str(int(self.day) + 1))

    def userrInfo(self):
        userInfo = {}
        with open('userInfo') as f:
            try:
                for x in f:
                    inf = x.split(':')
                    value = inf[0].strip(' ')
                    cleaned = (inf[1].strip(' ')).strip('\n')
                    if cleaned != '':
                        if value == 'month' or value == 'day':
                            if not cleaned.isdigit():
                                print('Invalid Day and/or Month Input')
                                quit()
                            if value == 'month':
                                if int(cleaned) < 1 or int(cleaned) > 12:
                                    print('INVALID MONTH, must be between 1 and 12')
                                    quit()
                            elif value == 'day':
                                if int(cleaned) < 1 or int(cleaned) > 31:
                                    print('INVALID DAY, must be between 1 and 31')
                                    quit()
                            if int(cleaned) < 10:
                                cleaned = '0{}'.format(cleaned)

                        userInfo[value] = cleaned
                    else:
                        print('Username and/or Password is blank')
                        quit()
            except:
                print('Error reading user info text file, exiting...')
                quit()

        if 'username' not in userInfo or 'password' not in userInfo or 'day' not in userInfo or 'month' not in userInfo:
            print('Missing a Value in userInfo text file -- Should include, username, password, day (1-31) and month '
                  '(1-12)')
            quit()

        self.month = str(userInfo['month'])
        self.day = str(userInfo['day'])

        self.settingTimes()

        self.username = userInfo['username']
        self.password = userInfo['password']

    def chooseLibrary(self):
        # data
        libraries = {'taylor': {'lid': '1348', 'gid': '2390'}, 'weldon': {'lid': '1349', 'gid': '2391'},
                     'ivey': {'lid': '1347', 'gid': '2388'}}

        # choose between taylor or weldon
        while True:
            print('Select a library:')
            print('1. Taylor Library')
            print('2. Weldon Library')
            print('3. Ivey Library')
            lib_select = input('Selection: ')
            if lib_select == '1':
                choose_library = 'taylor'
                break
            elif lib_select == '2':
                choose_library = 'weldon'
                break
            elif lib_select == '3':
                choose_library = 'ivey'
                break
            else:
                print('Invalid Library Selection, Try Again...\n\n')
        self.library = choose_library
        self.lid = libraries[choose_library]['lid']
        self.gid = libraries[choose_library]['gid']

        print('\nSelected {} Library For {}\n'.format(self.library.capitalize(), self.date_format))

    def grid(self):
        data = {'lid': self.lid,
                'gid': self.gid,
                'eid': '-1',
                'seat': '0',
                'seatId': '0',
                'zone': '0',
                'start': self.start,
                'end': self.end,
                'pageIndex': '0',
                'pageSize': '18'}

        # gets grid list of all library slots following the above search filters

        get_avai = (self.s.post('https://calendar.lib.uwo.ca/spaces/availability/grid', data=data))
        try:
            get_avai = get_avai.json()
            # It seems availability is indicated if the dicts include a className saying they have already been checked out
            # This filters for only available slots
            if not get_avai['slots']:
                self.available_slots = []
                self.org = []
            else:
                available_slots = [my_dict for my_dict in get_avai['slots'] if "className" not in my_dict]

                self.available_slots = available_slots

                org = {}
                for x in self.available_slots:
                    if x['itemId'] not in org:
                        org[x['itemId']] = [{'start': x['start'], 'end': x['end']}]
                    else:
                        org[x['itemId']].append({'start': x['start'], 'end': x['end']})
                self.org = org

            # goes through organized list of times per room - assigns a ranking to each time showing how many
            # consecutive available booking slots are in front of it with a maximum of 4 rooms/2 hours in a row
            for x in self.org:
                count = 0
                curRank = 0
                for i in reversed(self.org[x]):
                    if count == 0:
                        last = i['start']
                    else:
                        if i['end'] == last:
                            if curRank != 3:
                                curRank += 1
                        else:
                            curRank = 0
                        last = i['start']
                    (self.org[x][(len(self.org[x]) - 1) - count])['ranking'] = curRank
                    count += 1

            return True
        except:
            print('\n{}\n'.format(get_avai.text))
            return False

    def print_avai(self):
        conv = {0: "30 Minutes", 1: "1 Hour", 2: "1.5 Hours", 3: "2 Hours"}
        if self.org == {}:
            print('No Rooms Available For {}'.format(self.date_format))
        elif not self.org:
            print('Rooms Not Listed Yet For {}'.format(self.date_format))
        else:
            for x in self.org:
                print('Room {}:'.format(x))
                for i in self.org[x]:
                    print('    {} Available For Up To {}'.format(i['start'].split(' ')[1], conv[i['ranking']]))
        print('\n')

    def open_site(self):
        auth_url = 'https://calendar.lib.uwo.ca/r/new/availability?lid={}&zone={}&gid={}&capacity=2'.format(self.lid,
                                                                                                            '0',
                                                                                                            self.gid)
        auth_url = requests.Request('GET', auth_url).prepare().url
        webbrowser.open(auth_url)
        print('Browser Opened\n')

    def set_time(self, inTime):
        self.data_time = inTime

    def matchingFor(self, slots2):
        matching = []
        for x in slots2:
            if (x['start'].split(' '))[1] == self.data_time:
                matching.append(x)
        return matching

    def add(self):
        self.matching = self.matchingFor(self.available_slots)
        if len(self.matching) == 0:
            print('\nNo rooms available for that time, would you like to monitor? (y/n)')
            mon = input('Input:')
            if mon.lower() == "y":
                self.monitor()
                if self.stop_monitor:
                    return
            else:
                print('\n')
                return

        print('Starting')

        print("{} Available Rooms At {} {}".format(len(self.matching), self.data_time, self.date_format))

        print('Choosing Random Room...')
        chosen = random.choice(self.matching)

        data = {'add[eid]': chosen['itemId'],
                'add[gid]': self.gid,
                'add[lid]': self.lid,
                'add[start]': chosen['start'],
                'add[checksum]': chosen['checksum'],
                'lid': self.lid,
                'gid': self.gid,
                'start': self.start,
                'end': self.end,
                }

        # add booking to cart
        add = self.s.post('https://calendar.lib.uwo.ca/spaces/availability/booking/add', data=data)
        print('Added To Cart')
        print('\n')
        add = add.json()
        options = add['bookings'][0]['optionChecksums']

        # option stuff

        if len(options) > 1:
            print('How Long Would You Like To Book For?')
            times = {1: '30 Minutes', 2: '1 Hour', 3: '1 Hour 30 Minutes', 4: '2 Hours'}
            for x in range(1, (len(options) + 1)):
                print('  {}. {}'.format(x, times[x]))
            time_length = (input('Selection:'))
            if time_length != "1" and time_length != "2" and time_length != "3" and time_length != "4" :
                print("\nInvalid Time Length\n")
                return

            time_length = int(time_length) - 1

            if time_length != 1:
                if time_length > len(options):
                    print('Invalid Time Length')
                else:
                    data = {
                        'update[id]': add['bookings'][0]['id'],
                        'update[checksum]': options[time_length],
                        'update[end]': add['bookings'][0]['options'][time_length],
                        'lid': self.lid,
                        'gid': self.gid,
                        'start': self.start,
                        'end': self.end,
                        'bookings[0][id]': add['bookings'][0]['id'],
                        'bookings[0][eid]': chosen['itemId'],
                        'bookings[0][seat_id]': '0',
                        'bookings[0][gid]': self.gid,
                        'bookings[0][lid]': self.lid,
                        'bookings[0][start]': ((add['bookings'][0]['start']).rsplit(':', 1))[0],
                        'bookings[0][end]': ((add['bookings'][0]['end']).rsplit(':', 1))[0],
                        'bookings[0][checksum]': add['bookings'][0]['checksum']
                    }
                    add = (self.s.post('https://calendar.lib.uwo.ca/spaces/availability/booking/add', data=data)).json()
                    print('Updated Time')

        else:
            print('Only available for 30 minutes...')

        bookingChecksum = add['bookings'][0]['checksum']
        bookingID = add['bookings'][0]['id']
        start2 = ((add['bookings'][0]['start']).rsplit(':', 1))[0]
        end2 = ((add['bookings'][0]['end']).rsplit(':', 1))[0]

        data = {
            'libAuth': True,
            'blowAwayCart': True,
            'returnUrl': '/r/new?lid=1348&gid=2390&zone=204&capacity=2&date=2023-10-02&start=&end=',
            'bookings[0][id]': bookingID,
            'bookings[0][eid]': chosen['itemId'],
            'bookings[0][seat_id]': '0',
            'bookings[0][gid]': self.gid,
            'bookings[0][lid]': self.lid,
            'bookings[0][start]': start2,
            'bookings[0][end]': end2,
            'bookings[0][checksum]': bookingChecksum,
            'method': 13
        }

        # creating cart
        create_cart = self.s.post('https://calendar.lib.uwo.ca/ajax/space/createcart', data=data)
        print('Room Hold Secured... Finalizing Checkout')
        create_cart = create_cart.json()

        # creating redirect url
        link = 'https://calendar.lib.uwo.ca{}'.format(create_cart['redirect'])

        # requesting redirect url to initiate login
        go = self.s.get(link)

        # Find the input element with name="execution", needed for login authentication, encoded in the html
        soup = BeautifulSoup(go.text, 'html.parser')
        execution_input = (soup.find('input', {'name': 'execution'}))['value']

        # inputting  western username and password from variables above
        data = {
            'username': self.username,
            'password': self.password,
            'execution': execution_input,
            '_eventId': 'submit',
            'geolocation': '',
            'submit': 'Log In'

        }

        # "go" redirects to login page, capturing that url and submitting login info
        login_url = go.url
        print('Submitting Login Info...')
        loginn = self.s.post(login_url, data=data)

        # session id hidden in successful login pages html, SCRAPING THAT
        soup = BeautifulSoup(loginn.text, 'html.parser')
        session = (((soup.find('a', class_='s-lc-session-aware-link'))['href']).split('='))[1]

        data = {
            'returnUrl': create_cart['redirect'],
            'logoutUrl': 'logout',
            'session': session
        }

        # submitting final checkout
        checkout = self.s.post('https://calendar.lib.uwo.ca/ajax/equipment/checkout', data=data)
        if checkout.status_code == 200:
            print('Successfully Checked Out!')
        else:
            print('Error Reserving Room {}'.format(checkout.text))

    def monitor(self):
        self.stop_monitor = False
        print('\n')

        def user_input_thread():
            while True:
                user_input = input("Press 'q' at any time to stop monitoring\n")
                if user_input.lower() == 'q':
                    print("Stopping monitor...\n\n")
                    self.stop_monitor = True
                    break

        user_input_thread = threading.Thread(target=user_input_thread)
        user_input_thread.daemon = True
        user_input_thread.start()

        print('\nNo Rooms Available at {}, Starting Monitor...\n'.format(self.data_time))
        while True:
            if self.stop_monitor:
                break
            monitor = self.matchingFor(self.available_slots)
            if len(monitor) != 0:
                self.matching = monitor
                break
            else:
                print('Monitoring For Rooms at {}...'.format(self.data_time))
                for x in range(5):
                    if self.stop_monitor:
                        break
                    time.sleep(1)

    def refresh_file(self):
        with open('userInfo', 'w') as f:
            f.write("username: {}\npassword: {}\nday: {}\nmonth: {}".format(self.username, self.password, self.day,
                                                                            self.month))

    def setDay(self, day):
        if int(day) < 1 or int(day) > 31:
            print('\nINVALID DAY, must be between 1 and 31\n')
            return
        self.day = day
        self.settingTimes()
        self.refresh_file()

    def setLength(self, inLength):
        if inLength == '1' or inLength == '2' or inLength == '3' or inLength == '4':
            if inLength == '1':
                length = 30
            elif inLength == '2':
                length = 60
            elif inLength == '3':
                length = 90
            elif inLength == '4':
                length = 120
        else:
            print("\nInvalid Selection\n")
            return

        self.length = length
        print('\nSet Minimum Booking Length To {} Minutes'.format(self.length))

    def formatTimes(self):
        data = self.org
        if data == [] or data is None:
            print("\nNo Data To Display\n\n")
            return

        print('\n\n')
        print('x = available time slot\n')

        # Create a list of all unique times
        all_times = [f"{str(hour).zfill(2)}:{str(minute).zfill(2)}" for hour in range(8, 23) for minute in (0, 30)]

        # Calculate the width of each time slot
        time_slot_width = len(all_times[0]) + 1  # Each time slot plus an extra space

        # Create a dictionary to hold the schedule for each room
        room_schedules = {room_number: {time: '-' for time in all_times} for room_number in data.keys()}

        # Fill in the schedule dictionary
        for room_number, room_schedule in data.items():
            for entry in room_schedule:
                start_time = entry['start'].split()[-1][:5]  # Extract just the time part
                room_schedules[room_number][start_time] = 'x'

        # Calculate the padding for the start of the horizontal times
        time_padding = " " * 5  # 5 spaces

        # Print the matrix
        print(time_padding + "\t" + "\t".join(all_times))
        for room_number, schedule in room_schedules.items():
            row = [str(room_number)] + [schedule[time].center(time_slot_width) for time in all_times]
            print("\t".join(row))

        print('\n\n')
