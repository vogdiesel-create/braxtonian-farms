# Hydro Grow - Complete Wiring Guide

**Date**: 2026-04-18
**Status**: Ready for wiring day (relay board arrives Apr 19)

---

## SAFETY FIRST

- **UNPLUG EVERYTHING** before wiring. No exceptions.
- **120V AC mains can kill you.** Double-check every connection before plugging in.
- Never work on live circuits.
- Use wire nuts or solder + heat shrink on all AC connections. No bare wire exposed.
- Keep AC wiring away from water at all times.
- The relay board and Pi should be mounted OUTSIDE or ABOVE the tent, not inside where humidity is high.

---

## What You're Wiring

### Relay Channels (16 available)

| Channel | Device | Voltage | Type |
|---------|--------|---------|------|
| 1 | Grow Light | 120V AC | Scheduled |
| 2 | Air Pump | 120V AC | Always on (or scheduled) |
| 3 | Exhaust Fan | 120V AC | Sensor-triggered (future) |
| 4 | Water Chiller | 120V AC | Sensor-triggered (future) |
| 5 | Peristaltic Pump - pH Down | 12V DC | Software-triggered |
| 6 | Peristaltic Pump - pH Up | 12V DC | Software-triggered |
| 7 | Peristaltic Pump - Nutrient A | 12V DC | Software-triggered |
| 8 | Peristaltic Pump - Nutrient B | 12V DC | Software-triggered |
| 9 | Solenoid Valve - Bucket A | 12V DC | Software-triggered |
| 10 | Solenoid Valve - Bucket B | 12V DC | Software-triggered |
| 11-16 | SPARE | -- | Future use |

### Direct to Pi GPIO (no relay)

| Device | Pi Pin | Protocol |
|--------|--------|----------|
| Water Level Sensor - Bucket A | GPIO 23 | Digital |
| Water Level Sensor - Bucket B | GPIO 24 | Digital |
| Water Temp Probe (DS18B20) | GPIO 4 | 1-Wire (future, not yet ordered) |

---

## What You Need on Hand

### Parts
- [ ] Raspberry Pi 4 (with SD card, power supply)
- [ ] 16-channel relay board
- [ ] Grow light (Carambola CBG4000DM)
- [ ] Air pump
- [ ] 4x peristaltic pumps
- [ ] 2x solenoid valves
- [ ] 2x water level sensors
- [ ] 2x 5-gallon buckets with lids
- [ ] Air stones (2x, one per bucket)
- [ ] Clay pebbles
- [ ] Net pots

### Supplies
- [ ] Jumper wires (female-to-female, for Pi GPIO to relay board)
- [ ] 12V DC power supply (for pumps + solenoid valves) -- check amp requirements
- [ ] Wire nuts (for AC connections)
- [ ] Electrical tape or heat shrink tubing
- [ ] Wire strippers
- [ ] Small flathead screwdriver (for relay terminal screws)
- [ ] Zip ties (cable management)
- [ ] Silicone tubing (for peristaltic pumps to buckets)
- [ ] A power strip (to plug AC devices into)

### Nice to Have
- [ ] Multimeter (to verify connections)
- [ ] Mounting board or shelf (to mount Pi + relay outside tent)
- [ ] 4.7k ohm resistor (for DS18B20 temp probe pull-up, future)

---

## STEP-BY-STEP INSTRUCTIONS

### Phase 1: Set Up the Raspberry Pi

**Time: 15-20 min**

1. Flash Raspberry Pi OS (Lite or Desktop) onto the SD card using Raspberry Pi Imager
   - Enable SSH during setup
   - Set your WiFi credentials during setup
   - Set username/password

2. Boot the Pi, SSH in or connect a monitor

3. Update the system:
   ```
   sudo apt update && sudo apt upgrade -y
   ```

4. Install Python libraries:
   ```
   sudo apt install python3-pip python3-venv -y
   pip3 install RPi.GPIO Flask flask-socketio apscheduler
   ```

5. Enable 1-Wire interface (for future DS18B20 temp probe):
   ```
   sudo raspi-config
   ```
   -> Interface Options -> 1-Wire -> Enable

6. Verify GPIO works:
   ```
   python3 -c "import RPi.GPIO as GPIO; print('GPIO ready')"
   ```

---

### Phase 2: Mount the Relay Board

**Time: 10 min**

1. Pick a location OUTSIDE or on TOP of the tent -- keep it dry
2. Mount the relay board to a board/shelf with screws or standoffs
3. Place the Pi next to it

---

### Phase 3: Wire Relay Board to Pi

**Time: 15 min**

The 16-channel relay board has these pins:
- **VCC** -> Pi 5V (Pin 2 or 4)
- **GND** -> Pi GND (Pin 6, 9, 14, 20, 25, 30, 34, or 39)
- **IN1 through IN16** -> Pi GPIO pins

Use female-to-female jumper wires for all connections.

**GPIO Pin Assignments:**

| Relay Channel | Pi GPIO | Pi Physical Pin |
|---------------|---------|-----------------|
| IN1 (Grow Light) | GPIO 17 | Pin 11 |
| IN2 (Air Pump) | GPIO 27 | Pin 13 |
| IN3 (Exhaust Fan) | GPIO 22 | Pin 15 |
| IN4 (Water Chiller) | GPIO 5 | Pin 29 |
| IN5 (pH Down Pump) | GPIO 6 | Pin 31 |
| IN6 (pH Up Pump) | GPIO 13 | Pin 33 |
| IN7 (Nutrient A Pump) | GPIO 19 | Pin 35 |
| IN8 (Nutrient B Pump) | GPIO 26 | Pin 37 |
| IN9 (Solenoid Bucket A) | GPIO 12 | Pin 32 |
| IN10 (Solenoid Bucket B) | GPIO 16 | Pin 36 |
| IN11-16 (spare) | -- | -- |

**Water level sensors (direct to GPIO, no relay):**

| Sensor | Pi GPIO | Pi Physical Pin |
|--------|---------|-----------------|
| Water Level Bucket A | GPIO 23 | Pin 16 |
| Water Level Bucket B | GPIO 24 | Pin 18 |
| DS18B20 Temp (future) | GPIO 4 | Pin 7 |

**Wiring Steps:**
1. Connect VCC on relay board to Pi Pin 2 (5V) with jumper wire
2. Connect GND on relay board to Pi Pin 6 (GND) with jumper wire
3. Connect IN1 to Pi Pin 11 (GPIO 17) -- this is the grow light
4. Connect IN2 to Pi Pin 13 (GPIO 27) -- this is the air pump
5. Continue for each relay channel per the table above
6. Connect water level sensors: signal wire to GPIO, VCC to 3.3V (Pin 1), GND to GND

**NOTE:** Most 16-channel relay boards are active LOW -- the relay triggers when the GPIO pin goes LOW (0V). The software handles this, just be aware.

---

### Phase 4: Wire AC Devices Through Relays (120V -- BE CAREFUL)

**Time: 20-30 min**

**UNPLUG EVERYTHING FROM THE WALL FIRST.**

For each AC device (grow light, air pump, future exhaust fan, future chiller):

1. Cut the power cord's **hot wire only** (black wire). Leave neutral (white) and ground (green) intact.
   - Cut about 12 inches from the plug end so you have room to work

2. Strip about 1/2 inch of insulation from both cut ends

3. Connect to the relay terminal:
   - One end of the cut wire -> **COM** (Common) terminal on the relay
   - Other end -> **NO** (Normally Open) terminal on the relay
   - Tighten the terminal screws firmly

4. Secure connections with electrical tape

5. Repeat for each AC device:
   - Relay 1 COM/NO -> Grow light hot wire
   - Relay 2 COM/NO -> Air pump hot wire
   - (Relay 3 and 4 are for future exhaust fan and chiller)

**Why NO (Normally Open)?**
- If the Pi crashes or loses power, the relay opens and devices turn OFF
- This is the safe default -- you don't want the light running 24/7 if the Pi dies

**TEST BEFORE POWERING ON:**
- Use a multimeter on continuity mode
- Touch probes to the two ends of the cut wire
- Trigger the relay manually (jumper IN1 to GND briefly)
- You should hear a click and see continuity

---

### Phase 5: Wire DC Devices Through Relays (12V -- Low Voltage, Safe)

**Time: 20 min**

The peristaltic pumps and solenoid valves run on 12V DC. They need a separate 12V power supply.

**How it works:**
- 12V power supply positive (+) wire goes to relay COM
- Relay NO connects to the device's positive (+) wire
- Device's negative (-) wire goes back to power supply negative (-)
- When relay triggers, it completes the 12V circuit and the device turns on

**For each peristaltic pump (4 pumps):**
1. Run 12V+ from power supply to relay COM terminal (channels 5-8)
2. Run wire from relay NO terminal to pump + wire
3. Run pump - wire back to 12V power supply GND
4. Attach silicone tubing to pump inlet and outlet

**For each solenoid valve (2 valves):**
1. Run 12V+ from power supply to relay COM terminal (channels 9-10)
2. Run wire from relay NO terminal to solenoid + wire
3. Run solenoid - wire back to 12V power supply GND

**Tubing layout for dosing system:**
```
                    Solenoid A -----> Bucket A
Peristaltic Pump -->|
                    Solenoid B -----> Bucket B
```
Each peristaltic pump (pH down, pH up, nutrient A, nutrient B) feeds into a Y-splitter or manifold. The solenoid valves direct the flow to either Bucket A or Bucket B.

**Dosing sequence (software controls this):**
1. Open Solenoid A (close B)
2. Run pH Down pump for X seconds
3. Close Solenoid A
4. Open Solenoid B (close A)
5. Run pH Down pump for X seconds
6. Close Solenoid B

---

### Phase 6: Set Up the DWC Buckets

**Time: 20 min**

1. Drill holes in bucket lids for net pots (size depends on your net pots)
2. Drill a small hole in each lid for the air stone tubing
3. Drill holes for water level sensor wires
4. Fill buckets with water (leave 1-2 inches from the top of the net pot)
5. Add clay pebbles to net pots
6. Drop air stones into buckets, run tubing through lid holes to air pump
7. Mount water level sensors inside buckets (through lid)
8. Position buckets inside tent

---

### Phase 7: Set Up the Tent

**Time: 15 min**

1. Assemble the tent frame and cover
2. Hang the grow light from the top bars using ratchet hangers or zip ties
   - Start at 24 inches above where the plant tops will be
   - Consider running only 2 panels to reduce heat
3. Place buckets on the tent floor
4. Route all wiring out through a vent port -- keep relay/Pi OUTSIDE
5. Air pump stays OUTSIDE the tent (cleaner air intake)
6. Run air stone tubing from pump into tent through a vent port

---

### Phase 8: Power On and Test

**Time: 15 min**

1. Double-check ALL wiring connections
2. Make sure no bare wires are exposed on AC connections
3. Plug in the Pi -- let it boot
4. SSH in, run the test script:
   ```
   python3 test_relays.py
   ```
   This will cycle each relay on/off so you can verify each device works

5. Test each device one at a time:
   - Grow light: should turn on/off
   - Air pump: should turn on/off, check bubbles in buckets
   - Each peristaltic pump: should spin (run briefly, they shouldn't run dry for long)
   - Each solenoid valve: should click open/close

6. Check water level sensors: dip in water, verify readings

7. If everything works, start the dashboard:
   ```
   python3 app.py
   ```

---

## Wiring Diagram (Text)

```
                    [120V AC WALL OUTLET]
                           |
                     [POWER STRIP]
                      /    |    \
                     /     |     \
            [Relay1-NO] [Relay2-NO] [Relay3-NO future]
            [Relay1-COM] [Relay2-COM] ...
                |          |
          [GROW LIGHT] [AIR PUMP]


         [12V DC POWER SUPPLY]
          +                 -
          |                 |
    [Relay5-COM]     [All device GND]
    [Relay5-NO]-->[pH Down Pump +]
    [Relay6-NO]-->[pH Up Pump +]
    [Relay7-NO]-->[Nutrient A Pump +]
    [Relay8-NO]-->[Nutrient B Pump +]
    [Relay9-NO]-->[Solenoid Valve A +]
    [Relay10-NO]->[Solenoid Valve B +]


         [RASPBERRY PI 4]
          |  |  |  |  |
         GPIO pins via jumper wires
          |  |  |  |  |
    [16-CHANNEL RELAY BOARD]
     IN1 IN2 ... IN10  VCC GND
```

---

## Shopping List -- Stuff You Might Not Have

- [ ] Female-to-female jumper wires (at least 20) -- ~$6
- [ ] 12V DC power supply (enough amps for 4 pumps + 2 solenoids) -- ~$10-15
- [ ] Wire nuts assorted pack -- ~$5
- [ ] Wire strippers (if you don't have) -- ~$8
- [ ] Silicone tubing for peristaltic pumps -- check pump fitting size
- [ ] Small flathead screwdriver -- for relay terminals

---

## After Wiring Day

Once everything is wired and tested, I'll have the software ready:
- Light schedule automation (14/10, 8am-10pm)
- Air pump control
- Dashboard accessible from your phone
- Dosing logic framework (ready for when you calibrate pumps)
- Water level monitoring
