from gurobipy import Model, GRB, quicksum
from random import randint, seed
import numpy as np
import matplotlib.pyplot as plt

# ---------------------------------------- ABOUT DIGIT RECOGNITION  ----------------------------------------
def Parse(filename):
    fh = open(filename, 'r')

    fh.readline()

    Xs, Ys = [], []
    for row in fh:
        line = row.replace('\n','').split(';')
        Ys.append(int(line[0]))
        Xs.append(list(map(int, line[1:])))

    return np.matrix(Xs), np.array(Ys)


def DrawDigit(A):
    plt.imshow(A.reshape((28, 28)), cmap='binary')
    plt.show()


def AccuracyMLP(Xs, Ys, F):
    y_hat = np.array([int(F(x)) for x in Xs])

    n = len(Ys)
    print(y_hat)
    print(Ys)
    return (np.sum(Ys == y_hat))/n*100




def TrainingMLP(Xs, Ys, nh=2,lambda_ = 0.25, return_weights = False):
    # normalise dataset
    Xs  = Xs/np.max(Xs)

    model = Model()
    model.setParam("TimeLimit", 1200)      # Max 5 minutes
    model.Params.Threads = 0  
    epsilon = 0.001  # lower bound of X (nonzeros) will be 1/256
    
   
    # print(t,f) (f will be associated to 0, t to 1 )
    f = min(Ys)
    t = max(Ys)
    #  W1, W2 and absolute values 
    W1 = {}
    W2 = {}
    abs_w_1 = {}
    abs_w_2 = {}   # will do later
    
    n_points = Xs.shape[0]
    dim = Xs.shape[1]
    hidden_layer_dim = nh
    
    # create the matrices
    for i in range(dim+1):
        for j in range(hidden_layer_dim):
            W1[i, j] = model.addVar(lb = -1, ub = 1, obj = 0, vtype= GRB.INTEGER, name = f"W1_{i}_{j}")
            # the absolute values of W1 and W2 are weighted by lambda_ the regularization term
            abs_w_1[i, j] = model.addVar(obj = lambda_, vtype= GRB.BINARY, name = f"abs_W1_{i}_{j}")
            model.addConstr(abs_w_1[i,j] >= W1[i,j])
            model.addConstr(abs_w_1[i,j] >= -W1[i,j])

    for j in range(hidden_layer_dim+1):
        W2[j] = model.addVar(lb = -1, ub = 1, obj = 0, vtype= GRB.INTEGER, name = f"W2_{j}")
        
    sign_inner = {}
    M = 20
    for k in range(n_points):
        for j in range(hidden_layer_dim):
            # product between the elements of Xs and the weights
            p_k_j = quicksum([(1 if i == 0 else Xs[k][0, i-1]) * W1[i, j] for i in range(dim+1)])

            # sign of the product 
            sign_inner[k,j] = model.addVar(obj = 0, vtype= GRB.BINARY, name = f"sign_inner_{k}_{j}")
            
            model.addConstr(p_k_j >= epsilon -M*(1-sign_inner[k,j]), name = f"sign_1_pkj_pos_{k}_{j}")
            model.addConstr(p_k_j <= M*sign_inner[k,j], name = f"sign_0_pkj_neg_{k}_{j}")
    

    # hidden layer: done!
    # -------------------------------------------- 
    g = {}
    w2_neg = []
    w2_zero = []
    w2_pos = []
    prod_s_neg = {}
    prod_s_pos = {}
    
    # we divide W2 into positive negative or zero part which are all 0/1 variables (idea found with the help of chatgpt)   
    for j in range(hidden_layer_dim+1):
            # decomposition of W2
        w2_neg.append( model.addVar(vtype=GRB.BINARY, name=f"w2_neg_{j}"))
        w2_zero.append(  model.addVar(vtype=GRB.BINARY, name=f"w2_zero_{j}"))
        w2_pos.append( model.addVar(vtype=GRB.BINARY, name=f"w2_pos_{j}"))

        model.addConstr(w2_neg[j-1] + w2_zero[j-1] + w2_pos[j-1] == 1)
        model.addConstr(W2[j] == -1 *w2_neg[j-1] + 0 * w2_zero[j-1] + 1 * w2_pos[j-1])
            

    for k in range(n_points):
        # product between W2 and sign_inner; 
        for j in range(hidden_layer_dim+1):
            if j !=0:    
                # gkj is the product between W2[j] and sign[kj] except for j = 0 where we have the bias W2[0] 
                # => gkj is between -1 and 1 and is integer
                g[k,j] = model.addVar(lb = -1, ub = 1, obj = 0, vtype= GRB.INTEGER, name = f"g_{k}_{j}")

                # linearize product between the sign (01) and the positive part (01)...         
                prod_s_pos[k,j] = model.addVar(vtype=GRB.BINARY, name=f"prod_{k}_{j}_pos")
                model.addConstr(prod_s_pos[k,j] <= sign_inner[k,j-1])
                model.addConstr(prod_s_pos[k,j] <= w2_pos[j-1])
                model.addConstr(prod_s_pos[k,j] >= sign_inner[k,j-1] + w2_pos[j-1] - 1)

                
                # and between the sign and the negative part
                prod_s_neg[k,j] = model.addVar(vtype=GRB.BINARY, name=f"prod_{k}_{j}_neg")
                model.addConstr(prod_s_neg[k,j] <= sign_inner[k,j-1])
                model.addConstr(prod_s_neg[k,j] <= w2_neg[j-1])
                model.addConstr(prod_s_neg[k,j] >= sign_inner[k,j-1] + w2_neg[j-1] - 1)
                

                model.addConstr(g[k,j] == -1 * prod_s_neg[k,j] + 1 * prod_s_pos[k,j])
                

    # we use the positive and negative part for the absolute values, too
    for j in range(hidden_layer_dim+1):
        abs_w_2[j] = model.addVar(obj = lambda_, vtype= GRB.BINARY, name = f"abs_W2_{j}")
        model.addConstr(abs_w_2[j] == w2_neg[j-1] + w2_pos[j-1])
        



    # qk = sum of the products between W2 and the actual sign of the hidden layer
    # the sign of the hidden layer is actually 2*sign_inner[k,j] - 1 
    # so when we multiply W2[j] we'll have 2*g[kj] - W2[j] 
    # then we add W2[0] which isn't multiplied by anything
    q = []
    for k in range(n_points):
        q.append(model.addVar(lb = -GRB.INFINITY, ub = GRB.INFINITY, obj = 0, vtype= GRB.INTEGER, name = f"q_{k}"))
        model.addConstr(q[k] == quicksum([2*g[k, j] - W2[j] for j in range(1, hidden_layer_dim+1) ]) + W2[0] )
    
    # sign of q[k]
    sign_outer = []
    M = hidden_layer_dim + 2 #should be a good upper bound
    for k in range(n_points):
        sign_outer.append(model.addVar(obj=0, vtype= GRB.BINARY, name = f"sign_outer{k}")) 
        model.addConstr(q[k] >= 1- M*(1-sign_outer[k]))
        model.addConstr(q[k] <= M*sign_outer[k])

    val_abs = []
    true_Ys = []
    for k in range(n_points):
        true_Ys.append(-f/(t-f) + 1/(t-f)*Ys[k])
        val_abs.append(model.addVar(lb = 0, ub = GRB.INFINITY, obj = 1, vtype=GRB.CONTINUOUS, name = f"val_abs{k}")) 
        model.addConstr(val_abs[k] >= sign_outer[k] - true_Ys[k])
        model.addConstr(val_abs[k] >= -sign_outer[k] + true_Ys[k])

    model.update()
    model.optimize()
    model.write("MLP.lp")


    if model.Status in [2, 9]:
        print("STATUS: ", model.Status)
        W1_sol = np.zeros((dim+1, hidden_layer_dim))
        W2_sol = np.zeros(hidden_layer_dim+1)

        for i in range(dim+1):
            for j in range(hidden_layer_dim):
                W1_sol[i,j] = W1[i, j].X 
        for j in range(hidden_layer_dim+1):
            W2_sol[j] = W2[j].X



        def sol_func(X):
            def hard_sign(x):
                return np.where(x >= 0, 1, -1)
            # np.sign gives 0 when the input is 0 so we don't want that
            X = np.array(X) # we make X an array if it's not
            if len(X.shape) != 1:
                # add ones on the side and multiply by W1
                X_ = np.hstack((np.ones((X.shape[0], 1)), X.reshape(1, X.shape[1])))
                inner_out = hard_sign(X_ @ W1_sol)
                # add ones and multiply by W2
                out = np.hstack((np.ones((X.shape[0], 1)), inner_out)) @ W2_sol
                # we return t or f
                return 0.5*(t-f)*hard_sign(*out) + (t+f)/2
            else:
                # add ones on the side and multiply by W1
                X_ = np.array([1,  *X])
                inner_out = hard_sign(X_ @ W1_sol)
                # add ones and multiply by W2
                out = np.array([1, *inner_out]) @ W2_sol
                # we return t or f
                return 0.5*(t-f)*hard_sign(*out) + (t+f)/2
        
        if return_weights:
            return sol_func, W1_sol, W2_sol
        else:
            return sol_func
    else:
        print("Warning: something is wrong. The status of the model is:", model.Status)



if __name__ == "__main__":
    from sklearn.model_selection import train_test_split
    # for data_train, data_test in zip(['train_nine_four'], ["all_nine_four"]): 
    # for data_train, data_test in zip(['train_three_four'], ["all_three_four"]): 
    for data_train, data_test in zip(['train_three_four', 'train_nine_four'], ["all_three_four", "all_nine_four"]): 
        print("========================"+data_train+"============================")
        X_train, y_train = Parse('../data/'+data_train+'.csv')
        X_test, y_test = Parse('../data/'+data_test+'.csv')
        # X_train, X_test, y_train, y_test = train_test_split(X_all,y_all, test_size=0.7)
        if data_train == 'train_nine_four':
            lambda_= 0.0001
            nh = 5
        if data_train == "train_three_four":
            lambda_ = 0
            nh = 2
    
        print(f"nh: {nh}")
        print(f"lambda: {lambda_}")
        # prediction function
        F, W1, W2 = TrainingMLP(X_train, y_train, nh, lambda_, return_weights = True)
        # Evaluate accuracy
        train_acc = AccuracyMLP(X_train, y_train, F)
        print('training accuracy:', round(train_acc, 2))
        test_acc = AccuracyMLP(X_test, y_test, F)
        print('test accuracy:', round(test_acc, 2))
        
        # print("plot of the weights on the same axes of the images")
        # plt.imshow(W1[1:, 0].reshape(-1).reshape((28, 28)), cmap='binary')
        # plt.show()
        
    


