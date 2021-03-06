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
    def __init__(self, path, iteration, antNum, decayRate, IncreaseNum):
        print("Initialize ACO...\nReading conf from %s" % path)
        with open(path, "r") as f:
            self.conf = json.load(f)
        self.nurses = []
        self.operatingTheatres = []

        self.resultData = []
        self.critivalPointMatrix = []

        self.iteratorNum = iteration
        self.antNum = antNum
        self.decayRate = decayRate
        self.inceaseRate = IncreaseNum
        self.rate = 0
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
        self.HnurseNum = len([i for i in filter(lambda x: x.level == 3, self.nurses)])
        self.MnurseNum = len([i for i in filter(lambda x: x.level == 2, self.nurses)])
        self.LnurseNum = len([i for i in filter(lambda x: x.level == 1, self.nurses)])
        self.nurseNum = self.HnurseNum + self.MnurseNum + self.LnurseNum
        self.HOT = len([i for i in filter(lambda x: x.level == 1, self.operatingTheatres)])
        self.LOT = len([i for i in filter(lambda x: x.level == 2, self.operatingTheatres)])
        self.OTNum = self.HOT + self.LOT
        self.pheromoneMatrix = np.ones((self.OTNum, self.nurseNum))
        self.lossMatrix = self.getlossMatrix(self.nurses, self.operatingTheatres)

    def acoSearch(self):
        lastBestPathMatrix = []
        for i in range(self.iteratorNum):
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
            self.rate = int(float(i + 1) / self.iteratorNum * 100)

    def run(self):
        self.rate = 0
        self.resultData = []
        self.critivalPointMatrix = []
        self.pheromoneMatrix = np.ones((self.OTNum, self.nurseNum))

        self.acoSearch()
        print("Mission Complete!")
        self.bestScore = np.array([[min(i) for i in self.resultData]]) / self.nurseNum
        self.meanScore = np.array([[sum(i) / len(i) for i in self.resultData]]) / self.nurseNum
        print("Final Score:\t%g" % self.bestScore[0][-1])

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
        for i in filter(lambda x: x.requirement == 0, self.operatingTheatres):
            OTIndex = self.operatingTheatres.index(i)
            if (antIndex < self.critivalPointMatrix[-self.OTNum + OTIndex]):
                m = self.h_pheromoneDistribute(pathmatrix, OTIndex)
            else:
                m = self.h_randomDistribute(pathmatrix)
            pathmatrix[OTIndex][m] = 1
        for i in filter(lambda x: x.requirement == 1, self.operatingTheatres):
            OTIndex = self.operatingTheatres.index(i)
            if (antIndex < self.critivalPointMatrix[-self.OTNum + OTIndex]):
                m = self.l_pheromoneDistribute(pathmatrix, OTIndex)
            else:
                m = self.l_randomDistribute(pathmatrix)
            pathmatrix[OTIndex][m] = 1

    def h_pheromoneDistribute(self,pathmatrix, OTIndex):
            ret = self.pheromoneMatrix[OTIndex][:self.HnurseNum + self.MnurseNum].argsort()
            th = 1
            while pathmatrix.sum(0)[ret[-th]] >= 1:
                th += 1
            return ret[-th]

    def h_randomDistribute(self,pathmatrix):
        ret = np.arange(self.HnurseNum + self.MnurseNum)
        np.random.shuffle(ret)
        ret = list(ret)
        n = ret.pop()
        while pathmatrix.sum(0)[n] >= 1:
            n = ret.pop()
        return n
    def l_pheromoneDistribute(self,pathmatrix, OTIndex):
            ret = self.pheromoneMatrix[OTIndex].argsort()
            th = 1
            while pathmatrix.sum(0)[ret[-th]] >= 1:
                th += 1
            return ret[-th]
    def l_randomDistribute(self,pathmatrix):
        ret = np.arange(self.nurseNum)
        np.random.shuffle(ret)
        ret = list(ret)
        n = ret.pop()
        while pathmatrix.sum(0)[n] >= 1:
            n = ret.pop()
        return n

    def updatePheromoneMatrix(self, pathmatrix):
        self.pheromoneMatrix *= self.decayRate
        self.pheromoneMatrix[pathmatrix == 1] += self.inceaseRate

    def updatecritivalPointMatrix(self):
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
        r = [["OTId", "OTRequirement", "OTLevel", "NurseId", "NurseAge", "NurseLevel", "Score"]]
        self.assignNurses(pathM, -1)
        for i in range(self.OTNum):
            for m in range(self.nurseNum):
                if(pathM[i][m] == 1):
                    r.append([self.operatingTheatres[i].id, self.operatingTheatres[i].requirement,
                              self.operatingTheatres[i].level,self.nurses[m].id, self.nurses[m].age,
                              self.nurses[m].level, self.lossMatrix[i][m]])
                    break
        with open("output.csv", "w", newline='') as f:
            excel_writer = csv.writer(f)
            excel_writer.writerows(self.bestScore)
            excel_writer.writerows(self.meanScore)
            excel_writer.writerows(r)
            # excel_writer.writerows(pathM)
            # print(pathM)

    def drawImg(self, isRatioButtonOn, path="./src/results.png"):
        plt.cla()
        plt.subplot(111)
        plt.xlabel("Iteration")
        plt.ylabel("Score")
        legends = np.array(["bestScore", "meanScore", "Scatters"])
        if isRatioButtonOn[0]:
            plt.plot(self.bestScore[0], label="bestScore", color="#ef4026")
        if isRatioButtonOn[1]:
            plt.plot(self.meanScore[0], label="meanScore", color="#840000")
        if isRatioButtonOn[2]:
            for index, value in enumerate(self.resultData):
                plt.scatter(np.ones_like(value) * index, np.array(value) / self.nurseNum, s=10, c="#b1d1fc", marker='.')
        plt.legend(legends[np.array(isRatioButtonOn)==True])
        plt.savefig(path)


if __name__ == "__main__":
    confPath = "./conf.json"
    conf = aco(confPath)
    conf.run()
    conf.saveData()
    conf.drawImg()
