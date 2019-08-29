"""
Plot the results of one experiment, each dot is one seed plus one red dot for the average model
x-axis: precision
y-axis: recall

additional output to stdout:
  Mean F-Score
  Range
  Std F-Score
  Mean Precision
  Mean Recall
"""

import sys
import numpy as np
import matplotlib.pyplot as plt

results = open(sys.argv[1], "r")

precision = []
recall = []
f1 = []
for line in results:
    try:
        head,number = line.split(":")
        number = float(number.strip())
        if head == "precision":
            precision.append(number)
        elif head == "recall":
            recall.append(number)
        elif head == "F1":
            f1.append(number)
    except:
        pass
precision = np.array(precision)
recall = np.array(recall)
f1 = np.array(f1)

mean_f = np.mean(f1)
R_f = np.max(f1) - np.min(f1)
std_f = np.std(f1)

mean_p = np.mean(precision)
mean_r = np.mean(recall)

print("Mean F-Score:", mean_f)
print("R:", R_f)
print("Std F-Score:", std_f)
print("Mean Precision:", mean_p)
print("Mean Recall:", mean_r)

plt.scatter(precision,recall)
plt.xlabel('Precision')
plt.ylabel('Recall')
plt.scatter(mean_p, mean_r, color = "red")
plt.show()

