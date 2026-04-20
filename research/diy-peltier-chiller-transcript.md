# DIY Hydroponics DWC Reservoir Chiller - Transcript

**Source**: https://youtu.be/NkJIsulkoeY
**Channel**: Smart Grow Automation
**Duration**: 8m 28s
**Extracted**: 2026-04-18

## Full Transcript

Hey everybody, today I'm gonna show you how to make a DIY reservoir chiller for hydroponics. First I'm going to go over the components and then I'm going to show you it assembled and operating.

So the heart of this chiller is this thing -- this is called a thermoelectric cooler or Peltier cooler. It is a solid-state device that when voltage is applied to it, it moves heat. Basically what it does is when voltage is applied, one side gets hot, the other side gets cold. And the name of the game is: the cooler you can keep the hot side, the colder the cold side will get, because this essentially makes a difference in temperature. So if the hot side is cold, the cold side will be even colder.

To that end I have a CPU chiller that will sit on the hot side and keep it as cool as possible. And this CPU chiller is able to keep the cold side of this Peltier at about room temperature, which is great.

You also need thermal compound to attach the tube and then on the other side of this (which I can't show right now but I'll show in the final setup) is a water block -- an aluminum water block that will allow water to come in, get cold, and then come out. So that is another common device used in water chillers for CPU cooling on a computer.

### Pumps

Now to move the water through that block you're gonna need a pump. I got three pumps here actually:

1. **First pump (~$7)**: Great but it failed at ten days. Called Amazon, they gave me a replacement -- the replacement failed in ten days. Love the size, love the sound (this thing is silent compared to these guys), and the cost. But it just does not last. Can't recommend it.

2. **Second pump**: Mistakenly an air-only pump. That was fun figuring that out.

3. **Current pump (recommended)**: Large, can pump 4 liters a minute (vs 1.5 L/min for the first). It's loud but powerful and reliable. Been working well.

### Tubing

You also need silicon tubing or really any tubing. You probably don't want something totally transparent because the light can get through and allow algae to grow. Something to keep in mind. If you're buying stuff, you might want to get something not translucent.

### Other Components

- **Hose clamps**: Reusable springy hose clamps, pinch-style, in a few different sizes
- **Power supply**: Everything is 12 volts. Using a Meanwell power supply (reliable brand in the LED driver world)

### Power Supply Sizing (IMPORTANT)

The size of the power supply -- 12 volts, and in terms of amperage, you're gonna want to look at your TEC. Those last two numbers (e.g., TEC1-12**10**) -- that 10 is the amperage. So this guy can periodically draw 10 amps. The pump is about 3 amps and the fan is maybe an amp, probably less. So that puts us at 13-14 amps at 12 volts.

His power supply: 12V, 29 amps -- more than enough. Make sure your power supply can hit the currents needed.

### Assembly

1. Sandwich your Peltier cooler between your CPU fan and your water chilling block
2. **Figure out which side is the cold side**: Apply 12 volts for just like 2 seconds. If you apply voltage for longer than that without a cooling fan, you'll quickly overheat and destroy the device
3. Usually the side with the lettering is the cold side
4. Cold side goes against the water chilling block
5. Hot side goes against the CPU fan

### Operation

- Got everything up and running
- Filter setup: wire mesh wrapped with a large teabag-style filter
- Chiller has been working great
- Performance graphs shown in video

## Parts List (from video description)

| Item | Price |
|------|-------|
| Peltier (TEC1-12709) | $3.84 |
| Aluminum Water Block (40mm x 40mm) | $3.40 |
| Flexible tubing | $6.68 |
| 12V Power Supply | $17.98 |
| Water Pump | $17.99 |
| CPU Cooling Fan | $21.99 |
| **TOTAL** | **~$72** |

## Key Takeaways for Our Build

1. **Total cost ~$72** vs $280+ for commercial chiller -- massive savings
2. **Peltier TEC1-12709**: 9 amps max draw, needs 12V supply
3. **Power supply must handle total amp draw**: Peltier + pump + fan = ~14A at 12V
4. **Meanwell PSU recommended** -- reliable, commonly used for LED drivers
5. **Cheap pumps fail fast** -- spend more on a reliable pump (4 L/min recommended)
6. **Use opaque tubing** to prevent algae growth
7. **Cold side identification**: Quick 2-second 12V test, usually the lettered side
8. **Thermal compound required** between Peltier and both the CPU cooler and water block
9. **Don't run Peltier without cooling** -- will overheat and destroy itself in seconds
