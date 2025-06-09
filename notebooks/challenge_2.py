from gurobipy import Model, GRB, quicksum
from random import randint, seed
import numpy as np



## from the first part of the exercise

# AND function
Xand = [(-1,-1), (-1, 1), (1,-1), (1,1)]
Yand = [-1, -1, -1, 1] 

# OR function
Xor = [(-1,-1), (-1, 1), (1,-1), (1,1)]
Yor = [-1, 1, 1, 1]

# XOR function
Xxor = [(-1, -1), (-1, 1), (1, -1), (1, 1)]
Yxor = [-1, 1, 1, -1]

import matplotlib.pyplot as plt
def plot_mlp_decision_boundary(sol_func, Xs, Ys, title="Decision Boundary", random = False, ranges = [(-1.5, 1.5), (-1.5, 1.5)]):
    Xs = np.array(Xs)
    Ys = np.array(Ys)

    # Definizione della griglia
    num_points = 200

    grid_axes = [np.linspace(start, end, num_points) for start, end in ranges]
    xx, yy = np.meshgrid(*grid_axes)
    grid_points = np.c_[xx.ravel(), yy.ravel()]

    # Valori predetti sulla griglia
    Z = sol_func(grid_points).reshape(xx.shape)

    # Plot dello sfondo (output del modello)
    plt.contourf(xx, yy, Z, levels=[-1, 0, 1], alpha=0.4, cmap="coolwarm")

    if not random:
    # Punti di input originali
        for y_val, color, label in zip([-1, 1], ["blue", "pink"], ["FALSE (-1)", "TRUE (+1)"]):
            mask = (Ys == y_val)
            plt.scatter(Xs[mask][:, 0], Xs[mask][:, 1], 
                        c=color, edgecolors="k", label=label, s=80)
        plt.legend()
    
    plt.xlabel("X1")
    plt.ylabel("X2")
    plt.title(title)
   
    plt.grid(True)
    plt.axis('equal')
    plt.tight_layout()
    plt.show()


def MLP_integer(Xs, Ys, epsilon, max_hidden_layer = 100, return_weights = False):
    # Main ILP model
    model = Model()
    # variabili W1, W2 
    W1 = {}
    W2 = {}
    n_points = len(Xs)
    dim = len(Xs[0])
    hidden_layer_dim =max_hidden_layer
    M = 20
    # create the matrices
    for i in range(dim+1):
        for j in range(hidden_layer_dim):
            W1[i, j] = model.addVar(lb = -1, ub = 1, obj = 0, vtype= GRB.INTEGER, name = f"W1_{i}_{j}")
    for j in range(hidden_layer_dim+1):
        W2[j] = model.addVar(lb = -1, ub = 1, obj = 0, vtype= GRB.INTEGER, name = f"W2_{j}")

    sign_inner = {}
    z = {}
    for k in range(n_points):
        for j in range(hidden_layer_dim):
            p_k_j = quicksum((1 if i == 0 else Xs[k][i-1]) * W1[i, j] for i in range(dim+1))

            # devo calcolare il segno di p_k_j, lo penso come var binaria e poi lo converto in -1, 1
            sign_inner[k,j] = model.addVar(obj = 0, vtype= GRB.BINARY, name = f"sign_inner_{k}_{j}")
            
            model.addConstr(p_k_j >= epsilon-M*(1-sign_inner[k,j]), name = "sign = 1 then pkj >=0")
            model.addConstr(p_k_j <= -epsilon + M*sign_inner[k,j], name = "sign = 0 then pkj <= eps")
            

            # z[k,j] = model.addVar(lb = -1, ub = 1, vtype= GRB.INTEGER, obj = 0, name= f"z_{k}_{j}")
            # model.addConstr(z[k,j] == 2*sign_inner[k,j] - 1)

    # hidden layer: fatto! passo fuori
        # -------------------------------------------- 
    g = {}
    M = 2000
    for k in range(n_points):
        # devo modellizzare il prodotto
        for j in range(hidden_layer_dim+1):
            if j !=0:
                # gkj è il prodotto tra sign_inner e w2_k [senza il 0esimo]
                g[k,j] = model.addVar(lb = -GRB.INFINITY, ub = GRB.INFINITY, obj = 0, vtype= GRB.CONTINUOUS, name = f"g_{k}_{j}")
                model.addConstr(g[k,j] <= M*sign_inner[k,j-1])
                model.addConstr(g[k,j] >= -M*sign_inner[k,j-1])
                model.addConstr(g[k,j] <= W2[j])
                model.addConstr(g[k,j] >= W2[j] + M*(sign_inner[k,j-1]-1))
        # g[k, 0] = W2[0]

    # qk = somma di g[k,j] al variare di j
    q = []
    for k in range(n_points):
        q.append(model.addVar(lb = -GRB.INFINITY, ub = GRB.INFINITY, obj = 0, vtype= GRB.CONTINUOUS, name = f"q_{k}"))
        model.addConstr(q[k] == quicksum([2*g[k, j] - W2[j] for j in range(1, hidden_layer_dim+1) ]) + W2[0] )
    
    # devo fare il segno di qk
    sign_outer = []
    for k in range(n_points):
        sign_outer.append(model.addVar(obj=0, vtype= GRB.BINARY, name = f"sign_outer{k}")) 
        model.addConstr(q[k] >= epsilon - M*(1-sign_outer[k]))
        model.addConstr(q[k] <= - epsilon + M*sign_outer[k])


    val_abs = []
    for k in range(n_points):
        y_pred = 2 * sign_outer[k] - 1
        val_abs.append(model.addVar(lb = 0, ub = GRB.INFINITY, obj = 10, vtype=GRB.CONTINUOUS, name = f"val_abs{k}")) 
        model.addConstr(val_abs[k] >= y_pred-Ys[k])
        model.addConstr(val_abs[k] >= -y_pred + Ys[k])

    model.update()
    model.optimize()
    model.write("MLP.lp")



    if model.Status ==2:
        W1_sol = np.zeros((dim+1, hidden_layer_dim))
        W2_sol = np.zeros(hidden_layer_dim+1)

        for i in range(dim+1):
            for j in range(hidden_layer_dim):
                W1_sol[i,j] = W1[i, j].X 
        for j in range(hidden_layer_dim+1):
            W2_sol[j] = W2[j].X



        def sol_func(X):
            print("W1:", W1_sol)
            print("W2:", W2_sol)
            def hard_sign(x):
                return np.where(x >= 0, 1, -1)
            
            X = np.array(X)
            # print("Input:", X)
            if len(X.shape) != 1:
                X_ = np.hstack((np.ones((X.shape[0], 1)), np.array(X)))
                inner_out = hard_sign(X_ @ W1_sol)
                # print("Hidden layer output:", inner_out)
                out = np.hstack((np.ones((X.shape[0], 1)), inner_out)) @ W2_sol
                # print("Final raw output:", out)
                return hard_sign(out)
            else:
                X_ = np.array([1,  *X])
                inner_out = hard_sign(X_ @ W1_sol)
                # print("Hidden layer output:", inner_out)
                out = np.array([1, *inner_out]) @ W2_sol
                # print("Final raw output:", out)
                return hard_sign(out)
        if return_weights:
            return sol_func, W1_sol, W2_sol
        else:
            return sol_func
       
    else:
        print("Warning: something is wrong. The status of the model is:", model.Status)

# --------------------------------------------------------------------------------
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
    y_hat = np.array([F(x) for x in Xs])

    n = len(Ys)
    print(y_hat)
    print(Ys)
    return (np.sum(Ys == y_hat))/n*100




def TrainingMLP(Xs, Ys, nh=200):
    # Main ILP model
    lambda_ = 0.5
    model = Model()
    model.setParam("TimeLimit", 60)      # Max 60 secondi
    epsilon = 5
    return_weights = False
    # variabili W1, W2 
    f = min(Ys)
    t = max(Ys)
    # print(t,f)
    W1 = {}
    W2 = {}
    n_points = Xs.shape[0]
    dim = Xs.shape[1]
    # print(Xs.shape)
    # print(f"dim;{dim}")
    hidden_layer_dim =nh
    M = 2000
    # create the matrices
    for i in range(dim+1):
        for j in range(hidden_layer_dim):
            W1[i, j] = model.addVar(lb = 0, ub = 1, obj = lambda_, vtype= GRB.INTEGER, name = f"W1_{i}_{j}")
    for j in range(hidden_layer_dim+1):
        W2[j] = model.addVar(lb = 0, ub = 1, obj = lambda_, vtype= GRB.INTEGER, name = f"W2_{j}")

    sign_inner = {}
    
    for k in range(n_points):
        for j in range(hidden_layer_dim):
            # print(Xs[k].shape)
            p_k_j = quicksum([(1 if i == 0 else Xs[k][0, i-1]) * W1[i, j] for i in range(dim+1)])

            # devo calcolare il segno di p_k_j, lo penso come var binaria e poi lo converto in -1, 1
            sign_inner[k,j] = model.addVar(obj = 0, vtype= GRB.BINARY, name = f"sign_inner_{k}_{j}")
            
            model.addConstr(p_k_j >= epsilon-M*(1-sign_inner[k,j]), name = "sign = 1 then pkj >=0")
            model.addConstr(p_k_j <= -epsilon + M*sign_inner[k,j], name = "sign = 0 then pkj <= eps")
            

            # z[k,j] = model.addVar(lb = -1, ub = 1, vtype= GRB.INTEGER, obj = 0, name= f"z_{k}_{j}")
            # model.addConstr(z[k,j] == 2*sign_inner[k,j] - 1)

    # hidden layer: fatto! passo fuori
        # -------------------------------------------- 
    g = {}
    
    for k in range(n_points):
        # devo modellizzare il prodotto
        for j in range(hidden_layer_dim+1):
            if j !=0:
                # gkj è il prodotto tra sign_inner e w2_k [senza il 0esimo]
                g[k,j] = model.addVar(lb = -GRB.INFINITY, ub = GRB.INFINITY, obj = 0, vtype= GRB.CONTINUOUS, name = f"g_{k}_{j}")
                model.addConstr(g[k,j] <= M*sign_inner[k,j-1])
                model.addConstr(g[k,j] >= -M*sign_inner[k,j-1])
                model.addConstr(g[k,j] <= W2[j])
                model.addConstr(g[k,j] >= W2[j] + M*(sign_inner[k,j-1]-1))
        # g[k, 0] = W2[0]

    # qk = somma di g[k,j] al variare di j
    q = []
    for k in range(n_points):
        q.append(model.addVar(lb = -GRB.INFINITY, ub = GRB.INFINITY, obj = 0, vtype= GRB.CONTINUOUS, name = f"q_{k}"))
        model.addConstr(q[k] == quicksum([2*g[k, j] - W2[j] for j in range(1, hidden_layer_dim+1) ]) + W2[0] )
    
    # devo fare il segno di qk
    sign_outer = []
    for k in range(n_points):
        sign_outer.append(model.addVar(obj=0, vtype= GRB.BINARY, name = f"sign_outer{k}")) 
        model.addConstr(q[k] >= epsilon - M*(1-sign_outer[k]))
        model.addConstr(q[k] <= - epsilon + M*sign_outer[k])

    val_abs = []
    for k in range(n_points):
        y_pred =  f*(1-sign_outer[k]) + t*sign_outer[k]
        val_abs.append(model.addVar(lb = 0, ub = GRB.INFINITY, obj = 10, vtype=GRB.CONTINUOUS, name = f"val_abs{k}")) 
        model.addConstr(val_abs[k] >= y_pred-Ys[k])
        model.addConstr(val_abs[k] >= -y_pred + Ys[k])

    model.update()
    model.optimize()
    model.write("MLP.lp")


    if model.Status ==2:
        W1_sol = np.zeros((dim+1, hidden_layer_dim))
        W2_sol = np.zeros(hidden_layer_dim+1)

        for i in range(dim+1):
            for j in range(hidden_layer_dim):
                W1_sol[i,j] = W1[i, j].X 
        for j in range(hidden_layer_dim+1):
            W2_sol[j] = W2[j].X



        def sol_func(X):
            # print("W1:", W1_sol)
            # print("W2:", W2_sol)
            def hard_sign(x):
                return np.where(x >= 0, 1, -1)
            X = np.array(X)
            # print("Input:", X)
            if len(X.shape) != 1:
                # print("--------------")
                # print(X.shape)
                X_ = np.hstack((np.ones((X.shape[0], 1)), X.reshape(1, X.shape[1])))
                inner_out = hard_sign(X_ @ W1_sol)
                # print("Hidden layer output:", inner_out)
                out = np.hstack((np.ones((X.shape[0], 1)), inner_out)) @ W2_sol
                # print("Final raw output:", out)
                return 0.5*(t-f)*hard_sign(*out) + (t+f)/2
            else:
                X_ = np.array([1,  *X])
                inner_out = hard_sign(X_ @ W1_sol)
                # print("Hidden layer output:", inner_out)
                out = np.array([1, *inner_out]) @ W2_sol
                # print("Final raw output:", out)
                return 0.5*(t-f)*hard_sign(*out) + (t+f)/2
        
        if return_weights:
            return sol_func, W1_sol, W2_sol
        else:
            return sol_func
       
    else:
        print("Warning: something is wrong. The status of the model is:", model.Status)








if __name__ == "__main__":
    from sklearn.model_selection import train_test_split
    
    for data in ['train_nine_four']:#['train_three_four','train_nine_four']:
        print("========================"+data+"============================")
        Xs, Ys = Parse('../data/'+data+'.csv')
        print('matrix X:', Xs)
        
        print('dimension of y:', Ys.shape)
        print("drawing a digit...")
        DrawDigit(Xs[15])
        DrawDigit(Xs[4])
        DrawDigit(Xs[9])
        print(f"the digit should be... {Ys[15]}")


        
        X_train, X_test, y_train, y_test = train_test_split(
        Xs, Ys, test_size=0.20, random_state=42)
        # Number of internal states
        nh = 200
        # REMARK: the predict function
        F = TrainingMLP(X_train, y_train, nh)
        # # Evaluate accuracy (be careful of the matrix dimension)
        train_acc = AccuracyMLP(X_train, y_train, F)
        print('training accuracy:', round(train_acc, 2))
        test_acc = AccuracyMLP(X_test, y_test, F)
        print('training accuracy:', round(test_acc, 2))

    


