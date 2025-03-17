from pyqtrod.helpers.simulation_helpers import compute_differences
from tap import Tap
import numpy as np


class Arguments(Tap):
    nofresnel: bool = False  # Operation to perform (add, subtract)
    mask: bool = False  # First number


def main(args: Arguments):
    phil = np.arange(1, 90, 1)
    thetal = np.arange(1, 90, 1)

    computed_angles = compute_differences(phil, thetal, args.nofresnel, args.mask)
    np.savez(
        f"computed_angles_nofresnel_{args.nofresnel}_mask_{args.mask}",
        phil=phil,
        thetal=thetal,
        computed_angles=computed_angles,
    )


if __name__ == "__main__":
    args = Arguments().parse_args()
    main(args)
