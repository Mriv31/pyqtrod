import numpy as np
from sklearn.decomposition import PCA
from numba import njit, jit
from scipy.interpolate import splprep, splev
from matplotlib import pyplot as plt
from pyqtrod.ni_file import NIfile
import sys
import os
from scipy.spatial import KDTree
from scipy.signal import find_peaks, peak_widths


# Pre-processing
convolution_window = 100  # Window size for convolution


# Reference line
smoothing = 0.001  # Smoothing factor for the spline interpolation
reference_num_points = 200  # Number of points in the interpolated trajectory
do_update_reference_cycle = (
    False  # Whether to update the reference line (for drift correction)
)
update_reference_cycle = (
    250000  # Number of points to process before updating the reference cycle
)

# phase assigment
continuity_constraint = int(
    reference_num_points // 10
)  # Search neighborhood for phase continuity.


# cycle detection
window_detection = 400  # Size of sliding window for peroidicity detection. It will compare the distance between the first "window_dectection" points and later "window_detection" points
first_cycle_detection_limit = 500000  # The script loks for maxima in the first 500000 points of the main component of the trajectory for the beginning of the cycle
end_of_cycle_limit = 100000  # The script looks for the end of the cycle in the next 10000 points after the beginning of the cycle


def smooth_trajectory(points):
    """
    Smooth a closed 3D trajectory using cubic B-spline interpolation.

    Args:
        points (np.ndarray): Array of 3D points defining the trajectory
        smoothing (float): Smoothing factor for the spline interpolation
        num_points (int): Number of points in the interpolated trajectory

    Returns:
        np.ndarray: Smoothed trajectory points
    """
    points = np.array(points)

    # Ensure the loop is closed (repeat first point at the end)
    if not np.allclose(points[0], points[-1]):
        points = np.vstack([points, points[0]])

    # Fit a 3D spline curve
    tck, _ = splprep(points.T, per=True, s=smoothing)
    u_fine = np.linspace(0, 1, reference_num_points)  # Interpolation parameter
    smooth_points = np.array(splev(u_fine, tck)).T

    return smooth_points


def detect_cycle_bounds(trajectory):
    """
    Find the start and end indices of a representative cycle in the trajectory.

    Args:
        trajectory (np.ndarray): Time series data

    Returns:
        tuple: Start and end indices of the identified cycle
    """
    # Extract the main component of the trajectory for initial cycle detection
    main_component = trajectory[:first_cycle_detection_limit, 0]
    minp = np.min(main_component)
    maxp = np.max(main_component)
    amplitude_90 = minp + 0.9 * (maxp - minp)

    # Identify possible start points where the main component exceeds 90% of its amplitude
    possible_starts = np.where(main_component > amplitude_90)[0]
    print(amplitude_90)

    # Filter out closely spaced indices to keep only far apart indices
    min_distance = 1000  # Minimum distance between indices
    filtered_starts = [possible_starts[0]]
    for idx in possible_starts[1:]:
        if idx - filtered_starts[-1] > min_distance:
            filtered_starts.append(idx)
        if len(filtered_starts) > 5:
            break
    possible_starts = np.array(filtered_starts)

    # Determine the best start point based on the variation in the main component
    max_variation = 0
    best_start = possible_starts[0]
    for start in possible_starts:
        variation = np.sum(
            np.diff(main_component[start : start + end_of_cycle_limit]) ** 2
        )
        if variation > max_variation:
            max_variation = variation
            best_start = start
    start_index = best_start

    # Calculate the distance threshold for close points
    distances_close = np.linalg.norm(
        signals[start_index, :] - signals[start_index : start_index + 2, :], axis=1
    )
    close_distance_threshold = np.max(distances_close)

    # Create a KDTree for the trajectory segment starting at max_index
    tree_trajectory = KDTree(
        trajectory[start_index : start_index + window_detection, :]
    )

    # List to store the number of neighbors within the distance threshold
    nb_neighbours_l = []
    i_list = range(start_index + 400, start_index + end_of_cycle_limit, 10)
    for i in i_list:
        tree_next_points = KDTree(trajectory[i : i + window_detection, :])
        nb_neighbours = tree_next_points.count_neighbors(
            tree_trajectory, close_distance_threshold
        )
        nb_neighbours_l.append(nb_neighbours)

    # Find peaks in the number of neighbors to identify cycle boundaries
    threshold = 2
    peaks = []
    while len(peaks) == 0:
        peaks = find_peaks(nb_neighbours_l, prominence=window_detection / threshold)[0]
        threshold *= 2

    # Determine the width of the peaks
    widths, _, _, right_ips = peak_widths(nb_neighbours_l, peaks, rel_height=0.5)
    end_index = peaks[0]
    right_ips = right_ips.astype(int)

    peak_ind = 0

    # Adjust peak index based on the minimum number of neighbors
    while peak_ind < len(peaks) - 1:
        if np.min(nb_neighbours_l[: peaks[peak_ind]]) > 2 * np.min(nb_neighbours_l):
            peak_ind += 1
        else:
            break

    # Further adjust peak index based on the number of neighbors
    for k in range(peak_ind, peak_ind + 3):
        if nb_neighbours_l[peaks[k]] > nb_neighbours_l[peaks[peak_ind]] * 1.5:
            peak_ind = k

    # Determine the end index of the cycle
    end_index = i_list[right_ips[peak_ind]]
    nb_neighbours_l = np.array(nb_neighbours_l)
    peaks = np.array(peaks, dtype=int)

    return start_index, end_index


@njit
def assign_phase_indices(trajectory, reference_cycle, prev_phase=None):
    """
    Assign phase indices to trajectory points based on nearest neighbors in reference cycle.

    Args:
        trajectory (np.ndarray): Input trajectory
        reference_cycle (np.ndarray): Reference cycle for phase assignment
        prev_phase (int, optional): Previous phase index for continuity
        neighborhood (int): Search neighborhood size

            np.ndarray: Phase indices for each point
    """

    index = np.empty(len(trajectory), dtype=np.int32)
    len_array = reference_cycle.shape[0]
    num_points = trajectory.shape[0]
    if prev_phase is not None:
        neighboring_indices = (
            prev_phase - np.arange(-continuity_constraint, continuity_constraint)
        ) % len_array

        # Vectorized distance calculation
        diff = reference_cycle[neighboring_indices] - trajectory[0, :3]
        distancesar = np.sum(diff**2, axis=1)

        best_distance = np.argmin(distancesar)
        index[0] = neighboring_indices[best_distance]
    else:
        diff = reference_cycle - trajectory[0, :3]
        distancesar = np.sum(diff**2, axis=1)
        best_distance = np.argmin(distancesar)
        index[0] = best_distance

    for i in range(1, num_points):
        last_index = index[i - 1]

        # Optimized computation of neighboring indices (vectorized)
        neighboring_indices = (
            last_index - np.arange(-continuity_constraint, continuity_constraint)
        ) % len_array

        # Vectorized distance calculation
        diff = reference_cycle[neighboring_indices] - trajectory[i, :3]
        distancesar = np.sum(diff**2, axis=1)

        best_distance = np.argmin(distancesar)
        index[i] = neighboring_indices[best_distance]

    return index


def update_reference_cycle(phase_indices, reference_cycle, trajectory):
    """
    Update reference cycle using assigned phases.

    Args:
        phase_indices (np.ndarray): Phase indices
        reference_cycle (np.ndarray): Current reference cycle
        trajectory (np.ndarray): Input trajectory

    Returns:
        np.ndarray: Updated reference cycle
    """
    new_traj = np.zeros_like(reference_cycle)
    for i in range(reference_cycle.shape[0]):
        exp_points = np.where(phase_indices == i)[0]
        if len(exp_points) == 0:
            new_traj[i] = reference_cycle[i]
        else:
            new_traj[i] = np.mean(trajectory[exp_points[-100:]], axis=0)
    new_traj = smooth_trajectory(new_traj)
    return new_traj


def extract_phase(
    signals,
    output_path=None,
):
    """
    Extract phase from multivariate time series data.

    Args:
        data (np.ndarray): Input time series data
        window_size (int): Window size for smoothing
        output_path (str, optional): Path for saving results

    Returns:
        tuple: Phase angles and visualization data
    """
    print("convolving")

    # Apply convolution to smooth the signals
    signals = np.apply_along_axis(
        lambda m: np.convolve(
            m, np.ones(convolution_window) / convolution_window, mode="valid"
        ),
        axis=0,
        arr=signals,
    )
    print("pca")

    # Perform PCA to reduce dimensionality
    pca = PCA(n_components=4)
    X_pca = pca.fit_transform(signals)

    X_pca = X_pca[:, :3]

    # Load or detect cycle indices
    if os.path.exists(output_path + "_phase_indices_ui.txt"):
        indices = np.loadtxt(
            output_path + "_phase_indices_ui.txt", dtype=int, delimiter=";"
        )
    else:
        print("detecting cycle bounds")
        indices = detect_cycle_bounds(X_pca)
    np.savetxt(output_path + "_phase_indices.txt", indices, fmt="%i", delimiter=";")

    avg_signal_d = X_pca[indices[0] : indices[1]]

    print("smoothing")

    # Smooth the average signal
    M = len(avg_signal_d)
    avg_signal_d_av = np.zeros([M // reference_num_points, 3])
    for i in range(0, M // reference_num_points, 1):
        avg_signal_d_av[i] = np.mean(
            avg_signal_d[
                i * reference_num_points : i * reference_num_points
                + reference_num_points
            ],
            axis=0,
        )
    smooth_points = smooth_trajectory(avg_signal_d_av)

    print("computing index")
    i = 0
    phase0 = np.array([], dtype=np.int32)
    prev_phase = 0

    # Assign phase indices and update reference cycle if needed
    if do_update_reference_cycle:
        while i < X_pca.shape[0]:
            phaseh = assign_phase_indices(
                X_pca[indices[0] + i : indices[0] + i + update_reference_cycle_size],
                smooth_points,
                prev_phase=prev_phase,
            )
            smooth_points = update_reference_cycle(
                phaseh,
                smooth_points,
                X_pca[indices[0] + i : indices[0] + i + update_reference_cycle_size],
            )
            i += update_reference_cycle_size
            phase0 = np.concatenate((phase0, phaseh))
            prev_phase = phaseh[-1]
    else:
        phase0 = assign_phase_indices(X_pca[indices[0] :], smooth_points)

    # Calculate phase angles
    phase = phase0 / len(smooth_points) * 2 * np.pi
    phase = np.unwrap(phase)

    print("plotting")

    # Plot the results
    fig = plt.figure(figsize=(8, 6), dpi=300)
    ax = fig.add_subplot(321, projection="3d")
    ax.plot(*smooth_points.T, "-", linewidth=2, label="Smoothed Loop", color="blue")
    ax.plot(*avg_signal_d.T, "-", linewidth=2, label="Points", color="red")

    ax = fig.add_subplot(322)
    ax.plot(X_pca[indices[0] : indices[0] + 20000, 0], color="black")
    ax.plot(smooth_points[phase0[:20000], 0])

    ax = fig.add_subplot(323)
    ax.plot(signals[indices[0] : indices[0] + 20000])

    ax = fig.add_subplot(324)
    ax.plot(phase, label="Phase")

    ax = fig.add_subplot(313)
    ax.plot(X_pca[indices[0] : 2 * indices[1] - indices[0], 0], color="black")
    ax.plot(avg_signal_d[:, 0], color="red")
    xticks = np.linspace(0, 2 * indices[1] - 2 * indices[0], 40)
    xticks = xticks.astype(int)
    xticks = 100 * np.round(xticks / 100).astype(int)
    ax.set_xticks(xticks)
    labels = [str(indices[0] + xt) for xt in xticks]
    ax.set_xticklabels(labels, rotation=90)
    for tick in ax.get_xticks():
        ax.axvline(x=tick, color="gray", linestyle="--", linewidth=0.5)

    fig.tight_layout()
    fig.savefig(output_path + "_phase_debug.png")

    # Save the results
    np.save(output_path + "_phase.npy", phase)
    np.save(output_path + "_smooth_points.npy", smooth_points[phase0, 0])
    np.save(output_path + "_avg_signal.npy", X_pca[indices[0] :, 0])


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python extract_phase.py <folder_path>")
        sys.exit(1)

    folder_path = sys.argv[1]

    if not os.path.isdir(folder_path):
        print(f"Error: {folder_path} is not a valid directory.")
        sys.exit(1)

    # Process each file in the folder
    for filename in os.listdir(folder_path):
        file_path = os.path.join(folder_path, filename)
        if os.path.isfile(file_path) and file_path.endswith(".tdms"):
            try:
                f = NIfile(file_path, dec=1)
                start = 0
                stop = min(f.datasize, 10 * f.freq)
                # stop = f.datasize
                print("Getting channels")
                C0, C90, C45, C135 = f.ret_cor_channel_in_file(start, int(stop))
                signals = np.column_stack((C0, C90, C45, C135))
                indices = None
                extract_phase(signals, output_path=file_path[:-5])
            except Exception as e:
                print(f"Error processing {file_path}: {e}")
                continue
