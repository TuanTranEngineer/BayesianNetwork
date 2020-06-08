import test
import unittest

def main():
    runner = unittest.TextTestRunner()

    print("Running unit test for Adjacency matrix class")
    runner.run(test.AdjacencyMatrixTestSuite())

    print("Running unit test for Stack class")
    runner.run(test.StackTestSuite())

    print("Running unit test for Queue class")
    runner.run(test.QueueTestSuite())

if __name__ == "__main__":
    main()