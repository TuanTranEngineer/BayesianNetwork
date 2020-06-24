from graph import UnweightedDirectionAdjacencyMatrix, TopoSortAlgorithm
from copy import deepcopy
from .nodes import Node
from common import timeExecute
from .generator import GenerateRandomProbability
from functools import partial
from typing import (
    Dict,
    Optional,
    Generic,
    Generator,
    TypeVar,
    List,
    Set,
    Tuple,
    Hashable,
    Any,
    Union,
)
import multiprocessing
import time


def workers(n):
    pass


class BayesianNetwork(UnweightedDirectionAdjacencyMatrix):
    def __init__(self, initializedSamples: int = 1000000):
        super().__init__(None)
        self.__generator: GenerateRandomProbability = GenerateRandomProbability()
        self.__initSamples: int = initializedSamples
        self.__nodeTable: Dict[str, V] = dict()
        self.__topoNodes: Optional[List[Node]] = None
        self.__samples: Optional[List[Dict[str, str]]] = None

    def addNewNode(self, node: Node) -> None:
        if not isinstance(node, Node):
            raise Exception("input object is not a Node")
        super().addNewNode(node)
        self.__nodeTable[node.name] = node

    @timeExecute
    def __generateSample(self, nSamples: int) -> Dict[str, str]:
        samples = []
        for _ in range(nSamples):
            state: Dict[str, str] = dict()
            for node in self.__topoNodes:
                sample = node.generateSample(state)
                state[node.name] = sample
            samples.append(state)
        return samples

    @timeExecute
    def generateSamples(self, steps=-1) -> List[Dict[str, str]]:
        if len(self.vertexSet()) == 0:
            raise Exception("Graph haven't been initialized!")
        if self.__topoNodes is None:
            topo: TopoSortAlgorithm = TopoSortAlgorithm(self)
            self.__topoNodes = [node for node in topo.bfs()]
        samples: List[Dict[str, str]] = []
        if steps < 0:
            steps = self.__initSamples
        global workers

        def workers(nSamples):
            return self.__generateSample(nSamples)

        numPool = multiprocessing.cpu_count()
        samplesList = [int(steps / numPool) + 1 for _ in range(numPool)]

        pool = multiprocessing.Pool(processes=numPool)
        outputs = pool.map(workers, samplesList)
        for i in outputs:
            samples += i
        self.__samples = samples

    def __filterSample(self, prob: Dict[str, str], record: Dict[str, str]) -> bool:
        for name, feature in prob.items():
            if name not in record:
                raise Exception("Failed to get item {} in the record".format(name))
            if feature != record[name]:
                return False
        return True

    def __samplesFiltering(
        self, samples: List[Dict[str, str]], filters: Dict[str, str]
    ) -> Generator[Dict[str, str], None, None]:
        for result in filter(partial(self.__filterSample, filters), samples):
            yield result

    def __noneConditionStats(
        self, prob: Dict[str, str], samples: List[Dict[str, str]]
    ) -> float:
        cnt: int = 0
        for _ in self.__samplesFiltering(samples, prob):
            cnt += 1
        return cnt / len(samples)

    def __statsCheck(self, prob: Dict[str, str], conditions: Optional[Dict[str, str]]):
        if prob is None:
            raise Exception("No prob is required!!!")
        if self.__samples is None or len(self.__samples) == 0:
            self.generateSamples()
        if conditions is None:
            return
        for name in prob:
            if name in conditions:
                raise Exception(
                    "Invalid input, name {} duplicate in prob and conditions".format(
                        name
                    )
                )

    def forwardStats(
        self, prob: Dict[str, str], conditions: Optional[Dict[str, str]]
    ) -> float:
        self.__statsCheck(prob, conditions)
        if conditions is None:
            return self.__noneConditionStats(prob, self.__samples)
        return self.__noneConditionStats(
            prob,
            [item for item in self.__samplesFiltering(self.__samples, conditions)],
        )

    def __likelihoodSampleWeight(
        self, conditions: Dict[str, str], sample: Dict[str, str]
    ):
        w: float = 1.0
        for conditionName, conditionValue in conditions.items():
            w *= self.__nodeTable[conditionName].getProbability(sample, conditionValue)
        return sample, w

    def likelihoodStats(
        self, prob: Dict[str, str], conditions: Optional[Dict[str, str]]
    ) -> float:
        self.__statsCheck(prob, conditions)
        if conditions is None:
            return self.__noneConditionStats(prob, self.__samples)

        totalw: float = 0.0
        conditionw: float = 0.0
        for sample, w in map(
            partial(self.__likelihoodSampleWeight, conditions),
            self.__samplesFiltering(self.__samples, conditions),
        ):
            totalw += w
            if self.__filterSample(prob, sample):
                conditionw += w
        if totalw == 0.0:
            return 0.0
        return conditionw / totalw
