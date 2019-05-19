import numpy as np
import random
import sys, csv


class nurse():
    DIFFICULTY_SCORE = {
        1: {
            0: {
                1: [100, 100, 100],
                2: [2, 4, 5],
                3: [1, 3, 5]
            },  # hardwork
            1: {
                1: [3, 3, 3],
                2: [3, 3, 3],
                3: [3, 3, 3]
            }  # easywork
        },  # Hot
        2: {
            0: {
                1: [3, 3, 3],
                2: [3, 3, 3],
                3: [4, 3, 2]
            },  # hard
            1: {
                1: [3, 3, 3],
                2: [3, 3, 3],
                3: [3, 3, 3]
            }  # easywork
        }  # Lot
    }
    TIME_SCORE = {
        0: [3, 3],
        1: [1, 5]
    }

    def __init__(self, hasChild, age, level, id):
        self.hasChild = hasChild
        self.age = age
        self.level = level
        self.id = id

    def __str__(self):
        return "hasChild:%d\tage:%d\tlevel:%d\t" \
               % (self.hasChild, self.age, self.level)

    def getScore(self, operatingTheatre):
        if (self.age < 40):
            agePeriod = 0
        elif (self.age < 50):
            agePeriod = 1
        else:
            agePeriod = 2

        return nurse.DIFFICULTY_SCORE[operatingTheatre.level][operatingTheatre.requirement][self.level][agePeriod] + \
               nurse.TIME_SCORE[self.hasChild][operatingTheatre.time]


class operatingTheatre():
    def __init__(self, level, time, requirement, id):
        self.level = level  # 1 means hard 2 means easy
        self.time = time  # 0means morning 1 means afternoon
        self.requirement = requirement  # 0 means highlevel nurse,1 means lowlevel nurse
        self.id = id

    def __str__(self):
        return "level:%d\ttime%d" \
               % (self.level, self.time)


def getlossMatrix(nurses, operatingTheatres):
    ret = np.zeros((OTNum, nurseNum))
    for index_i, value_i in enumerate(operatingTheatres):
        for index_j, value_j in enumerate(nurses):
            ret[index_i][index_j] = value_j.getScore(value_i)
    return ret


# assign one nurse for OT
def assignNurses(pheromonematrix, pathmatrix, antIndex):
    for OTIndex in range(OTNum):
        if (antIndex < critivalPointMatrix[-OTNum + OTIndex]):
            m = pheromoneDistribute(pheromonematrix, pathmatrix, OTIndex)
        else:
            m = randomDistribute(pathmatrix, OTIndex)
        pathmatrix[OTIndex][m] = 1


def randomDistribute(pathmatrix, otindex):
    if (operatingTheatres[otindex].level == 1) and (operatingTheatres[otindex].requirement == 0):
        ret = np.arange(HnurseNum + MnurseNum)
        np.random.shuffle(ret)
        ret = list(ret)
        n = ret.pop()
        while pathmatrix.sum(0)[n] >= 1:
            n = ret.pop()
        return n
    else:
        ret = np.arange(nurseNum)
        np.random.shuffle(ret)
        ret = list(ret)
        n = ret.pop()
        while pathmatrix.sum(0)[n] >= 1:
            n = ret.pop()
    return n


def pheromoneDistribute(pheromonematrix, pathmatrix, otindex):
    if (operatingTheatres[otindex].level == 1) and (operatingTheatres[otindex].requirement == 0):
        ret = pheromonematrix[otindex][:HnurseNum + MnurseNum].argsort()
        th = 1
        while pathmatrix.sum(0)[ret[-th]] >= 1:
            th += 1
        return ret[-th]
    else:
        ret = pheromonematrix[otindex].argsort()
        th = 1
        while pathmatrix.sum(0)[ret[-th]] >= 1:
            th += 1
        return ret[-th]


def updatePheromoneMatrix(pheromoneMatrix, pathmatrix):
    pheromoneMatrix *= decayRate
    pheromoneMatrix[pathmatrix == 1] += inceaseRate


def updatecritivalPointMatrix(critivalPointMatrix, pheromoneMatrix):
    for i in range(HOT):
        is_allsame = (len(set(pheromoneMatrix[i])) == 1)
        if is_allsame:
            critivalPointMatrix.append(0)
            continue
        pheromoneMatrixSorted = sorted(pheromoneMatrix[i][:HnurseNum + MnurseNum])
        critivalPointMatrix.append(int(antNum * pheromoneMatrixSorted[-1] / sum(pheromoneMatrixSorted)))

    for i in range(LOT):
        is_allsame = (len(set(pheromoneMatrix[i + HOT])) == 1)
        if is_allsame:
            critivalPointMatrix.append(0)
            continue
        pheromoneMatrixSorted = sorted(pheromoneMatrix[i + HOT])
        critivalPointMatrix.append(int(antNum * pheromoneMatrixSorted[-1] / sum(pheromoneMatrixSorted)))


# output is a arrary containing score of each path
def cal_scores(pathmatrix_all):
    ret = []
    for i in pathmatrix_all:
        ret.append((i * lossMatrix).sum())
    return ret


def acoSearch(iteratorNum, antNum):
    for i in range(iteratorNum):
        print(i)
        pathmatrix_allant = []
        updatecritivalPointMatrix(critivalPointMatrix, pheromoneMatrix)
        for j in range(antNum):
            pathmatrix_oneant = np.zeros((OTNum, nurseNum))
            assignNurses(pheromoneMatrix, pathmatrix_oneant, j)
            pathmatrix_allant.append(pathmatrix_oneant)
        result = cal_scores(pathmatrix_allant)
        resultData.append(result)
        updatePheromoneMatrix(pheromoneMatrix, pathmatrix_allant[np.argmin(result)])


if __name__ == "__main__":
    nurses = []
    operatingTheatres = []

    resultData = []
    critivalPointMatrix = []

    iteratorNum = 100
    antNum = 100

    maxPheromoneMatrix = [[]]

    decayRate = 0.7
    inceaseRate = 0.1

    # read info into nurses , operatingTheatres
    with open("info.txt", "r") as f:
        while True:
            l = f.readline().strip()
            if not l:
                break
            arr = [int(i) for i in l.split()]
            if (arr[1] > 3):
                nurses.append(nurse(arr[0], arr[1], arr[2], arr[3]))
            else:
                operatingTheatres.append(operatingTheatre(arr[0], arr[1], arr[2], arr[3]))
    nurses.sort(key=lambda nurse: nurse.level, reverse=True)
    operatingTheatres.sort(key=lambda operatingTheatre: operatingTheatre.level)
    HnurseNum = len([i for i in filter(lambda x: x.level == 1, nurses)])
    MnurseNum = len([i for i in filter(lambda x: x.level == 2, nurses)])
    LnurseNum = len([i for i in filter(lambda x: x.level == 3, nurses)])
    nurseNum = HnurseNum + MnurseNum + LnurseNum
    HOT = len([i for i in filter(lambda x: x.level == 1, operatingTheatres)])
    LOT = len([i for i in filter(lambda x: x.level == 2, operatingTheatres)])
    OTNum = HOT + LOT
    pheromoneMatrix = np.ones((OTNum, nurseNum))
    lossMatrix = getlossMatrix(nurses, operatingTheatres)

    acoSearch(iteratorNum, antNum)
    print("H,M,L nurseNum:%d,%d,%d,sum: %d" % (HnurseNum, MnurseNum, LnurseNum, nurseNum))
    print("H,L otNum:%d,%d,sum: %d" % (HOT, LOT, OTNum))
    pathM = np.zeros_like(pheromoneMatrix)
    for i in range(OTNum):
        m = pheromoneDistribute(pheromoneMatrix, pathM, i)
        pathM[i][m] = 1

    bestresults = np.array([[min(i) for i in resultData]]) / nurseNum
    resultData = np.array(resultData).transpose() / nurseNum
    meanresults = [resultData.sum(0) / antNum]
    # print(paintData)
    # print(results)
    # print(results)
    with open("output.csv", "w", newline='') as f:
        excel_writer = csv.writer(f)
        excel_writer.writerows(bestresults)
        excel_writer.writerows(meanresults)
        # excel_writer.writerows(pathM)
        # print(pathM)
