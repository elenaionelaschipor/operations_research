\ LP format - for model browsing. Use MPS format to capture full model detail.
\ Signature: 0xfb3e59cf0bac755e
Minimize
  1500 b_0 + 9000 b_1 + 4000 b_2 + 5950 b_3 + 5520 b_4 + 5750 b_5
Subject To
 R0: 30 b_0 + 90 b_1 + 50 b_2 + 70 b_3 + 60 b_4 + 50 b_5 >= 100
 R1: - 3.9 b_0 - 4.5 b_1 - 3.5 b_2 - 1.4 b_3 - 7.2 b_4 + 2.5 b_5 = 0
 R2: - 3 b_0 + 0.9 b_1 + b_2 + 2.8 b_3 + 6 b_4 - b_5 = 0
 R3: 8.4 b_0 + 9.9 b_1 + 4.5 b_2 + 4.2 b_4 + 1.5 b_5 >= 0
 R4: 0.3 b_0 - 0.9 b_1 + b_2 + 2.8 b_3 + 0.6 b_4 <= 0
Bounds
 b_0 <= 1
 b_1 <= 1
 b_2 <= 1
 b_3 <= 1
 b_4 <= 1
 b_5 <= 1
End
