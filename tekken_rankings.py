import cv2, numpy, os, time, math, psutil, mss, pytesseract, glob
from directkeys import PressKey, ReleaseKey, W, A, S, D

# IMPORTANT NOTE: The following values are all calculate for a 1440p monitor
# I am assuming that you are playing 2560x1440 in borderless mode, not windowed
# Playing windowed mode will mess up all these numbers as they assume fullscreen
# If you are playing at 1080p or 4K, you need to manually edit these values

# the location and dimensions of the ranking box (rb)
# the 'ranking box' is the smallest rectangle enclosing all 12 rank rows
# this can be approximate, but all other values will be relative to this
rb_t = 370          # box starts this many pixels from the top  of game screen
rb_l = 450          # box starts this many pixels from the left of game screen
rb_w = 1670         # box is this many pixels wide
rb_h = 848          # box is this many pixels high
rb_r = rb_l + rb_w
rb_b = rb_t + rb_h

# the area of the screen that you want to capture (the ranking box area only)
monitor = {"top": rb_t, "left": rb_l, "width": rb_w, "height": rb_h}

# the height of each row in the rankings table (has to be exact to the pixel)
box_h = 71

# left and right x-values of the boxes for name, rank, and chararacter
# all of these values are relative to the ranking box, not the game window
name_l = 245            # name box starts this many pixles from the left of rb
name_r = name_l + 350   # name box ends this many pixles from the left of rb
rank_l = 1500           # rank box starts this many pixles from the left of rb
rank_r = 1660           # name box ends this many pixles from the left of rb
char_l = 1387           # char box starts this many pixles from the left of rb
char_r = 1490           # char box ends this many pixles from the left of rb

# check to see if the Tekken 7 process is running
def check_process():
    wow_process_names = ["TEKKEN 7.exe"]
    for pid in psutil.pids():
        p = psutil.Process(pid)
        if any(p.name() in s for s in wow_process_names):
            print("   ", p.name(), " found") 
            return True
    return False

# loads all of our character images / names into memory
# images are loaded from directory 'char' relative to execution
# these images must be the EXACT same size as what you capture
# to generate the images, use code below main(), they aren't included
char_images = []
char_names = []
def load_char_images():
    filenames = glob.glob("chars/*.png")
    for filename in filenames:
        char_names.append(filename[6:-4])
        img = cv2.imread(filename)
        char_images.append(img)
    print(char_names)

# loads all of our rank images / names into memory
# images are loaded from directory 'ranks' relative to execution
# these images must be the EXACT same size as what you capture
# to generate the images, use code below main(), they aren't included
rank_images = []
rank_names = []
def load_rank_images():
    filenames = glob.glob("ranks/*.png")
    for filename in filenames:
        rank_names.append(filename[6:-4])
        img = cv2.imread(filename)
        rank_images.append(img)
    print(rank_names)

# matches a given image to all our character imgaes
# returns index of char_images array which most closely matches
def match_char_image(char_img):
    min_mean = 255
    min_index = 0
    for i in range(0, len(char_images)):
        diff = cv2.absdiff(char_images[i], char_img)
        mean = diff.mean()
        if mean < min_mean:
            min_mean = mean
            min_index = i
    return min_index

# matches a given image to all our rank imgaes
# returns index of rank_images array which most closely matches
def match_rank_image(rank_img):
    min_mean = 255
    min_index = 0
    for i in range(0, len(rank_images)):
        diff = cv2.absdiff(rank_images[i], rank_img)
        mean = diff.mean()
        if mean < min_mean:
            min_mean = mean
            min_index = i
    return min_index

def process_screen():

    # counter for the player number
    player = 0

    # open the file in utf-8 mode because the OCR produces weird results
    f = open('tekken_rank_data_csv.txt', 'a+', encoding="utf-8")

    # loops forever, so make sure to stop manually when the rank table ends
    while True:
        # grab the specified area of the screen with mss
        img_rgb  = numpy.array(mss.mss().grab(monitor))
        img_rgb  = cv2.cvtColor(img_rgb, cv2.COLOR_RGBA2RGB)
        img_gray = cv2.cvtColor(img_rgb, cv2.COLOR_BGR2GRAY)

        # after we've captured the image, press the D key to advance leaderboard
        # it will load while we spend a few seconds parsing this screen
        # the sleep is required for the game to advance a frame and detect key press
        PressKey(D) 
        time.sleep(0.1)
        ReleaseKey(D) 

        # there are 12 rankings displayed per page, iterate through them
        for i in range(0, 12):
            # dimensions of the entire player row
            player_tl = (0, i*box_h)
            player_br = (rb_w-1, (i+1)*box_h)
            # dimensions of the box we'll extract the name from
            name_tl = (name_l,i*box_h + 15)
            name_br = (name_r,(i+1)*box_h - 15)
            # dimensions of the character box
            char_tl = (char_l + 25, i*box_h + 8)
            char_br = (char_r - 25, (i+1)*box_h - 8)
            # dimenions of the rank box
            rank_tl = (rank_l, i*box_h + 8)
            rank_br = (rank_r, (i+1)*box_h - 8)

            # draw those rectangles for debugging
            cv2.rectangle(img_rgb, name_tl, name_br, (0,0,255), 1)
            cv2.rectangle(img_rgb, char_tl, char_br, (0,0,255), 1)
            cv2.rectangle(img_rgb, player_tl, player_br, (255,255,255), 1)
            cv2.rectangle(img_rgb, rank_tl, rank_br, (0,0,255), 1)

            # show the current screen capture with debug information
            # next line is just so the image display doesn't block code
            cv2.imshow('Tekken', img_rgb)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

            # extract cv2 images from the boxes we constructed
            name_image = img_gray[name_tl[1]:name_br[1], name_tl[0]:name_br[0]]
            char_image = img_rgb[char_tl[1]:char_br[1], char_tl[0]:char_br[0]]
            rank_image = img_rgb[rank_tl[1]:rank_br[1], rank_tl[0]:rank_br[0]]

            # match the character image, giving us the index into the image/name array
            char_index = match_char_image(char_image)
            char_name = char_names[char_index]

            # match the rank image, giving us the index into the image/name array
            rank_index = match_rank_image(rank_image)
            rank_name = rank_names[rank_index]

            # use the pytesseract OCR library to convert the name image to a string
            player_name = pytesseract.image_to_string(name_image)

            # calculate the correct player leaderboard standing
            player_number = player + i + 1
            
            # construct the data line that we will print to file as CSV
            data_line = str(player_number) + ", " + player_name + ", " + char_name + ", " + rank_name

            # write out the data
            print(data_line)
            f.write(data_line + "\n")

        # each screen advances 12 new players
        player = player + 12      

    # close the file that we wrote to
    f.close()
        
def main():

    # Checks to see if Tekken is running
    # This can be removed if you want, it's used to give you 3 sec to switch to the window
    # Once you run the program, you must give focus to the Tekken 7 window
    print('Checking for Tekken 7 window')
    if check_process():
        print("    Tekken is running")
        print("    Waiting 3 seconds, so you can switch to Tekken Window")
        time.sleep(3)
    else:
        print("    Tekken is not running, exiting program")
        exit()

    load_char_images()
    load_rank_images()
    process_screen()

if __name__ == "__main__":
    main()



"""

Code for generating unique character / rank images
Unused if you already have the images
This works by checking all the images and seeing if we have found a 'new' one
When a new one is found, it saves it out to the given filename

def process_char_image(char_img):
    threshold = 30
    found = False
    for img in char_images:
        diff = cv2.absdiff(img, char_img)
        mean = diff.mean()
        #print(mean)
        if mean < threshold:
            found = True
            break
    if not found:
        char_images.append(char_img)
        print('New character image found:', len(char_images))
        cv2.imwrite('char' + str(len(char_images)) + '.png', char_img)

def process_rank_image(rank_image):
    threshold = 30
    found = False
    for img in rank_images:
        diff = cv2.absdiff(img, rank_image)
        mean = diff.mean()
        #print(mean)
        if mean < threshold:
            found = True
            break
    if not found:
        rank_images.append(rank_image)
        print('New character image found:', len(rank_images))
        cv2.imwrite('rank' + str(len(rank_images)) + '.png', rank_image)

"""