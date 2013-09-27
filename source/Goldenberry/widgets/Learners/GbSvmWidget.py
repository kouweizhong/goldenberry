# coding=utf-8
"""
<name>SVM</name>
<description>Support Vector Machines learner/classifier.</description>
<icon>icons/SVM.svg</icon>
<priority>100</priority>
"""

from Orange.OrangeWidgets.Classify.OWSVM import OWSVM
from Goldenberry.widgets import GbKernel
from Orange.OrangeWidgets.OWGUI import appendRadioButton
from orange import ExampleTable, Learner, Classifier
from orngWrap import PreprocessedLearner
from Orange.OrangeWidgets.OWWidget import Default

class GbSvmWidget(OWSVM):
    
    def __init__(self, parent=None, signalManager=None):
        super(GbSvmWidget, self).__init__(parent=parent, signalManager=None, name="SVM")
        appendRadioButton(self.kernelradio, self,"kernel_type","Custom")
        self.inputs = [('Kernel Function', GbKernel, self.set_kernel), ("Data", ExampleTable, self.setData),
                       ("Preprocess", PreprocessedLearner, self.setPreprocessor)]

        self.outputs = [("Learner", Learner, Default),
                        ("Classifier", Classifier, Default),
                        ("Support Vectors", ExampleTable)]

        self.settingsList.append("kernel_func")
        self.kernel_func = None

    def set_kernel(self, kernel):
        self.kernel_func = kernel

    ##TODO: Wrap kernel into a SVM kernel
        
    def search_(self):
        learner=orngSVM.SVMLearner()
        for attr in ("name", "kernel_type", "degree", "shrinking", "probability", "normalization"):
            setattr(learner, attr, getattr(self, attr))

        for attr in ("gamma", "coef0", "C", "p", "eps", "nu"):
            setattr(learner, attr, float(getattr(self, attr)))

        learner.svm_type=0

        if self.useNu:
            learner.svm_type=1
        params=[]
        if self.useNu:
            params.append("nu")
        else:
            params.append("C")
        if self.kernel_type in [1,2]:
            params.append("gamma")
        if self.kernel_type==1:
            params.append("degree")
        if self.kernel_type == 4 and self.kernel_func is None: 
            params.append("kernel_type")
        try:
            learner.tuneParameters(self.data, params, 4, verbose=0,
                                   progressCallback=self.progres)
        except UnhandledException:
            pass
        for param in params:
            setattr(self, param, getattr(learner, param))
            
        self.finishSearch()
