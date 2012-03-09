import sys
import spilib
import time
import datetime
import random

#
# SingleBytePacketTest: 
#
# Sends a predefined pattern of single-byte SPI transmissions (master-out)
#
def SingleBytePacketsSendTest():
  packetsToSend = [[0x55],[0xAA],[0x33],[0x66],[0xCC],[0x99],[0xF0],\
                   [0x0F],[0xFF],[0x00]]
  packetIndex = 0
  while True:
    dataToSend = packetsToSend[packetIndex]
    
    sys.stdout.write("Sending: [")
    for sendByte in dataToSend:
      sys.stdout.write(" 0x%02x" % (sendByte))
    sys.stdout.write(" ]\n")
    spi.SendToSlave(dataToSend)
  
    packetIndex = (packetIndex + 1) % len(packetsToSend)
    time.sleep(1)
  
    packetIndex + 1

#
# MultiBytePacketSendTest:
#
# Sends a predefined single multi-byte packet over SPI (master-out)
#
def MultiBytePacketSendTest():
  dataToSend = [0x01, 0x55, 0xAA, 0x33, 0x66, 0xCC, 0x99, 0xF0, 0xFF, 0x0F]
  sys.stdout.write("Sending: [")
  for sendByte in dataToSend:
    sys.stdout.write(" 0x%02x" % (sendByte))
  sys.stdout.write(" ]\n")
  spi.SendToSlave(dataToSend)

#
# LoopbackTest:
#
# Sends randomly generated blocks of data over SPI, then reads back 
# data. Assumes that slave is using a common read and write buffer
# and reads the block of data back. The test verifies that the block of 
# data is identical to the one sent. The test will run continuously
# until a received packet does not match the sent packet.
#
def LoopbackTest():
  passCount = 0
  loopbackErrors = 0
  packetByteSize = 4096
  while loopbackErrors == 0:
    print("PassCount: %d" % (passCount))
  
    dataToSend = []
    for randIndex in range(packetByteSize):
      dataToSend.append(random.randint(0, 255))
    
    print("Sending [0x%x 0x%x 0x%x 0x%x 0x%x ...]" % (
        dataToSend[0], dataToSend[1], dataToSend[2],
        dataToSend[3], dataToSend[4]))
    
    # Send some data to the slave
    sys.stdout.write("Sending data to slave...");
    spi.SendToSlave(dataToSend)
    sys.stdout.write("done!\n")
   
    # Receive some data from the slave
    recvData = spi.RecvFromSlave(packetByteSize)
    
    # Make sure bytes sent match bytes received
    if len(recvData) != packetByteSize:
      sys.stdout.write("[FAIL] Did not receive 4096 bytes from spiifc\n")
      sys.exit(0)
    for byteIndex in range(packetByteSize):
      if recvData[byteIndex] != dataToSend[byteIndex]:
        sys.stdout.write("[FAIL] mismatch at index %d: sent=0x%x, recv=0x%x\n" \
            % (byteIndex, dataToSend[byteIndex], recvData[byteIndex]))
        loopbackErrors = loopbackErrors + 1
        if loopbackErrors >= 5:
          break
    if 0 == loopbackErrors:
      sys.stdout.write("[PASS] All loopback SPI bytes match.\n");
      passCount = passCount + 1

  # Print number of passed tests before failure
  print("PassCount: %d" % (passCount))


#
# PrintCliSyntax:
#
# Displays the syntax for the command line interface (CLI)
def PrintCliSyntax():
  print """
Syntax:
  spitest.py test [random-seed]
            
Valid tests (case sensitive): 
  - SingleBytePacketsSend
  - MultiBytePacketSend
  - Loopback
"""

#
# Main
#  

# Parse CLI
if len(sys.argv) < 2 or len(sys.argv) > 3:
  PrintCliSyntax()
  sys.exit(1)

# Retreive specified test function(s)
cliTest = sys.argv[1]
testMapping = {'SingleBytePacketsSend' : [SingleBytePacketsSendTest],
               'MultiBytePacketSend' : [MultiBytePacketSendTest],
               'Loopback' : [LoopbackTest]}
if cliTest not in testMapping:
  sys.stderr.write('%s is not a valid test.\n' % (cliTest,))
  PrintCliSyntax()
  sys.exit(1)
testsToRun = testMapping[cliTest]

# Seed random number generator
if len(sys.argv) == 3:
  seed = int(sys.argv[2])
else:
  seed = datetime.datetime.utcnow().microsecond

# Initialize Cheetah SPI/USB adapter
spi = spilib.SpiComm()

# Seed random
print("Random seed: %d" % seed)
random.seed(seed)

# Run specified test
for testToRun in testsToRun:
  testToRun()

# Close and exit
sys.stdout.write("Exiting...\n")
sys.exit(0)

