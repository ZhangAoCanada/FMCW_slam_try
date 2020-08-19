import numpy as np
import cv2
import matplotlib.pyplot as plt
from tqdm import tqdm
from util import *
from radar_frame import Frame
from radar_slam import RSLAM

def generateImage(RAD_mag, ax):
    new_mag = getLog(getSumDim(RAD_mag, ax), scalar=10, log_10=True)
    image = norm2Image(new_mag)[..., :3]
    return image

def main(radar_dir, img_dir, mask_dir, sequences, save_dir, \
            window_sizes, max_disparity_channels):
    fig = plt.figure(figsize = (25, 15))
    ax1 = fig.add_subplot(121)
    ax2 = fig.add_subplot(122)

    slam = RSLAM(window_sizes, max_disparity_channels)
    checkoutDir(save_dir)
    for frame_i in tqdm(range(sequences[0], sequences[1])):
        RAD = readRAD(radar_dir, frame_i)
        RAD_mask = readRADMask(mask_dir, frame_i)
        img = readImg(img_dir, frame_i)
        if RAD is None or RAD_mask is None or img is None:
            continue
        RAD_mag = getMagnitude(RAD, power_order=2)
        RA_img = generateImage(RAD_mag, -1)
        RD_img = generateImage(RAD_mag, 1)
        RAD_mag = getLog(RAD_mag, scalar=10, log_10=True)

        this_frame = Frame(RAD_mag, RAD_mask)
        slam(this_frame)

        t_all = []
        for i in range(len(slam.H_all)):
            H = slam.H_all[i]
            t = H[:2, 2]
            t_all.append([t[0], t[1]])
        t_all = np.array(t_all)

        ax1.clear()
        ax1.plot(t_all[:, 0], t_all[:, 1], 'g')
        ax1.scatter(slam.pcl[:, 0], slam.pcl[:, 1], s=0.2, c='r')
        ax2.clear()
        ax2.imshow(RA_img)
        if slam.id_pairs is not None:
            for i in range(len(slam.id_pairs)):
                r1, a1, d1, r2, a2, d2 = slam.id_pairs[i]

                ax2.scatter(a1, r1, s=0.5, c='r')
                ax2.plot([a1, a2], [r1, r2], 'r')
                ax2.scatter(a2, r2, s=0.5, c='b')

        # fig.canvas.draw()
        plt.savefig(os.path.join(save_dir, "result.png"))
        # plt.pause(0.1)


if __name__ == "__main__":
    time_stamp = "2020-08-09-15-50-38"
    radar_dir = "/DATA/" + time_stamp + "/ral_outputs_" + time_stamp + "/RAD_numpy"
    img_dir = "/DATA/" + time_stamp + "/stereo_imgs/left"
    mask_dir = "/home/ao/Documents/stereo_radar_calibration_annotation/radar_process/radar_ral_process/radar_RAD_mask"

    save_dir = "./results"
    sequences = [20, 1000]

    window_half_sizes = [8, 8, 5]
    max_disparity_channels = [15, 15, 5]
    main(radar_dir, img_dir, mask_dir, sequences, save_dir, \
        window_half_sizes, max_disparity_channels)
