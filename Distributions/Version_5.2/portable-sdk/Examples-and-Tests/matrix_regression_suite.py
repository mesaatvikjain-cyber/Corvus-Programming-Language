import sys
import os
import unittest

# Add Interpreter directory to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'Interpreter')))

from lexercorvus import tokenize
from parsercorvus import Parser
from evaluatorcorvus import Evaluator, Environment
from errors import CorvusError
from std_memory import _global_mem_manager
from std_concurrency import _global_crow_engine
from std_net import _global_net_engine
from std_json import _global_json_engine

class TestCorvusMatrix(unittest.TestCase):
    def setUp(self):
        self.env = Environment()
        self.evaluator = Evaluator(self.env)

    def run_code(self, code_str):
        tokens = tokenize(code_str)
        parser = Parser(tokens)
        ast = parser.parse()
        return self.evaluator.evaluate(ast)

    # 1. Syntax & Variable Declarations
    def test_variables_and_constants(self):
        self.run_code('var x = 10\nx = 25')
        self.assertEqual(self.env.get('x'), 25)
        self.run_code('set const; PI = 3.14')
        self.assertEqual(self.env.get('PI'), 3.14)

    # 2. Control Flow & Match Statements
    def test_control_flow(self):
        self.run_code('''
var score = 90
var result = ""
if (score >= 90) [
    result = "PASSED"
] else [
    result = "FAILED"
]
''')
        self.assertEqual(self.env.get('result'), "PASSED")

    # 3. Functions & Recursion
    def test_functions_and_recursion(self):
        self.run_code('''
func factorial(n) [
    if (n <= 1) [ givout 1 ]
    givout n * factorial(n - 1)
]
var fact5 = factorial(5)
''')
        self.assertEqual(self.env.get('fact5'), 120)

    # 4. Functional Pipeline Operator
    def test_pipeline_operator(self):
        self.run_code('''
func double(x) [ givout x * 2 ]
func add_five(x) [ givout x + 5 ]
var res = 10 |> double |> add_five
''')
        self.assertEqual(self.env.get('res'), 25)

    # 5. Native JSON StdLib
    def test_json_module(self):
        parsed = _global_json_engine.parse('{"lang": "Corvus", "version": 4.2}')
        self.assertEqual(parsed["lang"], "Corvus")
        self.assertEqual(parsed["version"], 4.2)
        stringified = _global_json_engine.stringify(parsed)
        self.assertIn("Corvus", stringified)

    # 6. Memory Management, Cycle Collector & Weak References
    def test_memory_cycles_and_weakref(self):
        ptr = _global_mem_manager.alloc(64)
        self.assertIn("0x", ptr)
        self.assertTrue(_global_mem_manager.free(ptr))

        # Test Cycle Detection
        cycles_info = _global_mem_manager.detect_cycles()
        self.assertIn("status", cycles_info)

        # Test Weak Reference
        target_obj = [1, 2, 3]
        wref = _global_mem_manager.weak_ref(target_obj)
        self.assertEqual(_global_mem_manager.de_weak(wref), [1, 2, 3])

    # 7. Murder of Crows Concurrency Engine
    def test_murder_of_crows_engine(self):
        # Test parallel_map
        results = _global_crow_engine.parallel_map(lambda x: x * 2, [1, 2, 3, 4])
        self.assertEqual(results, [2, 4, 6, 8])

        # Test CrowChannel
        ch = _global_crow_engine.channel()
        ch.send("crow_msg")
        self.assertEqual(ch.recv(), "crow_msg")

    # 8. Native Networking Engine (HTTP GET mock test)
    def test_net_module_structure(self):
        res = _global_net_engine.http_get("https://httpbin.org/get")
        self.assertIn("status", res)

if __name__ == "__main__":
    print("=========================================================")
    print("   Running Corvus Master Matrix Regression Test Suite   ")
    print("=========================================================")
    unittest.main()
