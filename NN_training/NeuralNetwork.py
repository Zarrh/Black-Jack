# export ROBOFLOW_API_KEY=<your api key>

from inference import get_model
import supervision as sv
import cv2
import time
import urllib.request
import numpy as np
import requests

TITLE = "Live Table"
WIDTH = 1088
HEIGHT = 1088

IPCam = '192.168.4.10'
PortCam = 8080
PortServer = 5555
IPServer = f'127.0.0.1:{PortServer}'

model = get_model(model_id="playing-cards-ow27d/4")
camUrl = f'http://{IPCam}:{PortCam}/photo.jpg'
serverURL = f'http://{IPServer}/get-cards'

image = None
detections = []
MIN_CONFIDENCE = 0.6
MIN_CONSECUTIVE_FRAMES = 3

def receive():

    img_resp = urllib.request.urlopen(camUrl)
    imgnp = np.array(bytearray(img_resp.read()),dtype=np.uint8)
    im = cv2.imdecode(imgnp, -1)

    results = model.infer(im)

    detections = sv.Detections.from_inference(results[0].dict(by_alias=True, exclude_none=True))

    bounding_box_annotator = sv.BoundingBoxAnnotator()
    label_annotator = sv.LabelAnnotator()

    annotated_image = bounding_box_annotator.annotate(
        scene=im, detections=detections
    )

    annotated_image = label_annotator.annotate(
        scene=annotated_image, detections=detections
    )

    return im, detections.xyxy, detections.confidence, detections.data['class_name']

def get_zone(box: list):

    if (box[1] + box[3]) / 2 > HEIGHT*2 / 3:
        return "Dealer" # Under 2/3 of the screen
    if (box[0] + box[2]) / 2 < WIDTH / 3:
        return 1 # Left side
    if (box[0] + box[2]) / 2 > WIDTH / 3 and (box[0] + box[2]) / 2 < WIDTH*2 / 3:
        return 2 # Center side
    if (box[0] + box[2]) / 2 > WIDTH*2 / 3:
        return 3 # Right side
    else:
        return -1
            
if __name__ == '__main__':

    cv2.namedWindow(TITLE, cv2.WINDOW_AUTOSIZE)

    i = 0

    while True:

        image, boxes, confidences, cards = receive()

        new_detections = {"cards": [], "boxes": [], "confidences": [], "counts": []}
        temp = {}
        consecutive_counts = {}

        for card, confidence, box in zip(cards, confidences, boxes):
            try:
                if confidence >= MIN_CONFIDENCE:
                    if card not in temp or confidence > temp[card][0]:
                        temp[card] = [confidence, box]   
                        consecutive_counts[card] = consecutive_counts.get(card, 0) + 1                                
            except:
                continue

        for card, (confidence, box) in temp.items():
            new_detections["cards"].append(card)
            new_detections["confidences"].append(confidence)
            new_detections["boxes"].append(box)

        i += 1

        if i == MIN_CONSECUTIVE_FRAMES - 1:
            detections = []
            for card, box in zip(new_detections["cards"], new_detections["boxes"]):
                card = card[:-1] + card[-1].lower()
                detections.append({"card": card, "position": get_zone(box)})
            print(detections)
            try:
                res = requests.post(serverURL, json={"data": detections})
                if res.status_code == 200:
                    print(f"Cards sent successfully.")
                else:
                    print(f"Failed to send cards. Status code: {res.status_code}. Error: {res.json}")
            except requests.exceptions.RequestException as e:
                print(f"Error sending cards: {e}")
            i = 0
            time.sleep(3)

        cv2.imshow(TITLE, image)
        key = cv2.waitKey(5)
        if key == ord('q'):
            break

    cv2.destroyAllWindows()