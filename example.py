from model import (
    GenerateRandomProbability,
    DiscreteDistribution,
    ConditionalProbability,
    Node,
    BayesianNetwork,
    ModelParser,
)
from graph import UnweightedDirectionAdjacencyMatrix, TopoSortAlgorithm


def fromExample():
    PD = DiscreteDistribution("D", [0.6, 0.4], (1, 2), ["Easy", "Hard"])
    nodeP = Node.fromSample(PD)
    PI = DiscreteDistribution("I", [0.7, 0.3], (1, 2), ["Low", "High"])
    nodeI = Node.fromSample(PI)
    PS = ConditionalProbability(
        "S", [0.95, 0.05, 0.2, 0.8], (2, 2), ["Low", "High"], ["I"]
    )
    PS.setConditionalFeatures({PI.name: PI.features})
    nodeS = Node.fromSample(PS)
    PG = ConditionalProbability(
        "G",
        [0.3, 0.4, 0.3, 0.05, 0.25, 0.7, 0.9, 0.08, 0.02, 0.5, 0.3, 0.2],
        (2, 2, 3),
        ["A", "B", "C"],
        ["D", "I"],
    )
    PG.setConditionalFeatures({PI.name: PI.features, PD.name: PD.features})
    nodeG = Node.fromSample(PG)
    PL = ConditionalProbability(
        "L", [0.1, 0.9, 0.4, 0.6, 0.99, 0.01], (3, 2), ["Weak", "Strong"], ["G"]
    )
    PL.setConditionalFeatures({PG.name: PG.features})
    nodeL = Node.fromSample(PL)

    network = BayesianNetwork()
    network.addPath(nodeG, nodeL)
    network.addPath(nodeI, nodeS)
    network.addPath(nodeP, nodeG)
    network.addPath(nodeI, nodeG)
    samples = network.forward()
    print(network.forwardStats({"G": "A"}, None))
    print(network.forwardStats({"G": "B"}, None))
    print(network.forwardStats({"G": "C"}, None))
    print(network.forwardStats({"L": "Strong"}, {"I": "Low", "D": "Hard"}))
    print(network.forwardStats({"L": "Weak"}, {"I": "Low", "D": "Hard"}))
    print(network.forwardStats({"D": "Easy"}, {"L": "Strong"}))
    print(network.forwardStats({"D": "Easy"}, {"L": "Weak"}))


def fromTxt():
    parser = ModelParser("model.txt")
    parser.parse()

    nodes = parser.getNodes()
    network = BayesianNetwork()
    for name, node in nodes.items():
        if not node.isCondition():
            continue

        node.setConditionalFeatures(
            {
                nodes[condition].name: nodes[condition].features
                for condition in node.conditions
            }
        )

        for condition in node.conditions:
            network.addPath(nodes[condition], node)

    samples = network.forward()
    print(network.forwardStats({"G": "A"}, None))
    print(network.forwardStats({"G": "B"}, None))
    print(network.forwardStats({"G": "C"}, None))
    print(network.forwardStats({"L": "Strong"}, {"I": "Low", "D": "Hard"}))
    print(network.forwardStats({"L": "Weak"}, {"I": "Low", "D": "Hard"}))
    print(network.forwardStats({"D": "Easy"}, {"L": "Strong"}))
    print(network.forwardStats({"D": "Easy"}, {"L": "Weak"}))


fromTxt()
