import pandas as pd

from torch.utils import data
from torchvision import transforms as T
from torchvision.datasets import ImageFolder
from PIL import Image
import torch
import os
import random
from shutil import copyfile, copy2


class CelebA(data.Dataset):
    """
    Dataset class for the CelebA dataset.
    """

    def __init__(self, image_dir, attr_path, selected_attrs, transform, mode):
        """Initialize and preprocess the CelebA dataset."""
        self.image_dir = image_dir
        self.attr_path = attr_path
        self.selected_attrs = selected_attrs
        self.transform = transform
        self.mode = mode
        self.train_dataset = []
        self.test_dataset = []
        self.attr2idx = {}
        self.idx2attr = {}
        self.preprocess()

        if mode == 'train':
            self.num_images = len(self.train_dataset)
        else:
            self.num_images = len(self.test_dataset)

    def preprocess(self):
        """
        Preprocess the CelebA attribute file.
        """
        lines = [line.rstrip() for line in open(self.attr_path, 'r')]
        all_attr_names = lines[1].split()
        for i, attr_name in enumerate(all_attr_names):
            self.attr2idx[attr_name] = i
            self.idx2attr[i] = attr_name

        lines = lines[2:]
        random.seed(1234)
        random.shuffle(lines)
        for i, line in enumerate(lines):
            split = line.split()
            filename = split[0]
            values = split[1:]

            label = []
            for attr_name in self.selected_attrs:
                idx = self.attr2idx[attr_name]
                label.append(values[idx] == '1')

            if (i + 1) < 2000:
                self.test_dataset.append([filename, label])
            else:
                self.train_dataset.append([filename, label])

        print('Finished preprocessing the CelebA dataset...')

    def __getitem__(self, index):
        """
        Return one image and its corresponding attribute label.
        """
        dataset = self.train_dataset if self.mode == 'train' else self.test_dataset
        filename, label = dataset[index]
        image = Image.open(os.path.join(self.image_dir, filename))
        return self.transform(image), torch.FloatTensor(label)

    def __len__(self):
        """
        Return the number of images.
        """
        return self.num_images


# class CelebAHQ(data.Dataset):
#     """
#     Dataset class for the CelebA dataset.
#     """
#
#     def __init__(self, image_dir, transform, mode):
#         """Initialize and preprocess the CelebA dataset."""
#         self.image_dir = image_dir
#         self.transform = transform
#         self.mode = mode
#         self.train_dataset = []
#         self.test_dataset = []
#
#         self.preprocess()
#
#         if mode == 'train':
#             self.num_images = len(self.train_dataset)
#         else:
#             self.num_images = len(self.test_dataset)
#
#     def preprocess(self):
#         """
#         Preprocess the CelebA attribute file.
#         """
#         lines = [f for f in os.listdir(self.image_dir)]
#         random.seed(1234)
#         random.shuffle(lines)
#         for i, line in enumerate(lines):
#             if (i + 1) < 2000:
#                 self.test_dataset.append([line, random.choice(lines)])
#             else:
#                 self.train_dataset.append([line, random.choice(lines)])
#
#         print('Finished preprocessing the CelebA dataset...')
#
#     def __getitem__(self, index):
#         """
#         Return one image and its corresponding attribute label.
#         """
#         dataset = self.train_dataset if self.mode == 'train' else self.test_dataset
#         source, reference = dataset[index]
#         source_image = Image.open(os.path.join(self.image_dir, source))
#         reference_image = Image.open(os.path.join(self.image_dir, reference))
#         return self.transform(source_image), self.transform(reference_image)
#
#     def __len__(self):
#         """
#         Return the number of images.
#         """
#         return self.num_images


# def get_loader(image_dir, attr_path, selected_attrs, crop_size=178, image_size=128,
#                batch_size=16, dataset='CelebA', mode='train', num_workers=1):
#     """
#     Build and return a data loader.
#     """
#     transform = []
#     if mode == 'train':
#         transform.append(T.RandomHorizontalFlip())
#     transform.append(T.CenterCrop(crop_size))
#     transform.append(T.Resize(image_size))
#     transform.append(T.ToTensor())
#     transform.append(T.Normalize(mean=(0.5, 0.5, 0.5), std=(0.5, 0.5, 0.5)))
#     transform = T.Compose(transform)
#
#     if dataset == 'CelebA':
#         # dataset = CelebAHQ(image_dir, transform, mode)
#         dataset = CelebA(image_dir, attr_path, selected_attrs, transform, mode)
#     elif dataset == 'RaFD':
#         dataset = ImageFolder(image_dir, transform)
#
#     data_loader = data.DataLoader(dataset=dataset,
#                                   batch_size=batch_size,
#                                   shuffle=(mode == 'train'),
#                                   num_workers=num_workers)
#     return data_loader


def get_loader(image_dir, crop_size=178, image_size=128,
               batch_size=16, mode='train', num_workers=1):
    """
    Build and return a data loader.
    """
    transform = []
    if mode == 'train':
        transform.append(T.RandomHorizontalFlip())
    transform.append(T.CenterCrop(crop_size))
    transform.append(T.Resize(image_size))
    transform.append(T.ToTensor())
    transform.append(T.Normalize(mean=(0.5, 0.5, 0.5), std=(0.5, 0.5, 0.5)))
    transform = T.Compose(transform)
    #
    # if dataset == 'CelebA':
    #     # dataset = CelebAHQ(image_dir, transform, mode)
    #     dataset = CelebA(image_dir, attr_path, selected_attrs, transform, mode)
    # else:
    #     dataset = ImageFolder(image_dir, transform)

    dataset = ImageFolder(image_dir, transform)
    data_loader = data.DataLoader(dataset=dataset,
                                  batch_size=batch_size,
                                  shuffle=(mode == 'train'),
                                  num_workers=num_workers)
    return data_loader


def process_celeba():
    """
    split aligned celeba images into multiple domain folders
    :return:
    """
    csv_file = "/data/datasets/CelebA/Anno/list_attr_celeba.txt"
    attrs_df = pd.read_csv(csv_file, delim_whitespace=True, skiprows=2)

    # # print(attrs_df.loc[0, :])
    # for index, row in attrs_df.iterrows():
    #     try:
    #         print(row[0])
    #         # print(row[20])
    #     except Exception as e:
    #         print(str(e))
    total = len(attrs_df)
    for i in range(total):
        if i < int(0.7 * total):
            target = "train"
        else:
            target = "test"
        base_path = "/data/datasets/CelebA/Img/img_align_celeba"
        male_path = "/data/datasets/celeba/{}/male".format(target)
        female_path = "/data/datasets/celeba/{}/female".format(target)

        if not os.path.exists(male_path):
            os.mkdir(male_path)

        if not os.path.exists(female_path):
            os.mkdir(female_path)

        src_file = os.path.join(base_path, attrs_df.iloc[i, 0])
        male = attrs_df.iloc[i, 21]
        if male == 1:
            # male
            # copy2('/src/file.ext', '/dst/dir')
            copy2(src_file, male_path)
        else:
            # female
            copy2(src_file, female_path)
        print(attrs_df.iloc[i, 0])
        print(type(male))


    return


def getFaceBox(net, frame, conf_threshold=0.7):
    frameOpencvDnn = frame.copy()
    frameHeight = frameOpencvDnn.shape[0]
    frameWidth = frameOpencvDnn.shape[1]
    blob = cv.dnn.blobFromImage(frameOpencvDnn, 1.0, (300, 300), [104, 117, 123], True, False)

    net.setInput(blob)
    detections = net.forward()
    bboxes = []
    for i in range(detections.shape[2]):
        confidence = detections[0, 0, i, 2]
        if confidence > conf_threshold:
            x1 = int(detections[0, 0, i, 3] * frameWidth)
            y1 = int(detections[0, 0, i, 4] * frameHeight)
            x2 = int(detections[0, 0, i, 5] * frameWidth)
            y2 = int(detections[0, 0, i, 6] * frameHeight)
            bboxes.append([x1, y1, x2, y2])
            cv.rectangle(frameOpencvDnn, (x1, y1), (x2, y2), (0, 255, 0), int(round(frameHeight/150)), 8)
    return frameOpencvDnn, bboxes


genderProto = "gender_deploy.prototxt"
genderModel = "gender_net.caffemodel"
genderList = ['Male', 'Female']

blob = cv.dnn.blobFromImage(face, 1, (227, 227), MODEL_MEAN_VALUES, swapRB=False)
genderNet.setInput(blob)
genderPreds = genderNet.forward()
gender = genderList[genderPreds[0].argmax()]
print("Gender Output : {}".format(genderPreds))
print("Gender : {}".format(gender))

if __name__ == "__main__":
    process_celeba()
