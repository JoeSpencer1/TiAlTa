from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import itertools

import numpy as np
from sklearn.svm import SVR
from sklearn.model_selection import KFold, LeaveOneOut, RepeatedKFold, ShuffleSplit

import deepxde as dde
from data import BerkovichData, FEMData, ExpDataT, ExpData
import tensorflow as tf
tf.config.run_functions_eagerly(False)
from tensorflow.keras import layers, models
import os
import multiprocessing

def svm(data):
    clf = SVR(kernel="rbf")
    clf.fit(data.train_x, data.train_y[:, 0])
    y_pred = clf.predict(data.test_x)[:, None]
    return dde.metrics.get("MAPE")(data.test_y, y_pred)


def mfgp(data):
    from mfgp import LinearMFGP

    model = LinearMFGP(noise=0, n_optimization_restarts=5)
    model.train(data.X_lo_train, data.y_lo_train, data.X_hi_train, data.y_hi_train)
    _, _, y_pred, _ = model.predict(data.X_hi_test)
    return dde.metrics.get("MAPE")(data.y_hi_test, y_pred)


def nn(data, lay=9, wid=32):
    layer_size = [data.train_x.shape[1]] + [wid] * lay + [1]
    activation = "selu"
    initializer = "LeCun normal"
    regularization = ["l2", 0.01]

    loss = "MAPE"
    optimizer = "adam"
    if data.train_x.shape[1] == 3:
        lr = 0.0001
    else:
        lr = 0.001
    epochs = 30000
    net = dde.maps.FNN(
        layer_size, activation, initializer, regularization=regularization
    )
    model = dde.Model(data, net)
    model.compile(optimizer, lr=lr, loss=loss, metrics=["MAPE"])
    losshistory, train_state = model.train(epochs=epochs)
    dde.saveplot(losshistory, train_state, issave=True, isplot=False)
    return train_state.best_metrics[0]

'''
def nntf(data, lay=9, wid=32):
    model = models.Sequential()
    model.add(layers.InputLayer(input_shape=(data.train_x.shape[1],)))
    for _ in range(lay):
        model.add(layers.Dense(wid, activation='selu', kernel_initializer='lecun_normal', kernel_regularizer=tf.keras.regularizers.l2(0.01)))
    model.add(layers.Dense(1))
    model.compile(optimizer='adam', loss='mean_absolute_percentage_error', metrics=['mae'])
    history = model.fit(data.train_x, data.train_y, epochs=30000, verbose=1)
    mape = model.evaluate(data.test_x, data.test_y, verbose=0)[1]
    return mape
'''

def mfnn(data, lay=2, wid=128):
    x_dim, y_dim = 3, 1
    activation = "selu"
    initializer = "LeCun normal"
    regularization = ["l2", 0.01]
    net = dde.maps.MfNN(
        [x_dim] + [wid] * lay + [y_dim],
        [8] * lay + [y_dim],
        activation,
        initializer,
        regularization=regularization,
        residue=True,
        trainable_low_fidelity=True,
        trainable_high_fidelity=True,
    )

    model = dde.Model(data, net)
    model.compile("adam", lr=0.0001, loss="MAPE", metrics=["MAPE", "APE SD"])
    # Set weight of high-fidelity and low-fidelity data to 50%
    model.set_weights = [0.5, 0.5]
    losshistory, train_state = model.train(epochs=30000)

    dde.saveplot(losshistory, train_state, issave=True, isplot=False)
    return (
        train_state.best_metrics[1],
        train_state.best_metrics[3],
        train_state.best_y[1],
    )
'''
def 


    arguments = np.array([
        "validation_three('Estar', 20, 'TI33_25', 'TI33_25', lay=2)",
        "validation_three('Estar', 20, 'TI33_25', 'TI33_25', lay=2)"
        ])
    
    processes = []
    num_processes = len(arguments)
    for i in range(num_processes):        
        process = multiprocessing.Process(target=run_main, args=(arguments[i],))
        processes.append(process)

    for process in processes:
        process.start()
    for process in processes:
        process.join()
'''
def data_portion(train_size, div, dataexp, datatrain, dataBerk, dataFEM):
    ape, y = []
    kf = ShuffleSplit(n_splits=10, train_size=train_size, random_state=0)
    og = len(datatrain.X)
    for _ in range(int((div-1)*og/div)):
        size = datatrain.y.shape[0]
        index = np.random.choice(size)
        datatrain.X = np.delete(datatrain.X, index, axis=0)
        datatrain.y = np.delete(datatrain.y, index, axis=0)
    while len(datatrain.X) < og:
        datatrain.X = np.concatenate((datatrain.X, datatrain.X), axis=0)
        datatrain.y = np.concatenate((datatrain.y, datatrain.y), axis=0)
    for train_index, _ in kf.split(datatrain.X):
        print("\nIteration: {}".format(len(ape)))
        print(train_index)
        data = dde.data.MfDataSet(
            X_lo_train=dataFEM.X,
            X_hi_train=np.vstack((dataBerk.X, datatrain.X[train_index])),
            y_lo_train=dataFEM.y,
            y_hi_train=np.vstack((dataBerk.y, datatrain.y[train_index])),
            X_hi_test=dataexp.X,
            y_hi_test=dataexp.y,
            standardize=True
        )
        res = dde.utils.apply(mfnn, (data, lay, wid))
        ape.append(res[:2])
        y.append(res[2])
    return ape, y

        
def validation_one(yname, trnames, tstname, type, train_size, lay=9, wid=32):
    
    data = []
    if type == 'FEM':
        data = FEMData(yname)
    if type == 'Berk':
        data = BerkovichData(yname)
    if type == 'Exp':
        data = ExpDataT(trnames[0], yname)
    print(data)
    tdata = ExpDataT(tstname, yname)
    mape = []

    for i in range(0, len(trnames)):
        kf = ShuffleSplit(
            n_splits=10, test_size=len(data.X) - train_size[i], random_state=0
        )

        iter = 0
        for train_index, test_index in kf.split(data.X):
            iter += 1
            print('\nCross-validation iteration: {}'.format(iter))

            print(data.X)
            X_train, X_test = data.X[train_index], tdata.X[test_index]
            y_train, y_test = data.y[train_index], tdata.y[test_index]

            data1 = dde.data.DataSet(
                X_train=X_train, y_train=y_train, X_test=X_test, y_test=y_test
            )

            mape.append(dde.utils.apply(nn, (data1, lay, wid, )))
            #mape.append(dde.utils.apply(nntf, (data1, lay, wid, )))

    stsize = ''
    for digit in train_size:
        stsize += str(digit) + ' '
    print(mape)
    print(yname, 'validation_one ', trnames, ' ', tstname, ' ', str(train_size), ' ', np.mean(mape), ' ', np.std(mape))
    with open('Output.txt', 'a') as f:
        f.write('validation_one [' + ' '.join(map(str, trnames)) + '] ' +  tstname + ' ' + yname + ' ' + str(lay) + ' ' + str(wid) + ' [' + stsize + '] ' + str(np.mean(mape, axis=0)) + ' ' + str(np.std(mape, axis=0)) + '\n')

def validation_two(yname, train_size, exp, low, hi, lay=2, wid=128):
    dataexp = ExpData(exp, yname)
    if low == 'FEM':
        datalow = FEMData(yname)
    if low == 'Berk':
        datalow = BerkovichData(yname)
    if hi == 'Berk':
        datahigh = BerkovichData(yname)
    if hi == 'Exp':
        datahigh = ExpData(exp, yname)

    ape = []
    y = []
    
    if train_size == 0:
        kf = ShuffleSplit(n_splits=10, train_size=10, random_state=0)
        iter = 0
        while len(dataexp.X) < train_size:
            dataexp.X=np.vstack((dataexp.X, dataexp.X))
            dataexp.y=np.vstack((dataexp.y, dataexp.y))
        while len(datalow.X) < len(dataexp.X):
            datalow.X=np.vstack((datalow.X, datalow.X))
            datalow.y=np.vstack((datalow.y, datalow.y))
        for train_index, _ in kf.split(dataexp.X):
            iter += 1
            print("\nCross-validation iteration: {}".format(iter))

            X_train, X_test = datalow.X[train_index], dataexp.X
            y_train, y_test = datalow.y[train_index], dataexp.y

            data = dde.data.DataSet(
                X_train=X_train, y_train=y_train, X_test=X_test, y_test=y_test
            )

            ape.append(dde.utils.apply(nn, (data, lay, wid, )))
    else:
        kf = ShuffleSplit(n_splits=10, train_size=train_size, random_state=0)
        while len(dataexp.X) < train_size:
            dataexp.X=np.vstack((dataexp.X, dataexp.X))
            dataexp.y=np.vstack((dataexp.y, dataexp.y))
        while len(datalow.X) < train_size:
            datalow.X=np.vstack((datalow.X, datalow.X))
            datalow.y=np.vstack((datalow.y, datalow.y))
        while len(datahigh.X) < train_size:
            datahigh.X=np.vstack((datalow.X, datalow.X))
            datahigh.y=np.vstack((datalow.y, datalow.y))
        for train_index, _ in kf.split(dataexp.X):
            print("\nIteration: {}".format(len(ape)))
            print(train_index)
            data = dde.data.MfDataSet(
                X_lo_train=datalow.X,
                X_hi_train=datahigh.X[train_index],
                y_lo_train=datalow.y,
                y_hi_train=datahigh.y[train_index],
                X_hi_test=dataexp.X,
                y_hi_test=dataexp.y,
                standardize=True
            )
            res = dde.utils.apply(mfnn, (data, lay, wid))
            ape.append(res[:2])
            y.append(res[2])

    print(ape)
    with open('Output.txt', 'a') as f:
        if train_size > 0:
            print(yname, "validation_two ", np.mean(ape, axis=0), np.std(ape, axis=0))
            f.write('validation_two [' + low + ', ' + hi + '] ' + str(train_size) + ' ' + exp + ' ' + yname + ' ' + str(lay) + ' ' + str(wid) + ' ' + str(np.mean(ape, axis=0)[0]) + ' ' + str(np.std(ape, axis=0)[0]) + '\n')
        else:
            print(yname, "validation_two ", np.mean(ape, axis=0), np.std(ape, axis=0))
            f.write('validation_two [' + low + ', ' + hi + '] ' + str(train_size) + ' ' + exp + ' ' + yname + ' ' + str(lay) + ' ' + str(wid) + ' ' + str(np.mean(ape, axis=0)) + ' ' + str(np.std(ape, axis=0)) + '\n')

def validation_three(yname, train_size, train, exp, lay=2, wid=128):
    datatrain = ExpData(train, yname)
    dataFEM = FEMData(yname)
    dataBerk = BerkovichData(yname)
    dataexp = ExpData(exp, yname)

    ape = []
    y = []

    if train_size == 0:
        kf = ShuffleSplit(n_splits=10, train_size=10, random_state=0)
        if len(dataexp.X) < len(dataFEM.X):
            short = dataexp
        else:
            short = dataFEM
        for train_index, _ in kf.split(short.X):
            print("\nIteration: {}".format(len(ape)))
            print(train_index)
            data = dde.data.MfDataSet(
                X_lo_train=dataFEM.X,
                X_hi_train=dataBerk.X,
                y_lo_train=dataFEM.y,
                y_hi_train=dataBerk.y,
                X_hi_test=dataexp.X,
                y_hi_test=dataexp.y,
                standardize=True
            )
            res = dde.utils.apply(mfnn, (data, lay, wid))
            ape.append(res[:2])
            y.append(res[2])
    else:
        div = 10
        for _ in range(div):
            kf = ShuffleSplit(n_splits=10, train_size=train_size, random_state=0)
            og = len(datatrain.X)
            for _ in range(int((div-1)*og/div)):
                size = datatrain.y.shape[0]
                index = np.random.choice(size)
                datatrain.X = np.delete(datatrain.X, index, axis=0)
                datatrain.y = np.delete(datatrain.y, index, axis=0)
            while len(datatrain.X) < og:
                datatrain.X = np.concatenate((datatrain.X, datatrain.X), axis=0)
                datatrain.y = np.concatenate((datatrain.y, datatrain.y), axis=0)
            for train_index, _ in kf.split(datatrain.X):
                print("\nIteration: {}".format(len(ape)))
                print(train_index)
                data = dde.data.MfDataSet(
                    X_lo_train=dataFEM.X,
                    X_hi_train=np.vstack((dataBerk.X, datatrain.X[train_index])),
                    y_lo_train=dataFEM.y,
                    y_hi_train=np.vstack((dataBerk.y, datatrain.y[train_index])),
                    X_hi_test=dataexp.X,
                    y_hi_test=dataexp.y,
                    standardize=True
                )
                res = dde.utils.apply(mfnn, (data, lay, wid))
                ape.append(res[:2])
                y.append(res[2])
            del res

    print(ape)
    with open('Output.txt', 'a') as f:
        print(yname, "validation_three ", np.mean(ape, axis=0), np.std(ape, axis=0))
        f.write('validation_three [' + train + ', ' + exp + '] ' + str(train_size) + ' ' + yname + ' ' + str(lay) + ' ' + str(wid) + ' ' + str(np.mean(ape, axis=0)[0]) + ' ' + str(np.std(ape, axis=0)[0]) + '\n')



def main(argument=None):
    if argument != None:
        exec(argument)
    return

if __name__ == "__main__":
    main()