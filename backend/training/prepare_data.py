import os
import xml.etree.ElementTree as ET
import shutil
import random

# --- Paths ---
BASE_DIR = r"C:\Users\DELL\Projects\AMD_Hackathon\Hackathon-AMD\data\PCB_DATASET"
IMG_DIR = os.path.join(BASE_DIR, "images")
ANN_DIR = os.path.join(BASE_DIR, "Annotations")
PERFECT_DIR = os.path.join(BASE_DIR, "PCB_USED") # Added Perfect Directory
YOLO_DIR = r"C:\Users\DELL\Projects\AMD_Hackathon\Hackathon-AMD\backend\training\yolo_dataset"

# YOLO Structure Setup
for split in ['train', 'val']:
    os.makedirs(os.path.join(YOLO_DIR, f"images/{split}"), exist_ok=True)
    os.makedirs(os.path.join(YOLO_DIR, f"labels/{split}"), exist_ok=True)

# 6 DeepPCB Classes
CLASS_MAP = {
    "missing_hole": 0, "mouse_bite": 1, "open_circuit": 2,
    "short": 3, "spur": 4, "spurious_copper": 5
}

# Ultralytics recommends ~10% of your dataset be background images to reduce false positives.
# If we have ~1500 faulty images, 150 perfect images is a perfect 10% ratio.
PERFECT_MULTIPLIER = 15 

def convert_to_yolo_format(size, box):
    dw = 1. / size[0]
    dh = 1. / size[1]
    return ((box[0] + box[1]) / 2.0 * dw, (box[2] + box[3]) / 2.0 * dh, 
            (box[1] - box[0]) * dw, (box[3] - box[2]) * dh)

all_data = []

# ---------------------------------------------------------
# PART 1: Gather Faulty Boards (Image + XML pair)
# ---------------------------------------------------------
for category in os.listdir(ANN_DIR):
    cat_ann_dir = os.path.join(ANN_DIR, category)
    cat_img_dir = os.path.join(IMG_DIR, category)
    if not os.path.isdir(cat_ann_dir): continue
        
    for xml_file in os.listdir(cat_ann_dir):
        if not xml_file.endswith('.xml'): continue
            
        xml_path = os.path.join(cat_ann_dir, xml_file)
        img_file = xml_file.replace('.xml', '.jpg')
        img_path = os.path.join(cat_img_dir, img_file)
        
        if os.path.exists(img_path):
            # Tuple: (Image Path, XML Path, is_perfect flag)
            all_data.append((img_path, xml_path, False))

# ---------------------------------------------------------
# PART 2: Gather and Oversample Perfect Boards
# ---------------------------------------------------------
if os.path.exists(PERFECT_DIR):
    perfect_images = [f for f in os.listdir(PERFECT_DIR) if f.lower().endswith(('.png', '.jpg', '.jpeg'))]
    for img_filename in perfect_images:
        img_path = os.path.join(PERFECT_DIR, img_filename)
        for i in range(PERFECT_MULTIPLIER):
            # Tuple: (Image Path, None for XML, is_perfect flag)
            all_data.append((img_path, None, True))

# ---------------------------------------------------------
# PART 3: Shuffle and Split (80% Train, 20% Val)
# ---------------------------------------------------------
random.shuffle(all_data)
split_idx = int(len(all_data) * 0.8)
train_data = all_data[:split_idx]
val_data = all_data[split_idx:]

def process_set(data_list, subset):
    # Track copies to prevent filename collisions during oversampling
    perfect_counter = 0 
    
    for img_path, xml_path, is_perfect in data_list:
        if is_perfect:
            # Handle Perfect Boards (Background Images)
            img_filename = f"perfect_board_{perfect_counter}.jpg"
            perfect_counter += 1
            yolo_img_path = os.path.join(YOLO_DIR, f"images/{subset}", img_filename)
            shutil.copy(img_path, yolo_img_path)
            # YOLO simply needs the image to exist without a corresponding .txt file
            # to treat it as a perfect, zero-defect background image.
            
        else:
            # Handle Faulty Boards
            tree = ET.parse(xml_path)
            root = tree.getroot()
            size = root.find('size')
            w, h = int(size.find('width').text), int(size.find('height').text)
            
            img_filename = os.path.basename(img_path)
            txt_filename = img_filename.replace('.jpg', '.txt').replace('.png', '.txt')
            
            yolo_label_path = os.path.join(YOLO_DIR, f"labels/{subset}", txt_filename)
            yolo_img_path = os.path.join(YOLO_DIR, f"images/{subset}", img_filename)
            
            with open(yolo_label_path, 'w') as out_file:
                for obj in root.iter('object'):
                    cls_name = obj.find('name').text.lower().replace(" ", "_")
                    if cls_name not in CLASS_MAP: continue
                    cls_id = CLASS_MAP[cls_name]
                    
                    xmlbox = obj.find('bndbox')
                    b = (float(xmlbox.find('xmin').text), float(xmlbox.find('xmax').text), 
                         float(xmlbox.find('ymin').text), float(xmlbox.find('ymax').text))
                    bb = convert_to_yolo_format((w, h), b)
                    out_file.write(f"{cls_id} {' '.join([str(a) for a in bb])}\n")
                    
            shutil.copy(img_path, yolo_img_path)

print("Processing Training Data...")
process_set(train_data, "train")
print("Processing Validation Data...")
process_set(val_data, "val")
print(f"Dataset ready at {YOLO_DIR}")