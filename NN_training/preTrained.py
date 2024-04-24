from inference import get_model
import supervision as sv
import cv2

image_file = "./data/scenes/images/001041275.jpg"
image = cv2.imread(image_file)

model = get_model(model_id="playing-cards-ow27d/4")

results = model.infer(image)

detections = sv.Detections.from_inference(results[0].dict(by_alias=True, exclude_none=True))

bounding_box_annotator = sv.BoundingBoxAnnotator()
label_annotator = sv.LabelAnnotator()

annotated_image = bounding_box_annotator.annotate(
    scene=image, detections=detections)

print(detections.data)

annotated_image = label_annotator.annotate(
    scene=annotated_image, detections=detections)

sv.plot_image(annotated_image)