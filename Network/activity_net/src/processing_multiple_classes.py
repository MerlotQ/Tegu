import numpy as np


def get_classification(sequence_class_prob, k=3):
    ''' From predicted classes for a sequence of clips corresponfing to a video, it
    returns the top k classes and its respective scores
    '''
    class_prob = np.mean(sequence_class_prob, axis=0)
    labels_index = np.argsort(class_prob[1:])[::-1] + 1
    scores = class_prob[labels_index] / np.sum(class_prob[1:])
    return labels_index[:k], scores[:k]


def smoothing(x, k=5):
    ''' Applies a mean filter to an input sequence. The k value specifies the window
    size. window size = 2*k
    '''
    l = len(x)
    s = np.arange(-k, l - k)
    e = np.arange(k, l + k)
    s[s < 0] = 0
    e[e >= l] = l - 1
    y = np.zeros(x.shape)
    for i in range(l):
        y[i] = np.mean(x[s[i]:e[i]], axis=0)
    return y


def activity_localization(sequence_class_prob, activity_threshold=.2):
    ''' From predicted classes probability return a sequence of temporal intervals
    where activities might be happening '''
    activities_idx = []
    scores = []
    startings = []
    endings = []
    activity_idx, _ = get_classification(sequence_class_prob)
    #activity_idx = activity_idx[0]
    for ac_index in activity_idx:
        activity_prob = sequence_class_prob[:, ac_index]
        activity_tag = np.zeros(activity_prob.shape)
        activity_tag[activity_prob >= activity_threshold] = 1

        assert activity_tag.ndim == 1
        padded = np.pad(activity_tag, pad_width=1, mode='constant')
        dif = padded[1:] - padded[:-1]

        indexes = np.arange(dif.size).astype(np.float32)
        starting = indexes[dif == 1]
        starting = starting.tolist()
        ending = indexes[dif == -1]
        ending = ending.tolist()
        assert len(starting) == len(ending)
        for segment in zip(starting, ending):
            s, e = map(int, segment) 
            activities_idx.append(ac_index)
            scores.append(np.mean(sequence_class_prob[s:e, activity_idx]))
            
        startings = startings + starting
        endings = endings + ending
    return activities_idx, startings, endings, scores
