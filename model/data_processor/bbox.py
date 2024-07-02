import cv2
import json

# Sample bounding box data
bbox_data = """
{
  "bbox": [
    {
      "ymin": 128,
      "xmin": 202,
      "ymax": 903,
      "xmax": 708
    }
  ]
}
"""

# Load the bounding box data
bbox_data = json.loads(bbox_data)

# Function to draw bounding boxes on an image
def draw_bounding_boxes(image_path, bbox_data):
    # Read the image
    image = cv2.imread(image_path)
    
    # Check if the image was successfully loaded
    if image is None:
        print("Error: Image not found or unable to load.")
        return
    
    # Loop through each bounding box
    for bbox in bbox_data["bbox"]:
        ymin = bbox["ymin"]
        xmin = bbox["xmin"]
        ymax = bbox["ymax"]
        xmax = bbox["xmax"]
        
        # Draw the bounding box
        cv2.rectangle(image, (xmin, ymin), (xmax, ymax), (0, 0, 255), 2)
    
    # Display the image with bounding boxes
    cv2.imshow('Image with Bounding Boxes', image)
    
    # Save the image with bounding boxes (optional)
    cv2.imwrite('output_image_with_bboxes.jpg', image)
    
    # Wait for a key press and close the image window
    cv2.waitKey(0)
    cv2.destroyAllWindows()

# Path to the input image
image_path = 'dress.jpg'

# Draw bounding boxes on the image
draw_bounding_boxes(image_path, bbox_data)