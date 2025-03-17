import numpy as np
from matplotlib import pyplot as plt
from scipy.signal import savgol_filter


def calculate_msd(trajectory, lags):
    msd = []
    for t in lags:
        displacement_squared = (trajectory[t:] - trajectory[:-t]) ** 2
        msd.append(np.mean(displacement_squared))
    return np.array(msd)


def calculate_msd_non_overlapping(trajectory, lags):
    msd = []
    for t in lags:
        segment_msd = []
        for i in range(0, len(trajectory) - t, t):
            displacement_squared = (trajectory[i + t] - trajectory[i]) ** 2
            segment_msd.append(displacement_squared)
        msd.append(segment_msd)
    return msd


def calculate_msd_statistics(trajectory, lags):
    msd_mean = []
    msd_std = []
    msd_5th_percentile = []
    msd_95th_percentile = []
    length = []

    for t in lags:
        displacement_squared = (trajectory[t::t] - trajectory[:-t:t]) ** 2
        msd_mean.append(np.mean(displacement_squared))
        msd_std.append(np.std(displacement_squared))
        msd_5th_percentile.append(np.percentile(displacement_squared, 5))
        msd_95th_percentile.append(np.percentile(displacement_squared, 95))
        length.append(len(displacement_squared))
    return (
        np.array(msd_mean),
        np.array(msd_std),
        np.array(msd_5th_percentile),
        np.array(msd_95th_percentile),
        np.array(length),
    )


def calculate_ssd(trajectory, lags):
    ssd = []
    for t in lags:
        displacement_squared = (trajectory[t:] - trajectory[:-t]) ** 2
        ssd.append(np.std(displacement_squared))
    return np.array(ssd)


def draw_msd_partial(
    zo,
    start,
    stop,
    lagmin,
    lagmax,
    timestep=4e-6,
    dr=0,
    slopec=0.3,
    fit_tail=0,
    end=5,
    sd=0,
):
    istart = int(start / timestep)
    istop = int(stop / timestep)
    lagmin = int(lagmin / timestep)
    lagmax = int(lagmax / timestep)
    lags = np.logspace(np.log10(lagmin), np.log10(lagmax), 200)
    lags = lags.astype("int")
    lags_, counts = np.unique(lags, return_counts=True)
    # if (np.any(counts>1)):
    #     print("too points same")
    # print(lags)
    # Calculate MSD for different time lags
    msd_values = calculate_msd(zo[istart:istop], lags)

    # smooth  = make_interp_spline(np.log(timestep*lags), np.log(msd_values), k=2)(np.log(timestep*lags))  # k is the degree of the spline (cubic in this case)
    plt.figure()
    plt.plot(timestep * lags, msd_values, marker=".", linestyle="-", color="b")
    plt.xlabel("Time Lag (s)")
    plt.ylabel("Mean Squared Displacement (MSD)")
    plt.ylim([0.001, 10])
    plt.title("Mean Squared Displacement (MSD) vs Time Lag")
    plt.grid(True)
    plt.yscale("log")
    plt.xscale("log")

    if fit_tail:
        a, b = np.polyfit(np.log(timestep * lags[-end:]), np.log(msd_values[-end:]), 1)
        plt.plot(
            timestep * lags[-100:],
            np.exp(a * np.log(timestep * lags[-100:]) + b),
            c="red",
        )

    if dr:
        # Plot MSD
        window_size = 40
        poly_order = 4
        smooth = savgol_filter(
            np.log(msd_values),
            window_size,
            poly_order,
            deriv=1,
            delta=np.log(lags[-1]) - np.log(lags[-2]),
        )  # [window_size:-window_size]
        try:
            ind = np.where((smooth > slopec) & (timestep * lags > 1e-4))[0][0]
            arrow_point = (
                timestep * lags[ind],
                msd_values[ind],
            )  # Coordinates of the point to which the arrow points
            arrow_text = "Corner"
            plt.annotate(
                arrow_text,
                arrow_point,
                textcoords="offset pixels",
                xytext=(-40, 40),
                ha="center",
                fontsize=10,
                arrowprops=dict(width=4, color="red"),
            )
            ret = timestep * lags[ind]
        except:
            ret = np.nan

        ax = plt.gca().twinx()
        plt.ylabel("Smoothed derivative of log vs log")
        plt.plot(timestep * lags, smooth, color="r")
        plt.xscale("log")
        ax.set_ylim([0.001, 1.3])

        if sd:
            # poly_order = 3
            # dy_dx_smooth = savgol_filter(dy_dx, window_size, poly_order)
            d2y_dx2 = np.gradient(smooth, np.log(timestep * lags))
            # plt.figure()
            # plt.plot(np.log10(timestep*lags), dy_dx, label='Smoothed First Derivative', color='red')
            # plt.title('First Derivative and Smoothed Version')
            plt.figure()
            plt.plot(
                np.log10(timestep * lags),
                d2y_dx2,
                label="Second derivative",
                color="red",
            )
            plt.title("Second Derivative")
    return timestep * lags, msd_values, smooth


def draw_msd_all(zo, lagmin, lagmax, loglag=0, timestep=4e-6):
    lagmin = int(lagmin / timestep)
    lagmax = int(lagmax / timestep)
    lags = np.geomspace(lagmin, lagmax, 200)

    lags = lags.astype("int")

    # Calculate MSD for different time lags
    msd_values = calculate_msd(zo, lags)

    # Plot MSD
    if loglag:
        plt.plot(
            np.log(lags / lags[0]), (msd_values), marker="o", linestyle="-", color="b"
        )
        plt.yscale("linear")
        plt.xscale("linear")
        plt.xlabel("Log of Time Lag log($\\tau$) (s)")
        plt.ylabel("Mean Squared Displacement (MSD)")
        plt.title("Mean Squared Displacement (MSD) vs Time Lag")
        plt.grid(True)

    else:
        plt.plot(timestep * lags, msd_values, marker="o", linestyle="-", color="b")
        plt.xlabel("Time Lag (s)")
        plt.ylabel("Mean Squared Displacement (MSD)")
        plt.title("Mean Squared Displacement (MSD) vs Time Lag")
        plt.grid(True)
        plt.yscale("log")
        plt.xscale("log")
    return lags * timestep, msd_values


def autocorr2(x, lags):
    """manualy compute, non partial"""

    xp = x - np.mean(x)
    corr = [np.mean(xp[L:] * xp[:-L]) for L in lags]

    return np.array(corr)


## OLDDDDDDDDDDDDDDD
# # def power_law(x, a,c,F,d):
# # t = np.exp(x)
# # return c*(1-np.exp(-t/F)) +d
# # return a * x**0.5+c*(1-np.exp(-t/F)) +d
# def power_law(x, a, b,c):
#     return a * x**b+c
# # def power_law(x, a, b,c,d):
# #     return a * x**b+c*np.exp(x)+d
#
# def draw_msd_all(zo,lagmin,lagmax,loglag=0,timestep=4e-6,ax=None,index=0,correct=0,indexstop=-1):
#     lagmin = int(lagmin/timestep)
#     lagmax = int(lagmax/timestep)
#     lags = np.geomspace(lagmin,lagmax,100)
#     lags = lags.astype("int")
#
#
#     # Calculate MSD for different time lags
#     msd_values = calculate_msd(zo, lags)
#     if (ax is not None):
#         plt.sca(ax)
#         ax.clear()
#     # Plot MSD
#     if (loglag):
#         plt.plot(np.log(lags/correct), (msd_values), marker='o', linestyle='-', color='b')
#         params, covariance = curve_fit(power_law, np.log(lags[index:indexstop]/correct), (msd_values[index:indexstop]))
#         plt.plot(np.log(lags/correct),power_law(np.log(lags/correct),params[0],params[1],params[2]))
#         print(params)
#
#         plt.yscale("linear")
#         plt.xscale("linear")
#         plt.xlabel('Log of Time Lag log($\\tau$) (s)')
#         plt.ylabel('Mean Squared Displacement (MSD)')
#         plt.title('Mean Squared Displacement (MSD) vs Time Lag')
#         plt.grid(True)
#
#     else:
#         plt.plot(timestep*lags, 0.007-msd_values, marker='o', linestyle='-', color='b')
#         #params, covariance = curve_fit(power_law,timestep*lags, (msd_values))
#         #plt.plot(timestep*lags,power_law(timestep*lags,params[0],params[1],params[2]))
#         plt.xlabel('Time Lag (s)')
#         plt.ylabel('Mean Squared Displacement (MSD)')
#         plt.title('Mean Squared Displacement (MSD) vs Time Lag')
#         plt.grid(True)
#         plt.yscale("linear")
#         plt.xscale("linear")
#     return lags*timestep
