"""Reproduce the labeled worked example; this is not an empirical study."""
import json,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'src'))
from engagement_early_warning import core
outputs={'sigmoid of zero': core.sigmoid(0), 'Brier: predictions .8,.3; outcomes 1,0': ((.8-1)**2+(.3-0)**2)/2}
result={'kind':'illustrative_calculation','note':'Illustrative risk and probability-loss arithmetic.','outputs':outputs}
(ROOT/'results/review_examples.json').write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps(result,indent=2))
