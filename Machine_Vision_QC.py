import sensor, image, time, pyb

# ----------colors
# average RGB value for each color of board when shot at a 40000us exposure time
COLORS = {"yellow": (247, 255, 123),
          "blue": (110, 255, 255),
          "red": (255, 203, 115),
          "gray": (74, 215, 115)}

COLOR_ROI = (166, 31, 8, 13)

# ----------binary thresholds
# When the image of the board is evaluated, one threshold is used to look for the components on the
# perimeter.  Then the other threshold is used to look for the remaining components.
# In testing, it was found that (for boards other than gray) multiple thresholds were needed to
# avoid obscuring missing components around the perimeter.
BINARY_THRESHOLDS = {"gray": [[(80, 255)], [(80, 255)]],
                     "red": [[(150, 255)], [(170, 255)]],
                     "blue": [[(110, 255)], [(155, 255)]],
                     "yellow": [[(120, 255)], [(160, 255)]]
                     }

# ----------black thresholds
BLACK_THRESHOLDS = (0, 25)

# ----------inspection phases
# in phase 1, the perimeter of the board will be inspected
# then in phase 2, a new image will be taken, the binary thresholds will be adjusted, and the rest of
# the board will be analyzed
INSPECTION_PHASES = 2

# ----------exposure times
# optimal exposure times min and max in microseconds for each color
# these exposure times place the statistics.max() result in the 200-220 range for the exposure ROI
EXP_TIMES = {"blue": [10000, 50000],
             "yellow": [8000, 36000],
             "red": [60000, 130000],
             "gray": [80000, 250000],
             }

# ----------ROIS
# area used to sense when a new part has been placed
TRIGGER_ROI = (255, 76, 214, 328)

# area of board that should always be blank, used to determine the optimal exposure time
EXP_ROI = (382, 314, 21, 37)

# components near the perimeter of the board
PERIMETER_ROIS = {1: (252, 49, 53, 57),
                  2: (365, 51, 20, 52),
                  3: (382, 50, 21, 51),
                  4: (402, 50, 23, 53),
                  5: (441, 53, 49, 57),
                  13: (450, 129, 42, 47),
                  14: (238, 192, 33, 24),
                  15: (239, 216, 31, 22),
                  19: (452, 184, 37, 44),
                  25: (451, 233, 40, 48),
                  26: (233, 298, 21, 20),
                  27: (233, 317, 21, 18),
                  28: (234, 332, 21, 20),
                  34: (454, 289, 21, 24),
                  37: (296, 411, 46, 21),
                  39: (354, 406, 22, 25),
                  40: (384, 414, 10, 14),
                  41: (399, 413, 10, 14),
                  42: (414, 421, 12, 10),
                  43: (415, 331, 34, 78),
                  44: (458, 335, 26, 77),
                  }

# components not on the perimeter of the board
INNER_ROIS = {6: (316, 100, 20, 28),
              7: (332, 100, 20, 28),
              8: (349, 100, 20, 28),
              9: (263, 146, 28, 30),
              10: (324, 146, 45, 47),
              11: (385, 133, 31, 23),
              12: (386, 157, 30, 24),
              15: (239, 216, 31, 22),
              16: (320, 214, 51, 21),
              17: (385, 184, 31, 20),
              18: (386, 208, 30, 20),
              20: (265, 245, 21, 34),
              21: (295, 245, 20, 34),
              22: (331, 252, 51, 45),
              23: (385, 233, 33, 21),
              24: (385, 257, 31, 21),
              29: (277, 306, 47, 45),
              30: (339, 299, 22, 20),
              31: (339, 316, 22, 20),
              32: (339, 334, 23, 18),
              33: (425, 293, 27, 22),
              35: (264, 376, 28, 28),
              36: (296, 393, 48, 20),
              38: (354, 375, 23, 27),
              }

COMPONENT_ROIS = [PERIMETER_ROIS, INNER_ROIS]

# ----------reference parts
# for each board color, each component ROI has a corresponding "good" black pixel count
# on the next iteration of the machine, these values need to be built as averages of a larger sample set
GOOD_BOARDS = {"gray": {1: 3021, 2: 435, 3: 463, 4: 487, 5: 2765, 6: 147, 7: 164, 8: 156, 9: 430,
                        10: 2111, 11: 414, 12: 424, 13: 1492, 14: 447, 15: 438, 16: 503, 17: 428,
                        18: 422, 19: 1422, 20: 422, 21: 448, 22: 1458, 23: 453, 24: 419, 25: 1479,
                        26: 160, 27: 153, 28: 170, 29: 2112, 30: 152, 31: 168, 32: 164, 33: 403,
                        34: 360, 35: 442, 36: 541, 37: 558, 38: 416, 39: 379, 40: 106, 41: 92,
                        42: 78, 43: 2462, 44: 2002
                        },
               "red": {1: 2967, 2: 445, 3: 434, 4: 443, 5: 2793, 6: 137, 7: 154, 8: 154, 9: 432,
                       10: 2035, 11: 434, 12: 411, 13: 971, 14: 410, 15: 454, 16: 366, 17: 378,
                       18: 353, 19: 938, 20: 428, 21: 429, 22: 824, 23: 410, 24: 356, 25: 964,
                       26: 142, 27: 151, 28: 172, 29: 1988, 30: 119, 31: 173, 32: 164, 33: 361,
                       34: 312, 35: 457, 36: 527, 37: 551, 38: 400, 39: 347, 40: 87, 41: 70,
                       42: 94, 43: 2370, 44: 2002
                       },
               "blue": {1: 2865, 2: 393, 3: 396, 4: 408, 5: 2785, 6: 141, 7: 145, 8: 140, 9: 428,
                        10: 2106, 11: 436, 12: 422, 13: 896, 14: 312, 15: 442, 16: 392, 17: 413,
                        18: 389, 19: 868, 20: 439, 21: 447, 22: 881, 23: 426, 24: 389, 25: 845,
                        26: 27, 27: 19, 28: 34, 29: 2107, 30: 131, 31: 154, 32: 146, 33: 396,
                        34: 317, 35: 432, 36: 535, 37: 488, 38: 415, 39: 340, 40: 47, 41: 43,
                        42: 87, 43: 2378, 44: 2002
                        },
               "yellow": {1: 2523, 2: 498, 3: 481, 4: 502, 5: 2558, 6: 200, 7: 217, 8: 222, 9: 543,
                          10: 2014, 11: 469, 12: 457, 13: 1002, 14: 454, 15: 506, 16: 582, 17: 459,
                          18: 444, 19: 905, 20: 493, 21: 499, 22: 942, 23: 497, 24: 441, 25: 955,
                          26: 180, 27: 182, 28: 220, 29: 1988, 30: 213, 31: 258, 32: 229, 33: 459,
                          34: 345, 35: 572, 36: 639, 37: 564, 38: 453, 39: 367, 40: 97, 41: 79,
                          42: 94, 43: 2288, 44: 1921
                          },
               }

# for tracking the quantity of good and bad parts over time
history_tracker = {"good": 0,
                   "bad": 0,
                   }


# sets up the sensor for grayscale VGA images
def init():
    sensor.reset()  # reset sensor
    sensor.set_pixformat(sensor.GRAYSCALE)  # set pixel format to GRAYSCALE
    sensor.set_framesize(sensor.VGA)  # set frame size to VGA
    sensor.set_auto_gain(False)  # disabled for exposure control
    sensor.set_auto_whitebal(True)
    sensor.skip_frames(time=1000)  # wait for settings take effect


def get_color():
    sensor.reset()  # reset sensor
    sensor.set_pixformat(sensor.RGB565)  # set pixel format to RGB565
    sensor.set_framesize(sensor.QVGA)  # set frame size to QVGA
    sensor.set_auto_gain(False)  # disabled for exposure control
    sensor.set_auto_whitebal(False)  # disabled for exposure control
    sensor.set_auto_exposure(False, exposure_us=40000)
    sensor.skip_frames(time=2000)  # wait for settings take effect

    # blank region to check when evaluating the board's color
    color_roi = (162, 27, 17, 22)

    color_img = sensor.snapshot()
    # get the histogram for the blank region
    hist = color_img.histogram(roi=color_roi).get_statistics()
    # pull the LAB numbers from the histogram
    lab_nums = (hist[0], hist[8], hist[16])
    # convert them to RGB values
    rgb_nums = image.lab_to_rgb(lab_nums)

    # compare RGB values to those of known colors
    # if all values (R-G-B) are within a tolerance of the reference data, we have a successful match
    success = [1, 1, 1]
    for key in COLORS.keys():
        reference_nums = COLORS[key]
        print(f"ref nums: {reference_nums}")
        print(f"rgb nums: {rgb_nums}")
        # create empty array to track which values from RGB match with the reference set
        match = []
        # iterate through the 3 values in the RGB set
        for idx in range(len(reference_nums)):
            ref_num = reference_nums[idx]
            test_num = rgb_nums[idx]
            # get the absolute value of the difference between test and reference RGB values
            diff = abs(ref_num - test_num)
            # if a value (R, G, or B) differs by less than 40, consider it a match
            if diff < 40:
                match.append(1)  # binary representation of success
            else:
                match.append(0)  # binary representation of failure
        # after a successful match, reset the sensor for grayscale and return the correct color
        if match == success:
            init()
            return key
    # gray's variability made it especially hard to classify
    # so if all else fails, the board is most likely gray
    # return gray rather than crashing, and reset the sensor for grayscale imaging
    # this was a band-aid to meet an assignment deadline
    # in the future, more robust gray board detection is needed
    init()
    return "gray"


# tests a given exposure time and returns the value of get_statistics.max()
def test_new_exp_time(new_exp_time, test_roi):
    sensor.set_auto_exposure(False, exposure_us=new_exp_time)
    pyb.delay(100)
    img = sensor.snapshot()
    stats_max = img.get_statistics(roi=test_roi).max()
    return stats_max


# determines board color by observing the results of different exposure times
def get_exp_time(exp_times, exp_roi, color):
    stats_max = 0
    # begin by checking the average exposure time of the range
    min_exp_time = exp_times[color][0]
    max_exp_time = exp_times[color][1]
    exp_time_difference = max_exp_time - min_exp_time
    avg_exp_time = int((min_exp_time + max_exp_time) / 2)
    # how much to increment the exposure time by for each new attempt
    time_incr = 1000
    # set the number of attempts to the number of steps in 1000us increments between min and max
    attempts = int((exp_time_difference / time_incr) + 1)  # +1 to be able to try the avg first
    exp_time = avg_exp_time
    first_attempt = True  # flag
    for attempt in range(attempts):
        # get the value of get_statistics.max() for the given exposure time
        stats_max = test_new_exp_time(exp_time, exp_roi)
        # with the correct exp time, get_statistics.max() should return 200-220, ~207 in testing
        if (stats_max >= 200) and (stats_max <= 220):
            return exp_time
        else:
            if first_attempt:
                # if the average exposure time doesn't yield a solution, try the minimum time
                exp_time = min_exp_time
                first_attempt = False
            else:
                # if the new exposure time doesn't yield a solution, increment it and try again
                exp_time += time_incr
    return "none"


# compares the pixel counts in the ROIs on the test board against those in the ROIs on a good board
def inspect_board(color,
                  black_thresholds,
                  binary_thresholds,
                  reference_boards,
                  phases,
                  component_rois,
                  qc_history):
    # in phase 1, the perimeter of the board is checked with one binary threshold
    # in phase 2, the rest of the board is checked with a different binary threshold
    board_failed = False  # flag
    for phase in range(phases):
        img = sensor.snapshot()
        binary_threshold = binary_thresholds[color][phase]  # use correct threshold for given color
        img.binary(binary_threshold)

        # count black pixels in each ROI
        results = {}  # tabulate results in a dictionary
        reference_board = reference_boards[color]  # select the correct good board for comparison
        # select the correct set of ROIs (perimeter, then inner) for the given inspection phase
        for key in component_rois[phase].keys():
            blobs = img.find_blobs([black_thresholds],
                                   roi=component_rois[phase][key],
                                   pixels_threshold=1,
                                   area_threshold=1,
                                   merge=True)
            # count the black pixels in a given ROI
            black_pixels = sum(blob.pixels() for blob in blobs)
            # append the results to the dictionary
            results[key] = black_pixels
            # calculate the percent change in pixels from the reference board to the test board
            percent_change = (results[key] - reference_board[key]) / reference_board[key]
            # if more than 90% of pixels are lost, the ROI fails, and subsequently, the board fails
            if percent_change < -0.90:
                print(f"Pixel Count Change:\t{round(percent_change * 100, 2)}% in ROI {key}")
                print(f"\n\n\t\t\t----------\n\t\t\t! REJECT !\n\t\t\t----------\n\n")
                print(" ")
                # update the good/bad tracker
                qc_history['bad'] += 1
                print(f"\n\nGood:\t{qc_history['good']}\nBad:\t{qc_history['bad']}")
                return
    # if none of the ROIs fail, the board passes
    print(f"\n\n\t\t\t----------\n\t\t\t* ACCEPT *\n\t\t\t----------\n\n")
    # update the good/bad tracker
    qc_history['good'] += 1
    print(f"\n\nGood:\t{qc_history['good']}\nBad:\t{qc_history['bad']}")


# attempts to tell if the ROI where a part would be is empty
def sense_machine_empty(roi):
    test_img = sensor.snapshot()
    test_mean = test_img.get_statistics(roi=roi).mean()
    # if the mean of a sample image is over 190, it's presumed to be an image of a blank white space
    if test_mean > 190:
        return True
    else:
        return False


# determines if a new part is ready to shoot
# in the future, I'd try adding one thing to make this check more robust:
#       a check that the mean of a test shot is over a threshold (hand in shot makes for lower mean)
def ready_for_shot(roi):
    # the amount of seconds we are willing to wait while attempting to confirm we're ready to shoot
    observation_period = 5
    old_mean = 0
    # try once per second, for 5 seconds
    for second in range(observation_period):
        test_img = sensor.snapshot()
        new_mean = test_img.get_statistics(roi=roi).mean()
        # if the mean changes by less than 25, we presume it is safe to shoot the part for
        if abs(new_mean - old_mean) < 25:
            return True
        else:
            # if the difference between old and new means is > 25, update the old mean for next try
            old_mean = new_mean
            pyb.delay(1000)
    return False


# main
init()
while True:
    # while the machine has no part in its tool, keep checking for a new part every 1 second
    if sense_machine_empty(roi=TRIGGER_ROI):
        pyb.delay(1000)

    else:
        # once the machine is no longer empty, wait until the part is ready to shoot
        # should wait for no foreign objects to be present in the tool area
        if ready_for_shot(roi=TRIGGER_ROI):
            # wait 1 second to process the results
            pyb.delay(1000)

            # determine board color and exposure time
            color = get_color()
            # iterate through a range of exposure times most likely to work for the given color
            exp_time = get_exp_time(exp_times=EXP_TIMES, exp_roi=EXP_ROI, color=color)
            # in case a shot is taken with a hand in the tool area, try to get exp time again
            if exp_time == "none":
                # reset the sensor before re-attempting to get exposure time
                init()
                exp_time = get_exp_time(exp_times=EXP_TIMES, exp_roi=EXP_ROI, color=color)
            print(f"\nBoard Color:\t\t{color.upper()}")

            # set exposure time
            print(f"Optimal Exposure Time:\t{exp_time}")
            sensor.set_auto_exposure(False, exposure_us=exp_time)
            pyb.delay(1000)

            # inspect the board
            inspect_board(color=color,
                          black_thresholds=BLACK_THRESHOLDS,
                          binary_thresholds=BINARY_THRESHOLDS,
                          reference_boards=GOOD_BOARDS,
                          phases=INSPECTION_PHASES,
                          component_rois=COMPONENT_ROIS,
                          qc_history=history_tracker)

            # wait until the part has been removed
            # check every 1 second to see if the part has been removed
            while not sense_machine_empty(roi=TRIGGER_ROI):
                pyb.delay(1000)
