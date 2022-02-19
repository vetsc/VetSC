# encoding=utf-8

from operator import concat
from pprint import pprint
import os
import pickle as pkl

import numpy as np
from tqdm import tqdm


class SmartContractAnalyzer:
    def __init__(self, path, embedding_strategy = "glove", seed=123, re_generate=False):
        np.random.seed(seed)
        self.path = path
        self.busi_model = {
            "auction": ["bid", "cancel", "finalize"],
            "voting": ["vote"],
            "wallet": ["deposit", "withdraw", "transfer"],
            "gambling": ["buy", "refund", "draw"],
            "trading": ["buy", "sell"],
            # "gambling dice": ["roll"]
            "dice": ["roll"]

        }
        self.label2model = {'trade': "trading", 
            'lottery': "gambling", 
            'wallet': "wallet", 
            'vote': "voting", 
            'auction': "auction", 
            # 'dice': "gambling dice"
            'dice': "dice"
        }
        self.input_text = self.raw_data_to_dict()

        self.embedding_strategy = embedding_strategy
        if self.embedding_strategy == "glove":
            self.word_vocab = self.get_word_vocab()
            self.word2vec = self.glove_word_embedding(re_generate=re_generate)
        
        self.get_model_prediction()

    def raw_data_to_dict(self):
        files = os.listdir(self.path)
        input_text = {}
        key_str_1 = "button"
        key_str_2 = "context"
        key_str_3 = "semantic"
        for file_ in files:
            key_str = file_.split('(')[0].strip()
            category_str = file_.split('(')[1].strip().replace(').txt', '')
            # 1. label
            input_text[key_str] = {}
            input_text[key_str]['label'] = self.label2model[category_str]
            # 2. buttons and contexts
            with open(self.path + file_, "r") as f:
                context_read = 0
                button_read = 0
                for line in f:
                    line = line.replace("\n", "")
                    if '[' not in line and 'http' not in line and line.strip() != '':
                        if key_str_1 in line and key_str_2 not in line and key_str_3 not in line:
                            button_read = 1
                        elif key_str_2 in line:
                            context_read = 1
                        elif key_str_3 in line:
                            pass
                        else:
                            raise IOError("Wrong input format!")
    
                    if '[' in line and button_read == 1:
                        input_text[key_str]['button'] = self.preprocessRawString(line, sep_str='@').split('@')
                        button_read = 2
                    if '[' in line and context_read == 1:
                        input_text[key_str]['context'] = self.preprocessRawString(line)
                        context_read = 2
            # make sure buttons and contexts both exist.
            if button_read != 2 or context_read != 2:
                print(button_read)
                raise IOError(f"Wrong input format in {file_}!")

        return input_text

    def preprocessRawString(self, input_, sep_str=' '):
        input_ = ''.join(x for x in input_ if x.encode('utf-8').isalpha() or x in ' ]')
        return sep_str.join(x.strip() for x in input_.lower().strip(' ]').split(']'))

    def get_word_vocab(self):
        word_vocab = ""
        for k in self.input_text:
            word_vocab = word_vocab + " " + " ".join(self.input_text[k]['button'])
            word_vocab = word_vocab + " " + self.input_text[k]['context']
            word_vocab = word_vocab + " " + self.input_text[k]['label']
        for k in self.busi_model:
            word_vocab = word_vocab + " " + k
            word_vocab = word_vocab + " " + " ".join(self.busi_model[k])
        return set(word_vocab.strip().split())

    def glove_word_embedding(self, glove_path, re_generate = False):
        if hasattr(self, "word_vocab") is not True:
            print(self.get_word_vocab())

        out_file = "./{}_pretrain.pkl".format(self.path.replace('/', '').replace('.', ''))
        if os.path.exists(out_file) and re_generate is not True:
            return pkl.load(open(out_file, "rb"))
    
        glove2vec = {}
        words_arr = []
        with open(glove_path, "r") as f:
            for l in tqdm(f):
                line = l.split()
                word = line[0]
                words_arr.append(word)
                vect = np.array(line[1:]).astype(np.float)
                glove2vec[word] = vect
    
        word2vec = {}
        for w in tqdm(self.word_vocab):
            if w in list(glove2vec.keys()):
                word2vec[w] = glove2vec[w]
            else:
                word2vec[w] = np.zeros(300)
    
        with open(out_file, "wb") as out_data:
            pkl.dump(word2vec, out_data)
        return word2vec
    
    def sentence_embedding(self, sentence):
        if self.embedding_strategy == "glove":
            key_words = sentence.strip().split()
            key_res = []
            for w in key_words:
                key_res.append(self.word2vec[w])
            return sum(key_res)/len(key_res)

    def weighted_average(self, a, b, p_a, p_b):
        if p_a + p_b != 1.0:
            raise RuntimeError()
        return a*p_a + b*p_b

    def embedding_for_model_prediction(self, 
            input_format = 'model', 
            context_prop = 0.4, 
            data_augmentation="0",
            mutiply_for_button_name = 0.5,
            mutiply_for_model_name = 0.5
            ):
        res_embedding = {}
        if input_format == 'model':
            for k in self.busi_model:
                res_embedding[k] = self.weighted_average(
                    self.sentence_embedding(k),
                    self.sentence_embedding(
                        " ".join(self.busi_model[k])
                        ),
                    1-context_prop,
                    context_prop
                )
        if input_format == 'data':
            button_names = []
            for k_new in self.busi_model:
                button_names.extend(self.busi_model[k_new])
            model_names = list(self.busi_model.keys())

            for k in self.input_text:
                if data_augmentation == "1":
                    context_string = self.input_text[k]['context'].split()
                    new_context_string = []
                    for index in range(len(context_string)):
                        if context_string[index] in button_names:
                            new_context_string.append(
                                " ".join(
                                [context_string[index]]*int(np.ceil(mutiply_for_button_name*len(context_string)))
                                )
                            )
                        elif context_string[index] in model_names:
                            new_context_string.append(
                                " ".join(
                                    [context_string[index]]*int(np.ceil(mutiply_for_model_name*len(context_string)))
                                    )
                                )
                        else:
                            new_context_string.append(context_string[index])
                    context_embedding = self.sentence_embedding(" ".join(new_context_string))
                else:
                    context_embedding = self.sentence_embedding(self.input_text[k]['context'])

                res_embedding[k] = self.weighted_average(
                    self.sentence_embedding(
                        " ".join(self.input_text[k]['button'])
                        ),
                    context_embedding,
                    1-context_prop,
                    context_prop
                )
        return res_embedding

    def embedding_for_button_prediction(self, input_format = 'model', context_prop = 0.4, data_augmentation="0"):
        res_embedding = {}
        if input_format == 'model':
            for k in self.busi_model:
                res_embedding[k] = {}
                for b in self.busi_model[k]:
                    res_embedding[k][b] = self.weighted_average(
                        self.sentence_embedding(b),
                        self.sentence_embedding(k),
                        1-context_prop,
                        context_prop
                    )
        if input_format == 'data':
            mutiply_for_button_name = 50
            button_names = []
            for k_new in self.busi_model:
                button_names.extend(self.busi_model[k_new])
            mutiply_for_model_name = 20
            model_names = list(self.busi_model.keys())

            for k in self.input_text:
                res_embedding[k] = {}
                if data_augmentation == "1":
                    context_string = self.input_text[k]['context'].split()
                    new_context_string = []
                    for index in range(len(context_string)):
                        if context_string[index] in button_names:
                            new_context_string.append(" ".join([context_string[index]]*mutiply_for_button_name))
                        elif context_string[index] in model_names:
                            new_context_string.append(" ".join([context_string[index]]*mutiply_for_model_name))
                        else:
                            new_context_string.append(context_string[index])
                    context_embedding = self.sentence_embedding(" ".join(new_context_string))
                else:
                    context_embedding = self.sentence_embedding(self.input_text[k]['context'])

                for b in self.input_text[k]['button']:
                    res_embedding[k][b] = self.weighted_average(
                        self.sentence_embedding(b),
                        context_embedding,
                        1-context_prop,
                        context_prop
                    )
        return res_embedding

    @staticmethod
    def cosSim(vec1, vec2):
        return np.dot(vec1, vec2) / (np.linalg.norm(vec1) * np.linalg.norm(vec2))
    
    def get_model_prediction(self, k1=0.6, k2=0.8, k3=0.5):
        model_embedding = self.embedding_for_model_prediction(input_format='model', context_prop = k1)
        data_embedding = self.embedding_for_model_prediction(input_format='data', context_prop = k2, data_augmentation='1')

        model_prediction = {}
        for k in data_embedding:
            model_prediction[k] = {}
            model_prediction[k]['label'] = self.input_text[k]['label']
            model_prediction[k]['prediction'] = []

            for m in model_embedding:
                model_prediction[k]['prediction'].append(
                    (m, self.cosSim(model_embedding[m], data_embedding[k]))
                    )

        acc = 0.0
        for k in model_prediction:
            print("="*10, k, "="*10)
            pred_index = np.argmax([x[1] for x in model_prediction[k]['prediction']])
            if model_prediction[k]['prediction'][pred_index][1] > k3:
                pred_label = model_prediction[k]['prediction'][pred_index][0]
            else:
                pred_label = 'trading'
            print("label groundtruth:", model_prediction[k]['label'])
            print("label predicted:", pred_label)
            print("prediction results:")
            pprint(model_prediction[k]['prediction'])
            if pred_label == model_prediction[k]['label']:
                acc += 1.0
            else:
                # print("\"{}\":\t\t {} -> {}".format(k, model_prediction[k]['label'], pred_label))
                pass
        print("\nmodel prediction accuracy: {}".format(acc/len(model_prediction)))

