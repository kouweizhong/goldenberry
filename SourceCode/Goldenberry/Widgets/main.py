from Optimization.GbCgaWidget import test_widget
#from Optimization.GbCostFuncsWidget import test_widget
import sys

def main():
    try:
        
        test_widget()
        #GbCgaWidget.testWidget()
        
    except:
        print "Unexpected error:", sys.exc_info()[0]
        raise   
    
main()