from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import numpy as np
import pandas as pd

class FileData(object):
    def __init__(self, filename, yname):
        
        self.filename = filename
        self.yname = yname

        self.X = None
        self.y = None

        if type(self.filename) is tuple:
            for i in range(len(self.filename)):
                self.read(self.filename[i])

        else:
            self.read(self.filename)

    def read(self, name):
        df = pd.read_csv('../data/' + name + '.csv')

        # This is for Al alloys
        if name in ('Al7075', 'Al6061'):
            df["dP/dh (N/m)"] *= 0.2 * (df["C (GPa)"] / 3) ** 0.5 * 10 ** (-1.5)
        # This is for Ti alloys
        if name in ('B3090'):
            df["dP/dh (N/m)"] *= 0.2 / df["hmax(um)"]
        # Scale TI33 to hm=0.2μm
        if 'TI33' in name:
            # For 25˚ case
            df['dP/dh (N/m)'] *= 0.2 / df['hmax(um)']
        # Scale from Conical to Berkovich with small deformations
        if 'FEM_70deg' in name:
            df["dP/dh (N/m)"] *= 1.167 / 1.128
        # Scale from Conical to Berkovich with large deformations (See )
        if '2D' in name:
            df['dP/dh (N/m)'] *= 1.2370 / 1.1957
        # Get Estar if none provided
        if name == 'FEM_70deg' or 'Berkovich' in name or '2D' in name or '3D' in name:
            df['Er (GPa)'] = EtoEr(df['E (GPa)'].values, df['nu'].values)[:, None]

        print(df.describe())

        if self.X is None:
            self.X = df[["C (GPa)", "dP/dh (N/m)", "Wp/Wt"]].values
        else:
            self.X = np.vstack((self.X, df[["C (GPa)", "dP/dh (N/m)", "Wp/Wt"]].values))
        if self.yname == 'Er':
            if self.y is None:
                self.y = df['Er (GPa)'].values[:, None]
            else:
                self.y = np.vstack((self.y, df['Er (GPa)'].values[:, None]))
        elif self.yname == "sigma_y":
            if self.y is None:
                self.y = df["sy (GPa)"].values[:, None]
            else:
                self.y = np.vstack((self.y, df["sy (GPa)"].values[:, None]))
        elif self.yname.startswith("sigma_"):
            e_plastic = self.yname[6:]
            if self.y is None:
                self.y = df["s" + e_plastic + " (GPa)"].values[:, None]
            else:
                self.y = np.vstack((self.y, df["s" + e_plastic + " (GPa)"].values[:, None]))














































class FEMData0(object):
    def __init__(self, yname, angles):
        self.yname = yname
        self.angles = angles

        self.X = None
        self.y = None

        if len(angles) == 1:
            self.read_1angle()
        elif len(angles) == 2:
            self.read_2angles()
        elif len(angles) == 4:
            self.read_4angles()

    def read_1angle(self):
        df = pd.read_csv("../data/FEM_{}deg.csv".format(self.angles[0]))
        df['Er (GPa)'] = EtoEstar(df["E (GPa)"])
        df["sy/Estar"] = df["sy (GPa)"] / df['Er (GPa)']
        df = df.loc[~((df["n"] > 0.3) & (df["sy/Estar"] >= 0.03))]
        # df = df.loc[df["n"] <= 0.3]
        # Scale c* from Conical to Berkovich
        # df["dP/dh (N/m)"] *= 1.167 / 1.128
        # Add noise
        # sigma = 0.2
        # df['Er (GPa)'] *= 1 + sigma * np.random.randn(len(df))
        # df["sy (GPa)"] *= 1 + sigma * np.random.randn(len(df))
        print(df.describe())

        self.X = df[["C (GPa)", "dP/dh (N/m)", "Wp/Wt"]].values
        if self.yname == 'Er':
            self.y = df['Er (GPa)'].values[:, None]
        elif self.yname == "sigma_y":
            self.y = df["sy (GPa)"].values[:, None]
        elif self.yname.startswith("sigma_"):
            e_plastic = float(self.yname[6:])
            self.y = (
                df["sy (GPa)"]
                * (1 + e_plastic * df["E (GPa)"] / df["sy (GPa)"]) ** df["n"]
            ).values[:, None]

class Data1(object):
    def __init__(self, yname, filename):
        self.yname = yname
        self.filename = filename

        self.X = None
        self.y = None
        self.read_1angle()


    def read_1angle(self):
        name = '../data/' + self.filename + '.csv'
        print('Name=', name)
        df = pd.read_csv(name)
        if 'Estar (GPa)' not in df:
            df['Estar (GPa)'] = EtoEstar(df['E (GPa)'])
            #df['Er (GPa)'] = EtoEr(df['E (GPa)'].values, df['nu'].values)[:, None]
        df['sy/Estar'] = df['sy (GPa)'] / df['Er (GPa)']
        if self.filename == 'FEM_70deg':
            #df = df.loc[~((df["n"] > 0.3) & (df["sy/Estar"] >= 0.03))]
            df = df.loc[df['n'] <= 0.3]
        if self.filename == 'TI33_25':
            df['dP/dh (N/m)'] *= 200 / df['hmax(nm)']
        if self.filename == 'B3090':
            df["dP/dh (N/m)"] *= 200 / df["hmax(nm)"]
        if self.filename == 'Berkovich':
            self.y = EtoEstar(df['E (GPa)'].values)[:, None]
        # df = df.loc[df["n"] <= 0.3]
        # Scale c* from Conical to Berkovich
        # df["dP/dh (N/m)"] *= 1.167 / 1.128
        # Add noise
        # sigma = 0.2
        # df['Er (GPa)'] *= 1 + sigma * np.random.randn(len(df))
        # df["sy (GPa)"] *= 1 + sigma * np.random.randn(len(df))
        print(df.describe())

        self.X = df[["C (GPa)", "dP/dh (N/m)", "Wp/Wt"]].values
        if self.yname == 'Er':
            self.y = df['Er (GPa)'].values[:, None]
        else:
            self.y = df["sy (GPa)"].values[:, None]

class FEMDataC(object):
    def __init__(self, yname, filename):
        self.yname = yname
        self.filename = filename

        self.X = None
        self.y = None

        self.read_1angle()

    def read_1angle(self):
        df = pd.read_csv('../data/'+self.filename+'.csv')
        df['Er (GPa)'] = EtoEstar(df["E (GPa)"])
        df["sy/Estar"] = df["sy (GPa)"] / df['Er (GPa)']
        #
        if self.filename == 'FEM_70deg':
            df = df.loc[~((df["n"] > 0.3) & (df["sy/Estar"] >= 0.03))]
        #
        # Scale c* from Conical to Berkovich
        # df["dP/dh (N/m)"] *= 1.167 / 1.128
        # Add noise
        # sigma = 0.2
        # df['Er (GPa)'] *= 1 + sigma * np.random.randn(len(df))
        # df["sy (GPa)"] *= 1 + sigma * np.random.randn(len(df))
        #
        print(df.describe())

        self.X = df[["C (GPa)", "dP/dh (N/m)", "Wp/Wt"]].values
        if self.yname == 'Er':
            self.y = df['Er (GPa)'].values[:, None]
        elif self.yname == "sigma_y":
            self.y = df["sy (GPa)"].values[:, None]
        elif self.yname.startswith("sigma_"):
            e_plastic = float(self.yname[6:])
            self.y = (
                df["sy (GPa)"]
                * (1 + e_plastic * df["E (GPa)"] / df["sy (GPa)"]) ** df["n"]
            ).values[:, None]

class ExpDataC(object):
    def __init__(self, yname, filename):
        '''
        ExpData reads in data from an experimental data file. It intakes values \
            for C, Estar, sy, and s for varying plastic strains. The filename it \
            receives as an argument is the experimental data file that will be \
            read.
        '''
        self.filename = filename
        self.yname = yname

        self.X = None
        self.y = None

        self.read()

    def read(self):
        df = pd.read_csv('../data/'+self.filename+'.csv')

        #
        # Scale nm to um for Ti33 files
        # I'M PRETTY SURE THESE MULTI-LINE COMMENTED CAN BE DELETED.
        '''
        df["hm (um)"] = df["hmax(nm)"] / 1000
        df["C (GPA)"] = df["H(GPa)"] * df["hm (um)"] ** 2
        df["H(GPa)"]
        df["hc(nm)"]
        df["hf(nm)"]
        self.X = df[["hmax(nm)", "H(GPa)", "hc(nm)"]].values
        '''
        # Scale dP/dh from 3N to hm = 0.2um

# This is for Al alloys
#        df["dP/dh (N/m)"] *= 0.2 * (df["C (GPa)"] / 3) ** 0.5 * 10 ** (-1.5)

        
        # Scale dP/dh from Pm to hm = 0.2um
        # df["dP/dh (N/m)"] *= 0.2 * (df["C (GPa)"] / df["Pm (N)"]) ** 0.5 * 10 ** (-1.5)
        # Scale dP/dh from hm to hm = 0.2um 

# This is for Ti alloys
        if self.filename == 'B3090':
            df["dP/dh (N/m)"] *= 0.2 / df["hmax(um)"]
# This is for the Yanbo's Ti alloys
        if self.filename == 'TI33_25':
            df["dP/dh (N/m)"] *= 0.2 / df["hmax(um)"]

        # Scale c* from Berkovich to Conical
        df["dP/dh (N/m)"] *= 1.128 / 1.167
        #

        print(df.describe())

        self.X = df[["C (GPa)", "dP/dh (N/m)", "Wp/Wt"]].values
        if self.yname == 'Er':
            self.y = df['Er (GPa)'].values[:, None]
        elif self.yname == "sigma_y":
            self.y = df["sy (GPa)"].values[:, None]
        elif self.yname.startswith("sigma_"):
            e_plastic = self.yname[6:]
            self.y = df["s" + e_plastic + " (GPa)"].values[:, None]


class BerkovichDataC(object):
    def __init__(self, yname, filename, scale_c=False):
        self.yname = yname
        self.filename=filename
        self.scale_c = scale_c

        self.X = None
        self.y = None

        self.read()

    def read(self):
        df = pd.read_csv('../data/'+self.filename+'.csv')
        # Scale c* from Berkovich to Conical
        if self.scale_c:
            df["dP/dh (N/m)"] *= 1.128 / 1.167
        print(df.describe())

        self.X = df[["C (GPa)", "dP/dh (N/m)", "Wp/Wt"]].values
        if self.yname == 'Er':
            self.y = EtoEstar(df['E (GPa)'])
        elif self.yname == "sigma_y":
            self.y = df["sy (GPa)"].values[:, None]
        elif self.yname == "n":
            self.y = df["n"].values[:, None]
        elif self.yname.startswith("sigma_"):
            e_plastic = float(self.yname[6:])
            self.y = (
                df["sy (GPa)"]
                * (1 + e_plastic * df["E (GPa)"] / df["sy (GPa)"]) ** df["n"]
            ).values[:, None]

class FEMData2(object):
    def __init__(self, yname, angles):
        '''
        __init__ takes in a name and a quantity of angles. The number in [] is \
            passed to self.angles, which is the angle of the indentation. This \
            indentation angle is then used to find the correct file to read \
            to obtain the data. \n
        The class FEMData has member functions init, read_1angle, read_2angles, \
            and read_4angles. The half-included tip angles used for the read_angle \
            functions were 70.3˚, 60˚, 50˚, and 80˚. 70.3˚ was used in all \
            three and 60˚ was used in the last two. The same accuracy could be \
            achieved with a smaller training data set size for more indentors, \
            but only one indenter was used to train the single-fidelity NN.
        '''
        self.yname = yname
        self.angles = angles

        self.X = None
        self.y = None

        if len(angles) == 1:
            self.read_1angle()
        elif len(angles) == 2:
            self.read_2angles()
        elif len(angles) == 4:
            self.read_4angles()

    def read_1angle(self):
        df = pd.read_csv("../data/FEM_{}deg1.csv".format(self.angles[0]))
        df['Er (GPa)'] = EtoEstar(df["E (GPa)"])
        df["sy/Estar"] = df["sy (GPa)"] / df['Er (GPa)']
        df = df.loc[~((df["n"] > 0.3) & (df["sy/Estar"] >= 0.03))]
        #
        # df = df.loc[df["n"] <= 0.3]
        # Scale c* from Conical to Berkovich
        # df["dP/dh (N/m)"] *= 1.167 / 1.128
        # Add noise
        # sigma = 0.2
        # df['Er (GPa)'] *= 1 + sigma * np.random.randn(len(df))
        # df["sy (GPa)"] *= 1 + sigma * np.random.randn(len(df))
        print(df.describe())

        self.X = df[["C (GPa)", "dP/dh (N/m)", "Wp/Wt"]].values
        if self.yname == 'Er':
            self.y = df['Er (GPa)'].values[:, None]
        elif self.yname == "sigma_y":
            self.y = df["sy (GPa)"].values[:, None]
        elif self.yname.startswith("sigma_"):
            e_plastic = float(self.yname[6:])
            self.y = (
                df["sy (GPa)"]
                * (1 + e_plastic * df["E (GPa)"] / df["sy (GPa)"]) ** df["n"]
            ).values[:, None]

class ExpData2(object):
    def __init__(self, filename, yname):
        '''
        ExpData reads in data from an experimental data file. It intakes values \
            for C, Estar, sy, and s for varying plastic strains. The filename it \
            receives as an argument is the experimental data file that will be \
            read.
        '''
        self.filename = filename
        self.yname = yname

        self.X = None
        self.y = None

        self.read()

    def read(self):
        df = pd.read_csv(self.filename)

        #
        # Scale dP/dh from 3N to hm = 0.2um

# This is for Al alloys
#        df["dP/dh (N/m)"] *= 0.2 * (df["C (GPa)"] / 3) ** 0.5 * 10 ** (-1.5)

        
        # Scale dP/dh from Pm to hm = 0.2um
        # df["dP/dh (N/m)"] *= 0.2 * (df["C (GPa)"] / df["Pm (N)"]) ** 0.5 * 10 ** (-1.5)
        # Scale dP/dh from hm to hm = 0.2um 

# This is for Ti alloys
        df["dP/dh (N/m)"] *= 0.2 / df["hm (um)"]


        # Scale c* from Berkovich to Conical
        df["dP/dh (N/m)"] *= 1.128 / 1.167
        #

        print(df.describe())

        self.X = df[["C (GPa)", "dP/dh (N/m)", "Wp/Wt"]].values
        if self.yname == 'Er':
            self.y = df['Er (GPa)'].values[:, None]
        elif self.yname == "sigma_y":
            self.y = df["sy (GPa)"].values[:, None]
        elif self.yname.startswith("sigma_"):
            e_plastic = self.yname[6:]
            self.y = df["s" + e_plastic + " (GPa)"].values[:, None]

class BerkovichData2(object):
    def __init__(self, yname, scale_c=False):
        '''
        The class BerkovichData reads a file from a Berkovich indentation test. \
            It has member functions init and read. init sets the scale and the \
            name of the dependent variables. read reads the csv of the given name \
            and stores its C, Estar, sy, and n. It can also store dP/dh if scale is \
            listed as being true. \n
        The Berkovich indenter has a half angle of 65.3˚ from the tip to the pyramid \
            surface.
        '''
        self.yname = yname
        self.scale_c = scale_c

        self.X = None
        self.y = None

        self.read()

    def read(self):
        df = pd.read_csv("../data/Berkovich1.csv")
        # Scale c* from Berkovich to Conical
        if self.scale_c:
            df["dP/dh (N/m)"] *= 1.128 / 1.167
        print(df.describe())

        self.X = df[["C (GPa)", "dP/dh (N/m)", "Wp/Wt"]].values
        if self.yname == 'Er':
            self.y = EtoEstar(df["E (GPa)"].values)[:, None]
        elif self.yname == "sigma_y":
            self.y = df["sy (GPa)"].values[:, None]
        elif self.yname == "n":
            self.y = df["n"].values[:, None]
        elif self.yname.startswith("sigma_"):
            e_plastic = float(self.yname[6:])
            self.y = (
                df["sy (GPa)"]
                * (1 + e_plastic * df["E (GPa)"] / df["sy (GPa)"]) ** df["n"]
            ).values[:, None]



















class FEMData(object):
    def __init__(self, yname):
        self.yname = yname
        #self.angles = angles
        #self.angles = ['../data/TI33_conical_30.csv', '../data/TI33_conical_45.csv', '../data/TI33_conical_60.csv']
        #self.angles = ['../data/TI33_conical_30_i.csv', '../data/TI33_conical_45_i.csv', '../data/TI33_conical_60_i.csv']
        #self.angles = ['../data/TI33_conical_30_i.csv']
        self.angles = ['../data/TI33_conical_30.csv']
        #self.angles = ['../data/TI33_conical_30_i.csv', '../data/TI33_conical_30.csv']
        #self.angles = ['../data/FEM_70deg.csv']
        print('Size: '+str(len(self.angles)))

        self.X = None
        self.y = None

        self.read_angles()
        '''
        if len(angles) == 1:
            self.read_1angle()
        elif len(angles) == 2:
            self.read_2angles()
        elif len(angles) == 3:
            self.read_3angles()'''

    def read_angles(self):
        df_list = []
        for angle in self.angles:
            df_list.append(pd.read_csv(angle))
            print(df_list[-1].describe())

        df = pd.concat(df_list, ignore_index=True)

        self.X = df[[
                'C (GPa)',
                'dP/dh (N/m)',
                'Wp/Wt'
            ]].values
        if self.yname == 'Estar':
            self.y = EtoEr(df['E (GPa)'].values, df['nu'].values)[:, None]
        elif self.yname == 'sigma_y':
            self.y = df['sy (GPa)'].values[:, None]

class ExpData(object):
    def __init__(self, temp, yname):
        filename = '../data/' + temp + '.csv'
        self.filename = filename
        self.yname = yname

        self.X = None
        self.y = None

        self.read()

    def read(self):
        df = pd.read_csv(self.filename)

        #
        # Scale dP/dh from 3N to hm = 0.2um

# This is for Al alloys
#        df['dP/dh (N/m)'] *= 0.2 * (df['C (GPa)'] / 3) ** 0.5 * 10 ** (-1.5)

        
        # Scale dP/dh from Pm to hm = 0.2um
        # df['dP/dh (N/m)'] *= 0.2 * (df['C (GPa)'] / df['Pm (N)']) ** 0.5 * 10 ** (-1.5)
        # Scale dP/dh from hm to hm = 0.2um 

# This is for Ti alloys
#        df['dP/dh (N/m)'] *= 0.2 / df['hm (um)']
# This is for the Yanbo's Ti alloys
        df['dP/dh (N/m)'] *= 0.2 * 1000 / df['hmax(nm)']

        # Scale c* from Berkovich to Conical
#        df['dP/dh (N/m)'] *= 1.128 / 1.167
        #

        print(df.describe())

# I just commented this line for my own work.
        self.X = df[['C (GPa)', 'dP/dh (N/m)', 'Wp/Wt']].values
        if self.yname == 'Estar':
            self.y = df['Estar (GPa)'].values[:, None]
        if self.yname.startswith('E_'):
            self.y = df[self.yname].values[:, None]
        elif self.yname == 'sigma_y':
            self.y = df['sy (GPa)'].values[:, None]
        elif self.yname.startswith('sigma_'):
            e_plastic = self.yname[6:]
            self.y = df['s' + e_plastic + ' (GPa)'].values[:, None]

class ExpDataT(object):
    def __init__(self, temp, yname):
        filename = '../data/' + temp + '.csv'
        self.filename = filename
        self.yname = yname

        self.X = None
        self.y = None

        self.read()

    def read(self):
        df = pd.read_csv(self.filename)

        #
        # Scale dP/dh from 3N to hm = 0.2um

# This is for Al alloys
#        df['dP/dh (N/m)'] *= 0.2 * (df['C (GPa)'] / 3) ** 0.5 * 10 ** (-1.5)

        
        # Scale dP/dh from Pm to hm = 0.2um
        # df['dP/dh (N/m)'] *= 0.2 * (df['C (GPa)'] / df['Pm (N)']) ** 0.5 * 10 ** (-1.5)
        # Scale dP/dh from hm to hm = 0.2um 

# This is for Ti alloys
#        df['dP/dh (N/m)'] *= 0.2 / df['hm (um)']
# This is for the Yanbo's Ti alloys
        df['dP/dh (N/m)'] *= 0.2 * 1000 / df['hmax(nm)']

        # Scale c* from Berkovich to Conical
#        df['dP/dh (N/m)'] *= 1.128 / 1.167
        #

        print(df.describe())

# I just commented this line for my own work.
        self.X = df[['C (GPa)', 'dP/dh (N/m)', 'Wp/Wt', 'T (C)']].values
        if self.yname == 'Estar':
            self.y = df['Estar (GPa)'].values[:, None]
        if self.yname.startswith('E_'):
            self.y = df[self.yname].values[:, None]
        elif self.yname == 'sigma_y':
            self.y = df['sy (GPa)'].values[:, None]
        elif self.yname.startswith('sigma_'):
            e_plastic = self.yname[6:]
            self.y = df['s' + e_plastic + ' (GPa)'].values[:, None]


class BerkovichData(object):
    def __init__(self, yname, scale_c=False):
        self.yname = yname
        self.scale_c = scale_c

        self.X = None
        self.y = None

        self.read()

    def read(self):
        #df = pd.read_csv('../data/Berkovich.csv')
        df = pd.read_csv('../data/TI33_Berkovich.csv')
        if self.scale_c:
            df['dP/dh (N/m)'] *= 1.128 / 1.167
        print(df.describe())

        self.X = df[['C (GPa)', 'dP/dh (N/m)', 'Wp/Wt']].values
        if self.yname == 'Estar':
            self.y = EtoEr(df['E (GPa)'].values, df['nu'].values)[:, None]
        elif self.yname == 'sigma_y':
            self.y = df['sy (GPa)'].values[:, None]
        elif self.yname == 'n':
            self.y = df['n'].values[:, None]
        elif self.yname.startswith('sigma_'):
            e_plastic = float(self.yname[6:])
            self.y = (
                df['sy (GPa)']
                * (1 + e_plastic * df['E (GPa)'] / df['sy (GPa)']) ** df['n']
            ).values[:, None]


def EtoEr(E, nu):
    nu_i, E_i = 0.0691, 1143
    return 1 / ((1 - nu ** 2) / E + (1 - nu_i ** 2) / E_i)

def EtoEstar(E):
    nu = 0.3
    nu_i, E_i = 0.07, 1100
    return 1 / ((1 - nu ** 2) / E + (1 - nu_i ** 2) / E_i)