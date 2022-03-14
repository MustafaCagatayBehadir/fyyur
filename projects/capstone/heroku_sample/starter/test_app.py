import unittest
import json
import os
from app import create_app


class CapstoneTestCase(unittest.TestCase):
    """This class represents the capstone test case"""

    def setUp(self):
        """Define test variables and initialize app."""
        self.app = create_app()
        self.client = self.app.test_client
        self.level1_header = {
            'Content-Type': 'application/json',
            'Accept': 'application/json',
            'Authorization': f'Bearer {os.environ["level1_token"]}'
        }
        self.admin_header = {
            'Content-Type': 'application/json',
            'Accept': 'application/json',
            'Authorization': f'Bearer {os.environ["admin_token"]}'
        }
        self.new_node = {
            "fabric": "avr-dss1-lbox-yaani-fabric",
            "hostname": "AVR-DSS1-BIP-SPN-SW-03",
            "role": "spine",
            "type": None,
            "vpc-id": None
        }
        self.update_node = {
            "vpc-id": 1
        }

    def test_001_401_get_nodes(self):
        res = self.client().get('/nodes')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 401)
        self.assertEqual(data['message'], 'Authorization header is expected.')
        self.assertEqual(data['success'], False)

    def test_002_level1_get_nodes(self):
        res = self.client().get('/nodes', headers=self.level1_header)
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertTrue(len(data['nodes']))
        self.assertTrue(data['total_nodes'])

    def test_003_level_1_get_nodegroups(self):
        res = self.client().get('/nodegroups', headers=self.level1_header)
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertTrue(len(data['nodegroups']))
        self.assertTrue(data['total_nodegroups'])

    def test_004_405_get_nodes(self):
        res = self.client().get('/nodes/1', headers=self.level1_header)
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 405)
        self.assertEqual(data['message'], 'method not allowed')
        self.assertEqual(data['success'], False)

    def test_005_405_get_nodegroups(self):
        res = self.client().get('/nodegroups/1', headers=self.level1_header)
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 405)
        self.assertEqual(data['message'], 'method not allowed')
        self.assertEqual(data['success'], False)

    def test_006_403_level_1_create_nodes(self):
        res = self.client().post('/nodes', json=self.new_node, headers=self.level1_header)
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 403)
        self.assertEqual(data['message'], 'Permission not found.')
        self.assertEqual(data['success'], False)

    def test_007_403_level_1_delete_node(self):
        res = self.client().delete('/nodes/10', headers=self.level1_header)
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 403)
        self.assertEqual(data['message'], 'Permission not found.')
        self.assertEqual(data['success'], False)

    def test_008_admin_create_node(self):
        res = self.client().post('/nodes', json=self.new_node, headers=self.admin_header)
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 201)
        self.assertTrue(data['created'])
        self.assertTrue(len(data['nodes']))
        self.assertTrue(data['total_nodes'])
        self.assertEqual(data['success'], True)

    def test_009_admin_update_node(self):
        res = self.client().patch('/nodes/5', json=self.update_node, headers=self.admin_header)
        data = json.loads(res.data)

        self.assertTrue(len(data['node']))
        self.assertEqual(data['success'], True)

    def test_010_admin_delete_nodegroups(self):
        res = self.client().delete('/nodegroups/5', headers=self.admin_header)
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 404)
        self.assertEqual(data['message'], 'resource not found')
        self.assertEqual(data['success'], False)

    def tearDown(self):
        """Executed after reach test"""
        pass


# Make the tests conveniently executable
if __name__ == "__main__":
    unittest.main(verbosity=2)
