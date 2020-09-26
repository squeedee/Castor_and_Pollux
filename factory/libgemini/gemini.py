# Interface for Gemini's MIDI SysEx command set

import rtmidi.midiutil

SYSEX_START = 0xF0
SYSEX_END = 0xF7
SYSEX_MARKER = 0x77

def _wait_for_message(port_in):
    while True:
        msg = port_in.get_message()
        if msg:
            msg, _ = msg
            return msg


def _fix16(val):
    if val >= 0:
        return int(x * 65536.0 + 0.5)
    else:
        return int(x * 65536.0 - 0.5)


class Gemini:
    MIDI_PORT_NAME = "Gemini"

    def __init__(self):
        self.port_in, _ = rtmidi.midiutil.open_midiport(self.MIDI_PORT_NAME, type_="input")
        self.port_in.ignore_types(sysex=False)
        self.port_out, _ = rtmidi.midiutil.open_midiport(self.MIDI_PORT_NAME, type_="output")

    def enter_calibration_mode(self):
        self.port_out.send_message([SYSEX_START, SYSEX_MARKER, 0x01, SYSEX_END])
        msg = _wait_for_message(self.port_in)
        print(f"Gemini version: {msg[3]}")

    def read_adc(self, ch):
        self.port_out.send_message([SYSEX_START, SYSEX_MARKER, 0x05, ch, SYSEX_END])
        msg = _wait_for_message(self.port_in)
        val = (msg[3] << 16 | msg[4] << 8 | msg[5] << 4 | msg[6])
        return val

    def set_dac(self, ch, val, gain):
        self.port_out.send_message([SYSEX_START, SYSEX_MARKER, 0x06, ch, gain, (val >> 12) & 0xF, (val >> 8) & 0xF, (val >> 4) & 0xF, val & 0xF, SYSEX_END])

    def set_period(self, ch, val):
        self.port_out.send_message([SYSEX_START, SYSEX_MARKER, 0x07, ch, (val >> 12) & 0xF, (val >> 8) & 0xF, (val >> 4) & 0xF, val & 0xF, SYSEX_END])

    def set_adc_gain_error_int(self, val):
        self.port_out.send_message([SYSEX_START, SYSEX_MARKER, 0x02, (val >> 12) & 0xF, (val >> 8) & 0xF, (val >> 4) & 0xF, val & 0xF, SYSEX_END])
    
    def set_adc_gain_error(self, val):
        val = int(val * 2048)
        self.set_adc_gain_error_int(val)

    def set_adc_offset_error(self, val):
        self.port_out.send_message([SYSEX_START, SYSEX_MARKER, 0x03, (val >> 12) & 0xF, (val >> 8) & 0xF, (val >> 4) & 0xF, val & 0xF, SYSEX_END])

    def reset_settings(self):
        self.port_out.send_message([SYSEX_START, SYSEX_MARKER, 0x08, SYSEX_END])

    def set_led_brightness(self, val):
        self.port_out.send_message([SYSEX_START, SYSEX_MARKER, 0x04, (val >> 12) & 0xF, (val >> 8) & 0xF, (val >> 4) & 0xF, val & 0xF, SYSEX_END])
    
    def set_knob_ranges(self, castor_min, castor_max, pollux_mix, pollux_max):
        castor_min = _fix16(castor_min)
        castor_max = _fix16(castor_max)
        pollux_min = _fix16(pollux_min)
        pollux_max = _fix16(pollux_max)
        self.port_out.send_message([
            SYSEX_START, SYSEX_MARKER, 0x09,
            (castor_min >> 28) & 0xF, (castor_min >> 24) & 0xF, (castor_min >> 20) & 0xF, (castor_min >> 16) & 0xF, (castor_min >> 12) & 0xF, (castor_min >> 8) & 0xF, (castor_min >> 4) & 0xF, castor_min & 0xF,
            (castor_max >> 28) & 0xF, (castor_max >> 24) & 0xF, (castor_max >> 20) & 0xF, (castor_max >> 16) & 0xF, (castor_max >> 12) & 0xF, (castor_max >> 8) & 0xF, (castor_max >> 4) & 0xF, castor_max & 0xF,
            (pollux_min >> 28) & 0xF, (pollux_min >> 24) & 0xF, (pollux_min >> 20) & 0xF, (pollux_min >> 16) & 0xF, (pollux_min >> 12) & 0xF, (pollux_min >> 8) & 0xF, (pollux_min >> 4) & 0xF, pollux_min & 0xF,
            (pollux_max >> 28) & 0xF, (pollux_max >> 24) & 0xF, (pollux_max >> 20) & 0xF, (pollux_max >> 16) & 0xF, (pollux_max >> 12) & 0xF, (pollux_max >> 8) & 0xF, (pollux_max >> 4) & 0xF, pollux_max & 0xF,
            SYSEX_END
        ])