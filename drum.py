import usb_midi
from bitarray import bitarray

class drum:
    """drum class: represents a drum and its beat sequence"""
    channel = 10
    velocity = 120
    note_on = 0x90
    note_off = 0x80

    def __init__(self, name: str, note: int, sequence: bitarray):
        self.name = name
        self.note = note
        self.sequence = sequence

    def __repr__(self) -> str:
        """__repr___(): used to supply the repr(...) function with a string which would recreate the drum."""
        return f'drum({repr(self.name)},{repr(self.note)},{repr(self.sequence)})'

    def play(self, midi: usb_midi.PortOut, step: int) -> None:
        """play(midi, step): plays the drum's note, on the midi port, if the step is active."""
        if self.sequence[step]:
            channel_flag = drum.channel - 1 # 0 = ch 1, 1 = ch2, ..., 9 = ch 10
            midi_msg_on = bytearray([channel_flag | drum.note_on, self.note, drum.velocity])
            midi_msg_off = bytearray([channel_flag | drum.note_off, self.note, 0])
            midi.write(midi_msg_on)
            midi.write(midi_msg_off)

class drum_definition:
	def __init__(self, long_name: str, short_name: str, note: int):
		self.long_name = long_name
		self.short_name = short_name
		self.note = note

# See https://qsrdrums.com/webhelp-responsive/References/r_general_midi_drum_kit.html
AcousticBassDrum = drum_definition("Acoustic Bass Drum", "ABas", 35)
BassDrum = drum_definition("Bass Drum", "Bass", 36)
SideStick = drum_definition("Side Stick", "SStk", 37)
AcousticSnare = drum_definition("Acoustic Snare", "ASnr", 38)
HandClap = drum_definition("Hand Clap", "Hand", 39)
ElectricSnare = drum_definition("Electric Snare", "ESnr", 40)
LowFloorTom = drum_definition("Low Floor Tom", "LFTom", 41)
ClosedHiHat = drum_definition("Closed Hi Hat", "CHHt", 42)
HighFloorTom = drum_definition("High Floor Tom", "HTom", 43)
PedalHiHat = drum_definition("Pedal Hi-Hat", "PHat", 44)
LowTom = drum_definition("Low Tom", "LTom", 45)
OpenHiHat = drum_definition("Open Hi-Hat", "OHat", 46)
LowMidTom = drum_definition("Low-Mid Tom", "LMTm", 47)
HiMidTom = drum_definition("Hi-Mid Tom", "HMTm", 48)
CrashCymbal1 = drum_definition("Crash Cymbal 1", "Crsh1", 49)
HighTom = drum_definition("High Tom", "HTom", 50)
RideCymbal1 = drum_definition("Ride Cymbal 1", "RCy1", 51)
ChineseCymbal = drum_definition("Chinese Cymbal", "ChCy", 52)
RideBell = drum_definition("Ride Bell", "RBel", 53)
Tambourine = drum_definition("Tambourine", "Tamb", 54)
SplashCybal = drum_definition("Splash Cymbal", "SCym", 55)
CowBell = drum_definition("Cowbell", "CowB", 56)
CrashCymbal2 = drum_definition("Crash Cymbal 2", "Crsh2", 57)
Vibraslap = drum_definition("Vibraslap", "Vibr", 58)
RideCymbal2 = drum_definition("Ride Cymbal 2", "RCy2", 59)
HiBongo = drum_definition("Hi Bongo", "HBon", 60)
LowBongo = drum_definition("Low Bongo", "LBon", 61)
MuteHiConga = drum_definition("Mute Hi Conga", "MHCg", 62)
OpenHiConga = drum_definition("Open Hi Conga", "OHCg", 63)
LowConga = drum_definition("Low Conga", "LCng", 64)
HiTimbale = drum_definition("Hi Timbale", "HTim", 65)
LowTimbale = drum_definition("Low Timbale", "LTim", 66)
HiAgogo = drum_definition("Hi Agogo", "Hi Agogo", 67)
LowAgogo = drum_definition("Low Agogo", "Low Agogo", 68)
Cabasa = drum_definition("Cabasa", "Cabasa", 69)
Maracas = drum_definition("Maracas", "Maracas", 70)
ShortWhistle = drum_definition("Short Whistle", "SWhst", 71)
LongWhistle = drum_definition("Long Whistle", "LWhst", 72)
ShortGuiro = drum_definition("Short Guiro", "SGui", 73)
LongGuiro = drum_definition("Long Guiro", "LGui", 74)
Claves = drum_definition("Claves", "Clav", 75)
HiWoodBlock = drum_definition("Hi Wood Block", "HWdB", 76)
LowWoodBlock = drum_definition("Low Wood Block", "LWdB", 77)
MuteCuica = drum_definition("Mute Cuica", "MCui", 78)
OpenCuica = drum_definition("Open Cuica", "OCui", 79)
MuteTriangle = drum_definition("Mute Triangle", "MTri", 80)
OpenTriangle = drum_definition("Open Triangle", "OTri", 81)
