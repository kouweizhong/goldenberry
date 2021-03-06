"""
<name>BMDA</name>
<description>Bivariate marginal distribution algorithm.</description>
<contact>Nestor Rodriguez</contact>
<icon>icons/Bmda.svg</icon>
<priority>80</priority>

"""

from Goldenberry.widgets.optimization.GbBaseEdaWidget import GbBaseEdaWidget
from Goldenberry.widgets import Bmda, GbCostFunction, GbBaseOptimizer, OWGUI, Qt, DependencyMethod, GbSolution, QStandardItem, QStandardItemModel, QString, QHeaderView, QDoubleValidator

class GbBmdaWidget(GbBaseEdaWidget):
    """Widget for Bmda algorithm"""
    
    def __init__(self, parent=None, signalManager=None):
        self.method = 0
        self.threshold = 3.84
        self.optimizer = Bmda()
        GbBaseEdaWidget.__init__(self, parent, signalManager, 'BMDA')
        self.inputs = [("Cost Function", GbCostFunction, self.set_cost_function)]
        self.outputs = [("Optimizer", GbBaseOptimizer), ("Solution", GbSolution)]
        self.settingsList.append('method')

        radio_box = OWGUI.radioButtonsInBox(self, self, "method",
              box = "Dependency Method",
              btnLabels = ["Chi square", "Mutual information", "Combined mutual information and p-value"], callback = self.method_changed)
        self.threshold_textbox = OWGUI.lineEdit(radio_box, self, "threshold", label="Dependency strength threshold",valueType = float, validator = QDoubleValidator(0.0, 10000.0, 4, self.controlArea))
        #radio_box.layout().addWidget(self.threshold_textbox.box)
        self.verticalLayoutWidget.layout().addWidget(radio_box)
        self.attributesTree.header().setResizeMode(QHeaderView.ResizeToContents)


    def setup_optimizer(self):
        self.optimizer.setup(self.cand_size, max_evals = self.max_evals, dependency_method = DependencyMethod()[self.method], independence_threshold = self.threshold)

    def method_changed(self):
        if self.method == 0:
            self.threshold_textbox.setText("3.84")
        else:
            self.threshold_textbox.setText("0.0")

    def search_progress(self, progress_args):
        super(GbBmdaWidget, self).search_progress(progress_args)
        self.update_attributes_navigation(progress_args.result, self.attributesTree)
    
    def run(self):
        super(GbBmdaWidget, self).run()
        self._clean_tree()

    def _clean_tree(self):
        self.attributesTree.setModel(None)
          
    def update_attributes_navigation(self, solution, qtree):
        if solution is None:
            return

        model = QStandardItemModel()
        root_node = model.invisibleRootItem()
        
        # If there is a list of relevant attributes also known as the 'solution'
        att_items_list = [QStandardItem(QString('%1 (%L2)').arg(idx).arg(score)) \
                     for idx, score in enumerate(solution.params)]
            
        # Links roots with the invisible root node from the QStandardItemModel
        for root in solution.roots:
            root_node.appendRow(att_items_list[root])
            att_items_list[root].parent = root_node

        # Links children and parents
        for idx, children in enumerate(solution.children):
            for child_idx in children:
                parent = att_items_list[idx]
                child = att_items_list[child_idx]
                parent.appendRow(child)
                child.parent = parent
        
        #updates the navigation view
        qtree.setModel(model)
        qtree.expandAll()