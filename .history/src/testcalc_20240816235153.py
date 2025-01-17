import numpy as np
import pandas as pd
from scipy import optimize

def Pi1(Estar_sigma33):
    x = np.log(Estar_sigma33)
    return -1.131 * x ** 3 + 13.635 * x ** 2 - 30.594 * x + 29.267


def Pi2(Estar_sigma33, n):
    x = np.log(Estar_sigma33)
    return (
        (-1.40557 * n ** 3 + 0.77526 * n ** 2 + 0.1583 * n - 0.06831) * x ** 3
        + (17.93006 * n ** 3 - 9.22091 * n ** 2 - 2.37733 * n + 0.86295) * x ** 2
        + (-79.99715 * n ** 3 + 40.5562 * n ** 2 + 9.00157 * n - 2.54543) * x
        + 122.65069 * n ** 3
        - 63.88418 * n ** 2
        - 9.58936 * n
        + 6.20045
    )


def Pi4(hrhm):
    return 0.268536 * (0.9952495 - hrhm) ** 1.1142735


def Pi5(hrhm):
    return 1.61217 * (
        1.13111 - 1.74756 ** (-1.49291 * hrhm ** 2.535334) - 0.075187 * hrhm ** 1.135826
    )


def Pitheta(theta, Er_sigma):
    Ersig = np.log(Er_sigma)
    t1 = (-2.3985e-5 * theta ** 3 + 6.0446e-4 * theta ** 2 +0.13243 * theta - 5.0950)
    t2 = (0.0014741 * theta ** 3 - 0.21502 * theta ** 2 + 10.4415 * theta - 169.8767)
    t3 = (-3.9124e-3 * theta ** 3 + 0.53332 * theta ** 2 - 23.2834 * theta + 329.7724)
    t4 = (2.6981e-3 * theta ** 3 - 0.29197 * theta ** 2 + 7.5761 * theta + 2.0165)
    return t1 * Ersig ** 3 + t2 * Ersig ** 2 + t3 * Ersig + t4

# def Pitheta(theta, Estar_sigma):
#     x = np.log(Estar_sigma)
#     if theta == 60:
#         return -0.154 * x ** 3 + 0.932 * x ** 2 + 7.657 * x - 11.773
#     if theta == 80:
#         return -2.913 * x ** 3 + 44.023 * x ** 2 - 122.771 * x + 119.991
#     if theta == 50:
#         return 0.0394 * x ** 3 - 1.098 * x ** 2 + 9.862 * x - 11.837
#     raise NotImplementedError


def epsilon_r(theta):
    return 2.397e-5 * theta ** 2 - 5.311e-3 * theta + 0.2884


def model_dao(C, WpWt, dPdh, nu, hm, nu_i=0.07, E_i=1100e9):
    # cstar = 1.1957  # Conical
    cstar = 1.2370  # Berkovich

    if WpWt < Pi5(0):
        hr = 1e-9
    else:
        hr = optimize.brentq(lambda x: Pi5(x) - WpWt, 0, 1) * hm
    Pm = C * hm ** 2
    Am = (Pm * cstar / dPdh / Pi4(hr / hm)) ** 2
    Estar = dPdh / cstar / Am ** 0.5
    p_ave = Pm / Am
    sigma_33 = optimize.brentq(lambda x: Pi1(Estar / x) - C / x, 1e7, 1e10)
    E = (1 - nu ** 2) / (1 / Estar - (1 - nu_i ** 2) / E_i)
    try:
        n = optimize.brentq(
            lambda x: Pi2(Estar / sigma_33, x) - dPdh / Estar / hm, 0, 0.5
        )
    except ValueError:
        n = 0
    if n > 0:
        sigma_y = optimize.brentq(
            lambda x: (1 + E / x * 0.033) ** n - sigma_33 / x, 1e7, 1e10
        )
    else:
        sigma_y = sigma_33
    return E, Estar, n, sigma_y, p_ave


def model_swa(C, WpWt, dPdh, nu, hm, theta=70.3, nu_i=0.0691, E_i=1143):
    C *= 1e9
    E_i *= 1e9
    hm *= 1e-6
    # cstar = 1.1957  # Conical
    cstar = 1.2370  # Berkovich

    if WpWt < Pi5(0):
        hr = 1e-9
    else:
        hr = optimize.brentq(lambda x: Pi5(x) - WpWt, 0, 1) * hm
    Pm = C * hm ** 2
    Am = (Pm * cstar / dPdh / Pi4(hr / hm)) ** 2
    Estar = dPdh / cstar / Am ** 0.5
    p_ave = Pm / Am
    sigma_33 = optimize.brentq(lambda x: Pi1(Estar / x) - C / x, 1e7, 1e10)
    # for l, r in [[1e7, 1e9], [1e9, 5e9], [5e9, 1e10]]:
    #     if (Pitheta(theta, Estar / l) - Cb / l) * (
    #         Pitheta(theta, Estar / r) - Cb / r
    #     ) < 0:
    #         sigma_r = optimize.brentq(
    #             lambda x: Pitheta(theta, Estar / x) - Cb / x, l, r
    #         )
    #         break
    # else:
    #     raise ValueError
    # epsilon = epsilon_r(theta)
    # E = (1 - nu ** 2) / (1 / Estar - (1 - nu_i ** 2) / E_i)
    # if (epsilon > 0.033 and sigma_33 < sigma_r) or (
    #     epsilon < 0.033 and sigma_33 > sigma_r
    # ):
    #     sigma_y = optimize.brentq(
    #         lambda x: np.log(sigma_33 / x) / np.log(sigma_r / x)
    #         - np.log(1 + E / x * 0.033) / np.log(1 + E / x * epsilon),
    #         1e7,
    #         min(sigma_33, sigma_r),
    #     )
    #     n = np.log(sigma_33 / sigma_y) / np.log(1 + E / sigma_y * 0.033)
    # else:
    #     n = 0
    #     sigma_y = (sigma_33 + sigma_r) / 2
    # return E, Estar, n, sigma_y, p_ave
    return Estar/1e9

def main():
    filename = '../data/TI33_25.csv'
    df = pd.read_csv(filename)
    print('New')
    for i in range(len(df)):
        if i not in [0,4]: # Remove 2 indices that do not converge
            print(model_swa(df['C (GPa)'][i], df['Wp/Wt'][i], df['dP/dh (N/m)'][i], df['nu'][i], df['hmax(um)'][i]))
    print('Old')
    for i in range(len(df)):
        if i not in [25]: # Remove 1 indices that do not converge
            print(i, model_dao(df['C (GPa)'][i], df['dP/dh (N/m)'][i], df['nu'][i], df['E* (GPa)'][i], df['hmax(um)'][i], df['hr(um)'][i]))


if __name__ == "__main__":
    main()
