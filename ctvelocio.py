#!/usr/bin/env python

# Copyright 2017 Justin Searle
#
# Based on code from https://github.com/jsr5194/velocio-ace-remote and used with permission
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

import re
import sys
import time
import serial
import getopt


printoutmode = 'normal'


def print_help():
    print("")
    print("********************************************************************************")
    print("*                                                                              *")
    print("*                             Control Things Velocio                           *")
    print("*                                 version 1.0.1                                *")
    print("*                                                                              *")
    print("********************************************************************************")
    print("")
    print(" Usage: python ctvelocio [instruction]")
    print("")
    print(" Control Instructions:")
    print("")
    print(" \tplay \t\t\tstart the routine at current position")
    print(" \tpause\t\t\tpause the routine at current position")
    print(" \treset\t\t\treset the routine to the beginning")
    print(" \tset_output_1_off\tset output 1 to off")
    print(" \tset_output_2_off\tset output 2 to off")
    print(" \tset_output_3_off\tset output 3 to off")
    print(" \tset_output_4_off\tset output 4 to off")
    print(" \tset_output_5_off\tset output 5 to off")
    print(" \tset_output_6_off\tset output 6 to off")
    print(" \tset_output_all_off\tset all output to off")
    print("")
    print(" \tset_output_1_on\t\tset output 1 to on")
    print(" \tset_output_2_on\t\tset output 2 to on")
    print(" \tset_output_3_on\t\tset output 3 to on")
    print(" \tset_output_4_on\t\tset output 4 to on")
    print(" \tset_output_5_on\t\tset output 5 to on")
    print(" \tset_output_6_on\t\tset output 6 to on")
    print(" \tset_output_all_on\tset all output to on")
    print("")
    print("")
    print(" Read Instructions:")
    print("")
    print(" \tread_input_bits\t\tquery the input bits and print(the response")
    print(" \tread_output_bits\tquery the output bits and print the response")
    print("")
    print("")
    print(" Debug Instructions:")
    print("")
    print(" \tenter_debug\t\tput the device into debug mode for testing")
    print(" \texit_debug\t\texit the device debug mode for normal operation")
    print(" \tstep_into\t\tstandard procedure")
    print(" \tstep_out\t\tstandard procedure")
    print(" \tstep_over\t\tstandard procedure")
    print("")
    print("")
    print(" Sending RAW messages:")
    print("")
    print(" \t--raw <Raw hex data>\tsends raw data to the port. Can handle ranges in input in the form [<start>,<end>]")
    print("")
    print("")
    print(" Change the way the responses are showed:")
    print("")
    print(" \t--display=<mode>\tRecognized modes are ('normal', 'raw' and 'mixed')")
    print("")
    print("")
    print(" Example:\tpython ctvelocio play")
    print(" Example:\tpython ctvelocio read_output_bits")
    print(" Example:\tpython ctvelocio exit_debug")
    print(" Example:\tpython ctvelocio --raw 56 ff ff 00 08 0a 00 [07,0c]")
    print(" Example:\tpython ctvelocio --display=mixed --raw 56 ff ff 00 08 0a 00 [01,06]")
    print(" Example:\tpython ctvelocio exit_debug")
    print("")
    exit(1)


def raw_to_instruction(raw):
    raw_str = ''.join(raw)
    number_range = '\\[([0-9a-fA-F]{2})[,\\-]([0-9a-fA-F]{2})\\]'
    matches = re.search(number_range, raw_str)
    if matches:
        limits = [ord(x.decode('hex')) for x in matches.groups()]
        values = []
        for index in range(limits[0], limits[1] + 1):
            raw_gen = re.sub(number_range, as_hex_chars(index), raw_str, 1)
            for mod_msg in raw_to_instruction(raw_gen):
                values.append(mod_msg)
        return values
    return [raw_str.decode('hex')]


def as_hex_chars(charcode):
    return str.format('{:02x}', charcode)


def as_normal_chars(charcode):
    if (64 < charcode < 123) or (58 > charcode > 47):
        return chr(charcode)
    return '_'


def as_mixed_chars(charcode):
    if (64 < charcode < 123) or (58 > charcode > 47):
        return '\033[92m {0}\033[0m'.format(chr(charcode))
    if charcode == 32:
        return ' _'
    if charcode == ord('.'):
        return ' .'
    if charcode == 255:
        return '\033[2m{0}\033[0m'.format(as_hex_chars(charcode))
    return as_hex_chars(charcode)


def print_message(tx, rx):

    if 'mixed' == printoutmode:
        tx_hex = ' '.join(map(as_hex_chars, tx))
        rx_mix = ' '.join(map(as_mixed_chars, rx))
        print('\033[1mtx:\033[0m %s \033[1mrx:\033[0m %s' % (tx_hex, rx_mix))

    elif 'raw' == printoutmode:
        print(''.join(map(chr, rx)))

    else:
        tx_hex = ' '.join(map(as_hex_chars, tx))
        rx_hex = ' '.join(map(as_hex_chars, rx))
        rx_str = ''.join(map(as_normal_chars, rx))
        print('\033[1mtx:\033[0m %s \033[1mrx:\033[0m %s %s' % (tx_hex, rx_hex, rx_str))


# sends a set of instructions to the connected device
# @param instruction_set : an array of commands to send to the PLC in hex
# @param printstring     : runtime message for the user
def send_instruction(ser, instruction_set):

    # clear out any leftover data
    if ser.inWaiting() > 0:
        ser.flushInput()

    # perform the write
    for instruction in instruction_set:
        ser.write(instruction)
        time.sleep(0.1)

        rx_raw = []
        while ser.inWaiting() > 0:
            rx_raw.append(ord(ser.read()))

        time.sleep(0.1)

        tx_raw = [ord(elem) for elem in instruction]
        print_message(tx_raw, rx_raw)


def main():

    try:
        opts, args = getopt.getopt(sys.argv[1:], "h", ["raw", "display="])
    except getopt.GetoptError:
        print_help()
        sys.exit(2)

    command = []

    for opt, arg in opts:

        if opt == '-h':
            print_help()
            sys.exit()

        elif opt == '--display':
            global printoutmode
            printoutmode = arg

        elif opt == '--raw':
            command = raw_to_instruction(args)

    if len(command) == 0:
        if len(args) == 1 and args[0] in commands.keys():
            command = commands[args[0]]
        else:
            print_help()
            sys.exit()

    # define serial connection
    ser = serial.Serial(
        port='/dev/ttyACM0',
        baudrate=9600,
        parity=serial.PARITY_NONE,
        stopbits=serial.STOPBITS_ONE,
        bytesize=serial.EIGHTBITS
    )

    # initiate the connection
    ser.isOpen()

    # send messages
    send_instruction(ser, command)

    # clean up
    ser.close()


if __name__ == "__main__":

    ###
    # define the instructions
    ###

    commands = {

        # control instructions
        "pause":              ["\x56\xff\xff\x00\x07\xf1\x02"],
        "play":               ["\x56\xff\xff\x00\x07\xf1\x01"],
        "reset":              ["\x56\xff\xff\x00\x07\xf1\x06"],
        "step_into":          ["\x56\xff\xff\x00\x07\xf1\x03"],
        "step_out":           ["\x56\xff\xff\x00\x07\xf1\x04"],
        "step_over":          ["\x56\xff\xff\x00\x07\xf1\x05"],
        "enter_debug":        ["\x56\xff\xff\x00\x07\xf0\x02"],
        "exit_debug":         ["\x56\xff\xff\x00\x07\xf0\x01"],

        # set instructions
        "set_output_1_off":   ["\x56\xff\xff\x00\x15\x11\x01\x00\x01\x00\x00\x09\x01\x00\x00\x01\x00\x01\x00\x00\x00"],
        "set_output_1_on":    ["\x56\xff\xff\x00\x15\x11\x01\x00\x01\x00\x00\x09\x01\x00\x00\x01\x00\x01\x00\x00\x01"],
        "set_output_2_off":   ["\x56\xff\xff\x00\x15\x11\x01\x00\x01\x00\x00\x09\x01\x00\x00\x01\x00\x02\x00\x00\x00"],
        "set_output_2_on":    ["\x56\xff\xff\x00\x15\x11\x01\x00\x01\x00\x00\x09\x01\x00\x00\x01\x00\x02\x00\x00\x01"],
        "set_output_3_off":   ["\x56\xff\xff\x00\x15\x11\x01\x00\x01\x00\x00\x09\x01\x00\x00\x01\x00\x04\x00\x00\x00"],
        "set_output_3_on":    ["\x56\xff\xff\x00\x15\x11\x01\x00\x01\x00\x00\x09\x01\x00\x00\x01\x00\x04\x00\x00\x01"],
        "set_output_4_off":   ["\x56\xff\xff\x00\x15\x11\x01\x00\x01\x00\x00\x09\x01\x00\x00\x01\x00\x08\x00\x00\x00"],
        "set_output_4_on":    ["\x56\xff\xff\x00\x15\x11\x01\x00\x01\x00\x00\x09\x01\x00\x00\x01\x00\x08\x00\x00\x01"],
        "set_output_5_off":   ["\x56\xff\xff\x00\x15\x11\x01\x00\x01\x00\x00\x09\x01\x00\x00\x01\x00\x10\x00\x00\x00"],
        "set_output_5_on":    ["\x56\xff\xff\x00\x15\x11\x01\x00\x01\x00\x00\x09\x01\x00\x00\x01\x00\x10\x00\x00\x01"],
        "set_output_6_off":   ["\x56\xff\xff\x00\x15\x11\x01\x00\x01\x00\x00\x09\x01\x00\x00\x01\x00\x20\x00\x00\x00"],
        "set_output_6_on":    ["\x56\xff\xff\x00\x15\x11\x01\x00\x01\x00\x00\x09\x01\x00\x00\x01\x00\x20\x00\x00\x01"],
        "set_output_all_on":  ["\x56\xff\xff\x00\x15\x11\x01\x00\x01\x00\x00\x09\x01\x00\x00\x01\x00\x3f\x00\x00\x01"],
        "set_output_all_off": ["\x56\xff\xff\x00\x15\x11\x01\x00\x01\x00\x00\x09\x01\x00\x00\x01\x00\x3f\x00\x00\x00"],

        # read instructions
        "read_input_bits": [
            "\x56\xff\xff\x00\x08\x0a\x00\x01",
            "\x56\xff\xff\x00\x08\x0a\x00\x02",
            "\x56\xff\xff\x00\x08\x0a\x00\x03",
            "\x56\xff\xff\x00\x08\x0a\x00\x04",
            "\x56\xff\xff\x00\x08\x0a\x00\x05",
            "\x56\xff\xff\x00\x08\x0a\x00\x06"
        ],
        "read_output_bits": [
            "\x56\xff\xff\x00\x08\x0a\x00\x07",
            "\x56\xff\xff\x00\x08\x0a\x00\x08",
            "\x56\xff\xff\x00\x08\x0a\x00\x09",
            "\x56\xff\xff\x00\x08\x0a\x00\x0a",
            "\x56\xff\xff\x00\x08\x0a\x00\x0b",
            "\x56\xff\xff\x00\x08\x0a\x00\x0c"
        ]}

    try:
        main()

    except Exception as e:
        print("")
        print("[!] ERROR")
        print("[!] MSG: %s" % e)
        print("")
        exit(1)
