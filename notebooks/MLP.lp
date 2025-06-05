\ LP format - for model browsing. Use MPS format to capture full model detail.
\ Signature: 0xaab515ca6fcfb36a
Minimize
  z_0 + z_1 + z_2 + z_3
Subject To
 sign_pos_1_0_0: bias_w - w_00 - w_10 - 100000 sign_inner_0_0
   >= -99999.99980000001
 sign_neg_1_0_0: bias_w - w_00 - w_10 - 100000 sign_inner_0_0 <= -0.0002
 sign_pos_1_0_1: bias_w - w_01 - w_11 - 100000 sign_inner_0_1
   >= -99999.99980000001
 sign_neg_1_0_1: bias_w - w_01 - w_11 - 100000 sign_inner_0_1 <= -0.0002
 sign_pos_1_1_0: bias_w - w_00 + w_10 - 100000 sign_inner_1_0
   >= -99999.99980000001
 sign_neg_1_1_0: bias_w - w_00 + w_10 - 100000 sign_inner_1_0 <= -0.0002
 sign_pos_1_1_1: bias_w - w_01 + w_11 - 100000 sign_inner_1_1
   >= -99999.99980000001
 sign_neg_1_1_1: bias_w - w_01 + w_11 - 100000 sign_inner_1_1 <= -0.0002
 sign_pos_1_2_0: bias_w + w_00 - w_10 - 100000 sign_inner_2_0
   >= -99999.99980000001
 sign_neg_1_2_0: bias_w + w_00 - w_10 - 100000 sign_inner_2_0 <= -0.0002
 sign_pos_1_2_1: bias_w + w_01 - w_11 - 100000 sign_inner_2_1
   >= -99999.99980000001
 sign_neg_1_2_1: bias_w + w_01 - w_11 - 100000 sign_inner_2_1 <= -0.0002
 sign_pos_1_3_0: bias_w + w_00 + w_10 - 100000 sign_inner_3_0
   >= -99999.99980000001
 sign_neg_1_3_0: bias_w + w_00 + w_10 - 100000 sign_inner_3_0 <= -0.0002
 sign_pos_1_3_1: bias_w + w_01 + w_11 - 100000 sign_inner_3_1
   >= -99999.99980000001
 sign_neg_1_3_1: bias_w + w_01 + w_11 - 100000 sign_inner_3_1 <= -0.0002
 product1_0: 100000 sign_inner_0_0 + y_0_0 >= 0
 product2_0: - 100000 sign_inner_0_0 + y_0_0 <= 0
 product3_0: - u_0 + y_0_0 <= 0
 product4_0: - u_0 - 100000 sign_inner_0_0 + y_0_0 >= -100000
 product1_0: 100000 sign_inner_0_1 + y_0_1 >= 0
 product2_0: - 100000 sign_inner_0_1 + y_0_1 <= 0
 product3_0: - u_1 + y_0_1 <= 0
 product4_0: - u_1 - 100000 sign_inner_0_1 + y_0_1 >= -100000
 product1_1: 100000 sign_inner_1_0 + y_1_0 >= 0
 product2_1: - 100000 sign_inner_1_0 + y_1_0 <= 0
 product3_1: - u_0 + y_1_0 <= 0
 product4_1: - u_0 - 100000 sign_inner_1_0 + y_1_0 >= -100000
 product1_1: 100000 sign_inner_1_1 + y_1_1 >= 0
 product2_1: - 100000 sign_inner_1_1 + y_1_1 <= 0
 product3_1: - u_1 + y_1_1 <= 0
 product4_1: - u_1 - 100000 sign_inner_1_1 + y_1_1 >= -100000
 product1_2: 100000 sign_inner_2_0 + y_2_0 >= 0
 product2_2: - 100000 sign_inner_2_0 + y_2_0 <= 0
 product3_2: - u_0 + y_2_0 <= 0
 product4_2: - u_0 - 100000 sign_inner_2_0 + y_2_0 >= -100000
 product1_2: 100000 sign_inner_2_1 + y_2_1 >= 0
 product2_2: - 100000 sign_inner_2_1 + y_2_1 <= 0
 product3_2: - u_1 + y_2_1 <= 0
 product4_2: - u_1 - 100000 sign_inner_2_1 + y_2_1 >= -100000
 product1_3: 100000 sign_inner_3_0 + y_3_0 >= 0
 product2_3: - 100000 sign_inner_3_0 + y_3_0 <= 0
 product3_3: - u_0 + y_3_0 <= 0
 product4_3: - u_0 - 100000 sign_inner_3_0 + y_3_0 >= -100000
 product1_3: 100000 sign_inner_3_1 + y_3_1 >= 0
 product2_3: - 100000 sign_inner_3_1 + y_3_1 <= 0
 product3_3: - u_1 + y_3_1 <= 0
 product4_3: - u_1 - 100000 sign_inner_3_1 + y_3_1 >= -100000
 sign_pos_2_0: bias_u - 100000 sign_outer_0 + y_0_0 + y_0_1
   >= -99999.99980000001
 sign_neg_2_0: bias_u - 100000 sign_outer_0 + y_0_0 + y_0_1 <= -0.0002
 sign_pos_2_1: bias_u - 100000 sign_outer_1 + y_1_0 + y_1_1
   >= -99999.99980000001
 sign_neg_2_1: bias_u - 100000 sign_outer_1 + y_1_0 + y_1_1 <= -0.0002
 sign_pos_2_2: bias_u - 100000 sign_outer_2 + y_2_0 + y_2_1
   >= -99999.99980000001
 sign_neg_2_2: bias_u - 100000 sign_outer_2 + y_2_0 + y_2_1 <= -0.0002
 sign_pos_2_3: bias_u - 100000 sign_outer_3 + y_3_0 + y_3_1
   >= -99999.99980000001
 sign_neg_2_3: bias_u - 100000 sign_outer_3 + y_3_0 + y_3_1 <= -0.0002
 abs_0_1: 2 bias_u + 2 y_3_0 + 2 y_3_1 + z_0 >= 0
 abs_0_2: - 2 bias_u - 2 y_3_0 - 2 y_3_1 + z_0 >= 0
 abs_1_1: 2 bias_u + 2 y_3_0 + 2 y_3_1 + z_1 >= 2
 abs_1_2: - 2 bias_u - 2 y_3_0 - 2 y_3_1 + z_1 >= -2
 abs_2_1: 2 bias_u + 2 y_3_0 + 2 y_3_1 + z_2 >= 2
 abs_2_2: - 2 bias_u - 2 y_3_0 - 2 y_3_1 + z_2 >= -2
 abs_3_1: 2 bias_u + 2 y_3_0 + 2 y_3_1 + z_3 >= 0
 abs_3_2: - 2 bias_u - 2 y_3_0 - 2 y_3_1 + z_3 >= 0
Bounds
 bias_w free
 bias_u free
 w_00 free
 w_10 free
 u_0 free
 w_01 free
 w_11 free
 u_1 free
 y_0_0 free
 y_0_1 free
 y_1_0 free
 y_1_1 free
 y_2_0 free
 y_2_1 free
 y_3_0 free
 y_3_1 free
Binaries
 sign_inner_0_0 sign_inner_0_1 sign_inner_1_0 sign_inner_1_1 sign_inner_2_0
 sign_inner_2_1 sign_inner_3_0 sign_inner_3_1 sign_outer_0 sign_outer_1
 sign_outer_2 sign_outer_3
End
