# Hydro Grow - Running Project State

Last updated: 2026-04-18

## Setup
- 5x5x7 grow tent, Jacksonville FL apartment, AC at 72F
- DWC (deep water culture), two 5-gallon buckets
- Growing: 2x tomato plants, one per bucket
  - Seeds available (all Baker Creek Heirloom): Purple Tomatillo, Gold Medal, Spoon, Black Strawberry, Black Krim, Alice's Dream, Evil Olive
  - GROWING: Black Krim (Bucket A) + Evil Olive (Bucket B) -- Tim's plants, gift from Braxton
  - Future expansion: lettuce, basil, radicchio, remaining tomato varieties

## Equipment - What We Have
- Raspberry Pi 4
- 8-channel relay board
- Air stones
- Air pump
- Solenoid valves (arrived Apr 17) -- routes nutrient/pH dosing flow to either bucket A or bucket B. One set of peristaltic pumps serves both buckets, solenoid valve switches which bucket receives the dose.
- TDS/EC meter probe (for measuring nutrient concentration in PPM)
- 12V DC power supply (for pumps/solenoids)
- Grow light: Carambola CBG4000DM (dimmable), 560W actual draw
- Nutrients: PowerGrow MasterBlend 3-part system (powdered)
  - MasterBlend 4-18-38 + Calcium Nitrate 15.5-0-0 + Epsom Salt
  - Mix ratio: 2g MB + 2g CalNit + 1g Epsom per gallon
  - CRITICAL: CalNit SEPARATE from MB+Epsom in stock solutions
  - Reservoir A = MasterBlend + Epsom | Reservoir B = Calcium Nitrate
- pH Down + pH Up solutions
  - Need wide-mouth HDPE containers for all 4 stock solutions
- Clay pebbles (growing medium)

## Equipment - Arriving Today/Tomorrow
- 4 peristaltic pumps (ordered, arriving Apr 18)
- Bucket lids (ordered, arriving Apr 18)
- Water level sensors (ordered, arriving Apr 18)
- 16-channel relay board - ACEIRMC 5V 16-channel, $14.99 (ordered Apr 16, arriving Apr 19)
- Inline exhaust fan - Simple Deluxe 6" 240 CFM (ordered Apr 18, arriving Apr 19)
- CPU cooler for chiller - ID-COOLING SE-903-XT V2, $14.99 (ordered Apr 18, arriving Apr 19)

## Equipment - Arriving Apr 19 (ordered Apr 18)
- DROK 5-pack DS18B20 waterproof temp probes w/ adapter board + resistors ($9.99)
- JLJ Thermal Paste 4g ($4.44)
- Water Cooling Block 2-pack 40x40mm ($7.99)
- Simple Deluxe 6" Inline Fan 240 CFM ($24.99)
- SUPERNIGHT 12V 30A Switching PSU ($20.99) -- dedicated chiller power supply
- bayite 12V DC Diaphragm Pump ($20.95) -- chiller water pump
- ID-COOLING SE-903-XT V2 CPU Cooler ($14.99) -- chiller hot side

## Equipment - Arriving Apr 20
- Web cam
- 4.7K ohm resistors 100-pack ($5.99) -- may not need, DROK kit includes some

## Equipment - Arriving Apr 22-27
- Peltier TEC1-12709 (ordered from eBay, Apr 22-27)

## Equipment - Arriving Apr 27 - May 6
- pH sensor module (Reland Sung, BNC electrode, $20, ordered Apr 15)

## Equipment - Already Have (not previously tracked)
- Grow light: Carambola CBG4000 quantum board LED, 4-panel layout
  - Model: CBG4000DM (dimmable), 560W actual draw
  - Braxton may run 2 panels instead of 4 to reduce heat
  - 1,152 LEDs: 720x 3500K white + 400x red + 32x UV
  - Generic SMD LEDs (not Samsung LM301B)
  - Efficacy: 2.7 umol/J, PPF ~1,100-1,274 umol/s
  - Coverage: 5x5 veg, 4x4 bloom
  - Fanless passive cooling, ~1,638-1,911 BTU/hr heat output
  - 24" x 24" x 2.17", 11 lbs
- Nutrients: PowerGrow MasterBlend 3-part system (powdered)
  - MasterBlend 4-18-38 + Calcium Nitrate 15.5-0-0 + Epsom Salt
  - Mix ratio: 2g MB + 2g CalNit + 1g Epsom per gallon
  - CRITICAL: CalNit SEPARATE from MB+Epsom in stock solutions
  - Reservoir A = MasterBlend + Epsom | Reservoir B = Calcium Nitrate
- pH Down + pH Up solutions
  - Need wide-mouth HDPE containers for all 4 stock solutions
- Clay pebbles (growing medium)

## Equipment - Already Have (additional)
- 27-gallon reservoir tote (central reservoir for RDWC hybrid)
- TotalPond 1/2" I.D. flexible tubing, 20 ft (chiller loop)
- Drip irrigation kit (white tubing + red drip emitters + clips) -- repurpose for top-feed
- Clear vinyl/silicone tubing (~1/4"-3/8" ID) -- for peristaltic pump lines
- Wire nuts (red + orange assorted bag)
- Hose clamps (small pack)
- Mechanical plug-in timer (backup, Pi handles scheduling)
- Multiple coils of black tubing (various sizes)
- Small power adapters (wall warts)

## Equipment - Still Needed (not yet ordered)
- Net pots (if not already have)
- 5-gallon buckets (2x, if not already have)
- PVC pipe + fittings (connect buckets to reservoir)
- Small submersible/inline pump (return water from reservoir to drip rings)

## Key Decisions Made
- Light schedule: 14/10 (8am-10pm) for tomatoes
- Chiller control: hysteresis (on >70F, off <66F)
- Exhaust fan: hysteresis (on >80F, off <76F)
- DIY where possible to keep costs down
- NO CO2 enrichment -- unsafe in apartment setting, ambient CO2 is fine
- Need oscillating clip fan inside tent for air circulation + pollination
- Need CO2 sensor (monitoring only), light sensor, possibly DO sensor

## Software Status
- Flask + SocketIO dashboard working (app.py)
- Mock sensors with realistic drift for dev testing
- 8 relay channels configured: grow light, air pump, exhaust fan, water chiller, pH down, pH up, nutrient A, nutrient B
- Water temp sensor card added to dashboard

## Open Questions
- Nutrient brand/type chosen?
- Does Braxton have net pots and 5-gallon buckets?
- Thermal paste + hose clamps -- does he have these already?

## Braxton's Vision
- "Braxtonian Farms" -- life purpose from Ayahuasca ceremony
- This grow is the seed of something bigger
- AI-controlled garden, content creation opportunity
- Keep costs down -- not profitable on sports betting yet
- Domain: BraxtonianFarms.com (Braxton buying)
- Dashboard needs to be visual/futuristic for content -- dark theme, live data, charts, webcam
- Future: public dashboard at BraxtonianFarms.com showing live grow data
