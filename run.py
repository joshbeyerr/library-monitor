
# TURN LIBRARY BOOKINGS INTO A CLASS OBJECT, WRITE THE USAGE HERE
from proper_class import *
from ai import ask

print(Ws())
print(western())

print('Welcoming to Westerns Automated Library Bookings\n')

c = library()
c.userrInfo()

c.chooseLibrary()
run = False

while True:
    print('Select from the following options:')
    print(' 1. Input a time')
    print(' 2. See all available times for {} Library {}'.format(c.library.capitalize(), c.date_format))
    print(' 3. See availability on booking site')
    print(' 4. Change Library')
    print(' 5. Change Day')
    print(' 6. Save Booking Length')
    print(' 7. Print Formatted Times Available')
    print(' 8. Quit')
    print(' 9. Ask AI')

    choice = input('Selection: ')
    if choice == '1':
        if c.grid():
            while True:
                print('Input Time in 24 hour format, eg. 09:30 for 9:30am, 17:00 for 4:00pm')
                time3 = input('Time: ')
                if not is_valid_24h_time(time3):
                    print('Print not a valid time, try again...')
                else:
                    c.set_time('{}:00'.format(time3))
                    break
            c.add()

    elif choice == '2':
        c.grid()
        c.print_avai()

        print(c.org)

    elif choice == '3':
        c.open_site()

    elif choice == '4':
        print('\n')
        c.chooseLibrary()

    elif choice == '5':
        print('\n')
        day = input('Input New Day:')
        c.setDay(day)
        print('\n')

    elif choice == '6':
        print('\nWhat is the MINIMUM Amount of Time You Would Like To Book The Room For:')
        print('   1. 30 Minutes:')
        print('   2. 1 Hour:')
        print('   3. 1 Hour and 30 Minutes:')
        print('   4. 2 Hours (maximum):')
        inLength = input('Selection:')
        c.setLength(inLength)
        print('\n')

    elif choice == '7':
        c.grid()
        c.formatTimes()

    elif choice == '8':
        print('\nAdios!')
        quit()

    elif choice == '9':
        print('\n')
        question = input("Input Your Question: ")
        print('\n')
        # ques = "Given the following data showing a dict of library rooms and available times for them to be booked: {} - answer the following questions: {}".format(c.org, question)
        # print(ques)
        print(ask(question))
        print('\n')
        run = True

    else:
        print('Invalid Option \n')