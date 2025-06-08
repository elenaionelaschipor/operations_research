\ LP format - for model browsing. Use MPS format to capture full model detail.
\ Signature: 0x9f8709c4922bf835
Minimize
  z_1 + z_2 + z_3 + z_4
Subject To
 sign_pos_0: bias - w_1 - w_2 - 2 c_1 >= -1.99998
 sign_neg_0: bias - w_1 - w_2 - 2 c_1 <= -2e-05
 abs_0_1: 2 c_1 + z_1 >= 0
 abs_0_2: - 2 c_1 + z_1 >= 0
 sign_pos_1: bias - w_1 + w_2 - 2 c_2 >= -1.99998
 sign_neg_1: bias - w_1 + w_2 - 2 c_2 <= -2e-05
 abs_1_1: 2 c_2 + z_2 >= 0
 abs_1_2: - 2 c_2 + z_2 >= 0
 sign_pos_2: bias + w_1 - w_2 - 2 c_3 >= -1.99998
 sign_neg_2: bias + w_1 - w_2 - 2 c_3 <= -2e-05
 abs_2_1: 2 c_3 + z_3 >= 0
 abs_2_2: - 2 c_3 + z_3 >= 0
 sign_pos_3: bias + w_1 + w_2 - 2 c_4 >= -1.99998
 sign_neg_3: bias + w_1 + w_2 - 2 c_4 <= -2e-05
 abs_3_1: 2 c_4 + z_4 >= 2
 abs_3_2: - 2 c_4 + z_4 >= -2
Bounds
 bias free
 w_1 free
 w_2 free
Binaries
 c_1 c_2 c_3 c_4
End
