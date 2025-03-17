import numpy as np
from sklearn.decomposition import PCA
from numba import njit
from scipy.interpolate import splprep, splev
from matplotlib import pyplot as plt
from scipy.spatial import KDTree
from scipy.signal import find_peaks, peak_widths
import sys
import os
from pyqtrod.ni_file import NIfile


def smooth_trajectory(points, smoothing=0.001, num_points=200):
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
    if not np.allclose(points[0], points[-1]):
        points = np.vstack([points, points[0]])
    tck, _ = splprep(points.T, per=True, s=smoothing)
    u = np.linspace(0, 1, num_points)
    return np.array(splev(u, tck)).T


def detect_cycle_bounds(trajectory, window=400):
    """
    Find the start and end indices of a representative cycle in the trajectory.

    Args:
        trajectory (np.ndarray): Time series data
        window (int): Size of sliding window for comparison

    Returns:
        tuple: Start and end indices of the identified cycle
    """
    primary_signal = trajectory[:500000, 0]
    threshold = np.min(primary_signal) + 0.9 * (
        np.max(primary_signal) - np.min(primary_signal)
    )
    candidates = np.where(primary_signal > threshold)[0]

    filtered_candidates = [candidates[0]]
    min_gap = 1000
    for idx in candidates[1:]:
        if idx - filtered_candidates[-1] > min_gap:
            filtered_candidates.append(idx)
        if len(filtered_candidates) > 5:
            break

    cycle_start = filtered_candidates[0]
    max_variance = 0
    for start in filtered_candidates:
        variance = np.sum(np.diff(primary_signal[start : start + 10000]) ** 2)
        if variance > max_variance:
            max_variance = variance
            cycle_start = start

    reference_window = KDTree(trajectory[cycle_start : cycle_start + window, :])
    similarity_scores = []
    distance_threshold = np.max(
        np.linalg.norm(
            trajectory[cycle_start, :] - trajectory[cycle_start : cycle_start + 2, :],
            axis=1,
        )
    )
    i_list = np.arange(cycle_start + 400, cycle_start + 100000, 10)
    for i in i_list:
        comparison_window = KDTree(trajectory[i : i + window, :])
        similarity_scores.append(
            comparison_window.count_neighbors(reference_window, distance_threshold)
        )

    threshold = 2
    peaks = []
    while len(peaks) == 0:
        peaks = find_peaks(similarity_scores, prominence=window / threshold)[0]
        threshold *= 2

    _, _, _, right_ips = peak_widths(similarity_scores, peaks, rel_height=0.5)
    cycle_end = peaks[0]
    right_ips = right_ips.astype(int)

    peak_ind = 0

    while peak_ind < len(peaks) - 1:
        if np.min(similarity_scores[: peaks[peak_ind]]) > 2 * np.min(similarity_scores):
            peak_ind += 1
        else:
            break

    for k in range(peak_ind, peak_ind + 3):
        if similarity_scores[peaks[k]] > similarity_scores[peaks[peak_ind]] * 1.5:
            peak_ind = k

    cycle_end = i_list[right_ips[peak_ind]]
    similarity_scores = np.array(similarity_scores)
    peaks = np.array(peaks, dtype=int)
    plt.plot(similarity_scores)
    plt.plot(peaks, similarity_scores[peaks], "ro")
    plt.plot(peaks[peak_ind], similarity_scores[peaks[peak_ind]], "go")
    plt.show(block=True)

    return cycle_start, cycle_end


@njit
def assign_phase_indices(trajectory, reference_cycle, prev_phase=None, neighborhood=20):
    """
    Assign phase indices to trajectory points based on nearest neighbors in reference cycle.

    Args:
        trajectory (np.ndarray): Input trajectory
        reference_cycle (np.ndarray): Reference cycle for phase assignment
        prev_phase (int, optional): Previous phase index for continuity
        neighborhood (int): Search neighborhood size

    Returns:
        np.ndarray: Phase indices for each point
    """
    indices = np.empty(len(trajectory), dtype=np.int32)
    cycle_length = len(reference_cycle)

    if prev_phase is None:
        distances = np.sum((reference_cycle - trajectory[0, :3]) ** 2, axis=1)
        indices[0] = np.argmin(distances)
    else:
        neighbors = (prev_phase - np.arange(-neighborhood, neighborhood)) % cycle_length
        distances = np.sum(
            (reference_cycle[neighbors] - trajectory[0, :3]) ** 2, axis=1
        )
        indices[0] = neighbors[np.argmin(distances)]

    for i in range(1, len(trajectory)):
        neighbors = (
            indices[i - 1] - np.arange(-neighborhood, neighborhood)
        ) % cycle_length
        distances = np.sum(
            (reference_cycle[neighbors] - trajectory[i, :3]) ** 2, axis=1
        )
        indices[i] = neighbors[np.argmin(distances)]

    return indices


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
    updated_cycle = np.zeros_like(reference_cycle)
    for i in range(len(reference_cycle)):
        matches = np.where(phase_indices == i)[0]
        if len(matches) == 0:
            updated_cycle[i] = reference_cycle[i]
        else:
            updated_cycle[i] = np.mean(trajectory[matches[-10:]], axis=0)
    return reference_cycle


def extract_phase(data, window_size=100, output_path=None):
    """
    Extract phase from multivariate time series data.

    Args:
        data (np.ndarray): Input time series data
        window_size (int): Window size for smoothing
        output_path (str, optional): Path for saving results

    Returns:
        tuple: Phase angles and visualization data
    """
    # Smooth data
    smoothed_data = np.apply_along_axis(
        lambda x: np.convolve(x, np.ones(window_size) / window_size, mode="valid"),
        axis=0,
        arr=data,
    )

    # Dimensionality reduction
    pca = PCA(n_components=4)
    reduced_data = pca.fit_transform(smoothed_data)
    trajectory = reduced_data[:, :3]

    # Find cycle boundaries
    start_idx, end_idx = detect_cycle_bounds(trajectory)
    reference_cycle = trajectory[start_idx:end_idx]

    # Smooth reference cycle
    reference_points = np.mean(reference_cycle.reshape(-1, 200, 3), axis=1)
    smooth_reference = smooth_trajectory(reference_points)

    # Phase assignment
    phase_indices = np.array([], dtype=np.int32)
    last_phase = 0
    chunk_size = 250000

    for i in range(0, len(trajectory), chunk_size):
        chunk_indices = assign_phase_indices(
            trajectory[i : i + chunk_size], smooth_reference, last_phase=last_phase
        )
        smooth_reference = update_reference_cycle(
            chunk_indices, smooth_reference, trajectory[i : i + chunk_size]
        )
        phase_indices = np.concatenate((phase_indices, chunk_indices))
        last_phase = chunk_indices[-1]

    # Convert to phase angles
    phase_angles = phase_indices / len(smooth_reference) * 2 * np.pi
    phase_angles = np.unwrap(phase_angles)

    if output_path:
        np.save(f"{output_path}_phase.npy", phase_angles)
        np.save(f"{output_path}_reference.npy", smooth_reference)
        np.save(f"{output_path}_trajectory.npy", trajectory)

        # Generate diagnostic plots
        plot_diagnostic_figures(
            trajectory, smooth_reference, phase_indices, phase_angles, output_path
        )

    return phase_angles, smooth_reference, trajectory


def plot_diagnostic_figures(trajectory, reference, indices, phase, output_path):
    """
    Generate diagnostic plots for phase extraction results.

    Args:
        trajectory (np.ndarray): Input trajectory
        reference (np.ndarray): Reference cycle
        indices (np.ndarray): Phase indices
        phase (np.ndarray): Phase angles
        output_path (str): Output path for saving figures
    """
    fig = plt.figure(figsize=(12, 8))

    # 3D trajectory plot
    ax1 = fig.add_subplot(231, projection="3d")
    ax1.plot(*reference.T, label="Reference")
    ax1.plot(*trajectory[:1000].T, label="Trajectory")
    ax1.legend()

    # Phase assignment plot
    ax2 = fig.add_subplot(232)
    ax2.plot(trajectory[:1000, 0], label="Original")
    ax2.plot(reference[indices[:1000], 0], label="Phase-aligned")
    ax2.legend()

    # Phase angle plot
    ax3 = fig.add_subplot(233)
    ax3.plot(phase[:1000], label="Phase")
    ax3.legend()

    plt.tight_layout()
    plt.show(block=True)


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python extract_phase.py <data_directory>")
        sys.exit(1)

    data_dir = sys.argv[1]
    if not os.path.isdir(data_dir):
        print(f"Error: {data_dir} is not a valid directory")
        sys.exit(1)

    for filename in os.listdir(data_dir):
        if filename.endswith(".tdms"):
            input_path = os.path.join(data_dir, filename)
            output_base = os.path.splitext(input_path)[0]
            f = NIfile(input_path)
            start = 0
            stop = min(f.datasize, int(f.freq * 10))
            # Load and process data
            C0, C90, C45, C135 = f.ret_cor_channel_in_file(start, int(stop))
            data = np.column_stack((C0, C90, C45, C135))
            extract_phase(data, output_path=output_base)

        # except Exception as e:
        #     print(f"Error processing {filename}: {str(e)}")
