import numpy as np
import cv2
import os
from tqdm import tqdm
import random
import os
import matplotlib.pyplot as plt
import matplotlib.image as mpimg
import matplotlib.patches as patches
import pickle
from glob import glob 
import imgaug as ia
from imgaug import augmenters as iaa
from shapely.geometry import Polygon

# === Measures === #

cardW=65
cardH=90
cornerXmin=4
cornerXmax=13
cornerYmin=4
cornerYmax=25

# === === #

# We convert the measures from mm to pixels: multiply by an arbitrary factor 'zoom'
# You shouldn't need to change this
zoom=4
cardW*=zoom
cardH*=zoom
cornerXmin=int(cornerXmin*zoom)
cornerXmax=int(cornerXmax*zoom)
cornerYmin=int(cornerYmin*zoom)
cornerYmax=int(cornerYmax*zoom)

def display_img(img, polygons=[], channels="bgr", size=9):
    """
        Function to display an inline image, and draw optional polygons (bounding boxes, convex hulls) on it.
        Use the param 'channels' to specify the order of the channels ("bgr" for an image coming from OpenCV world)
    """
    if not isinstance(polygons, list):
        polygons=[polygons] # Turn polygons into list #
    if channels == "bgr": # bgr (cv2 image)
        nb_channels = img.shape[2]
        if nb_channels == 4:
            img=cv2.cvtColor(img, cv2.COLOR_BGRA2RGBA) # Image with alpha channel #
        else:
            img=cv2.cvtColor(img,cv2.COLOR_BGR2RGB) # Image without alpha channel #  
    fig, ax=plt.subplots(figsize=(size,size))
    ax.set_facecolor((0,0,0))
    ax.imshow(img)
    for polygon in polygons:
        # A polygon has either shape (n,2), 
        # either (n,1,2) if it is a cv2 contour (like convex hull).
        # In the latter case, reshape in (n,2)
        if len(np.shape(polygon)) == 3:
            polygon = polygon.reshape(-1, 2)
        patch = patches.Polygon(polygon, linewidth=1, edgecolor='g', facecolor='none')
        ax.add_patch(patch)

def give_me_filename(dirname, suffixes, prefix=""): # Generate a random file name #
    """
        Function that returns a filename or a list of filenames in directory 'dirname'
        that does not exist yet. If 'suffixes' is a list, one filename per suffix in 'suffixes':
        filename = dirname + "/" + prefix + random number + "." + suffix
        Same random number for all the file name
        Ex: 
        > give_me_filename("dir","jpg", prefix="prefix")
        'dir/prefix408290659.jpg'
        > give_me_filename("dir",["jpg","xml"])
        ['dir/877739594.jpg', 'dir/877739594.xml']        
    """
    if not isinstance(suffixes, list):
        suffixes=[suffixes]
    
    suffixes=[p if p[0]=='.' else '.'+p for p in suffixes]
          
    while True:
        bname="%09d"%random.randint(0,999999999)
        fnames=[]
        for suffix in suffixes:
            fname=os.path.join(dirname,prefix+bname+suffix)
            if not os.path.isfile(fname):
                fnames.append(fname)
                
        if len(fnames) == len(suffixes): break
    
    if len(fnames) == 1:
        return fnames[0]
    else:
        return fnames

data_dir = "data" # Directory that will contain all kinds of data (the data we download and the data we generate)

if not os.path.isdir(data_dir):
    os.makedirs(data_dir)

card_suits=['s','h','d','c']
card_values=['A','K','Q','J','10','9','8','7','6','5','4','3','2']

# Pickle file containing the background images from the DTD
backgrounds_pck_fn = data_dir + "/backgrounds.pck"

# Pickle file containing the card images
cards_pck_fn = data_dir+"/cards.pck"

# imgW,imgH: dimensions of the generated dataset images 
# === Resolution === #
imgW = 720
imgH = 720
# === === #

refCard=np.array([[0,0],[cardW,0],[cardW,cardH],[0,cardH]],dtype=np.float32)
refCardRot=np.array([[cardW,0],[cardW,cardH],[0,cardH],[0,0]],dtype=np.float32)
refCornerHL=np.array([[cornerXmin,cornerYmin],[cornerXmax,cornerYmin],[cornerXmax,cornerYmax],[cornerXmin,cornerYmax]],dtype=np.float32)
refCornerLR=np.array([[cardW-cornerXmax,cardH-cornerYmax],[cardW-cornerXmin,cardH-cornerYmax],[cardW-cornerXmin,cardH-cornerYmin],[cardW-cornerXmax,cardH-cornerYmin]],dtype=np.float32)
refCorners=np.array([refCornerHL,refCornerLR])

"""
# Load all backgrounds into pickle file #
dtd_dir = "./dtd/images/" # Backgrounds directory #
bg_images=[]
for subdir in glob(dtd_dir+"/*"):
    for f in glob(subdir+"/*.jpg"):
        bg_images.append(mpimg.imread(f))
print("Nb of images loaded :", len(bg_images))
print("Saved in :", backgrounds_pck_fn)
pickle.dump(bg_images, open(backgrounds_pck_fn, 'wb'))
"""

class Backgrounds():
    def __init__(self, backgrounds_pck_fn=backgrounds_pck_fn):
        self._images=pickle.load(open(backgrounds_pck_fn, 'rb'))
        self._nb_images = len(self._images)
        print("Nb of images loaded :", self._nb_images)
    def get_random(self, display=False):
        bg=self._images[random.randint(0,self._nb_images-1)]
        if display: plt.imshow(bg)
        return bg
    
#backgrounds = Backgrounds() # Load all backgrounds into RAM #

# Test random background picking #
"""
_=backgrounds.get_random(display=True) 
plt.show()
"""

bord_size=2 # bord_size alpha=0
alphamask=np.ones((cardH,cardW),dtype=np.uint8)*255
cv2.rectangle(alphamask,(0,0),(cardW-1,cardH-1),0,bord_size)
cv2.line(alphamask,(bord_size*3,0),(0,bord_size*3),0,bord_size)
cv2.line(alphamask,(cardW-bord_size*3,0),(cardW,bord_size*3),0,bord_size)
cv2.line(alphamask,(0,cardH-bord_size*3),(bord_size*3,cardH),0,bord_size)
cv2.line(alphamask,(cardW-bord_size*3,cardH),(cardW,cardH-bord_size*3),0,bord_size)
plt.figure(figsize=(10,10))
#plt.imshow(alphamask)
#plt.show()

def varianceOfLaplacian(img):
    """
    Compute the Laplacian of the image and then return the focus
    measure, which is simply the variance of the Laplacian
    Source: A.Rosebrock, https://www.pyimagesearch.com/2015/09/07/blur-detection-with-opencv/
    """
    return cv2.Laplacian(img, cv2.CV_64F).var()

def extract_card(img, output_fn=None, min_focus=120, debug=False):
    """
    """
    
    imgwarp=None
    
    # Check the image is not too blurry
    focus=varianceOfLaplacian(img)
    if focus < min_focus: 
        if debug: print("Focus too low :", focus)
        return False, None
    
    # Convert in gray color
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    
    # Noise-reducing and edge-preserving filter
    gray = cv2.bilateralFilter(gray, 11, 17, 17) 

    # apply binary thresholding
    ret, thresh = cv2.threshold(gray, 150, 255, cv2.THRESH_BINARY)
    # visualize the binary image
    #cv2.imwrite('image_thres1.jpg', thresh)
    #cv2.destroyAllWindows()

    # detect the contours on the binary image using cv2.CHAIN_APPROX_NONE
    contours, hierarchy = cv2.findContours(image=thresh, mode=cv2.RETR_TREE, method=cv2.CHAIN_APPROX_NONE)
                                        
    # draw contours on the original image
    image_copy = img.copy()
    cv2.drawContours(image=image_copy, contours=contours, contourIdx=-1, color=(0, 255, 0), thickness=2, lineType=cv2.LINE_AA)
                    
    # see the results
    #cv2.imwrite('contours_none_image1.jpg', image_copy)
    #cv2.destroyAllWindows()       
    
    # We suppose that the contour with largest area corresponds to the contour delimiting the card
    cnt = sorted(contours, key = cv2.contourArea, reverse = True)[0]
    
    # We want to check that 'cnt' is the contour of a rectangular shape
    # First, determine 'box', the minimum area bounding rectangle of 'cnt'
    # Then compare area of 'cnt' and area of 'box'
    # Both areas sould be very close
    rect=cv2.minAreaRect(cnt)
    box=cv2.boxPoints(rect)
    box=np.intp(box)
    areaCnt=cv2.contourArea(cnt)
    areaBox=cv2.contourArea(box)
    valid=areaCnt/areaBox > 0.95
    
    if valid:
        # We want transform the zone inside the contour into the reference rectangle of dimensions (cardW,cardH)
        ((xr,yr), (wr,hr), thetar) = rect
        # Determine 'Mp' the transformation that transforms 'box' into the reference rectangle
        if wr > hr:
            Mp = cv2.getPerspectiveTransform(np.float32(box), refCard)
        else:
            Mp = cv2.getPerspectiveTransform(np.float32(box), refCardRot)
        # Determine the warped image by applying the transformation to the image
        imgwarp = cv2.warpPerspective(img, Mp, (cardW, cardH))
        # Add alpha layer
        imgwarp = cv2.cvtColor(imgwarp, cv2.COLOR_BGR2BGRA)
        
        # Shape of 'cnt' is (n,1,2), type=int with n = number of points
        # We reshape into (1,n,2), type=float32, before feeding to perspectiveTransform
        cnta = cnt.reshape(1,-1,2).astype(np.float32)
        # Apply the transformation 'Mp' to the contour
        cntwarp = cv2.perspectiveTransform(cnta, Mp)
        cntwarp = cntwarp.astype(np.int32)
        
        # We build the alpha channel so that we have transparency on the
        # external border of the card
        # First, initialize alpha channel fully transparent
        alphachannel=np.zeros(imgwarp.shape[:2],dtype=np.uint8)
        # Then fill in the contour to make opaque this zone of the card 
        cv2.drawContours(alphachannel,cntwarp,0,255,-1)
        
        # Apply the alphamask onto the alpha channel to clean it
        alphachannel=cv2.bitwise_and(alphachannel, alphamask)
        
        # Add the alphachannel to the warped image
        imgwarp[:,:,3]=alphachannel
        
        # Save the image to file
        if output_fn is not None:
            cv2.imwrite(output_fn, imgwarp)
        
    if debug:
        cv2.imshow("Gray", gray)
        cv2.imshow("Canny", thresh)
        edge_bgr = cv2.cvtColor(thresh,cv2.COLOR_GRAY2BGR)
        cv2.drawContours(edge_bgr, [box], 0, (0,0,255), 3)
        cv2.drawContours(edge_bgr, [cnt], 0, (0,255,0), -1)
        cv2.imshow("Contour with biggest area", edge_bgr)
        if valid:
            cv2.imshow("Alphachannel", alphachannel)
            cv2.imshow("Extracted card", imgwarp)

    return valid, imgwarp

# Test on one image the function for extracting the card #
"""
debug = False
img = cv2.imread("test/scene.png")
display_img(img)
valid, card = extract_card(img, "extracted_card.png", debug=debug)
if valid:
    display_img(card)
if debug:
    cv2.waitKey(0)
    cv2.destroyAllWindows()
plt.show()
"""

# Loop for extracting images #
"""
video_dir="./data/video"
extension="png"
imgs_dir="./data/cards"

for suit in card_suits:
    for value in card_values:
        
        card_name = value + suit # Name of the card #
        image_fn = card_name + "." + extension
        output_dir=os.path.join(imgs_dir, card_name)
        if not os.path.isdir(output_dir):
            os.makedirs(output_dir)
        img = cv2.imread(os.path.join(video_dir, image_fn))
        valid, card = extract_card(img, os.path.join(output_dir, image_fn))
        print(f"Extracted image {card_name}")
"""

# Extract one single card (Ace of spades) #
"""
video_dir="./data/video"
extension="png"
imgs_dir="./data/cards"

card_name = "A" + "s" # Name of the card #
image_fn = card_name + "." + extension
output_dir = os.path.join(imgs_dir, card_name)
if not os.path.isdir(output_dir):
    os.makedirs(output_dir)
img = cv2.imread(os.path.join(video_dir, image_fn))
valid, card = extract_card(img, os.path.join(output_dir, image_fn))
print(f"Extracted image {card_name}")
"""

# Check everything is correct #
# Run a few times...
"""
imgs_dir = "./data/cards"
imgs_fns = glob(imgs_dir + "/*/*.png")
img_fn = random.choice(imgs_fns)
display_img(cv2.imread(img_fn, cv2.IMREAD_UNCHANGED), polygons=[refCornerHL,refCornerLR])
plt.show()
"""

# Function used to reduce the area containing the suit and the value of the card #
def findHull(img, corner=refCornerHL, debug="no"):
    """
        Find in the zone 'corner' of image 'img' and return, the convex hull delimiting
        the value and suit symbols
        'corner' (shape (4,2)) is an array of 4 points delimiting a rectangular zone, 
        takes one of the 2 possible values : refCornerHL or refCornerLR
        debug=
    """
    
    kernel = np.ones((3,3), np.uint8)
    corner = corner.astype(np.int32)

    # We will focus on the zone of 'img' delimited by 'corner'
    x1 = int(corner[0][0])
    y1 = int(corner[0][1])
    x2 = int(corner[2][0])
    y2 = int(corner[2][1])
    w = x2-x1
    h = y2-y1
    zone = img[y1:y2, x1:x2].copy()

    strange_cnt = np.zeros_like(zone)
    gray = cv2.cvtColor(zone, cv2.COLOR_BGR2GRAY)
    ret, thld = cv2.threshold(gray, 150, 255, cv2.THRESH_BINARY)
    thld = cv2.dilate(thld, kernel, iterations=1)
    if debug != "no": cv2.imshow("thld", thld)
    
    # Find the contours
    contours, hierarchy = cv2.findContours(image=thld, mode=cv2.RETR_TREE, method=cv2.CHAIN_APPROX_NONE)

    min_area=30 # We will reject contours with small area. TWEAK, 'zoom' dependant
    min_solidity=0.3 # Reject contours with a low solidity. TWEAK
    
    concat_contour=None # We will aggregate in 'concat_contour' the contours that we want to keep
    
    ok=True
    for c in contours:
        area=cv2.contourArea(c)

        hull = cv2.convexHull(c)
        hull_area = cv2.contourArea(hull)
        solidity = float(area) / hull_area
        # Determine the center of gravity (cx,cy) of the contour
        M = cv2.moments(c)
        cx = int(M['m10'] / M['m00'])
        cy = int(M['m01'] / M['m00'])
        #  abs(w/2-cx)<w*0.3 and abs(h/2-cy)<h*0.4 : TWEAK, the idea here is to keep only the contours which are closed to the center of the zone
        if area >= min_area and abs(w/2-cx) < w*0.3 and abs(h/2-cy) < h*0.4 and solidity > min_solidity:
            if debug != "no" :
                cv2.drawContours(zone, [c], 0, (255,0,0), -1)
            if concat_contour is None:
                concat_contour=c
            else:
                concat_contour=np.concatenate((concat_contour, c))
        if debug != "no" and solidity <= min_solidity :
            print("Solidity", solidity)
            cv2.drawContours(strange_cnt, [c], 0, 255, 2)
            cv2.imshow("Strange contours", strange_cnt)
            
     
    if concat_contour is not None:
        # At this point, we suppose that 'concat_contour' contains only the contours corresponding the value and suit symbols   
        # We can now determine the hull
        hull = cv2.convexHull(concat_contour)
        hull_area = cv2.contourArea(hull)
        # If the area of the hull is to small or too big, there may be a problem
        min_hull_area = 940 # TWEAK, deck and 'zoom' dependant
        max_hull_area = 2120 # TWEAK, deck and 'zoom' dependant
        if hull_area < min_hull_area or hull_area > max_hull_area: 
            ok = False
            if debug!="no":
                print("Hull area=", hull_area, "too large or too small")
        # So far, the coordinates of the hull are relative to 'zone'
        # We need the coordinates relative to the image -> 'hull_in_img' 
        hull_in_img=hull+corner[0]

    else:
        ok=False
    
    
    if debug != "no" :
        if concat_contour is not None:
            cv2.drawContours(zone, [hull], 0, (0,255,0), 1)
            cv2.drawContours(img, [hull_in_img], 0, (0,255,0), 1)
        cv2.imshow("Zone", zone)
        cv2.imshow("Image", img)
        if ok and debug != "pause_always":
            key = cv2.waitKey(1)
        else:
            key = cv2.waitKey(0)
        if key == 27:
            return None
    if ok == False:
        
        return None
    
    return hull_in_img

# Test find_hull on a random card image
# debug = "no" or "pause_always" or "pause_on_pb"
# If debug!="no", you may have to press a key to continue execution after pause
debug="no"
imgs_dir="./data/cards"
imgs_fns=glob(imgs_dir+"/*/*.png")
img_fn=random.choice(imgs_fns)
print(img_fn)
img = cv2.imread(img_fn, cv2.IMREAD_UNCHANGED)

hullHL = findHull(img, refCornerHL, debug=debug)
hullLR = findHull(img, refCornerLR, debug=debug)
display_img(img, [refCornerHL, refCornerLR, hullHL, hullLR])

if debug!="no": cv2.destroyAllWindows()
plt.show()