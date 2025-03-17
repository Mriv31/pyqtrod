from PIL import Image
import numpy as np
import itertools


def FresnelPolres(phi0, t0, nofresnel=0, mask=0):
    R = 900
    t0 = t0 * np.pi / 180
    phi0 = phi0 * np.pi / 180
    pol = np.array([np.sin(t0) * np.cos(phi0), np.sin(t0) * np.sin(phi0), np.cos(t0)])
    NA = 1.3
    nw = 1.33
    no = 1.51
    # NA = 2
    # nw = 1.33
    # no = 2.5
    maxangle = np.arcsin(NA / no)
    xl = 1000  # discretization of x direction
    yl = 500  # discretiation of y direction
    R = 167  # radius of the BFP in pixels
    orscale = 2.4 / R
    cx = xl / 2
    cy = yl / 2

    a = Image.open(
        "Y:/Martin Rieu/Post-Doc/2021_11_17_1.3_nikon_DIC_H/image_mirror_binary.tif"
    )
    maski = np.array(a)
    centermaskx = 217
    centermasky = 230
    scale = 1.4 / 235  # mm / px

    def find_in_mask(dx, dy, orscale):
        retmask = np.zeros(dx.shape)

        indicesx = (
            centermaskx + dx * orscale / scale
        )  # index x in the origin mask image
        indicesy = (
            centermasky + dy * orscale / scale
        )  # index y in the origin mask image

        indicesx = indicesx.astype("int")
        indicesy = indicesy.astype("int")

        wherexfar = np.where(np.logical_or(indicesx >= maski.shape[0], indicesx < 0))
        whereyfar = np.where(np.logical_or(indicesy >= maski.shape[1], indicesy < 0))
        indicesx[wherexfar] = 0
        indicesy[whereyfar] = 0
        retmask = maski[indicesx, indicesy]
        return np.where(retmask != 0)  # indices to remove

    x = np.arange(0, xl, 1)
    y = np.arange(0, yl, 1)

    Rh = R / np.sin(maxangle)
    xx, yy = np.meshgrid(x, y)  # position in the BFP

    hole = find_in_mask(
        xx - cx, yy - cy, orscale
    )  # find mask from mask image defined above

    RR = np.sqrt((xx - cx) ** 2 + (yy - cy) ** 2)
    theta = np.arcsin(
        RR / Rh
    )  # emission angles in oil corresponding the position in the BFP
    thetaw = np.arcsin(
        RR / Rh * no / nw
    )  # emission angles in water corresponding the position in the BFP

    ind = np.where(
        theta > maxangle
    )  # positions in the BFP corresponding to angles above the max angle allowed by the NA

    phi = np.arctan2(yy - cy, xx - cx)  # phi angle corresponding to a position the BFP

    kw = np.array(
        [np.sin(thetaw) * np.cos(phi), np.sin(thetaw) * np.sin(phi), np.cos(thetaw)]
    )
    k = np.array(
        [np.sin(theta) * np.cos(phi), np.sin(theta) * np.sin(phi), np.cos(theta)]
    )

    rotvec = np.array(
        [np.sin(phi), -np.cos(phi), 0 * np.sin(phi)]
    )  # vectors along which we rotate to simulate effect of the objectivepvec = np.array([np.cos(phi),np.sin(phi),0*np.sin(phi)])

    # angle = np.empty([xl, yl])  # for later

    # cross product formula to get intensity and angle of E-field
    polres = np.cross(kw, pol, axisa=0, axisc=0)
    polres = np.cross(polres, kw, axisa=0, axisb=0, axisc=0)

    # rotate due to interface in oil
    a = np.cross(rotvec, polres, axisa=0, axisb=0, axisc=0)
    b = np.cross(rotvec, a, axisa=0, axisb=0, axisc=0)
    polres = (
        polres
        + np.sin(thetaw[None, :, :] - theta[None, :, :]) * a
        + (1 - np.cos(theta[None, :, :] - thetaw[None, :, :])) * b
    )  # rotation using angle in oil

    if not nofresnel:
        # Here to ADD, FRESNEL computation at the oil water interface
        tp = (2 * nw * np.cos(thetaw)) / (
            nw * np.cos(theta) + no * np.cos(thetaw)
        )  # fresnel transmission of s and p polarisation
        ts = (2 * nw * np.cos(thetaw)) / (nw * np.cos(thetaw) + no * np.cos(theta))

        r = np.array([np.cos(phi), np.sin(phi), 0 * np.sin(phi)])
        svec = np.cross(k, r, axisa=0, axisb=0, axisc=0)
        pvec = np.cross(svec, k, axisa=0, axisb=0, axisc=0)
        svec = svec / np.sqrt(np.sum(svec**2, axis=0))
        pvec = pvec / np.sqrt(np.sum(pvec**2, axis=0))

        smag1 = np.sum(svec * polres, axis=0)
        pmag1 = np.sum(pvec * polres, axis=0)

        smag2 = ts * smag1
        pmag2 = tp * pmag1

        polres = smag2 * svec + pmag2 * pvec

    # rotation due to objective
    a = np.cross(rotvec, polres, axisa=0, axisb=0, axisc=0)
    b = np.cross(rotvec, a, axisa=0, axisb=0, axisc=0)
    polres = (
        polres + np.sin(theta[None, :, :]) * a + (1 - np.cos(theta[None, :, :])) * b
    )  # rotation using angle in oil

    # Compute orientation of E-field
    # angle = np.arctan2(polres[0,:,:],polres[1,:,:])*180/np.pi-90
    # angle[ind] = 0

    # Compute Intensity of E-field
    # intensity = np.linalg.norm(polres,axis=0)/np.sqrt(1-RR**2/Rh**2)
    # intensity[ind] = 0

    polres = polres / (Rh**2 * np.sqrt(1 - RR**2 / Rh**2))

    polres = np.nan_to_num(polres)
    polres[0][ind] = 0
    polres[1][ind] = 0
    polres[2][ind] = 0
    if mask:
        polres[0][hole] = 0
        polres[1][hole] = 0
        polres[2][hole] = 0

    return polres


def F_angles(I0, I45, I90, I135):

    NA = 1.3
    nw = 1.33
    f_phi = 1 / 2 * np.arctan2((I45 - I135), ((I0 - I90)))

    alpha = np.arcsin(NA / nw)
    ca = np.cos(alpha)
    A = 1 / 6 - 1 / 4 * ca + 1 / 12 * ca**3
    B = 1 / 8 * ca - 1 / 8 * ca**3
    C = 7 / 48 - 1 / 16 * ca - 1 / 16 * ca**2 - 1 / 48 * ca**3

    O = I0 + I45 + I90 + I135
    P = I0 - I90 + I45 - I135

    c = np.cos(2 * f_phi)
    s = np.sin(2 * f_phi)

    sinsqtheta = 4 * A * P / (2 * (s + c) * O * C - 4 * B * P)
    test = np.sqrt(sinsqtheta)
    test = np.where(test > 1, 1, test)
    f_theta = np.arcsin(test)

    f_phi = f_phi * 180 / np.pi
    f_theta = f_theta * 180 / np.pi

    return f_phi, f_theta


def fresnel_ints(phi0, t0, nofresnel, mask):

    polres = FresnelPolres(phi0, t0, nofresnel=nofresnel, mask=mask)
    # plt.imshow(np.linalg.norm(polres, axis=0))
    # plt.show()

    I90 = np.dot(np.moveaxis(polres, 0, 2), [0, 1, 0]) ** 2

    I0 = np.dot(np.moveaxis(polres, 0, 2), [1, 0, 0]) ** 2

    I45 = np.dot(np.moveaxis(polres, 0, 2), [np.sqrt(2) / 2, np.sqrt(2) / 2, 0]) ** 2

    I135 = np.dot(np.moveaxis(polres, 0, 2), [np.sqrt(2) / 2, -np.sqrt(2) / 2, 0]) ** 2

    I90 = np.nansum(I90)
    I0 = np.nansum(I0)
    I45 = np.nansum(I45)
    I135 = np.nansum(I135)

    return I0, I45, I90, I135


def FourkasIntensities(phi0, t0):
    t0 = t0 * np.pi / 180
    phi0 = phi0 * np.pi / 180
    NA = 1.3
    nw = 1.33
    sst0 = np.sin(t0) ** 2
    c2p = np.cos(2 * phi0)
    s2p = np.sin(2 * phi0)
    alpha = np.arcsin(NA / nw)
    ca = np.cos(alpha)
    A = 1 / 6 - 1 / 4 * ca + 1 / 12 * ca**3
    B = 1 / 8 * ca - 1 / 8 * ca**3
    C = 7 / 48 - 1 / 16 * ca - 1 / 16 * ca**2 - 1 / 48 * ca**3

    f_I0 = A + B * sst0 + C * sst0 * c2p
    f_I45 = A + B * sst0 + C * sst0 * s2p
    f_I90 = A + B * sst0 - C * sst0 * c2p
    f_I135 = A + B * sst0 - C * sst0 * s2p

    return f_I0, f_I45, f_I90, f_I135


def compute_differences(phil, thetal, nofresnel=1, mask=0):
    Ints = np.zeros([phil.shape[0], thetal.shape[0], 4])
    computed_angles = np.zeros([phil.shape[0], thetal.shape[0], 2])

    for i, j in itertools.product(range(phil.shape[0]), range(thetal.shape[0])):
        Ints[i, j] = fresnel_ints(phil[i], thetal[j], nofresnel, mask)
        computed_angles[i, j] = F_angles(*(Ints[i, j]))
        if computed_angles[i, j][0] < -45:
            computed_angles[i, j][0] += 180

        print(i, j, phil[i], thetal[j], computed_angles[i, j])
    return computed_angles
