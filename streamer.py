#!/usr/bin/env python3
"""Pass input directly to output.
https://app.assembla.com/spaces/portaudio/git/source/master/test/patest_wire.c
"""
import argparse
import sounddevice as sd
import numpy  # Make sure NumPy is loaded before it is used in the callback
import time as tim
import random

def int_or_str(text):
    """Helper function for argument parsing."""
    try:
        return int(text)
    except ValueError:
        return text


volumes = [(17,83), (33,67), (50,50), (83,17), (67,33)]
# Select a random speaker
vol = [random.randint(0, len(volumes)-1)]

# function that creates visual of who is speaking
speakers = [[" * ", " * ", " * ", " * ", " * "], 0]
def renderStr(changeIdx):
    speakers[0][speakers[1]] = " * "
    speakers[0][changeIdx] = '\x1b[6;30;42m' + ' S ' + '\x1b[0m'
    speakers[1] = changeIdx
    strings = f'''
    . . . * *{speakers[0][2]}* * .  .
    . . * . . . . . * . .
    . * . . . . . . . * .
    {speakers[0][3]}. . . . . . . .{speakers[0][1]}
    * . . . . . . . . . *
    * . . . . . . . . . *
    .{speakers[0][4]}. . . . . . .{speakers[0][0]}.
    . . * . . . . . * . .
    . . . * *\x1b[6;30;41m L \x1b[0m* * . . .
    '''
    return strings

print(renderStr(vol[0]))
start_time = [tim.time()]

parser = argparse.ArgumentParser(add_help=False)
parser.add_argument(
    '-l', '--list-devices', action='store_true',
    help='show list of audio devices and exit')
args, remaining = parser.parse_known_args()
if args.list_devices:
    print(sd.query_devices())
    parser.exit(0)
parser = argparse.ArgumentParser(
    description=__doc__,
    formatter_class=argparse.RawDescriptionHelpFormatter,
    parents=[parser])
parser.add_argument(
    '-i', '--input-device', type=int_or_str,
    help='input device (numeric ID or substring)')
parser.add_argument(
    '-o', '--output-device', type=int_or_str,
    help='output device (numeric ID or substring)')
parser.add_argument(
    '-c', '--channels', type=int, default=2,
    help='number of channels')
parser.add_argument('--dtype', help='audio data type')
parser.add_argument('--samplerate', type=float, help='sampling rate')
parser.add_argument('--blocksize', type=int, help='block size')
parser.add_argument('--latency', type=float, help='latency in seconds')
args = parser.parse_args(remaining)


def callback(indata, outdata, frames, time, status):
    if status:
        print(status)
    for item in indata:
        item[0] = ((volumes[vol[0]][0]/100)*item[0])
        item[1] = ((volumes[vol[0]][1]/100)*item[1])

    if(tim.time() - start_time[0] >= 10):
        print ("\n" * 100)
        vol[0] = random.randint(0, len(volumes)-1)
        print(renderStr(vol[0]))
        start_time[0] = tim.time()
    outdata[:] = indata


try:
    with sd.Stream(device=(args.input_device, args.output_device),
                   samplerate=args.samplerate, blocksize=args.blocksize,
                   dtype=args.dtype, latency=args.latency,
                   channels=args.channels, callback=callback):
        input()
except KeyboardInterrupt:
    parser.exit('')
except Exception as e:
    parser.exit(type(e).__name__ + ': ' + str(e))
