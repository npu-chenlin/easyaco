import numpy as np
import csv, json
import matplotlib.pyplot as plt

class nurse():
    mapTable = {
        "OTLevel": {
            1: "HighLevelOT",
            2: "LowLevelOT"
        },
        "NurseLevel": {
            1: "No1",
            2: "No2",
            3: "No3"
        },
        "JobType": {
            0: "HRequirement",
            1: "LRequirement"
        },
        "WorkTime": {
            0: "Morning",
            1: "Afternoon"
        }
    }

    def __init__(self, hasChild, age, level, id):
        self.hasChild = hasChild
        self.age = age
        self.level = level
        self.id = id

    def __str__(self):
        return "hasChild:%d\tage:%d\tlevel:%d\t" \
               % (self.hasChild, self.age, self.level)

    def getScore(self, operatingTheatre, conf):
        if (self.age < 40):
            agePeriod = 0
        elif (self.age < 50):
            agePeriod = 1
        else:
            agePeriod = 2

        return conf["DIFFICULTY_SCORE"][nurse.mapTable["OTLevel"][operatingTheatre.level]][
                   nurse.mapTable["JobType"][operatingTheatre.requirement]][nurse.mapTable["NurseLevel"][self.level]][
                   agePeriod] + \
               conf["TIME_SCORE"][nurse.mapTable["WorkTime"][operatingTheatre.time]][self.hasChild]


class operatingTheatre():
    def __init__(self, level, time, requirement, id):
        self.level = level  # 1 means hard 2 means easy
        self.time = time  # 0means morning 1 means afternoon
        self.requirement = requirement  # 0 means highlevel nurse,1 means lowlevel nurse
        self.id = id

    def __str__(self):
        return "level:%d\ttime%d" \
               % (self.level, self.time)

class aco():
    def __init__(self, path):
        print("Initialize ACO...\nReading conf from %s" % path)
        with open(path, "r") as f:
            self.conf = json.load(f)
        self.nurses = []
        self.operatingTheatres = []

        self.resultData = []
        self.critivalPointMatrix = []

        self.iteratorNum = self.conf["Iteration"]
        self.antNum = self.conf["AntNum"]
        self.decayRate = self.conf["DecayRate"]
        self.inceaseRate = self.conf["IncreaseNum"]
        print("Iteration:\t%d AntNum:\t%d" % (self.iteratorNum, self.antNum))
        print("DecayRate:\t%g IncreaseNum:\t%g" % (self.decayRate, self.inceaseRate))
        # read info into nurses , operatingTheatres
        with open("info.txt", "r") as f:
            while True:
                l = f.readline().strip()
                if not l:
                    break
                arr = [int(i) for i in l.split()]
                if (arr[1] > 3):
                    self.nurses.append(nurse(arr[0], arr[1], arr[2], arr[3]))
                else:
                    self.operatingTheatres.append(operatingTheatre(arr[0], arr[1], arr[2], arr[3]))

        self.nurses.sort(key=lambda nurse: nurse.level, reverse=True)
        self.operatingTheatres.sort(key=lambda operatingTheatre: operatingTheatre.level)
        self.HnurseNum = len([i for i in filter(lambda x: x.level == 1, self.nurses)])
        self.MnurseNum = len([i for i in filter(lambda x: x.level == 2, self.nurses)])
        self.LnurseNum = len([i for i in filter(lambda x: x.level == 3, self.nurses)])
        self.nurseNum = self.HnurseNum + self.MnurseNum + self.LnurseNum
        self.HOT = len([i for i in filter(lambda x: x.level == 1, self.operatingTheatres)])
        self.LOT = len([i for i in filter(lambda x: x.level == 2, self.operatingTheatres)])
        self.OTNum = self.HOT + self.LOT
        self.pheromoneMatrix = np.ones((self.OTNum, self.nurseNum))
        self.lossMatrix = self.getlossMatrix(self.nurses, self.operatingTheatres)
        print("\nNurse\nNo1:\t%d\nNo2:\t%d\nNo3:\t%d \tTotal:\t%d" % (
            self.HnurseNum, self.MnurseNum, self.LnurseNum, self.nurseNum))
        print("\nOperatingTheatre\nHighOT\t%d\nLowOT\t%d \tTotal:\t%d" % (self.HOT, self.LOT, self.OTNum))

    def acoSearch(self):
        lastBestPathMatrix = []
        for i in range(self.iteratorNum):
            rate=int(float(i+1)/self.iteratorNum*100)
            print("[" + ">" * rate + "]%d%%\r"%rate,end='')
            pathmatrix_allant = []
            self.updatecritivalPointMatrix()
            for j in range(self.antNum):
                pathmatrix_oneant = np.zeros((self.OTNum, self.nurseNum))
                self.assignNurses(pathmatrix_oneant, j)
                pathmatrix_allant.append(pathmatrix_oneant)
            if len(lastBestPathMatrix) != 0:
                pathmatrix_allant.append(lastBestPathMatrix)
            result = self.cal_scores(pathmatrix_allant)
            self.resultData.append(result)
            lastBestPathMatrix = pathmatrix_allant[np.argmin(result)]
            self.updatePheromoneMatrix(lastBestPathMatrix)
        print("\n")

    def run(self):
        self.acoSearch()
        print("Mission Complete!")
        self.bestScore = np.array([[min(i) for i in self.resultData]]) / self.nurseNum
        self.meanScore = np.array([[sum(i) / len(i) for i in self.resultData]]) / self.nurseNum
        print("Final Score:\t%g"%self.bestScore[0][-1])

    # output is a arrary containing score of each pat
    def cal_scores(self, pathmatrix_all):
        ret = []
        for i in pathmatrix_all:
            ret.append((i * self.lossMatrix).sum())
        return ret

    def getlossMatrix(self, nurses, operatingTheatres):
        ret = np.zeros((self.OTNum, self.nurseNum))
        for index_i, value_i in enumerate(self.operatingTheatres):
            for index_j, value_j in enumerate(self.nurses):
                ret[index_i][index_j] = value_j.getScore(value_i, self.conf)
        return ret

    # assign one nurse for OT
    def assignNurses(self, pathmatrix, antIndex):
        for OTIndex in range(self.OTNum):
            if (antIndex < self.critivalPointMatrix[-self.OTNum + OTIndex]):
                m = self.pheromoneDistribute(pathmatrix, OTIndex)
            else:
                m = self.randomDistribute(pathmatrix, OTIndex)
            pathmatrix[OTIndex][m] = 1

    def randomDistribute(self, pathmatrix, otindex):
        if (self.operatingTheatres[otindex].level == 1) and (self.operatingTheatres[otindex].requirement == 0):
            ret = np.arange(self.HnurseNum + self.MnurseNum)
            np.random.shuffle(ret)
            ret = list(ret)
            n = ret.pop()
            while pathmatrix.sum(0)[n] >= 1:
                n = ret.pop()
            return n
        else:
            ret = np.arange(self.nurseNum)
            np.random.shuffle(ret)
            ret = list(ret)
            n = ret.pop()
            while pathmatrix.sum(0)[n] >= 1:
                n = ret.pop()
        return n

    def pheromoneDistribute(self, pathmatrix, otindex):
        if (self.operatingTheatres[otindex].level == 1) and (self.operatingTheatres[otindex].requirement == 0):
            ret = self.pheromoneMatrix[otindex][:self.HnurseNum + self.MnurseNum].argsort()
            th = 1
            while pathmatrix.sum(0)[ret[-th]] >= 1:
                th += 1
            return ret[-th]
        else:
            ret = self.pheromoneMatrix[otindex].argsort()
            th = 1
            while pathmatrix.sum(0)[ret[-th]] >= 1:
                th += 1
            return ret[-th]

    def updatePheromoneMatrix(self, pathmatrix):
        self.pheromoneMatrix *= self.decayRate
        self.pheromoneMatrix[pathmatrix == 1] += self.inceaseRate

    def updatecritivalPointMatrix(self, ):
        for i in range(self.HOT):
            is_allsame = (len(set(self.pheromoneMatrix[i])) == 1)
            if is_allsame:
                self.critivalPointMatrix.append(0)
                continue
            pheromoneMatrixSorted = sorted(self.pheromoneMatrix[i][:self.HnurseNum + self.MnurseNum])
            self.critivalPointMatrix.append(int(self.antNum * pheromoneMatrixSorted[-1] / sum(pheromoneMatrixSorted)))

        for i in range(self.LOT):
            is_allsame = (len(set(self.pheromoneMatrix[i + self.HOT])) == 1)
            if is_allsame:
                self.critivalPointMatrix.append(0)
                continue
            pheromoneMatrixSorted = sorted(self.pheromoneMatrix[i + self.HOT])
            self.critivalPointMatrix.append(int(self.antNum * pheromoneMatrixSorted[-1] / sum(pheromoneMatrixSorted)))

    def saveData(self):
        pathM = np.zeros_like(self.pheromoneMatrix)
        r = []
        for i in range(self.OTNum):
            m = self.pheromoneDistribute(pathM, i)
            pathM[i][m] = 1
            r.append([self.operatingTheatres[i].id,self.nurses[m].id])
        with open("output.csv", "w", newline='') as f:
            excel_writer = csv.writer(f)
            excel_writer.writerows(self.bestScore)
            excel_writer.writerows(self.meanScore)
            excel_writer.writerows(r)
            # excel_writer.writerows(pathM)
            # print(pathM)
if __name__ == "__main__":
    confPath = "./conf.json"
    conf = aco(confPath)
    conf.run()
    conf.saveData()
    plt.xlabel("Iteration")
    plt.ylabel("Score")
    for index,value in enumerate(conf.resultData):
        plt.scatter(np.ones_like(value)*index,np.array(value)/conf.nurseNum,s=10,c='r',marker='.')
    plt.plot(conf.bestScore[0],label="bestScore")
    plt.plot(conf.meanScore[0],label="meanScore")
    plt.legend(["bestScore","meanScore"])
    plt.savefig("results.png")
    plt.show()