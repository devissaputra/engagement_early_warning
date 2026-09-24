import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'src'))
from engagement_early_warning.core import risk_probability, calibration_bins

probabilities=[risk_probability(1,0,2,.8), risk_probability(10,2,0,.4)]
print('Risk probabilities:', [round(p,3) for p in probabilities])
print('Calibration bins:', calibration_bins(probabilities,[0,1]))
