import argparse
import numpy as np
import cv2
import os


def convert_200mp(data):
    width = 16320
    height = 12288
    data = data.reshape(height, width)

    greens1 = [data[i::8, j::8] for i in range(4) for j in range(4)]
    greens2 = [data[i::8, j::8] for i in range(4, 8) for j in range(4, 8)]
    reds = [data[i::8, j::8] for i in range(4) for j in range(4, 8)]
    blues = [data[i::8, j::8] for i in range(4, 8) for j in range(4)]

    green_1 = np.zeros((height // 2, width // 2), dtype=np.uint8)
    green_2 = np.zeros((height // 2, width // 2), dtype=np.uint8)
    red = np.zeros((height // 2, width // 2), dtype=np.uint8)
    blue = np.zeros((height // 2, width // 2), dtype=np.uint8)

    for i in range(4):
        for j in range(4):
            green_1[0+i::4, 0+j::4] = greens1[j*4+i]

    for i in range(4):
        for j in range(4):
            green_2[0+i::4, 0+j::4] = greens2[j*4+i]

    for i in range(4):
        for j in range(4):
            red[0+i::4, 0+j::4] = reds[j*4+i]

    for i in range(4):
        for j in range(4):
            blue[0+i::4, 0+j::4] = blues[j*4+i]

    bayer = np.zeros((height, width), dtype=np.uint8)
    bayer[0::2, 0::2] = green_1
    bayer[0::2, 1::2] = red
    bayer[1::2, 0::2] = blue
    bayer[1::2, 1::2] = green_2
    color = cv2.cvtColor(bayer, cv2.COLOR_BayerGB2BGR)
    return color


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('-f', '--filepath', type=str, required=True, help='200mp raw images file path or directory path, if it is a directory, please set -b/--batch option')
    parser.add_argument('-b', '--batch', action='store_true', required=False, help="if -f/--filepath is a directory, set this option to process all files in the directory")

    args = parser.parse_args()
    filepath = args.filepath
    batch = args.batch
    if not filepath.endswith(".RAW") and not batch:
        raise ValueError("if -b/--batch option is not set, -f/--filepath should be a 200mp raw image file path")

    if batch:
        output_dir = "output"
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
        for root, dirs, files in os.walk(filepath):
            for file in files:
                if file.endswith(".RAW"):
                    data = np.fromfile(os.path.join(root, file), dtype=np.uint8)
                    color = convert_200mp(data)
                    filename = os.path.basename(file).split(".")[0]
                    print(f"Saving {output_dir}/{filename}.jpg")
                    cv2.imwrite(f"{output_dir}/{filename}.jpg", color)
    else:
        data = np.fromfile(filepath, dtype=np.uint8)
        color = convert_200mp(data)
        filename = os.path.basename(filepath).split(".")[0]
        print(f"Saving {filename}.jpg")
        cv2.imwrite(f"{filename}.jpg", color)
