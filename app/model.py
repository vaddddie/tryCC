import sys
import os
sys.path.append(os.path.abspath('face_parsing'))

import cv2
import numpy as np
import torch
from face_parsing.model import BiSeNet
from torchvision import transforms


def load_model():
    n_classes = 19
    net = BiSeNet(n_classes=n_classes)
    net.load_state_dict(torch.load('face_parsing/res/cp/79999_iter.pth', map_location='cpu'))
    net.eval()
    return net

# Получение маски лица
def get_face_mask(net, image):
    to_tensor = transforms.Compose([
        transforms.ToTensor(),
        transforms.Normalize([0.5]*3, [0.5]*3)
    ])
    h, w, _ = image.shape
    resized = cv2.resize(image, (512, 512))
    tensor = to_tensor(resized).unsqueeze(0)
    with torch.no_grad():
        out = net(tensor)[0]
        parsing = out.squeeze(0).cpu().numpy().argmax(0)
    parsing = cv2.resize(parsing.astype(np.uint8), (w, h), interpolation=cv2.INTER_NEAREST)
    return parsing

# Окрашивание волос
def recolor_hair(image, mask, target_color=(255, 0, 255)):
    color_layer = np.zeros_like(image)
    color_layer[:, :] = target_color
    hair_mask = (mask == 17).astype(np.uint8)  # 17 — это волосы
    hair_mask = cv2.GaussianBlur(hair_mask.astype(np.float32), (11,11), 0)
    hair_mask = np.expand_dims(hair_mask, axis=2)
    blended = image * (1 - hair_mask) + color_layer * hair_mask
    return blended.astype(np.uint8)
