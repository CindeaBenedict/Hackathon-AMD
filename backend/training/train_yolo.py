from ultralytics import YOLO
import torch

def main():
    # 1. Verify ROCm/GPU availability
    print(f"CUDA/ROCm Available: {torch.cuda.is_available()}")
    if torch.cuda.is_available():
        print(f"Device Name: {torch.cuda.get_device_name(0)}")
        
    print("\nInitializing YOLOv11 Extra-Large...")
    
    # 2. Load the Extra-Large YOLOv11 model
    # The 'x' model has the most parameters and highest accuracy capability.
    model = YOLO("yolo11x.pt") 

    # 3. Unleash the VRAM
    print("Starting training pipeline...")
    results = model.train(
        data="/workspace/pcb_data.yaml", # The YAML file we created in the last step
        epochs=150,                      # 150 is usually the sweet spot for PCB datasets
        imgsz=1024,                      # Massive resolution to catch tiny spurs/mousebites
        batch=64,                        # Devours VRAM. If it crashes, drop to 32. If it doesn't, try 128!
        device=0,                        # Target your main GPU
        workers=16,                      # Uses your CPU cores to feed data to the GPU fast enough
        optimizer="AdamW",               # Best optimizer for complex object detection
        patience=30,                     # Early stopping if the model stops improving for 30 epochs
        save=True,                       # Save the best weights
        save_period=10,                  # Save a backup checkpoint every 10 epochs
        project="/workspace/runs",       # Where to save the output
        name="pcb_yolo_1024"             # Folder name for this specific training run
    )
    
    print("\nTraining Complete! Best model saved to: /workspace/runs/pcb_yolo_1024/weights/best.pt")

if __name__ == "__main__":
    main()