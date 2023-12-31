import os
import codecs
from torchtext import data


class MMHS50K(data.Dataset):

    @staticmethod
    def sort_key(ex):
        return len(ex.text)

    def __init__(self, text_field, label_field, id_field, path=None, split_name = None, train_vocab_path = None, examples=None, **kwargs):
        """Create an Emotion Dataset instance given a path and fields.
        Arguments:
            text_field: The field that will be used for text data.
            label_field: The field that will be used for label data.
            path: Path to the data file.
            examples: The examples contain all the data.
            Remaining keyword arguments: Passed to the constructor of
                data.Dataset.
        """
        # text_field.preprocessing = data.Pipeline(clean_str)
        fields = [('text', text_field), ('label', label_field) , ('id', id_field)]
        if examples is None:
            path = self.dirname if path is None else path
            examples = []
            with codecs.open(os.path.join(path, split_name),'r','utf8') as f:
                lines = []
                for line in f:
                    if len(line.split(',')) >= 2:
                        lines.append(line)
            examples += [
                data.Example.fromlist([line.split(',')[2], line.split(',')[1], line.split(',')[0]], fields) for line in lines]

        super(MMHS50K, self).__init__(examples, fields, **kwargs)

    @classmethod
    def splits(cls, text_field, label_field, id_field, split_folder, split_name, shuffle=True ,root='.', **kwargs):
        """Create dataset objects for splits of the MR dataset.
        Arguments:
            text_field: The field that will be used for the sentence.
            label_field: The field that will be used for label data.
            dev_ratio: The ratio that will be used to get split validation dataset.
            shuffle: Whether to shuffle the data before split.
            root: The root directory that the dataset's zip archive will be
                expanded into; therefore the directory in whose trees
                subdirectory the data files will be stored.
            train: The filename of the train data. Default: 'train.txt'.
            Remaining keyword arguments: Passed to the splits method of
                Dataset.
        """
        path = "../../../datasets/HateSPic/MMHS50K/lstm_data_classes/" + split_folder + "/"
        print "Split:  "  + path
        test_examples = cls(text_field, label_field, id_field, path=path, split_name=split_name, **kwargs).examples

        # LOAD TRAIN VOCAB SINCE I NEED IT TO RUN THE MODEL
        # ANNOTATED
        # fields = [('text', text_field), ('label', label_field), ('id', id_field)]
        # train_examples = []
        # train_path = "../../../datasets/HateSPic/lstm_data/annotated/"
        # with codecs.open(os.path.join(train_path, 'tweets.hate'), 'r', 'utf8') as f:
        #     train_examples += [
        #         data.Example.fromlist([line, 'hate','0'], fields) for line in f]
        # with codecs.open(os.path.join(train_path, 'tweets.nothate'), 'r', 'utf8') as f:
        #     train_examples += [
        #         data.Example.fromlist([line, 'nothate','0'], fields) for line in f]
        # with codecs.open(os.path.join(train_path, 'val_tweets.hate'), 'r', 'utf8') as f:
        #     train_examples += [
        #         data.Example.fromlist([line, 'hate','0'], fields) for line in f]
        # with codecs.open(os.path.join(train_path, 'val_tweets.nothate'), 'r', 'utf8') as f:
        #     train_examples += [
        #         data.Example.fromlist([line, 'nothate','0'], fields) for line in f]

        # LOAD TRAIN VOCAB SINCE I NEED IT TO RUN THE MODEL
        # MMHS10K
        fields = [('text', text_field), ('label', label_field), ('id', id_field)]
        train_examples = []

        train_path = "../../../datasets/HateSPic/MMHS50K/lstm_data_classes/"

        with codecs.open(os.path.join(train_path, 'tweets.train'), 'r', 'utf8') as f:
            train_examples += [
                data.Example.fromlist([line.split(',')[2], line.split(',')[1],'0'], fields) for line in f]

        with codecs.open(os.path.join(train_path, 'tweets.val'), 'r', 'utf8') as f:
            train_examples += [
                data.Example.fromlist([line.split(',')[2], line.split(',')[1],'0'], fields) for line in f]


        #random.shuffle(test_examples)
        print('num train samples (for vocab initialization):',len(train_examples))
        print('test test samples:',len(test_examples))
        return (cls(text_field, label_field, id_field, examples=train_examples),
                cls(text_field, label_field, id_field, examples=test_examples),)
# load ED dataset
def load_MMHS50K(text_field, label_field, id_field, batch_size = 1, split_folder='test', split_name = 'tweets.test'):
    print('loading data')
    train_data, test_data = MMHS50K.splits(text_field, label_field, id_field, split_folder, split_name)
    text_field.build_vocab(train_data, train_data)
    label_field.build_vocab(train_data, train_data)
    print('Size vocab: ' + str(len(text_field.vocab.itos)))
    print('building batches')
    test_iter, aux_iter = data.Iterator.splits(
        (test_data, train_data), batch_sizes=(batch_size, batch_size, batch_size), repeat=False, shuffle=False, device = -1)

    return test_iter

