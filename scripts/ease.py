"""Find the initial Anki ease factor which makes the Anki 'Good'
difficulty rating most closely match the WaniKani SRS intervals.
"""
import sys
import numpy as np

def days_to_months(days):
    return round(days / 28, 1)

def stages(rate, print_results):
  stage = 1
  # targets = [3, 7, 14, 28, 28*4]
  targets = [3, 7, 14, 28, 28*2, 28*4]
  max_error = 0
  for i in range(10):
     stage *= rate * 1.24
     stage = round(stage + 0.0001)
     if i < len(targets):
         target = targets[i]
         error = target - stage
         if abs(error) > max_error: max_error = abs(error)
         if print_results: print(stage, target, error)
     else:
         if print_results: print(days_to_months(stage), 'months')
  return max_error

if len(sys.argv) > 1:
    stages(float(sys.argv[1]), True)
else:
    min_max_error = 1000000
    min_max_error_rate = 0

    for rate in np.arange(2, 3, 0.001):
        max_error = stages(rate, False)
        if max_error < min_max_error:
            min_max_error = max_error
            min_max_error_rate = rate

    print('min max error and its rate:', min_max_error, min_max_error_rate)
