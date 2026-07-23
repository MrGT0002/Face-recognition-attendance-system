"""
Face Recognition Trainer Module
Trains OpenCV LBPH (Local Binary Patterns Histograms) Face Recognizer on student face images.
"""

import cv2
import numpy as np
import os
from pathlib import Path


def load_student_images(datasets_path):
    """
    Load all student face images from datasets/students/ directory.
    
    This function scans the datasets/students/ directory structure:
    datasets/students/
        ├── student_id_1/
        │   ├── image1.jpg
        │   ├── image2.jpg
        │   └── ...
        ├── student_id_2/
        │   ├── image1.jpg
        │   └── ...
    
    It loads images and assigns numeric labels based on student_id.
    Each student gets a unique numeric label.
    
    Args:
        datasets_path (str or Path): Path to datasets/students/ directory
        
    Returns:
        tuple: (images, labels, label_to_student_id)
            - images (list): List of grayscale image arrays
            - labels (list): List of integer labels corresponding to each image
            - label_to_student_id (dict): Mapping from numeric label to student_id
        None: If dataset is empty or cannot be loaded
        
    Example:
        images, labels, mapping = load_student_images("datasets/students")
        if images:
            print(f"Loaded {len(images)} images for {len(set(labels))} students")
    """
    # Convert string path to Path object for easier manipulation
    datasets_path = Path(datasets_path)
    students_dir = datasets_path / "students"
    
    # Check if students directory exists
    if not students_dir.exists():
        print(f"Error: Directory {students_dir} does not exist.")
        return None
    
    # Lists to store images and their corresponding labels
    images = []
    labels = []
    
    # Dictionary to map numeric labels to student IDs
    # Example: {0: "12345", 1: "12346", ...}
    label_to_student_id = {}
    
    # Counter for assigning numeric labels
    # Each student gets a unique integer label (0, 1, 2, ...)
    current_label = 0
    
    # Iterate through each student directory
    # Each subdirectory in students/ represents one student
    for student_dir in sorted(students_dir.iterdir()):
        # Skip if not a directory
        if not student_dir.is_dir():
            continue
        
        # Get student ID from directory name
        student_id = student_dir.name
        
        # Assign numeric label to this student
        label_to_student_id[current_label] = student_id
        
        # Count images for this student
        student_image_count = 0
        
        # Iterate through all image files in the student's directory
        for image_file in sorted(student_dir.glob("*.jpg")):
            # Read the image file using OpenCV
            # cv2.IMREAD_GRAYSCALE ensures image is loaded as grayscale
            image = cv2.imread(str(image_file), cv2.IMREAD_GRAYSCALE)
            
            # Check if image was loaded successfully
            if image is None:
                print(f"Warning: Could not load image {image_file}")
                continue
            
            # Add image and label to training data
            images.append(image)
            labels.append(current_label)
            student_image_count += 1
        
        # Only increment label if student has images
        if student_image_count > 0:
            current_label += 1
            print(f"Loaded {student_image_count} images for student ID: {student_id}")
        else:
            # Remove label mapping if no images found for this student
            if current_label in label_to_student_id:
                del label_to_student_id[current_label]
            print(f"Warning: No images found for student ID: {student_id}")
    
    # Check if any images were loaded
    if len(images) == 0:
        print("Error: No images found in dataset. Cannot train model.")
        return None
    
    # Convert lists to numpy arrays for efficient processing
    # OpenCV face recognizer requires numpy arrays
    images = np.array(images, dtype=object)
    labels = np.array(labels, dtype=np.int32)
    
    print(f"\n=== Dataset Summary ===")
    print(f"Total images loaded: {len(images)}")
    print(f"Number of students: {len(label_to_student_id)}")
    print(f"Label mapping: {label_to_student_id}")
    
    return images, labels, label_to_student_id


def prepare_training_data(datasets_path):
    """
    Prepare training data by loading and validating student images.
    
    This function loads images and ensures they are in the correct format
    for OpenCV LBPH face recognizer training.
    
    Args:
        datasets_path (str or Path): Path to datasets/students/ directory
        
    Returns:
        tuple: (images, labels, label_mapping) same as load_student_images()
        None: If preparation fails
    """
    # Load images and labels from dataset
    result = load_student_images(datasets_path)
    
    if result is None:
        return None
    
    images, labels, label_mapping = result
    
    # Validate that we have images and labels
    if len(images) == 0 or len(labels) == 0:
        print("Error: Empty training dataset.")
        return None
    
    # Ensure labels and images have same length
    if len(images) != len(labels):
        print("Error: Mismatch between number of images and labels.")
        return None
    
    # Verify all images are grayscale (2D arrays)
    # Grayscale images should have shape (height, width)
    for i, image in enumerate(images):
        if len(image.shape) != 2:
            print(f"Warning: Image {i} is not grayscale. Converting...")
            # Convert to grayscale if needed
            if len(image.shape) == 3:
                images[i] = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    
    return images, labels, label_mapping


def train_lbph_recognizer(images, labels, neighbors=8, grid_x=8, grid_y=8):
    """
    Train OpenCV LBPH Face Recognizer on provided images and labels.
    
    LBPH (Local Binary Patterns Histograms) is a face recognition algorithm
    that analyzes local patterns in face images. It's robust to lighting
    variations and suitable for training with multiple images per person.
    
    Args:
        images (numpy.ndarray): Array of grayscale face images
        labels (numpy.ndarray): Array of integer labels corresponding to images
        neighbors (int): Number of neighbors for LBP (default: 8)
            - Controls the quality of LBP pattern
            - Higher values = more detailed patterns, slower processing
        grid_x (int): Horizontal grid size for histogram (default: 8)
        grid_y (int): Vertical grid size for histogram (default: 8)
            - Divides face into grid cells for analysis
            - Higher values = more detailed analysis
    
    Returns:
        cv2.face.LBPHFaceRecognizer: Trained LBPH face recognizer model
        None: If training fails
        
    Example:
        recognizer = train_lbph_recognizer(images, labels)
        if recognizer:
            print("Model trained successfully")
    """
    # Validate inputs
    if images is None or labels is None:
        print("Error: Images or labels are None.")
        return None
    
    if len(images) == 0 or len(labels) == 0:
        print("Error: Empty training data.")
        return None
    
    try:
        # Create LBPH Face Recognizer object
        # LBPH is one of OpenCV's face recognition algorithms
        # It's based on Local Binary Patterns Histograms
        recognizer = cv2.face.LBPHFaceRecognizer_create(
            radius=1,           # Radius for LBP pattern (1 pixel)
            neighbors=neighbors,  # Number of neighbors in LBP pattern
            grid_x=grid_x,      # Number of horizontal grid cells
            grid_y=grid_y       # Number of vertical grid cells
        )
        
        print("\n=== Training LBPH Face Recognizer ===")
        print(f"Training on {len(images)} images...")
        print(f"Number of unique labels (students): {len(np.unique(labels))}")
        
        # Train the recognizer
        # This process analyzes all images and builds a model that can
        # recognize faces based on learned patterns
        recognizer.train(images, labels)
        
        print("Training completed successfully!")
        
        return recognizer
        
    except Exception as e:
        print(f"Error during training: {e}")
        return None


def save_model(recognizer, model_path, label_mapping):
    """
    Save trained LBPH model and label mapping to files.
    """
    if recognizer is None:
        print("Error: Recognizer model is None. Cannot save.")
        return False

    try:
        model_path = Path(model_path)
        model_path.parent.mkdir(parents=True, exist_ok=True)

        # 1️⃣ Save LBPH model
        recognizer.save(str(model_path))
        print(f"Model saved to: {model_path}")

        # 2️⃣ Save label mapping for recognizer (REQUIRED)
        labels_npy_path = model_path.parent / "labels.npy"
        np.save(labels_npy_path, label_mapping)
        print(f"Label mapping saved to: {labels_npy_path}")

        # 3️⃣ Save human-readable mapping (optional, good for debugging)
        mapping_txt_path = model_path.parent / "label_mapping.txt"
        with open(mapping_txt_path, "w") as f:
            f.write("Label to Student ID Mapping\n")
            f.write("=" * 40 + "\n")
            for label, student_id in sorted(label_mapping.items()):
                f.write(f"{label} -> {student_id}\n")

        print(f"Readable label mapping saved to: {mapping_txt_path}")

        return True

    except Exception as e:
        print(f"Error saving model: {e}")
        return False



def train_model(datasets_path="datasets", model_path="models/lbph_model.yml"):
    """
    Complete training pipeline: load data, train model, and save.
    
    This is the main function that orchestrates the entire training process:
    1. Load student images from datasets/students/
    2. Prepare training data (images and labels)
    3. Train LBPH face recognizer
    4. Save trained model to file
    
    Args:
        datasets_path (str): Path to datasets directory (default: "datasets")
        model_path (str): Path to save trained model (default: "models/lbph_model.yml")
        
    Returns:
        tuple: (recognizer, label_mapping) if successful
        None: If training fails
        
    Example:
        result = train_model()
        if result:
            recognizer, mapping = result
            print("Training complete!")
    """
    # Get project root directory
    project_root = Path(__file__).parent.parent
    
    # Construct full paths
    datasets_full_path = project_root / datasets_path
    model_full_path = project_root / model_path
    
    print("=== Starting Face Recognition Model Training ===\n")
    print(f"Datasets path: {datasets_full_path}")
    print(f"Model save path: {model_full_path}\n")
    
    # Step 1: Load and prepare training data
    print("Step 1: Loading training images...")
    training_data = prepare_training_data(datasets_full_path)
    
    if training_data is None:
        print("Training failed: Could not load training data.")
        return None
    
    images, labels, label_mapping = training_data
    
    # Step 2: Train LBPH recognizer
    print("\nStep 2: Training LBPH Face Recognizer...")
    recognizer = train_lbph_recognizer(images, labels)
    
    if recognizer is None:
        print("Training failed: Could not train recognizer.")
        return None
    
    # Step 3: Save trained model
    print("\nStep 3: Saving trained model...")
    success = save_model(recognizer, model_full_path, label_mapping)
    
    if not success:
        print("Training failed: Could not save model.")
        return None
    
    print("\n=== Training Pipeline Complete ===")
    print(f"Model successfully trained and saved to: {model_full_path}")
    
    return recognizer, label_mapping


# Example usage and testing
if __name__ == "__main__":
    # Run complete training pipeline
    print("Starting face recognition model training...\n")
    
    result = train_model()
    
    if result:
        recognizer, label_mapping = result
        print("\nTraining successful!")
        print(f"Label mapping: {label_mapping}")
    else:
        print("\nTraining failed. Please check the error messages above.")
