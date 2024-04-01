#!/bin/bash
hypo=/Usr/local/bin/hyp1.40

# ## gamma to hypoinverse
# python convert_stations.py
# python convert_picks.py
$hypo < hypoinverse.command

