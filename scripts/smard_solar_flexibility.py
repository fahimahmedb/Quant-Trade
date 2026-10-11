#!/usr/bin/env python3
"""Single pre-registered noon-to-evening policy, never the consumed night policy."""
import argparse
import json
from pathlib import Path
from quant.edge_lab.smard_solar import run

parser=argparse.ArgumentParser(description=__doc__)
parser.add_argument('--protocol',required=True)
parser.add_argument('--look',required=True)
args=parser.parse_args()
print(json.dumps(run(Path(__file__).resolve().parents[1],args.protocol,args.look),allow_nan=False),flush=True)
