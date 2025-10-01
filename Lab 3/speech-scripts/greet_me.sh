#!/bin/bash
echo "Generating greeting audio..."
pico2wave -w temp.wav "Welcome Yannis!"
aplay temp.wav
sleep 1 #!/bin/bash
pico2wave -w temp.wav "Welcome Yannis!" && aplay temp.wav

