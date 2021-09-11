import os
from collections import OrderedDict

from dassl.data.datasets import DATASET_REGISTRY, Datum, DatasetBase
from dassl.utils import listdir_nohidden

from .oxford_pets import OxfordPets

TO_BE_IGNORED = ['new_val_prep.sh', 'train1.txt', 'train.txt']


@DATASET_REGISTRY.register()
class ImageNet(DatasetBase):

    dataset_dir = 'imagenet'

    def __init__(self, cfg):
        root = os.path.abspath(os.path.expanduser(cfg.DATASET.ROOT))
        self.dataset_dir = os.path.join(root, self.dataset_dir)
        self.image_dir = os.path.join(self.dataset_dir, 'images')

        text_file = os.path.join(self.dataset_dir, 'classnames.txt')
        classnames = self.read_classnames(text_file)
        
        train = self.read_data(classnames, 'train')
        # Follow standard practice to perform evaluation on the val set
        # Also used as the val set (so evaluate the last-step model)
        test = self.read_data(classnames, 'val')
        
        num_shots = cfg.DATASET.NUM_SHOTS
        train = self.generate_fewshot_dataset(train, num_shots=num_shots)

        super().__init__(train_x=train, val=test, test=test)
    
    @staticmethod
    def read_classnames(text_file):
        """Return a dictionary containing
        key-value pairs of <folder name>: <class name>.
        """
        classnames = OrderedDict()
        with open(text_file, 'r') as f:
            lines = f.readlines()
            for line in lines:
                line = line.strip().split(' ')
                folder = line[0]
                classname = ' '.join(line[1:])
                classnames[folder] = classname
        return classnames
    
    def read_data(self, classnames, split_dir):
        split_dir = os.path.join(self.image_dir, split_dir)
        folders = listdir_nohidden(split_dir, sort=True)
        folders = [f for f in folders if f not in TO_BE_IGNORED]
        items = []

        for label, folder in enumerate(folders):
            imnames = listdir_nohidden(os.path.join(split_dir, folder))
            classname = classnames[folder]
            for imname in imnames:
                impath = os.path.join(split_dir, folder, imname)
                item = Datum(
                    impath=impath,
                    label=label,
                    classname=classname
                )
                items.append(item)
        
        return items
