---
tags:
  - image preprocessing
  - scientific computing
  - wildlife classification
  - VGGNet
  - transfer learning
  - data augmentation
  - deep learning
  - YOLOv8
  - ResNet
  - DenseNet
---
#### **1. Introduction**

- **Objective**: Evaluate and compare deep learning models (YOLOv8, DenseNet, ResNet, VGGNet) for classifying endangered wildlife species using a custom dataset.
- **Key Challenges**:
    - Manual wildlife monitoring is labor-intensive and error-prone.
    - Deep learning offers automation potential but requires robust evaluation on niche datasets.
- **Significance**: Highlights YOLOv8's efficiency in image classification, despite being traditionally used for object detection.

---

#### **2. Dataset and Preprocessing**

1. **Dataset Details**:
    
    - **Species**: 23 endangered species, covering mammals, reptiles, and amphibians (e.g., Red Panda, Bengal Tiger, Snow Leopard).
    - **Source**: Images curated from online repositories like iNaturalist and ZooChat.
    - **Size**: 575 images (25 per species), balanced to avoid bias.
2. **Preprocessing Steps**:
    
    - **Aspect Ratio Standardization**: Images resized to 400x400 resolution with 1:1 aspect ratio.
    - **Data Normalization**: Scaled to enhance model convergence.
    - **Splitting**: Dataset divided into 80% training and 20% validation sets.
    - **Data Augmentation**: Techniques like random shearing, zooming, flipping, rotation, and shifting applied to improve generalization.

---

#### **3. Methodology**

1. **Transfer Learning**:
    
    - Utilized pre-trained models for feature extraction; only final layers fine-tuned.
    - Benefits: Reduced training time and computational costs.
2. **Models Compared**:
    
    - **DenseNet**: Deep network with dense layer connections for efficient feature reuse.
    - **ResNet**: Employs residual blocks for stable training of deep architectures.
    - **VGGNet**: Simple, stacked convolutional layers; computationally expensive.
    - **YOLOv8**: Advanced object detection framework; adapted for classification using anchor-free detection and CSPNet for feature efficiency.
3. **Hyperparameters**:
    
    - Optimizer: AdamW.
    - Loss Functions: Categorical Cross-Entropy (CCE) for multi-class classification.
    - Training Configuration: 100 epochs, batch size of 32, early stopping.

---

#### **4. Performance Metrics**

- **Accuracy**: Measures correct classifications over total samples.
- **Precision and Recall**: Indicate specificity and sensitivity, respectively.
- **F1-Score**: Harmonic mean of precision and recall.
- **Loss**: Tracks error reduction during training.

---

#### **5. Results**

1. **YOLOv8**:
    
    - **Performance**:
        - Training accuracy: 97.39%; Validation accuracy: 99.13%.
        - F1-score: Training: 96.50%; Validation: 99.12%.
    - **Key Strengths**:
        - Fast convergence with low loss.
        - Effective for classification due to advanced architecture (CSPNet and PANet).
2. **DenseNet**:
    
    - **Performance**:
        - DenseNet-169: Validation accuracy: 93.91%; F1-score: 93.95%.
        - DenseNet-201: Validation accuracy: 92.17%; F1-score: 92.22%.
    - Robust feature reuse but computationally expensive.
3. **ResNet**:
    
    - **Performance**:
        - ResNet-101 V2: Validation accuracy: 92.17%; F1-score: 92.09%.
        - ResNet-152 V2: Validation accuracy: 93.04%; F1-score: 93.22%.
    - Consistent generalization and minimal overfitting.
4. **VGGNet**:
    
    - **Performance**:
        - VGG-16: Validation accuracy: 33.91%; F1-score: 28.65%.
        - VGG-19: Validation accuracy: 33.04%; F1-score: 31.19%.
    - Underperformed due to outdated architecture and limited depth.

---

#### **6. Discussion**

- YOLOv8 emerged as the most effective model, outperforming classification-specific architectures.
- DenseNet and ResNet offered competitive performance but lacked the adaptability of YOLOv8.
- VGGNet struggled due to its simplicity and computational inefficiency.

---

#### **7. Conclusion**

- **Findings**:
    - YOLOv8 demonstrates strong potential for wildlife classification tasks, extending beyond its primary design for detection.
    - DenseNet and ResNet remain viable options for similar applications, albeit with slightly lower performance.
- **Future Work**:
    - Explore ensemble methods combining strengths of multiple architectures.
    - Integrate real-time monitoring for proactive conservation efforts.