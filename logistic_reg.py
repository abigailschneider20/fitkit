import numpy 
import matplotlib.pyplot as plt
import pandas

def load_data(path):
    df = pandas.read_csv(path)
    df = pandas.DataFrame(df)
    return df


if __name__=='__main__':

    #loads data from CSVs for PHQ vs. biometric variables

    rhrphqdata = load_data(r"rhrphq")
    print(rhrphqdata.shape)
    print(list(rhrphqdata.columns))
    rhrphqdata.head()
    # exerphqdata = load_data(r"exerphq")
    # sedphqdata = load_data(r"sedphq")
    # sleepphqdata = load_data(r"sleepphq")
    # stepsphqdata = load_data(r"stepsphq")

    # #loads data from CSVs for PHQ vs. biometric variables
    # rhrgaddata = load_data(r"rhrgad")
    # exergaddata = load_data(r"exergad")
    # sedgaddata = load_data(r"sedgad")
    # sleepgaddata = load_data(r"sleepgad")
    # stepsgaddata = load_data(r"stepsgad")

    # #loads data from CSVs for PHQ vs. biometric variables
    # rhrisidata = load_data(r"rhrisi")
    # exerisidata = load_data(r"exerisi")
    # sedisidata = load_data(r"sedisi")
    # sleeisidata = load_data(r"sleepisi")
    # stepsisidata = load_data(r"stepsisi")

    #fitbit data will always be compared to test data
    #start with resting hr, move on to comparing steps, mins active,
    #mins sedentary, mins sleep

    #starting with resting hr vs. phq scores/severity
    phqrhrx = rhrphqdata.iloc[:, 8]
    phqrhry = rhrphqdata.iloc[:, 1]
    phqrhr_affected = rhrphqdata.loc[phqrhry == 1]
    phqrhr_unaffected = rhrphqdata.loc[phqrhry == 0]

    plt.scatter(phqrhr_affected.iloc[:, 0], phqrhr_affected.iloc[:, 1], s=10, label ='PHQ/RHR Affected')
    plt.scatter(phqrhr_unaffected.iloc[:, 0], phqrhr_unaffected.iloc[:, 1], s=10, label = 'PHQ/RHR Unaffected')
    plt.legend()
    plt.show()