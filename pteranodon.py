#!/usr/bin/python3
"""
4D Pteranodon

Description:
This program controls the motor of a toy Pteranodon. A button is
pressed to make the Pteranodon squawk and flap its wings.

....................

Functions:
- file_check: Checks to see if the necessary files exist
- permission_check: Checks to see if the user has permission to read
  the necessary files
- read_file: Reads the dino_facts file
- empty_file_check: Checks to see if the dino_facts list is empty
- print_header: Prints a header
- prompt_user_for_input: Prompts user to push a button
- get_roar: Gets one random sound file
- print_dinosaur_fact: Prints a random dinosaur fact
- activate_t_rex: Starts the T. rex motor
- release_gpio_pins: Realeases the GPIO pins.
- stop_the_program: Stops the program

....................

Author: Paul Ryan

This program was written on a Raspberry Pi using the Geany IDE.
"""

########################################################################
#                          Import modules                              #
########################################################################

import os
import logging
import random
from time import sleep
from gpiozero import Motor, Button, OutputDevice
import pygame

########################################################################
#                           Variables                                  #
########################################################################

PTERANODON_MOTOR = Motor(2, 3, True)            # forward, backward, pwm
PTERANODON_MOTOR_ENABLE = OutputDevice(4)
YELLOW_BUTTON = Button(17)
RED_BUTTON = Button(9)

########################################################################
#                           Initialize                                 #
########################################################################

pygame.mixer.init()

logging.basicConfig(filename='Files/pteranodon.log', filemode='w',
                    level=logging.INFO,
                    format='%(asctime)s %(levelname)s: %(message)s',
                    datefmt='%m/%d/%y %I:%M:%S %p:')

########################################################################
#                            Functions                                 #
########################################################################


def main():
    """
    This is the main function. It will wait until one of two buttons is
    pressed. One button will activate the Pteranodon and the other
    button will stop the program. Pressing Ctrl-C will also stop the
    program.
    """

    try:
        logging.info("START")
        # Check to see that the necessary files exist
        file_check()
        # Check to see if files are accessible
        permission_check()
        # Read the dinosaur_facts.txt file to populate the dino_facts list.
        dino_facts = read_file("Files/dinosaur_facts.txt")
        # Check to see if the file is empty
        empty_file_check(dino_facts)
        # Acknowledge that prelimiary checks are complete
        logging.info("Prelimiary checks are complete. Starting program...")
        # Display program header
        print_header()
        # Pre-load the first sound file
        squawk, squawk_length = get_squawk()
        # Prompt the user to press a button
        prompt_user_for_input()

        while True:

            if YELLOW_BUTTON.is_pressed:
                # Print out a random dinosaur fun fact
                print_dinosaur_fact(dino_facts)
                # Move the Pteranodon for the duration of the sound file
                activate_pteranodon(squawk, squawk_length)
                # Load the next sound file
                squawk, squawk_length = get_squawk()
                # Prompt the user to press a button
                prompt_user_for_input()

            if RED_BUTTON.is_pressed:
                stop_the_program()

    except KeyboardInterrupt:
        stop_the_program()


def file_check():
    """
    Checks to see if the necessary files exist

    This function checks to see if the necessary files exist.
    If they all exist, the program will continue.
    If a file is missing, the program will print out a message to the
    screen and then exit.
    """

    file_missing_flag = 0

    sounds = ['Pteranodon1.ogg', 'Pteranodon2.ogg', 'Pteranodon3.ogg',
              'Pteranodon4.ogg']

    # Check to see if sound files exists
    for sound in sounds:
        if os.path.isfile('Sounds/' + sound):
            logging.info("%s file was found!", sound)
        else:
            logging.error("%s file was not found! Make sure " +
                          "that the %s file exists in the " +
                          "'Sounds' folder.", sound, sound)
            file_missing_flag = 1

    # If there are no missing files, return to the main function
    # Otherwise print out message and exit the program
    if file_missing_flag == 0:
        return
    else:
        print("\033[1;31;40m\nCould not run the program. Some files are " +
              "missing. Check the log in the 'Files' folder for more " +
              "information.\n")
        stop_the_program()


def permission_check():
    """
    Checks to see if the user has permission to read the necessary files

    This function checks to see if the user has permission to read the
    necessary files. If so, the program will continue. If not, the
    program will print out a message to the screen and then exit.
    """

    permission_flag = 0

    sounds = ['Pteranodon1.ogg', 'Pteranodon2.ogg', 'Pteranodon3.ogg',
              'Pteranodon4.ogg']

    logging.info("PERMISSION CHECK")
    # Check to see if user has read access to dinosaur_facts.txt
    if os.access('Files/dinosaur_facts.txt', os.R_OK):
        logging.info("User has permission to read the dinosaur_facts.txt " +
                     "file.")
    else:
        logging.error("User does not have permission to read the " +
                      "dinosaur_facts.txt file.")
        permission_flag = 1

    # Check to see if user has read access to sound files
    for sound in sounds:
        if os.access('Sounds/' + sound, os.R_OK):
            logging.info("User has permission to read the " +
                         "%s file.", sound)
        else:
            logging.error("User does not have permission to read the " +
                          "%s file.", sound)
            permission_flag = 1

    if permission_flag == 0:
        return
    else:
        print("\033[1;31;40m\nCould not run the program. Check the log " +
              "in the 'Files' folder for more information.")
        stop_the_program()


def read_file(file_name):
    """
    Reads the dino_facts file

    This function reads the dino_facts file and populates a list. Each
    line of the file will be an element in the dino_facts list. It will
    then return the dino_facts list to the main function. If the program
    is unable to populate the list, it will display an error message and
    then exit the program.

    Arguments:
        file_name: The dinosaur_facts.txt file located in the 'Files'
        folder.

    Returns:
        dino_facts: a list of dinosaur facts
    """

    logging.info("READING DINOSAUR_FACTS.TXT")
    try:
        with open(file_name, "r") as facts:     # open the file as read-only
            dino_facts = facts.readlines()
        logging.info("The dino_facts list was successfully populated.")
    except IOError:
        print("\033[1;31;40mErrors were encountered. Check the log in the " +
              "'Files' folder for more information.")
        logging.error("The dino_facts list could not be populated.")
        stop_the_program()

    return dino_facts


def empty_file_check(list_name):
    """
    Checks to see if the dino_facts list is empty

    This function will check to see if the list is empty. If it is, the
    program will print a message to the screen and then exit. If the
    file is not empty, the program will continue.

    Arguments:
        list_name: the dino_facts list

    """

    logging.info("EMPTY FILE CHECK")
    if list_name == []:
        logging.error("The dinosaur.txt file is empty. The program won't " +
                      "work.")
        print("\033[1;31;40mErrors were encountered. Check the log in the " +
              "'Files' folder for more information.")
        stop_the_program()
    else:
        logging.info("The dinosaur.txt file is not empty.(This is good. "
                     "We don't want an empty file.)")


def print_header():
    """
    Prints a header


    This function will print out the program header to the
    screen.

    This is the only part of the program that doesn't adhere to the PEP
    standards (It exceeds recommended line length). I decided that
    "Readability Counts" and "Beautiful is better than ugly" from The
    Zen of Python should trump the PEP standards in this case. I had
    rewritten it to meet the PEP standard, but is was ugly and
    unreadable. This is much better. The program still compiles and runs
    OK.
    """

    # The r prefix is to let Pylint know that it is a raw string.
    # It prevents the Pylint message "Anomolous backslash in string:
    # string constant might be missing an r prefix"
    print("\n\033[1;33;40m")
    print(r"===========================================================================")
    print(r"   _  _   ____     ____  _                                 _               ")
    print(r"  | || | |  _ \   |  _ \| |_ ___ _ __ __ _ _ __   ___   __| | ___  _ __    ")
    print(r"  | || |_| | | |  | |_) | __/ _ \ '__/ _` | '_ \ / _ \ / _` |/ _ \| '_ \   ")
    print(r"  |__   _| |_| |  |  __/| ||  __/ | | (_| | | | | (_) | (_| | (_) | | | |  ")
    print(r"     |_| |____/   |_|    \__\___|_|  \__,_|_| |_|\___/ \__,_|\___/|_| |_|  ")
    print(r"                                                                           ")
    print(r"===========================================================================")
    print("\n")


def prompt_user_for_input():
    """
    Prompts user to push a button

    This function prompts a user to push a button.
    """

    # First line
    print("\033[1;37;40mPush the " +                 # print white text
          "\033[1;33;40myellow button " +            # print yellow text
          "\033[1;37;40mto activate the " +          # print white text
          "\033[1;33;40mPteranodon.")                # print yellow text
    # Second line
    print("\033[1;37;40mPush the " +                 # print white text
          "\033[1;31;40mred button " +               # print red text
          "\033[1;37;40mor press Ctrl-C to " +       # print white text
          "\033[1;31;40mstop " +                     # print red text
          "\033[1;37;40mthe program.\n")             # print white text


def get_squawk():
    """
    Gets one random sound file

    This function will randomly select one of the Pteranodon squawk
    sound files.

    Returns:
        a sound file and the length of the file in seconds
    """

    # The key/value pair is sound file name : length of file in seconds
    squawks = {'Sounds/Pteranodon1.ogg': 6.5, 'Sounds/Pteranodon2.ogg': 6.5,
               'Sounds/Pteranodon3.ogg': 6, 'Sounds/Pteranodon4.ogg': 6}

    return random.choice(list(squawks.items()))


def print_dinosaur_fact(dino_facts):
    """
    Prints a random dinosaur fact

    This function will select a random fact from the dino_facts list and
    print it out.

    Arguments:
        dino_facts: a list of dinosaur_facts
    """

    print("\033[1;34;40mDINOSAUR FUN FACT:")
    print(random.choice(dino_facts))


def activate_pteranodon(sound, sound_length):
    """
    Starts the Pteranodon motor

    This function will play the sound file and activate the
    Pteranodon motor for the duration of the sound file.

    Arguments:
        sound: The randomly selected Pteranodon sound file
        sound_length: The length of the sound file in seconds
    """

    try:
        PTERANODON_MOTOR.value = 0.6       # Controls the motor speed
    except ValueError:
        logging.error("A bad value was specified for the pteranodon_" +
                      "motor. The value should be between 0 and 1.")
        print("\033[1;31;40mAn error was encountered. Check the log in the " +
              "'Files' folder for more information.\n")
        stop_the_program()
    pygame.mixer.music.load(sound)         # Loads the sound file
    PTERANODON_MOTOR_ENABLE.on()           # Starts the motor
    pygame.mixer.music.play()              # Plays the sound file
    sleep(sound_length)                    # Length of sound file in seconds
    PTERANODON_MOTOR_ENABLE.off()          # Stops the motor


def release_gpio_pins():
    """
    Realeases the GPIO pins.
    """

    PTERANODON_MOTOR.close()
    PTERANODON_MOTOR_ENABLE.close()
    RED_BUTTON.close()
    YELLOW_BUTTON.close()


def stop_the_program():
    """
    Stops the program

    This function will call the release_gpio_pins function, print a
    message to the screen, and then exit the program.
    """

    release_gpio_pins()
    print("\033[1;37;40mExiting program.\n")
    logging.info("END")
    exit()


if __name__ == '__main__':
    main()
