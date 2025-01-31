import os
import argparse
import time
import numpy as np
import optuna

import torch
import torch.nn as nn
import torch.optim as optim

import numpy as np
from scipy import linalg as la

from matplotlib import pyplot as plt

params = {}
params['data_name'] = 'Duffing_oscillator'

def objective(trial):
    optimizer.zero_grad()
    pred_sai = net(x_data)
    y_pred_sai = net(y_data)

    fixed_sai = torch.tensor([i + [0.1] for i in x_data.detach().tolist()], dtype=torch.float32)
    pred_sai = torch.cat([pred_sai, fixed_sai], dim=1)
    y_fixed_sai = torch.tensor([i + [0.1] for i in y_data.detach().tolist()], dtype=torch.float32)
    y_pred_sai = torch.cat([y_pred_sai, y_fixed_sai], dim=1)

    pred_sai_T = torch.transpose(pred_sai, 0, 1)

    G = inv_N * torch.mm(pred_sai_T, pred_sai)  # 本当はエルミート
    A = inv_N * torch.mm(pred_sai_T, y_pred_sai)

    K_tilde = torch.mm(torch.inverse(G + lambda_ * I), A)
    K_tilde = torch.tensor(K_tilde, requires_grad=False)

    Pred = torch.mm(K_tilde, pred_sai_T)
    y_pred_sai_T = torch.transpose(y_pred_sai, 0, 1)
    res = lambda_ * Frobenius_norm(K_tilde)

    loss = res
    QWRETY = y_pred_sai_T - Pred  # pred_sai_T
    PPAP = QWRETY ** 2
    loss += torch.sum(PPAP)
    y.append(loss)
    print("loss", loss)
    # print(net.parameters().item())
    loss.backward()
    optimizer.step()

    params = {
        'objective': 'binary',
        'max_bin': trial.suggest_int('max_bin'),
        'learning_rate': trial.suggest_int('learning_rate'),
        'num_leaves': trial.suggest_int('num_leaves'),
    }

    return loss

study = optuna.create_study(sampler=optuna.samplers.RandomSampler(seed=0))
study.optimize(objective, n_trials=40)

#最適化したハイパーパラメータの結果
study.best_params

#最適化後の目的関数の値
study.best_value

#全試行過程
study.trials

def J(K, theta):
    pass


lambda_ = 1e-6  # 1e-6

# K_tilde = np.linalg.pinv(G + lambda_.dot(I)).dot(A)
epsilon = 0.1

d = 2
l = 100  # 70
M = 22  # 22
I = torch.eye(M + 3, M + 3)

N = 10000
#width = 11  #11
inv_N = 1/N  #0.1

net = nn.Sequential(
    nn.Linear(d, l),
    nn.Tanh(),
    nn.Linear(l, l),
    nn.Tanh(),
    #nn.Dropout(0.5),
    nn.Linear(l, l),
    nn.Tanh(),
    nn.Linear(l, M),
)
# optimizer = optim.SGD(net.parameters(), lr=2e-4)
optimizer = optim.Adam(net.parameters(), lr=1e-4)  # 1e-5
loss_fn = nn.MSELoss()  # J(K, theta)

def data_Preprocessing(tr_val_te):
    data = np.loadtxt(('./data/%s_%s_x.csv' % (params['data_name'], tr_val_te)), delimiter=',', dtype=np.float64)[:N]
    # np.loadtxt(('./data/%s_val_x.csv' % (params['data_name'])), delimiter=',', dtype=np.float64)  # ここでデータを読み込む
    data = torch.tensor(data, dtype=torch.float32)
    return data

def p_inv(X):
    X_T = torch.transpose(X, 0, 1)
    return torch.mm(torch.inverse(torch.mm(X_T, X)), X_T)  # (X_TX)-1X_T

def Frobenius_norm(X):
    M = torch.mm(X, torch.transpose(X, 0, 1))
    return torch.sum(torch.diag(M, 0))

"""def graph__________(y, st):
    plots = plt.plot(y)
    plt.legend(plots, st,  # 3つのプロットラベルの設定
               loc='best',  # 線が隠れない位置の指定
               framealpha=0.25,  # 凡例の透明度
               prop={'size': 'small', 'family': 'monospace'})  # 凡例のfontプロパティ
    plt.title('Data Graph')  # タイトル名
    plt.xlabel('count')  # 横軸のラベル名
    plt.ylabel('loss')  # 縦軸のラベル名
    plt.grid(True)  # 目盛の表示
    plt.tight_layout()  # 全てのプロット要素を図ボックスに収める
    # 描画実行
    plt.show()"""

#グラフ
def graph(x, y, name, type, correct=[], predict=[], phi_predict=[]):  # plt.xlim(1300,)
    plt.figure()
    if type == "plot":
        plt.plot(x, y)
        plt.title('MLP Model Loss')  # タイトル名
        plt.xlabel('epoch')
        plt.ylabel('loss')
    elif type == "scatter":
        plt.scatter(x, y)
        plt.title('Eigenvalue')  # タイトル名
        plt.xlabel('Re(μ)')
        plt.ylabel('Im(μ)')
    elif type == "multi_plot":
        plt.plot(correct, label="correct")  # 実データ，青
        plt.plot(predict, label="predict")  # 予測，オレンジ
        plt.plot(phi_predict, label="phi_predict")  # 予測Φ，緑
        plt.title("x1_trajectory")
        plt.xlabel('n')
        plt.ylabel('x1')
        plt.legend()
    plt.savefig("png/" + name + ".png")
    plt.savefig("eps/" + name + ".eps")
    plt.show()



# while J(K, theta) > epsilon:
x = []
y = []
X = []
Y = []
count = 0
K_tilde = []

"""netを学習"""
x_data = data_Preprocessing("x_train")
y_data = data_Preprocessing("y_train")
"""data = np.loadtxt('./data/E_recon_50.csv', delimiter=',', dtype=np.float64)
data = torch.tensor(data, dtype=torch.float32)"""
# if tr_val_te != "train":
count = 0
rotation = 5000
x = [i for i in range(rotation)]
for _ in range(1):
    while count < rotation:
        if count % 100 == 0:
            print(count)


        count += 1
    graph(x, y, "train", "plot")
    count = 0


"""学習済みのnetを使って，E_reconを計算"""
K = K_tilde # torch.rand(25, 25) #K_tilde
mu = 0
for tr_val_te in ["E_recon_50"]:
    data = data_Preprocessing("x_train")
    count = 0
    width = 10
    """Bを計算，X=BΨ"""
    X25 = data[0].view(2, -1)
    for i in range(1, M + 3):
        x2_data = data[width * i].view(2, -1)
        X25 = torch.cat([X25, x2_data], dim=1)

    Sai = net(data[0])
    tmp = data[0].detach().tolist() + [0.1]  # [i + [0.1] for i in data[0].detach().tolist()]
    fixed_sai1 = torch.tensor(tmp, dtype=torch.float32)
    Sai = torch.cat([Sai, fixed_sai1])
    Sai = Sai.view(M + 3, -1)
    for i in range(1, M + 3):
        sai = net(data[width * i])
        tmp = data[width * i].detach().tolist() + [0.1]
        fixed_sai = torch.tensor(tmp, dtype=torch.float32)
        sai = torch.cat([sai, fixed_sai])
        sai = sai.view(M + 3, -1)
        Sai = torch.cat([Sai, sai], dim=1)

    # Sai = torch.transpose(Sai, 0, 1)
    B = torch.mm(X25, torch.inverse(Sai))
    B = B.detach().numpy()
    K = K.detach().numpy()
    data = np.loadtxt('./data/E_recon_50.csv', delimiter=',', dtype=np.float64)
    data = torch.tensor(data, dtype=torch.float32)
    width = 51

    mu, xi, zeta = la.eig(K, left=True, right=True)

    # mu zeta = K zeta
    # mu z = K.T z
    # mu z.T = z.T K，xi = z.T
    mu2, _, z = la.eig(K.T, left=True, right=True)
    # print(mu[0:20])
    # print(mu2[0:20])
    # print(mu2[1] * z[:, 1].T - z[:, 1].T.dot(K))

    print(mu[1] * zeta[:, 1] - K.dot(zeta[:, 1]))
    print(mu[1] * xi[:, 1].T - xi[:, 1].T.dot(K))
    print(mu[1] * zeta[:, 1], K.dot(zeta[:, 1]))
    print(mu[1] * xi[:, 1].T, xi[:, 1].T.dot(K))

    mu_real = [i.real for i in mu]
    mu_imag = [i.imag for i in mu]
    graph(mu_real, mu_imag, "eigenvalue", "scatter")

    while count < 99:
        x_data = data[count * width:count * width + width]  # N = 10
        sai = net(x_data)
        fixed_sai = torch.tensor([i + [0.1] for i in x_data.detach().tolist()], dtype=torch.float32)
        sai = torch.cat([sai, fixed_sai], dim=1).detach().numpy()
        sai_T = sai.T

        """E_reconを計算"""
        m = B.dot(zeta)  # (xi.T.dot(B)).T  # 本当はエルミート
        m = m.T
        # sai_T = torch.rand(M + 3, width - 1) * 100
        phi = (xi.T).dot(sai_T)

        x_tilde = [[0, 0] for _ in range(width)]  # [[0, 0]] * (width - 1)
        x_tilde_phi = [[0, 0] for _ in range(width)]
        x_tilde[0][0] = x_data[0][0]
        x_tilde[0][1] = x_data[0][1]
        x_tilde_phi[0][0] = x_data[0][0]
        x_tilde_phi[0][1] = x_data[0][1]
        for n in range(1, width):
            print((mu[1] ** n) * phi[1][0], phi[1][n])
            x_tilde[n][0] = sum([(mu[k] ** n) * phi[k][0] * m[k][0] for k in range(M + 3)]).real  # sum([(mu[k] ** count) * true_phi[k] * data_val[count] * v[k] for k in range(25)])
            x_tilde[n][1] = sum([(mu[k] ** n) * phi[k][0] * m[k][1] for k in range(M + 3)]).real

            x_tilde_phi[n][0] = sum([phi[k][n] * m[k][0] for k in range(M + 3)]).real  # sum([(mu[k] ** count) * true_phi[k] * data_val[count] * v[k] for k in range(25)])
            x_tilde_phi[n][1] = sum([phi[k][n] * m[k][1] for k in range(M + 3)]).real

        x_data = x_data.detach().numpy()
        E_recon = (inv_N * sum([abs(x_data[n][0] - x_tilde[n][0]) ** 2 + abs(x_data[n][1] - x_tilde[n][1]) ** 2
                                for n in range(width)])) ** 0.5
        print("E_recon", E_recon)

        count += 1
        x_tilde_0 = [i for i, j in x_tilde]
        x_tilde_phi_0 = [i for i, j in x_tilde_phi]

        graph([], [], "x1_traj_" + "{stp:02}".format(stp=count), "multi_plot"
              , x_data[:, 0], x_tilde_0, x_tilde_phi_0)


"""学習済みのnetを使って，E_eigfuncを計算"""
I_number = 1000
data = np.loadtxt('./data/E_eigfunc_confirm.csv', delimiter=',', dtype=np.float64)
data = torch.tensor(data, dtype=torch.float32)
width = 2
phi_list = [[0 for count in range(I_number)] for j in range(25)]
y_phi_list = [[0 for count in range(I_number)] for j in range(25)]

for count in range(I_number):
    x_data = data[count * width:count * width + width]
    pred_sai = net(x_data)  # count * 50 : count * 50 + 50

    for j in range(M + 3):
        if j < 22:
            phi_list[j][count] = pred_sai[0][j].detach().numpy()
            y_phi_list[j][count] = pred_sai[1][j].detach().numpy()
        elif j == M:
            phi_list[j][count] = x_data[0][0].detach().numpy()
            y_phi_list[j][count] = x_data[1][0].detach().numpy()
        elif j == M + 1:
            phi_list[j][count] = x_data[0][1].detach().numpy()
            y_phi_list[j][count] = x_data[1][1].detach().numpy()
        elif j == M + 2:
            phi_list[j][count] = 0.1
            y_phi_list[j][count] = 0.1


phi_list = phi_list
y_phi_list = y_phi_list
"""E_eigfunc_jを計算"""
E_eigfunc = [0] * (M + 3)
for j in range(M + 3):
    E_eigfunc[j] = np.sqrt(1 / I_number * sum([abs(y_phi_list[j][count] - mu[j] * phi_list[j][count]) ** 2
                                   for count in range(I_number)]))
    print("E_eigfunc", E_eigfunc[j])