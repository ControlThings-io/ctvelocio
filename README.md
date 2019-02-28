# Control Things Velocio

### Overview:
A simple script to interact with the Velocio Ace 11 PLC via USB

Testing was performed on an Ace 11. Other versions may not function as desired

### Dependancies:
py-serial  http://pyserial.readthedocs.io/en/latest/pyserial.html

### Usage: 
    python ctvelocio [instruction]

### Control Instructions:
 
        play                    start the routine at current position
        pause                   pause the routine at current position
        reset                   reset the routine to the beginning
        set_output_1_off        set output 1 to off
        set_output_2_off        set output 2 to off
        set_output_3_off        set output 3 to off
        set_output_4_off        set output 4 to off
        set_output_5_off        set output 5 to off
        set_output_6_off        set output 6 to off
        set_output_1_on         set output 1 to on
        set_output_2_on         set output 2 to on
        set_output_3_on         set output 3 to on
        set_output_4_on         set output 4 to on
        set_output_5_on         set output 5 to on
        set_output_6_on         set output 6 to on


### Read Instructions:

        read_input_bits         query the input bits and print the response
        read_output_bits        query the output bits and print the response


### Debug Instructions:

        enter_debug             put the device into debug mode for testing
        exit_debug              exit the device debug mode for normal operation
        step_into               standard procedure
        step_out                standard procedure
        step_over               standard procedure
